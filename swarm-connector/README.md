# FixedCoin AxeOS / NMMiner Swarm Connector

A small LAN adapter that discovers NMMiner/AxeOS-compatible devices and normalizes NMMiner telemetry into the AxeOS `/api/system/info` shape.

## What it does

- scans the configured LAN for miner HTTP APIs
- probes `/probe` first
- falls back to `/api/system/info`
- normalizes NMMiner telemetry to the AxeOS system-info contract
- exposes per-device proxy endpoints
- exposes CORS for the LiveShare dashboard
- keeps control endpoints disabled by default

AxeOS exposes its device API on HTTP port 80 and documents `/api/system/info`, `/api/swarm/scan`, `/api/swarm/find`, and `/probe` as part of its API. The connector follows that contract for the normalized data surface.

## Endpoints

```text
GET  /health
GET  /api/swarm/devices
GET  /api/swarm/scan
POST /api/swarm/scan
GET  /device/<ip>/probe
GET  /device/<ip>/api/system/info
POST /device/<ip>/api/system/restart
POST /device/<ip>/api/system/clearhits
PATCH /device/<ip>/api/mining/state
PATCH /device/<ip>/api/setting/mining
```

Control operations are blocked unless:

```env
SWARM_ALLOW_CONTROL=true
```

Targets are restricted to:

```env
SWARM_CIDR=192.168.50.0/24
```

## Compose

The connector is exposed at:

```text
http://<node-ip>:5080
```

Example:

```bash
curl http://192.168.50.173:5080/health
curl http://192.168.50.173:5080/api/swarm/devices
```

## Important architecture note

This is a compatibility/normalization layer. It does **not** claim that a single Linux container IP can impersonate every physical NMMiner as a separate AxeOS swarm neighbor. AxeOS swarm discovery is device/IP based. The connector gives us a stable API and per-device proxy now; a firmware-side `/probe` implementation or an L2/IP-per-device bridge can be added later if native AxeOS Swarm discovery is required.
