(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => {
    n = Number(n) || 0;
    if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(2) + 'K';
    return n.toFixed(n < 10 ? 2 : 0);
  };
  const fix = (n) => (Number(n) || 0).toFixed(8) + ' FIX';
  async function enrich() {
    try {
      const s = await fetch('/api/status?ts=' + Date.now(), { cache: 'no-store' }).then((r) => r.json());
      const effort = s?.mining?.round_effort ?? s?.round?.effort_pct;
      if ($('roundEffort') && effort != null) $('roundEffort').textContent = (Number(effort) || 0).toFixed(2) + '%';
      if ($('workerCount')) $('workerCount').textContent = String(s?.mining?.worker_count ?? s?.mining?.active_workers?.length ?? 0);
      if ($('nodeStatus')) $('nodeStatus').textContent = s?.node?.online ? 'ONLINE' : 'OFFLINE';
      const w = s?.wallet || {};
      if ($('confirmedBalance')) $('confirmedBalance').textContent = fix(w.confirmed);
      if ($('unconfirmedBalance')) $('unconfirmedBalance').textContent = fix(w.unconfirmed ?? w.pending);
      if ($('immatureBalance')) $('immatureBalance').textContent = fix(w.immature);
      if ($('totalBalance')) $('totalBalance').textContent = fix(w.total);
    } catch (_) {}
  }
  setInterval(enrich, 3000);
  enrich();
})();
