#!/usr/bin/env python3
"""Add robust Stratum user-agent detection for NMMiner/NerdMiner clients.

The pinned FreeCash base exposes a generic Client request loop. Detection is
installed at the actual ``mining.subscribe`` dispatch point, where ``params``
is defined, so miner identity is available before authorization without
leaking request-local state into the connection thread setup.
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

# Find the real request function containing the mining.subscribe dispatcher.
clines = client_text.splitlines(keepends=True)
subscribe_fn = None
for node in ast.walk(client_tree):
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    segment = ast.get_source_segment(client_text, node) or ""
    if "mining.subscribe" in segment:
        subscribe_fn = node
        break

if subscribe_fn is None:
    raise RuntimeError("Client mining.subscribe dispatcher not found")

fn_start = sum(map(len, clines[:subscribe_fn.lineno - 1]))
fn_end = sum(map(len, clines[:subscribe_fn.end_lineno]))
fn_text = client_text[fn_start:fn_end]

# Detection runs exactly once per connection, when mining.subscribe is
# dispatched. At this point the receive loop has already assigned `params`.
detection = '''        # Stratum v1 exposes the miner firmware/user-agent in the first
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

# Insert immediately before the subscribe dispatch. This guarantees `params`
# is in scope and guarantees detection precedes handle_authorize on the same
# Stratum connection.
marker = "                    if method == \"mining.subscribe\":"
if marker in fn_text:
    if "# Stratum v1 exposes the miner firmware/user-agent" in fn_text:
        raise RuntimeError("miner detection already installed; refusing duplicate patch")
    fn_text = fn_text.replace(marker, detection + marker, 1)
else:
    raise RuntimeError("mining.subscribe dispatch marker not found")

client_text = client_text[:fn_start] + fn_text + client_text[fn_end:]

# Initialize identity fields in Client.__init__, independently of the
# detection block. This makes the fields safe for authorization/dashboard
# telemetry even before a valid subscribe has been received.
client_tree = ast.parse(client_text)
init_fn = None
for node in ast.walk(client_tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
        init_fn = node
        break
if init_fn is None:
    raise RuntimeError("Client.__init__ not found")

if 'self.miner_user_agent = ""' not in client_text:
    init_lines = client_text.splitlines(keepends=True)
    init_start = sum(map(len, init_lines[:init_fn.lineno - 1]))
    init_end = sum(map(len, init_lines[:init_fn.end_lineno]))
    init_text = client_text[init_start:init_end]
    init_marker = '        self.worker = "?"'
    if init_marker not in init_text:
        raise RuntimeError("Client worker initialization marker not found")
    init_fields = '''\n        self.miner_user_agent = ""\n        self.miner_family = "unknown"\n        self.miner_version = ""\n        self.miner_variant = ""\n        self.miner_is_nmminer_v2 = False\n        self.miner_is_nerdminer_v2 = False'''
    init_text = init_text.replace(init_marker, init_marker + init_fields, 1)
    client_text = client_text[:init_start] + init_text + client_text[init_end:]

text = text[:start] + client_text + text[end:]

# Structural verification: the generated file must compile and the detector
# must no longer occur at Client.run() entry.
compile(text, str(PATH), "exec")
verify_tree = ast.parse(text)
verify_client = next((n for n in verify_tree.body if isinstance(n, ast.ClassDef) and n.name == "Client"), None)
if verify_client is None:
    raise RuntimeError("verification: Client class missing")
verify_run = next((n for n in verify_client.body if isinstance(n, ast.FunctionDef) and n.name == "run"), None)
if verify_run is None:
    raise RuntimeError("verification: Client.run missing")
run_segment = ast.get_source_segment(text, verify_run) or ""
if "# Stratum v1 exposes the miner firmware/user-agent" in run_segment:
    raise RuntimeError("verification: miner detection still installed at run() entry")

# Verify the detector is placed after params assignment and before subscribe
# dispatch in the same request loop.
params_pos = text.find('msg.get("params") or []')
detect_pos = text.find("# Stratum v1 exposes the miner firmware/user-agent")
subscribe_pos = text.find('if method == "mining.subscribe":')
if not (params_pos >= 0 and params_pos < detect_pos < subscribe_pos):
    raise RuntimeError("verification: detector/params/subscribe ordering invalid")

PATH.write_text(text)
print(f"verified {PATH}: miner detection scoped to mining.subscribe params; authorization-safe initialization installed")
