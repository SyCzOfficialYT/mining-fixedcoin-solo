(() => {
  'use strict';
  if (window.__FIXEDCOIN_SHARE_PARALLAX_V11__) return;
  window.__FIXEDCOIN_SHARE_PARALLAX_V11__ = true;

  const stage = document.getElementById('forgeStage');
  if (!stage) return;

  const shareCards = [
    stage.querySelector('.forge-counter.accepted'),
    stage.querySelector('.forge-counter.rejected'),
  ].filter(Boolean);

  const metricCards = [
    stage.querySelector('.hashrate-card'),
    stage.querySelector('.forge-shares-min'),
  ].filter(Boolean);

  if (!shareCards.length && !metricCards.length) return;

  let raf = 0;
  let tx = 0, ty = 0;
  let cx = 0, cy = 0;

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  const render = () => {
    raf = 0;
    cx += (tx - cx) * 0.12;
    cy += (ty - cy) * 0.12;

    const px = cx.toFixed(3) + 'deg';
    const py = cy.toFixed(3) + 'deg';

    // Accepted / rejected use the reference card's exact parallax range.
    for (const card of shareCards) {
      card.style.setProperty('--px', px);
      card.style.setProperty('--py', py);
    }

    // Metrics deliberately use the SAME parallax values — no weakened 0.72x layer.
    for (const card of metricCards) {
      card.style.setProperty('--metric-px', px);
      card.style.setProperty('--metric-py', py);
    }

    if (Math.abs(tx - cx) > 0.02 || Math.abs(ty - cy) > 0.02) {
      raf = requestAnimationFrame(render);
    }
  };

  const go = () => {
    if (!raf) raf = requestAnimationFrame(render);
  };

  const set = (x, y) => {
    tx = clamp(x, -5, 5);
    ty = clamp(y, -3, 3);
    go();
  };

  const pointer = (x, y) => {
    const r = stage.getBoundingClientRect();
    if (!r.width || !r.height) return;

    const nx = clamp(((x - r.left) / r.width) * 2 - 1, -1, 1);
    const ny = clamp(((y - r.top) / r.height) * 2 - 1, -1, 1);

    set(-nx * 5, -ny * 3);
  };

  stage.addEventListener('pointermove', e => pointer(e.clientX, e.clientY), { passive: true });
  stage.addEventListener('pointerleave', () => set(0, 0), { passive: true });
  stage.addEventListener('touchmove', e => {
    const t = e.touches[0];
    if (t) pointer(t.clientX, t.clientY);
  }, { passive: true });
  stage.addEventListener('touchend', () => set(0, 0), { passive: true });
  window.addEventListener('blur', () => set(0, 0), { passive: true });
})();
