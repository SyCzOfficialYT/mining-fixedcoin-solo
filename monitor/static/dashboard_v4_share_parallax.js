(() => {
  'use strict';
  if (window.__FIXEDCOIN_SHARE_PARALLAX_V7__) return;
  window.__FIXEDCOIN_SHARE_PARALLAX_V7__ = true;

  const stage = document.getElementById('forgeStage');
  if (!stage) return;

  const cards = [
    stage.querySelector('.forge-counter.accepted'),
    stage.querySelector('.forge-counter.rejected'),
  ].filter(Boolean);
  if (!cards.length) return;

  let raf = 0;
  let tx = 0, ty = 0, cx = 0, cy = 0;

  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  const render = () => {
    raf = 0;
    cx += (tx - cx) * 0.1;
    cy += (ty - cy) * 0.1;
    const px = cx.toFixed(3) + 'deg';
    const py = cy.toFixed(3) + 'deg';
    for (const c of cards) {
      c.style.setProperty('--px', px);
      c.style.setProperty('--py', py);
    }
    if (Math.abs(tx - cx) > 0.02 || Math.abs(ty - cy) > 0.02) {
      raf = requestAnimationFrame(render);
    }
  };

  const schedule = () => { if (!raf) raf = requestAnimationFrame(render); };

  const setTarget = (x, y) => {
    tx = clamp(x, -4, 4);
    ty = clamp(y, -2.5, 2.5);
    schedule();
  };

  const pointer = (clientX, clientY) => {
    const r = stage.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const nx = clamp(((clientX - r.left) / r.width) * 2 - 1, -1, 1);
    const ny = clamp(((clientY - r.top) / r.height) * 2 - 1, -1, 1);
    setTarget(-nx * 4, -ny * 2.5);
  };

  stage.addEventListener('pointermove', (e) => pointer(e.clientX, e.clientY), { passive: true });
  stage.addEventListener('pointerleave', () => setTarget(0, 0), { passive: true });
  stage.addEventListener('touchmove', (e) => {
    const t = e.touches[0];
    if (t) pointer(t.clientX, t.clientY);
  }, { passive: true });
  stage.addEventListener('touchend', () => setTarget(0, 0), { passive: true });
  window.addEventListener('blur', () => setTarget(0, 0), { passive: true });
  schedule();
})();
