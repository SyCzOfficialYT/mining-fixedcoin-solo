#!/usr/bin/env python3
"""FixedCoin AxeOS/NMMiner Swarm Connector.

The connector discovers NMMiner devices and publishes one AxeOS-compatible
mDNS service per device.  Requests arriving for the advertised *.local name
are transparently proxied to the real NMMiner, so AxeOS can use its normal
/probe, /alive and /api/* contract without modifying NMMiner firmware.

This deliberately uses mDNS/DNS-SD rather than pretending that one connector
IP represents every miner. ESP-Miner documents `_axeos._sub._http._tcp` and
`.local` hostname based swarm discovery, so each NMMiner gets its own virtual
service identity while the connector remains the HTTP gateway.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    from zeroconf import IPVersion, ServiceInfo, Zeroconf
except ImportError as exc:  # pragma: no cover
    raise SystemExit("python-zeroconf is required") from exc

HOST = os.getenv("SWARM_HOST", "0.0.0.0")
PORT = int(os.getenv("SWARM_PORT", "5080"))
CIDR = os.getenv("SWARM_CIDR", "192.168.50.0/24")
SCAN_PORT = int(os.getenv("MINER_HTTP_PORT", "80"))
TIMEOUT = float(os.getenv("MINER_HTTP_TIMEOUT", "0.8"))
MAX_WORKERS = int(os.getenv("SWARM_SCAN_WORKERS", "32"))
SCAN_INTERVAL = float(os.getenv("SWARM_SCAN_INTERVAL", "15"))
ALLOW_CONTROL = os.getenv("SWARM_ALLOW_CONTROL", "false").lower() in {"1", "true", "yes"}
ADVERTISE_PORT = int(os.getenv("SWARM_ADVERTISE_PORT", str(PORT)))
ADVERTISE_IP = os.getenv("SWARM_ADVERTISE_IP", "")
SERVICE_TYPE = "_axeos._sub._http._tcp.local."
NETWORK = ipaddress.ip_network(CIDR, strict=False)

STATE_LOCK = threading.RLock()
DEVICES: dict[str, dict] = {}
HOST_TO_IP: dict[str, str] = {}
SERVICES: dict[str, ServiceInfo] = {}
ZC: Zeroconf | None = None


def allowed_ip(value: str) -> str:
    ip = ipaddress.ip_address(value)
    if ip not in NETWORK:
        raise ValueError(f"target outside SWARM_CIDR: {ip}")
    return str(ip)


def local_advertise_ip() -> str:
    if ADVERTISE_IP:
        return allowed_ip(ADVERTISE_IP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("1.1.1.1", 53))
        return sock.getsockname()[0]
    finally:
        sock.close()


def http_json(ip: str, path: str, method: str = "GET", body=None):
    ip = allowed_ip(ip)
    data = json.dumps(body).encode() if body is not None else None
    req = Request(
        f"http://{ip}:{SCAN_PORT}{path}",
        data=data,
        method=method,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=TIMEOUT) as response:
        raw = response.read()
        return json.loads(raw.decode("utf-8", "replace"))


def first(d: dict, *keys, default=None):
    for key in keys:
        if isinstance(d, dict) and key in d and d[key] is not None:
            return d[key]
    return default


def num(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_system_info(raw: dict, ip: str) -> dict:
    miner = raw.get("miner") if isinstance(raw.get("miner"), dict) else raw
    identity = raw.get("identity") if isinstance(raw.get("identity"), dict) else raw.get("system", {})
    temps = raw.get("temps") if isinstance(raw.get("temps"), dict) else {}
    power = raw.get("power") if isinstance(raw.get("power"), dict) else {}
    asic = raw.get("asic") if isinstance(raw.get("asic"), dict) else {}
    stratum = raw.get("stratum") if isinstance(raw.get("stratum"), dict) else {}
    fans = raw.get("fans") if isinstance(raw.get("fans"), list) else []

    return {
        "power": {"power": num(first(power, "power", "watts", "w", default=first(raw, "power", "watts", default=0))), "vbus": int(num(first(power, "vbus", "voltage", default=0))), "ibus": int(num(first(power, "ibus", "current", default=0)))},
        "temps": {"vcore": num(first(temps, "vcore", "vrm", "regulator", default=first(raw, "vcore", default=0))), "asic": num(first(temps, "asic", "chip", "core", "temperature", default=first(raw, "temperature", "temp", default=0)))},
        "asic": {"count": int(num(first(asic, "count", "chips", default=first(raw, "asicCount", default=0)))), "model": str(first(asic, "model", "chipModel", default=first(raw, "asicModel", default="NMMiner"))), "vcoreReq": int(num(first(asic, "vcoreReq", "vcore", default=first(raw, "vcore", default=0)))), "vcoreReal": int(num(first(asic, "vcoreReal", default=0))), "freqReq": int(num(first(asic, "freqReq", "frequency", "freq", default=first(raw, "frequency", "freq", default=0)))), "smallCoreCnt": int(num(first(asic, "smallCoreCnt", default=0)))},
        "miner": {"state": str(first(miner, "state", "status", default="running")), "paused": bool(first(miner, "paused", default=False)), "pauseReason": str(first(miner, "pauseReason", default="")), "hashRate": num(first(miner, "hashRate", "hashrate", "hr", default=0)), "bestDiffEver": str(first(miner, "bestDiffEver", "bestShare", "best", default="0")), "bestDiffSession": str(first(miner, "bestDiffSession", default="0")), "networkDiff": str(first(miner, "networkDiff", "networkDifficulty", default="0")), "poolDiff": str(first(miner, "poolDiff", "difficulty", "diff", default="0")), "lastDiff": str(first(miner, "lastDiff", default="0")), "blkhits": int(num(first(miner, "blkhits", "blockHits", default=0))), "sAccepted": int(num(first(miner, "sAccepted", "accepted", "sharesAccepted", default=0))), "sRejected": int(num(first(miner, "sRejected", "rejected", "sharesRejected", default=0))), "uptimeSeconds": int(num(first(miner, "uptimeSeconds", "uptime", default=0))), "uptimeEver": int(num(first(miner, "uptimeEver", default=0))), "freeHeap": int(num(first(miner, "freeHeap", default=0))), "minFreeHeap": int(num(first(miner, "minFreeHeap", default=0)))},
        "identity": {"fwVersion": str(first(identity, "fwVersion", "version", "ver", default="NMMiner")), "hwModel": str(first(identity, "hwModel", "model", default="NMMiner")), "displayName": str(first(identity, "displayName", "hostname", "hostName", default=f"NMMiner-{ip}")), "hostName": str(first(identity, "hostName", "hostname", default=f"NMMiner-{ip}")), "ssid": str(first(identity, "ssid", default="")), "rssi": int(num(first(identity, "rssi", "wifiRssi", default=0))), "appSha256": str(first(identity, "appSha256", default="")), "ip": ip},
        "fans": fans,
        "stratum": {"url": str(first(stratum, "url", "pool", default="")), "user": str(first(stratum, "user", "username", default="")), "pwd": str(first(stratum, "pwd", "password", default=""))},
    }


def normalize_probe(raw: dict, ip: str) -> dict:
    raw = dict(raw or {})
    raw["model"] = str(raw.get("model") or "NMMiner")
    raw["hostname"] = str(raw.get("hostname") or f"nmminer-{ip.replace('.', '-')}")
    raw["ver"] = str(raw.get("ver") or "NMMiner")
    raw["sw"] = int(num(raw.get("sw"), 240))
    raw["sh"] = int(num(raw.get("sh"), 135))
    raw["hr"] = num(raw.get("hr"), 0)
    raw["sbd"] = num(raw.get("sbd"), 0)
    raw["ebd"] = num(raw.get("ebd"), 0)
    raw["ut"] = int(num(raw.get("ut"), 0))
    return raw


def probe(ip: str) -> dict | None:
    try:
        raw = http_json(ip, "/probe")
        # NMMiner already implements /probe. Accept it when its shape is sane.
        if isinstance(raw, dict) and any(k in raw for k in ("model", "hostname", "ver", "hr")):
            result = normalize_probe(raw, ip)
        else:
            info = http_json(ip, "/api/system/info")
            result = normalize_probe({"model": "NMMiner", "hostname": f"nmminer-{ip.replace('.', '-')}", "hr": num(info.get("hashRate", info.get("hr", 0)))}, ip)
        result["_connector"] = "fixedcoin-swarm"
        result["_ip"] = ip
        result["_type"] = "NMMiner"
        return result
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError):
        return None


def safe_hostname(value: str, ip: str) -> str:
    value = re.sub(r"\.local$", "", str(value or ""), flags=re.I)
    value = re.sub(r"[^a-zA-Z0-9-]+", "-", value).strip("-").lower()
    if not value:
        value = f"nmminer-{ip.replace('.', '-')}"
    return value[:63]


def service_name(hostname: str) -> str:
    return f"NMMiner {hostname}._axeos._sub._http._tcp.local."


def register_device_service(ip: str, device: dict) -> None:
    global ZC
    if ZC is None:
        return
    hostname = safe_hostname(device.get("hostname"), ip)
    # Avoid collisions between duplicate NMMiner hostnames.
    with STATE_LOCK:
        existing = HOST_TO_IP.get(hostname)
        if existing and existing != ip:
            hostname = f"{hostname}-{ip.replace('.', '-')[-5:]}"
        HOST_TO_IP[hostname] = ip
        DEVICES[ip] = {**device, "_virtual_hostname": hostname}
    name = service_name(hostname)
    props = {
        b"board": str(device.get("model", "NMMiner")).encode(),
        b"family": b"NMMiner",
        b"asic": b"SHA256d",
        b"asic_count": b"1",
        b"fw_version": str(device.get("ver", "NMMiner")).encode(),
        b"proxy": b"fixedcoin-swarm",
    }
    info = ServiceInfo(
        SERVICE_TYPE,
        name,
        port=ADVERTISE_PORT,
        addresses=[socket.inet_aton(local_advertise_ip())],
        properties=props,
        server=f"{hostname}.local.",
    )
    with STATE_LOCK:
        old = SERVICES.get(ip)
    try:
        if old:
            ZC.update_service(info)
        else:
            ZC.register_service(info, allow_name_change=True)
        with STATE_LOCK:
            SERVICES[ip] = info
        print(f"[swarm] advertised AxeOS node {hostname}.local -> {ip}:{SCAN_PORT}", flush=True)
    except Exception as exc:
        print(f"[swarm] mDNS registration failed for {ip}: {exc}", flush=True)


def unregister_missing(active_ips: set[str]) -> None:
    global ZC
    if ZC is None:
        return
    with STATE_LOCK:
        stale = [ip for ip in SERVICES if ip not in active_ips]
    for ip in stale:
        with STATE_LOCK:
            info = SERVICES.pop(ip, None)
            device = DEVICES.pop(ip, {})
            hostname = device.get("_virtual_hostname")
            if hostname:
                HOST_TO_IP.pop(hostname, None)
        if info:
            try:
                ZC.unregister_service(info)
            except Exception:
                pass
            print(f"[swarm] removed AxeOS node for {ip}", flush=True)


def scan_and_advertise() -> list[dict]:
    hosts = [str(ip) for ip in NETWORK.hosts()]
    found: list[dict] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(probe, ip): ip for ip in hosts}
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
    active = {d["_ip"] for d in found}
    unregister_missing(active)
    for device in found:
        register_device_service(device["_ip"], device)
    return sorted(found, key=lambda x: x.get("_ip", ""))


def scanner_loop() -> None:
    while True:
        try:
            devices = scan_and_advertise()
            print(f"[swarm] scan complete: {len(devices)} device(s)", flush=True)
        except Exception as exc:
            print(f"[swarm] scan error: {exc}", flush=True)
        time.sleep(SCAN_INTERVAL)


def target_from_host(host_header: str) -> str | None:
    host = (host_header or "").split(":", 1)[0].strip().lower()
    host = re.sub(r"\.local$", "", host)
    with STATE_LOCK:
        return HOST_TO_IP.get(host)


def json_response(handler, payload, status=200):
    data = json.dumps(payload, separators=(",", ":")).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    server_version = "FixedCoin-Swarm/2.0"

    def log_message(self, fmt, *args):
        print(f"[swarm] {self.address_string()} {fmt % args}", flush=True)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PATCH,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _proxy_target(self) -> str | None:
        parsed = urlparse(self.path)
        if parsed.path in {"/health", "/api/swarm/scan", "/api/swarm/devices"}:
            return None
        target = target_from_host(self.headers.get("Host", ""))
        if target:
            return target
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 3 and parts[0] == "device":
            return allowed_ip(parts[1])
        return None

    def _proxy(self, method: str, target: str):
        parsed = urlparse(self.path)
        subpath = parsed.path
        if parsed.query:
            subpath += "?" + parsed.query
        if subpath in {"/api/system/restart", "/api/system/clearhits", "/api/swarm/find"} and not ALLOW_CONTROL:
            return json_response(self, {"error": "control disabled; set SWARM_ALLOW_CONTROL=true"}, 403)
        body = None
        length = int(self.headers.get("Content-Length", "0"))
        if length:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        raw = http_json(target, subpath, method=method, body=body)
        if parsed.path == "/api/system/info":
            raw = normalize_system_info(raw, target)
        elif parsed.path == "/probe":
            raw = normalize_probe(raw, target)
        return json_response(self, raw)

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/health":
                return json_response(self, {"status": "ok", "service": "fixedcoin-swarm", "cidr": CIDR, "mdns": True, "advertise_port": ADVERTISE_PORT})
            if parsed.path in {"/api/swarm/scan", "/api/swarm/devices"}:
                devices = scan_and_advertise()
                return json_response(self, {"devices": devices, "count": len(devices)})
            target = self._proxy_target()
            if target:
                return self._proxy("GET", target)
            return json_response(self, {"error": "not found"}, 404)
        except (HTTPError, URLError, ValueError, json.JSONDecodeError, OSError) as exc:
            return json_response(self, {"error": str(exc)}, 502)

    def do_POST(self):
        try:
            if self.path == "/api/swarm/scan":
                devices = scan_and_advertise()
                return json_response(self, {"devices": devices, "count": len(devices)})
            target = self._proxy_target()
            if target:
                return self._proxy("POST", target)
            return json_response(self, {"error": "not found"}, 404)
        except (HTTPError, URLError, ValueError, json.JSONDecodeError, OSError) as exc:
            return json_response(self, {"error": str(exc)}, 502)

    def do_PATCH(self):
        try:
            target = self._proxy_target()
            if target:
                return self._proxy("PATCH", target)
            return json_response(self, {"error": "not found"}, 404)
        except (HTTPError, URLError, ValueError, json.JSONDecodeError, OSError) as exc:
            return json_response(self, {"error": str(exc)}, 502)


def main() -> None:
    global ZC
    advertise_ip = local_advertise_ip()
    ZC = Zeroconf(ip_version=IPVersion.V4Only)
    print(f"FixedCoin Swarm Connector listening on {HOST}:{PORT}", flush=True)
    print(f"LAN scan: {CIDR}; mDNS: _axeos._sub._http._tcp.local. -> {advertise_ip}:{ADVERTISE_PORT}", flush=True)
    scanner = threading.Thread(target=scanner_loop, name="swarm-scan", daemon=True)
    scanner.start()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        if ZC:
            ZC.close()


if __name__ == "__main__":
    main()
