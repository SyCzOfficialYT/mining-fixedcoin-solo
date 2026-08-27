#!/usr/bin/env python3
"""Install Stratum miner/user-agent detection without rewriting Client.run().

server.py regenerates server_full.py from a clean pinned upstream source on
every build. Therefore this patch only performs a single, exact textual
insertion after the request loop has assigned ``params``. The previous
versions attempted to remove/rewrite generated blocks and could corrupt
unrelated code around Client.run().
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

START = "        # FIXCOIN MINER DETECTION START\n"
END = "        # FIXCOIN MINER DETECTION END\n"
PARAMS = '                    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or []\n'
SUBSCRIBE = '                    if method == "mining.subscribe":\n'

# server.py always generates a fresh server_full.py, but fail loudly rather
# than creating a second detector if that invariant ever changes.
if START in text or END in text:
    raise RuntimeError("miner detection block already present in generated server_full.py")

if PARAMS not in text:
    raise RuntimeError("Stratum request params assignment not found")
if SUBSCRIBE not in text:
    raise RuntimeError("mining.subscribe dispatch not found")

params_pos = text.find(PARAMS)
subscribe_pos = text.find(SUBSCRIBE)
if params_pos >= subscribe_pos:
    raise RuntimeError("invalid request-loop ordering: subscribe precedes params assignment")

# Do not touch Client.__init__ or any other generated function. The detector
# initializes all telemetry fields when the first subscribe request arrives,
# which is exactly before authorization on normal Stratum v1 clients.
detection = '''        # FIXCOIN MINER DETECTION START
        # Stratum v1 exposes miner firmware/user-agent in mining.subscribe[0].
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
        # FIXCOIN MINER DETECTION END
'''

patched = text.replace(SUBSCRIBE, detection + SUBSCRIBE, 1)

# The generated file must remain valid Python before it is written.
compile(patched, str(PATH), "exec")

# Verify the insertion is exactly between params assignment and subscribe.
detect_pos = patched.find(START)
if not (params_pos < detect_pos < patched.find(SUBSCRIBE)):
    raise RuntimeError("miner detection placement verification failed")

PATH.write_text(patched)
print(f"patched {PATH}: miner detection scoped to mining.subscribe params")
print(f"verified {PATH}: syntax valid; params -> detection -> subscribe ordering")
