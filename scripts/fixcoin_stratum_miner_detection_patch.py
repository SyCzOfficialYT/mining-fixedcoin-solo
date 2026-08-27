#!/usr/bin/env python3
"""Install deterministic Stratum miner/user-agent detection.

server.py regenerates server_full.py from the pinned upstream source on every
build.  Keep this patch deliberately small: insert one detector immediately
after ``params`` is assigned and before Stratum dispatch.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "stratum" / "server_full.py"
text = PATH.read_text()

START = "                    # FIXCOIN MINER DETECTION START\n"
END = "                    # FIXCOIN MINER DETECTION END\n"
PARAMS = '                    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or []\n'
SUBSCRIBE = '                    if method == "mining.subscribe":\n'

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

# Keep detection directly between params assignment and mining.subscribe.
# NerdQAxe++ is reported as e.g.:
#   NerdQAxe++/BM1370/v1.0.37.3-LTS
# It is low-hashrate hardware and must therefore enter the same low-hash
# difficulty authority as NMMiner/NerdMiner.
detection = r'''                    # FIXCOIN MINER DETECTION START
                    ua = str(params[0]).strip() if params and isinstance(params, (list, tuple)) else ""
                    self.miner_user_agent = ua
                    self.miner_family = "unknown"
                    self.miner_version = ""
                    self.miner_variant = ""
                    self.miner_is_nmminer_v2 = False
                    self.miner_is_nerdminer_v2 = False
                    self.miner_is_nerdqaxe = False

                    # NMMiner[/vX], including versioned forms.
                    nm = re.search(
                        r"NMMiner(?:\s*[-_/ ]?\s*(?:v)?(\d+(?:\.\d+){1,3}))?",
                        ua,
                        re.IGNORECASE,
                    )
                    if nm:
                        self.miner_family = "NMMiner"
                        self.miner_version = nm.group(1) or ""
                        major = self.miner_version.split(".", 1)[0] if self.miner_version else ""
                        explicit_v2 = bool(re.search(r"NMMiner\s*[-_/ ]?\s*v?2(?:\D|$)", ua, re.IGNORECASE))
                        self.miner_is_nmminer_v2 = explicit_v2 or major == "2"
                        self.miner_variant = "v2" if self.miner_is_nmminer_v2 else "legacy"
                    else:
                        # NerdMiner and NerdQAxe are separate families because
                        # the dashboard should be able to distinguish hardware.
                        nerdqaxe = re.search(
                            r"NerdQ?Axe\+*(?:\s*[/_-]\s*(?:BM\d+|v)?\s*)?(?:[/ ]\s*(v?\d+(?:\.\d+){1,3}))?",
                            ua,
                            re.IGNORECASE,
                        )
                        if nerdqaxe:
                            self.miner_family = "NerdQAxe"
                            self.miner_is_nerdqaxe = True
                            version_match = re.search(r"(?:^|[/ _-])v?(\d+(?:\.\d+){1,3})(?:[-/ _]|$)", ua, re.IGNORECASE)
                            self.miner_version = version_match.group(1) if version_match else ""
                            self.miner_variant = "bm1370" if re.search(r"BM1370", ua, re.IGNORECASE) else "standard"
                        else:
                            nerd = re.search(
                                r"NerdMiner(?:V2|\s*[-_/ ]?\s*v?2)?(?:\s*[/ ]\s*(\d+(?:\.\d+){1,3}))?",
                                ua,
                                re.IGNORECASE,
                            )
                            if nerd:
                                self.miner_family = "NerdMiner"
                                self.miner_version = nerd.group(1) or ""
                                self.miner_is_nerdminer_v2 = bool(re.search(r"NerdMinerV?2", ua, re.IGNORECASE))
                                self.miner_variant = "v2" if self.miner_is_nerdminer_v2 else "legacy"

                    if self.miner_family != "unknown":
                        version = self.miner_version or "unknown"
                        emit(
                            "INFO",
                            f"MINER DETECT family={self.miner_family} variant={self.miner_variant} "
                            f"version={version} ua={ua!r}",
                        )
                    else:
                        emit("INFO", f"MINER DETECT family=unknown ua={ua!r}")
                    # FIXCOIN MINER DETECTION END
'''

patched = text.replace(SUBSCRIBE, detection + SUBSCRIBE, 1)
compile(patched, str(PATH), "exec")

detect_pos = patched.find(START)
subscribe_pos_patched = patched.find(SUBSCRIBE)
if not (params_pos < detect_pos < subscribe_pos_patched):
    raise RuntimeError("miner detection placement verification failed")

PATH.write_text(patched)
print(f"patched {PATH}: NMMiner/NerdMiner/NerdQAxe detection installed")
print(f"verified {PATH}: syntax valid; params -> detection -> subscribe ordering")
