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
RUN STRATUM_BUILD_ONLY=1 python3 /app/stratum/server.py \
 && python3 /app/scripts/fixcoin_consensus_patch.py \
 && python3 /app/scripts/fixcoin_network_difficulty_patch.py \
 && python3 /app/scripts/fixcoin_stratum_difficulty_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_difficulty_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_realtime_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_v4_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_v4_js_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_round_authority_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_forge_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_balance_activity_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_activity_authority_patch.py \
 && python3 /app/scripts/fixcoin_axeos_hashrate_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_forge_upgrade_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_forge_collision_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_forge_metrics_bevel_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_route_v4_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_candidate_final_patch.py \
 && python3 /app/scripts/fixcoin_dashboard_animation_perf_patch.py \
 && sed -i 's/dashboard_v4_candidate_final\.css?v=20260825-1/dashboard_v4_candidate_final.css?v=20260825-2/g; s/dashboard_v4_animation_perf\.css?v=20260825-1/dashboard_v4_animation_perf.css?v=20260825-2/g; s/dashboard_v4_animation_perf\.js?v=20260825-1/dashboard_v4_animation_perf.js?v=20260825-2/g' /app/monitor/templates/dashboard_v4.html \
 && python3 -m py_compile /app/monitor/app.py /app/stratum/server.py /app/stratum/server_full.py /app/scripts/fixcoin_consensus_patch.py /app/scripts/fixcoin_network_difficulty_patch.py /app/scripts/fixcoin_stratum_difficulty_patch.py /app/scripts/fixcoin_dashboard_difficulty_patch.py /app/scripts/fixcoin_dashboard_realtime_patch.py /app/scripts/fixcoin_dashboard_v4_patch.py /app/scripts/fixcoin_dashboard_v4_js_patch.py /app/scripts/fixcoin_dashboard_round_authority_patch.py /app/scripts/fixcoin_dashboard_forge_patch.py /app/scripts/fixcoin_dashboard_balance_activity_patch.py /app/scripts/fixcoin_dashboard_activity_authority_patch.py /app/scripts/fixcoin_axeos_hashrate_patch.py /app/scripts/fixcoin_dashboard_forge_upgrade_patch.py /app/scripts/fixcoin_dashboard_forge_collision_patch.py /app/scripts/fixcoin_dashboard_forge_metrics_bevel_patch.py /app/scripts/fixcoin_dashboard_route_v4_patch.py /app/scripts/fixcoin_dashboard_candidate_final_patch.py /app/scripts/fixcoin_dashboard_animation_perf_patch.py \
 && chmod +x /app/docker/entrypoint.sh /app/scripts/setup_address.py
ENV FIX_DATADIR=/data/fixedcoin FIX_RPCPORT=24761 FIX_P2PPORT=24768 FIX_DASH_PORT=5050
EXPOSE 3333 5050 24768
ENTRYPOINT ["/app/docker/entrypoint.sh"]
