#!/usr/bin/env python3
"""Add robust Stratum user-agent detection for NMMiner/NerdMiner clients."""
import ast
import re
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

if "self.miner_family = \"unknown\"" not in client_text:
    marker = "        self.worker = \"?\""
    if marker not in client_text:
        raise RuntimeError("Client worker initialization marker not found")
    client_text = client_text.replace(marker, marker + '''\n        self.miner_user_agent = \"\"\n        self.miner_family = \"unknown\"\n        self.miner_version = \"\"\n        self.miner_variant = \"\"\n        self.miner_is_nmminer_v2 = False\n        self.miner_is_nerdminer_v2 = False''', 1)

new_subscribe = '''    def handle_subscribe(self, mid, params):
        # Stratum v1 exposes the miner firmware/user-agent as params[0].
        # NMMiner v2 commonly reports NMMiner/2.0.03; tolerate common variants.
        ua = str(params[0]).strip() if params else ""
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

        en1_hex = binascii.hexlify(self.en1).decode()
        self.send({
            "id": mid,
            "result": [[["mining.notify", en1_hex], ["mining.set_difficulty", en1_hex]], en1_hex, self.en2_size],
            "error": None,
        })
'''

client_tree = ast.parse(client_text)
sub = next((n for n in client_tree.body if isinstance(n, ast.FunctionDef) and n.name == "handle_subscribe"), None)
if sub is None:
    raise RuntimeError("Client.handle_subscribe not found")
clines = client_text.splitlines(keepends=True)
sub_start = sum(map(len, clines[:sub.lineno - 1]))
sub_end = sum(map(len, clines[:sub.end_lineno]))
client_text = client_text[:sub_start] + new_subscribe.rstrip() + "\n" + client_text[sub_end:]

auth_old = '        emit("INFO", f"authorize {self.worker} diff={self.diff} mode={mode}")'
auth_new = '        emit("INFO", f"authorize {self.worker} diff={self.diff} mode={mode} miner={self.miner_family}/{self.miner_variant or \"unknown\"} version={self.miner_version or \"unknown\"}")'
if auth_old in client_text:
    client_text = client_text.replace(auth_old, auth_new, 1)

text = text[:start] + client_text + text[end:]

for marker in (
    "self.miner_family = \"unknown\"",
    "self.miner_is_nmminer_v2 = False",
    "NMMiner",
    "self.miner_is_nmminer_v2 = explicit_v2 or major == \"2\"",
    "MINER DETECT family=",
    "miner={self.miner_family}",
):
    if marker not in text:
        raise RuntimeError(f"miner detection marker missing: {marker}")

compile(text, str(PATH), "exec")
PATH.write_text(text)
print(f"verified {PATH}: NMMiner/NerdMiner v2 detection installed")
