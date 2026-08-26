# FixedCoin AxeOS / NMMiner Swarm Connector

The connector makes LAN NMMiner devices discoverable by AxeOS using the same DNS-SD service family used by ESP-Miner:

- `_http._tcp`
- `_axeos._sub._http._tcp`
- `<hostname>.local`

NMMiner already exposes `/probe`, `/alive` and `/api/system/info`; the connector adds the AxeOS discovery identity and proxies requests back to the real miner. The NMMiner firmware does not need to be modified.

## Architecture

```text
AxeOS Swarm
    |
    | mDNS: _axeos._sub._http._tcp
    v
fixedcoin-swarm-connector:5080
    |
    +-- nmaxe-001.local  ---> 192.168.50.101:80
    +-- nmaxe-002.local  ---> 192.168.50.102:80
    +-- nmminer-003.local ---> 192.168.50.103:80
```

The connector runs with `network_mode: host` so multicast DNS can reach the LAN. It is intentionally read-only by default; control endpoints remain disabled until `SWARM_ALLOW_CONTROL=true` is explicitly enabled.

## Configuration

```env
SWARM_CIDR=192.168.50.0/24
SWARM_ADVERTISE_IP=192.168.50.173
SWARM_ADVERTISE_PORT=5080
SWARM_SCAN_INTERVAL=15
SWARM_ALLOW_CONTROL=false
```

The advertised service points to the connector port, not the NMMiner port. The HTTP `Host` header identifies the virtual `.local` miner and selects the real target.

## Verification

```bash
curl http://192.168.50.173:5080/health
curl -s http://192.168.50.173:5080/api/swarm/devices | jq
```

On Linux with Avahi:

```bash
avahi-browse -rt _axeos._sub._http._tcp
```

A discovered NMMiner should appear with a `.local` hostname. Opening that hostname on port `5080` returns the proxied AxeOS-compatible API.

## Limitations

This is an API/DNS-SD compatibility bridge, not a firmware replacement. The original NMMiner IP remains the actual mining/management device; the connector supplies the AxeOS-facing discovery identity. OTA and destructive control operations are deliberately not enabled by default.
