(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => {
    n = Number(n) || 0;
    if (n >= 1e12) return (n / 1e12).toFixed(2) + 'T';
    if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(2) + 'K';
    return n.toFixed(n < 10 ? 2 : 0);
  };
  const fix = (n) => (Number(n) || 0).toFixed(8) + ' FIX';
  const fixShort = (n) => {
    const v = Number(n) || 0;
    if (v >= 1) return v.toFixed(3) + ' FIX';
    if (v >= 0.001) return v.toFixed(6) + ' FIX';
    return v.toFixed(8) + ' FIX';
  };
  // Placeholder USD rate until price feed exists (display only)
  const USD_RATE = 36.0;
  const usd = (n) => '≈ $' + ((Number(n) || 0) * USD_RATE).toFixed(2) + ' USD';

  function setText(id, val) {
    const el = $(id);
    if (el) el.textContent = val;
  }

  function enrich() {
    fetch('/api/status?ts=' + Date.now(), { cache: 'no-store' })
      .then((r) => r.json())
      .then((s) => {
        if (!s) return;
        const m = s.mining || {};
        const r = s.round || {};
        const w = s.wallet || {};
        const n = s.node || {};

        // Effort / Luck
        const effort = m.round_effort ?? r.effort_pct;
        if (effort != null) {
          const e = Number(effort) || 0;
          setText('roundEffort', e.toFixed(1) + '%');
          setText('luckLabel', e >= 100 ? 'Above Average' : 'Round Effort');
        }

        // Workers
        const wc = m.worker_count ?? (m.active_workers || []).length ?? 0;
        setText('workerCount', String(wc));
        setText('liveWorkersDisplay', String(wc));

        // Node
        setText('nodeStatus', n.online ? 'ONLINE' : 'OFFLINE');
        const st = document.getElementById('nodeStatus');
        if (st) st.className = n.online ? 'ok' : 'bad';

        // Balances
        setText('confirmedBalance', fix(w.confirmed));
        setText('unconfirmedBalance', fix(w.unconfirmed ?? w.pending));
        setText('immatureBalance', fix(w.immature));
        setText('totalBalance', fixShort(w.total));
        setText('usdApprox', usd(w.total));

        // Earnings cards (map from wallet until dedicated payout API)
        setText('estEarn', fixShort(w.immature || 0));
        setText('estEarnUsd', usd(w.immature || 0));
        setText('pendingPayout', fixShort(w.unconfirmed ?? w.pending ?? 0));
        setText('pendingUsd', usd(w.unconfirmed ?? w.pending ?? 0));
        setText('totalPaid', fixShort(w.total_rewards ?? w.confirmed ?? 0));
        setText('totalPaidUsd', usd(w.total_rewards ?? w.confirmed ?? 0));

        // Server time
        const now = new Date();
        setText('serverTime', now.toISOString().slice(11, 19));

        // Net meter visual (always full for network target side)
        const nm = $('netMeter');
        if (nm) nm.style.width = '100%';
      })
      .catch(() => {});
  }

  // Particle sparkles on core
  function spawnParticles() {
    const host = $('coreParticles');
    if (!host) return;
    host.innerHTML = '';
    for (let i = 0; i < 18; i++) {
      const d = document.createElement('div');
      d.style.cssText = [
        'position:absolute',
        'width:' + (1 + Math.random() * 2) + 'px',
        'height:' + (1 + Math.random() * 2) + 'px',
        'border-radius:50%',
        'background:' + (Math.random() > 0.5 ? '#c4b5fd' : '#67e8f9'),
        'left:' + (20 + Math.random() * 60) + '%',
        'top:' + (15 + Math.random() * 70) + '%',
        'opacity:' + (0.3 + Math.random() * 0.6),
        'box-shadow:0 0 6px currentColor',
        'animation:float ' + (3 + Math.random() * 4) + 's ease-in-out infinite',
        'animation-delay:' + (Math.random() * 2) + 's',
      ].join(';');
      host.appendChild(d);
    }
  }

  spawnParticles();
  setInterval(enrich, 3000);
  enrich();
})();
