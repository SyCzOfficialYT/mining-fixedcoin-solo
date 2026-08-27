#!/usr/bin/env python3
"""Install Stratum miner/user-agent detection safely.

Detection must run inside Client.run()'s request loop, after ``params`` is
assigned from the decoded JSON message and immediately before
``mining.subscribe`` is dispatched.  The previous implementation attempted
AST line-offset surgery on the Client class and could leave server_full.py
syntactically invalid after repeated/generated patches.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

DETECTION_START = "        # FIXCOIN MINER DETECTION START\n"
DETECTION_END = "        # FIXCOIN MINER DETECTION END\n"

# Full detector body. It intentionally references `params` only at the point
# where the request loop has already assigned it.
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

# Remove any previous detector block, including the broken pre-loop version.
if DETECTION_START in text:
    before, rest = text.split(DETECTION_START, 1)
    if DETECTION_END not in rest:
        raise RuntimeError("incomplete existing miner detection block")
    _, after = rest.split(DETECTION_END, 1)
    text = before + after
else:
    # Remove the exact legacy block installed by the earlier patch revision.
    legacy_start = '        # Stratum v1 exposes the miner firmware/user-agent in the first\n'
    if legacy_start in text:
        before, rest = text.split(legacy_start, 1)
        legacy_end = '        with _clients_lock:\n'
        if legacy_end not in rest:
            raise RuntimeError("legacy miner detection block has unexpected shape")
        _, after = rest.split(legacy_end, 1)
        text = before + legacy_end + after

# Initialize telemetry fields once in Client.__init__, if the generated base
# does not already define them. This keeps dashboard access safe before the
# first subscribe request.
if 'self.miner_user_agent = ""' not in text:
    marker = '        self.worker = "?"\n'
    if marker not in text:
        raise RuntimeError("Client worker initialization marker not found")
    init_fields = '''        self.worker = "?"
        self.miner_user_agent = ""
        self.miner_family = "unknown"
        self.miner_version = ""
        self.miner_variant = ""
        self.miner_is_nmminer_v2 = False
        self.miner_is_nerdminer_v2 = False
'''
    text = text.replace(marker, init_fields, 1)

# Find the request-loop params assignment and the subscribe dispatch. Insert
# only after params exists, eliminating the original UnboundLocalError.
params_marker = '                    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or []\n'
subscribe_marker = '                    if method == "mining.subscribe":\n'
if params_marker not in text:
    raise RuntimeError("Stratum request params assignment not found")
if subscribe_marker not in text:
    raise RuntimeError("mining.subscribe dispatch not found")

if text.find(params_marker) > text.find(subscribe_marker):
    raise RuntimeError("invalid request-loop ordering: subscribe precedes params assignment")

text = text.replace(subscribe_marker, detection + subscribe_marker, 1)

# Compile before writing. Also verify the detector is no longer at run() entry
# and that params assignment precedes every detector insertion.
compile(text, str(PATH), "exec")

run_pos = text.find('    def run(self):\n')
detect_pos = text.find(DETECTION_START)
params_pos = text.find(params_marker)
subscribe_pos = text.find(subscribe_marker)
if run_pos < 0 or not (params_pos < detect_pos < subscribe_pos):
    raise RuntimeError("miner detection placement verification failed")
if detect_pos - run_pos < 200:
    raise RuntimeError("miner detection unexpectedly remains at run() entry")

PATH.write_text(text)
print(f"patched {PATH}: miner detection is scoped to mining.subscribe params")
print(f"verified {PATH}: syntax valid; params -> detection -> subscribe ordering")
