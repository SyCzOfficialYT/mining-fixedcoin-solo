#!/usr/bin/env python3
"""FixedCoin AxeOS/NMMiner Swarm Connector.

Discovers NMMiner/AxeOS-compatible miners on the configured LAN, normalizes
NMMiner telemetry to the AxeOS /api/system/info shape, and exposes safe proxy
endpoints for the FixedCoin dashboard and future swarm integrations.

This service deliberately does not pretend to be an AxeOS firmware device on
its own IP. AxeOS swarm discovery is neighbor/IP based; the connector instead
provides a stable compatibility API and a per-device proxy. Direct NMMiner
compatibility can later be enabled on the miner itself without changing the
normalizer.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

HOST = os.getenv("SWARM_HOST", "0.0.0.0")
PORT = int(os.getenv("SWARM_PORT", "5080"))
CIDR = os.getenv("SWARM_CIDR", "192.168.50.0/24")
SCAN_PORT = int(os.getenv("MINER_HTTP_PORT", "80"))
TIMEOUT = float(os.getenv("MINER_HTTP_TIMEOUT", "0.8"))
MAX_WORKERS = int(os.getenv("SWARM_SCAN_WORKERS", "32"))
ALLOW_CONTROL = os.getenv("SWARM_ALLOW_CONTROL", "false").lower() in {"1", "true", "yes"}

NETWORK = ipaddress.ip_network(CIDR, strict=False)

def allowed_ip(value: str) -> str:
    ip = ipaddress.ip_address(value)
    if ip not in NETWORK:
        raise ValueError(f"target outside SWARM_CIDR: {ip}")
    return str(ip)


def http_json(ip: str, path: str, method: str = "GET", body: dict | None = None):
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
    """Map common NMMiner telemetry into AxeOS-compatible field names."""
    miner = raw.get("miner") if isinstance(raw.get("miner"), dict) else raw
    identity = raw.get("identity") if isinstance(raw.get("identity"), dict) else raw.get("system", {})
    temps = raw.get("temps") if isinstance(raw.get("temps"), dict) else {}
    power = raw.get("power") if isinstance(raw.get("power"), dict) else {}
    asic = raw.get("asic") if isinstance(raw.get("asic"), dict) else {}
    stratum = raw.get("stratum") if isinstance(raw.get("stratum"), dict) else {}
    fans = raw.get("fans") if isinstance(raw.get("fans"), list) else []

    return {
        "power": {
            "power": num(first(power, "power", "watts", "w", default=first(raw, "power", "watts", default=0))),
            "vbus": int(num(first(power, "vbus", "voltage", default=0))),
            "ibus": int(num(first(power, "ibus", "current", default=0))),
        },
        "temps": {
            "vcore": num(first(temps, "vcore", "vrm", "regulator", default=first(raw, "vcore", default=0))),
            "asic": num(first(temps, "asic", "chip", "core", "temperature", default=first(raw, "temperature", "temp", default=0))),
        },
        "asic": {
            "count": int(num(first(asic, "count", "chips", default=first(raw, "asicCount", default=0)))),
            "model": str(first(asic, "model", "chipModel", default=first(raw, "asicModel", default="NMMiner"))),
            "vcoreReq": int(num(first(asic, "vcoreReq", "vcore", default=first(raw, "vcore", default=0)))),
            "vcoreReal": int(num(first(asic, "vcoreReal", default=0))),
            "freqReq": int(num(first(asic, "freqReq", "frequency", "freq", default=first(raw, "frequency", "freq", default=0)))),
            "smallCoreCnt": int(num(first(asic, "smallCoreCnt", default=0))),
        },
        "miner": {
            "state": str(first(miner, "state", "status", default="running")),
            "paused": bool(first(miner, "paused", default=False)),
            "pauseReason": str(first(miner, "pauseReason", default="")),
            "hashRate": num(first(miner, "hashRate", "hashrate", "hr", default=0)),
            "bestDiffEver": str(first(miner, "bestDiffEver", "bestShare", "best", default="0")),
            "bestDiffSession": str(first(miner, "bestDiffSession", default="0")),
            "networkDiff": str(first(miner, "networkDiff", "networkDifficulty", default="0")),
            "poolDiff": str(first(miner, "poolDiff", "difficulty", "diff", default="0")),
            "lastDiff": str(first(miner, "lastDiff", default="0")),
            "blkhits": int(num(first(miner, "blkhits", "blockHits", default=0))),
            "sAccepted": int(num(first(miner, "sAccepted", "accepted", "sharesAccepted", default=0))),
            "sRejected": int(num(first(miner, "sRejected", "rejected", "sharesRejected", default=0))),
            "uptimeSeconds": int(num(first(miner, "uptimeSeconds", "uptime", default=0))),
            "uptimeEver": int(num(first(miner, "uptimeEver", default=0))),
            "freeHeap": int(num(first(miner, "freeHeap", default=0))),
            "minFreeHeap": int(num(first(miner, "minFreeHeap", default=0))),
        },
        "identity": {
            "fwVersion": str(first(identity, "fwVersion", "version", "ver", default="NMMiner")),
            "hwModel": str(first(identity, "hwModel", "model", default="NMMiner")),
            "displayName": str(first(identity, "displayName", "hostname", "hostName", default=f"NMMiner-{ip}")),
            "hostName": str(first(identity, "hostName", "hostname", default=f"NMMiner-{ip}")),
            "ssid": str(first(identity, "ssid", default="")),
            "rssi": int(num(first(identity, "rssi", "wifiRssi", default=0))),
            "appSha256": str(first(identity, "appSha256", default="")),
            "ip": ip,
        },
        "fans": fans,
        "stratum": {
            "url": str(first(stratum, "url", "pool", default="")),
            "user": str(first(stratum, "user", "username", default="")),
            "pwd": str(first(stratum, "pwd", "password", default="")),
        },
    }


def probe(ip: str) -> dict | None:
    try:
        raw = http_json(ip, "/probe")
        text = json.dumps(raw).lower()
        # Accept native AxeOS devices as well as NMMiner/NMAxe variants.
        if any(token in text for token in ("nmm", "nmminer", "nmaxe", "axeos", "nerdminer")):
            raw["_connector"] = "fixedcoin-swarm"
            raw["_ip"] = ip
            return raw
        # Some NMMiner builds expose only system info; use it as a fallback.
        info = http_json(ip, "/api/system/info")
        normalized = normalize_system_info(info, ip)
        normalized["_connector"] = "fixedcoin-swarm"
        normalized["_ip"] = ip
        normalized["_type"] = "NMMiner"
        return normalized
    except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError):
        return None


def scan() -> list[dict]:
    hosts = [str(ip) for ip in NETWORK.hosts()]
    found = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(probe, ip): ip for ip in hosts}
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)
    return sorted(found, key=lambda x: x.get("_ip", ""))


def json_response(handler, payload, status=200):
    data = json.dumps(payload, separators=(",", ":")).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    server_version = "FixedCoin-Swarm/1.0"

    def log_message(self, fmt, *args):
        print(f"[swarm] {self.address_string()} {fmt % args}", flush=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        try:
            if parsed.path == "/health":
                return json_response(self, {"status": "ok", "service": "fixedcoin-swarm", "cidr": CIDR})
            if parsed.path == "/api/swarm/scan":
                return json_response(self, {"devices": scan(), "count": len(scan())})
            if len(parts) >= 3 and parts[0] == "device":
                ip = allowed_ip(parts[1])
                subpath = "/" + "/".join(parts[2:])
                raw = http_json(ip, subpath)
                if subpath == "/api/system/info":
                    raw = normalize_system_info(raw, ip)
                return json_response(self, raw)
            if parsed.path == "/api/swarm/devices":
                return json_response(self, {"devices": scan()})
            return json_response(self, {"error": "not found"}, 404)
        except (HTTPError, URLError, ValueError, json.JSONDecodeError, OSError) as exc:
            return json_response(self, {"error": str(exc)}, 502)

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        try:
            if parsed.path == "/api/swarm/scan":
                devices = scan()
                return json_response(self, {"devices": devices, "count": len(devices)})
            if len(parts) == 4 and parts[0] == "device" and parts[2] == "api" and parts[3] == "swarm":
                return json_response(self, {"error": "invalid swarm endpoint"}, 404)
            if len(parts) >= 4 and parts[0] == "device":
                ip = allowed_ip(parts[1])
                subpath = "/" + "/".join(parts[2:])
                if subpath == "/api/system/restart" and not ALLOW_CONTROL:
                    return json_response(self, {"error": "control disabled; set SWARM_ALLOW_CONTROL=true"}, 403)
                raw = http_json(ip, subpath, method="POST")
                return json_response(self, raw)
            return json_response(self, {"error": "not found"}, 404)
        except (HTTPError, URLError, ValueError, json.JSONDecodeError, OSError) as exc:
            return json_response(self, {"error": str(exc)}, 502)


if __name__ == "__main__":
    print(f"FixedCoin Swarm Connector listening on {HOST}:{PORT} scanning {CIDR}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
