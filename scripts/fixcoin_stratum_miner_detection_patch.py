#!/usr/bin/env python3
"""Add robust Stratum user-agent detection for NMMiner/NerdMiner clients.

The pinned FreeCash base does not expose a Client.handle_subscribe method.
Detection therefore hooks the actual function that dispatches
``mining.subscribe`` instead of assuming a particular upstream method name.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()
tree = ast.parse(text)
client = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Client"), None)
if client is None:
    raise RuntimeError("Client class not found")

lines = text.splitlines(keepends=True)
start = sum(map(len, lines[:client.lineno - 1]))
end = sum(map(len, lines[:client.end_lineno]))
client_text = text[start:end]
client_tree = ast.parse(client_text)

# Find the real subscribe dispatcher in the pinned upstream implementation.
# Do not assume it is named handle_subscribe: FreeCash currently dispatches
# mining methods from a generic request handler.
clines = client_text.splitlines(keepends=True)
subscribe_fn = None
for node in ast.walk(client_tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    try:
        segment = ast.get_source_segment(client_text, node) or ""
    except Exception:
        segment = ""
    if "mining.subscribe" in segment:
        subscribe_fn = node
        break

if subscribe_fn is None:
    # Fallback: locate a function containing the subscribe method literal in
    # its AST constants, even if source-segment extraction is unavailable.
    for node in ast.walk(client_tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        constants = [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        if any("mining.subscribe" in value for value in constants):
            subscribe_fn = node
            break

if subscribe_fn is None:
    raise RuntimeError("Client mining.subscribe dispatcher not found")

fn_start = sum(map(len, clines[:subscribe_fn.lineno - 1]))
fn_end = sum(map(len, clines[:subscribe_fn.end_lineno]))
fn_text = client_text[fn_start:fn_end]

# Detection runs once per connection when mining.subscribe arrives.
detection = '''
        # Stratum v1 exposes the miner firmware/user-agent in the first
        # mining.subscribe parameter. Keep this independent of authorization
        # so password-x VarDiff remains a separate concern.
        ua = str(params[0]).strip() if params and isinstance(params, (list, tuple)) else ""
        self.miner_user_agent = ua
        self.miner_family = "unknown"
        self.miner_version = ""
        self.miner_variant = ""
        self.miner_is_nmminer_v2 = False
        self.miner_is_nerdminer_v2 = False

        nm = re.search(r"NMMiner(?:\\s*[-_/ ]?\\s*(?:v)?(\\d+(?:\\.\\d+){1,3}))?", ua, re.IGNORECASE)
        if nm:
            self.miner_family = "NMMiner"
            self.miner_version = nm.group(1) or ""
            major = self.miner_version.split(".", 1)[0] if self.miner_version else ""
            explicit_v2 = bool(re.search(r"NMMiner\\s*[-_/ ]?\\s*v?2(?:\\D|$)", ua, re.IGNORECASE))
            self.miner_is_nmminer_v2 = explicit_v2 or major == "2"
            self.miner_variant = "v2" if self.miner_is_nmminer_v2 else "legacy"
        else:
            nerd = re.search(r"NerdMiner(?:V2|\\s*[-_/ ]?\\s*v?2)?(?:\\s*[/ ]\\s*(\\d+(?:\\.\\d+){1,3}))?", ua, re.IGNORECASE)
            if nerd:
                self.miner_family = "NerdMiner"
                self.miner_version = nerd.group(1) or ""
                self.miner_is_nerdminer_v2 = bool(re.search(r"NerdMinerV?2", ua, re.IGNORECASE))
                self.miner_variant = "v2" if self.miner_is_nerdminer_v2 else "legacy"

        if self.miner_family != "unknown":
            version = self.miner_version or "unknown"
            emit("INFO", f"MINER DETECT family={self.miner_family} variant={self.miner_variant} version={version} ua={ua!r}")
        else:
            emit("INFO", f"MINER DETECT family=unknown ua={ua!r}")
'''

# Insert after the function signature/body indentation. For async and regular
# functions the first executable statement may be a docstring; placing the
# detector after it keeps Python's function metadata semantics intact.
fn_lines = fn_text.splitlines(keepends=True)
insert_at = 1
if len(fn_lines) > 1:
    first_body = fn_lines[1]
    if first_body.lstrip().startswith(('"""', "'''")):
        quote = first_body.lstrip()[:3]
        for i in range(1, len(fn_lines)):
            if quote in fn_lines[i] and i > 1:
                insert_at = i + 1
                break

fn_lines[insert_at:insert_at] = [detection]
new_fn_text = "".join(fn_lines)
client_text = client_text[:fn_start] + new_fn_text + client_text[fn_end:]

# Add per-connection identity fields during Client initialization.
if "self.miner_family = \"unknown\"" not in client_text:
    marker = "        self.worker = \"?\""
    if marker not in client_text:
        raise RuntimeError("Client worker initialization marker not found")
    client_text = client_text.replace(
        marker,
        marker + '''
        self.miner_user_agent = ""
        self.miner_family = "unknown"
        self.miner_version = ""
        self.miner_variant = ""
        self.miner_is_nmminer_v2 = False
        self.miner_is_nerdminer_v2 = False''',
        1,
    )

# Include miner identity in the authorization line when the existing logging
# statement is present. Do not fail if an upstream formatting change moves it.
auth_old = 'emit("INFO", f"authorize {self.worker} diff={self.diff} mode={mode}")'
auth_new = 'emit("INFO", f"authorize {self.worker} diff={self.diff} mode={mode} miner={self.miner_family}/{self.miner_variant or \"unknown\"} version={self.miner_version or \"unknown\"}")'
if auth_old in client_text:
    client_text = client_text.replace(auth_old, auth_new, 1)

text = text[:start] + client_text + text[end:]

for marker in (
    "self.miner_family = \"unknown\"",
    "self.miner_is_nmminer_v2 = False",
    "NMMiner",
    "self.miner_is_nmminer_v2 = explicit_v2 or major == \"2\"",
    "MINER DETECT family=",
):
    if marker not in text:
        raise RuntimeError(f"miner detection marker missing: {marker}")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: NMMiner/NerdMiner v2 detection installed via mining.subscribe dispatcher")
