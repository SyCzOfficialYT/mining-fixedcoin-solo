# Operations

## Deploy

```bash
git pull --ff-only
sudo docker compose down
sudo docker compose up -d --build
```

## Verify GhostBot patch

```bash
sudo docker logs --since 2m fixedcoin-solo 2>&1 | grep -Ei 'GhostBot|BLOCK CANDIDATE|webhook'
```

## Verify runtime environment

```bash
sudo docker exec fixedcoin-solo sh -c 'python3 - <<"PY"
import os
print("GHOSTBOT_WEBHOOK_URL configured:", bool(os.getenv("GHOSTBOT_WEBHOOK_URL")))
print("GHOSTBOT_WEBHOOK_USERNAME:", os.getenv("GHOSTBOT_WEBHOOK_USERNAME"))
PY'
```

Never print the webhook URL itself in shared logs or screenshots.

## Rebuild trigger

Webhook integration is installed during the Docker build because `stratum/server.py` generates `server_full.py` first.

#operations #docker #deployment
