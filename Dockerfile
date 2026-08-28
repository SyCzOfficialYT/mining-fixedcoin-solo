FROM python:3.12-slim-bookworm
ARG FIX_VER=29.1.3
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates wget tar && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/fixedcoin \
 && curl -fsSL -o /tmp/fix.tgz "https://github.com/Fixed-Blockchain/fixedcoin/releases/download/v${FIX_VER}/fixedcoin-${FIX_VER}-x86_64-linux-gnu.tar.gz" \
 && tar -xzf /tmp/fix.tgz -C /opt/fixedcoin --strip-components=1 \
 && rm /tmp/fix.tgz \
 && ln -sf /opt/fixedcoin/bin/fixedcoind /usr/local/bin/fixedcoind \
 && ln -sf /opt/fixedcoin/bin/fixedcoin-cli /usr/local/bin/fixedcoin-cli
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app

# Apply deterministic backend/telemetry patches plus the repository-owned
# complete Arcane LiveShare reference presentation. Historical visual layers
# are intentionally not part of the production build.
RUN STRATUM_BUILD_ONLY=1 python3 /app/stratum/server.py \
 && python3 /app/scripts/fixcoin_ghostbot_webhook_patch.py \
 && python3 /app/scripts/fixcoin_consensus_patch.py \
 && python3 /app/scripts/fixcoin_network_difficulty_patch.py \
 && python3 /app/scripts/fixcoin_stratum_difficulty_patch.py \
 && python3 /app/scripts/fixcoin_stratum_miner_detection_patch.py \
 && python3 /app/scripts/fixcoin_stratum_nmminer_diff_patch.py \
 && python3 /app/scripts/fixcoin_stratum_diff_job_epoch_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_difficulty_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_realtime_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_route_v4_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_v4_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_v4_js_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_round_authority_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_forge_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_balance_activity_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_activity_authority_patch.py \
 && python3 /app/scripts/fixcoin_axeos_hashrate_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_fx_identity_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_miner_identity_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_miner_stats_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_worker_attribution_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_block_fx_patch.py \
 && python3 -c "from pathlib import Path; p=Path('/app/scripts/fixcoin_dashboard_reference_complete_patch.py'); s=p.read_text(encoding='utf-8'); bad=\"compile(compile(Path(__file__).read_text(encoding='utf-8'), str(__file__), 'exec'), str(__file__), 'exec')\"; good=\"compile(Path(__file__).read_text(encoding='utf-8'), str(__file__), 'exec')\"; p.write_text(s.replace(bad, good), encoding='utf-8') if bad in s else None; print('normalized dashboard reference patch self-validation')" \
 && python3 -m py_compile /app/scripts/fixcoin_dashboard_reference_complete_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_reference_complete_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_reference_runtime_patch.py \
 && python3 -m py_compile /app/monitor/app.py /app/stratum/server.py /app/stratum/server_full.py /app/scripts/fixcoin_consensus_patch.py /app/scripts/fixcoin_network_difficulty_patch.py /app/scripts/fixcoin_stratum_difficulty_patch.py /app/scripts/fixcoin_stratum_miner_detection_patch.py /app/scripts/fixcoin_stratum_nmminer_diff_patch.py /app/scripts/fixcoin_stratum_diff_job_epoch_patch.py /app/scripts/fixcoin_dashboard_difficulty_patch.py /app/scripts/fixcoin_dashboard_realtime_patch.py /app/scripts/fixcoin_dashboard_route_v4_patch.py /app/scripts/fixcoin_dashboard_v4_patch.py /app/scripts/fixcoin_dashboard_v4_js_patch.py /app/scripts/fixcoin_dashboard_round_authority_patch.py /app/scripts/fixcoin_dashboard_forge_patch.py /app/scripts/fixcoin_dashboard_balance_activity_patch.py /app/scripts/fixcoin_dashboard_activity_authority_patch.py /app/scripts/fixcoin_axeos_hashrate_patch.py /app/scripts/fixcoin_dashboard_fx_identity_patch.py /app/scripts/fixcoin_dashboard_miner_identity_patch.py /app/scripts/fixcoin_dashboard_miner_stats_patch.py /app/scripts/fixcoin_dashboard_worker_attribution_patch.py /app/scripts/fixcoin_dashboard_block_fx_patch.py /app/scripts/fixcoin_dashboard_reference_complete_patch.py /app/scripts/fixcoin_dashboard_reference_runtime_patch.py /app/scripts/fixcoin_ghostbot_webhook_patch.py /app/scripts/test_stratum_authorization.py \
 && python3 /app/scripts/test_stratum_authorization.py \
 && chmod +x /app/docker/entrypoint.sh /app/scripts/setup_address.py

ENV FIX_DATADIR=/data/fixedcoin FIX_RPCPORT=24761 FIX_P2PPORT=24768 FIX_DASH_PORT=5050
EXPOSE 3333 5050 5051 24768
ENTRYPOINT ["/app/docker/entrypoint.sh"]
