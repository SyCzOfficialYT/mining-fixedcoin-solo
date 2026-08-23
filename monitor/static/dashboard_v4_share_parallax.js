(() => {
  'use strict';
  if (window.__FIXEDCOIN_SHARE_PARALLAX_V5__) return;
  window.__FIXEDCOIN_SHARE_PARALLAX_V5__ = true;

  const stage = document.getElementById('forgeStage');
  if (!stage) return;

  const accepted = stage.querySelector('.forge-counter.accepted');
  const rejected = stage.querySelector('.forge-counter.rejected');
  const cards = [accepted, rejected].filter(Boolean);
  if (!cards.length) return;

  let raf = 0;
  let targetX = 0, targetY = 0;
  let currentX = 0, currentY = 0;

  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));

  const render = () => {
    raf = 0;
    currentX += (targetX - currentX) * 0.1;
    currentY += (targetY - currentY) * 0.1;
    for (const c of cards) {
      c.style.setProperty('--px', `${currentX.toFixed(3)}deg`);
      c.style.setProperty('--py', `${currentY.toFixed(3)}deg`);
    }
    if (Math.abs(targetX - currentX) > 0.01 || Math.abs(targetY - currentY) > 0.01) {
      raf = requestAnimationFrame(render);
    }
  };

  const schedule = () => {
    if (!raf) raf = requestAnimationFrame(render);
  };

  const setTarget = (x, y) => {
    targetX = clamp(x, -2, 2);
    targetY = clamp(y, -1.2, 1.2);
    schedule();
  };

  const pointer = (clientX, clientY) => {
    const r = stage.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const nx = clamp(((clientX - r.left) / r.width) * 2 - 1, -1, 1);
    const ny = clamp(((clientY - r.top) / r.height) * 2 - 1, -1, 1);
    setTarget(-nx * 2, -ny * 1.2);
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
