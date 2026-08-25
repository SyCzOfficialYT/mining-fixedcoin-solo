#!/usr/bin/env python3
"""Reduce the cost of the animated FIX core on mobile devices.

The visual core is intentionally kept smooth, but expensive transform/style
updates are capped relative to the physical display refresh rate:
  <= 60 Hz  -> 30 fps
  <= 90 Hz  -> 45 fps
  <= 120 Hz -> 60 fps
  > 120 Hz  -> 60 fps (including 600 Hz panels)

This avoids trying to animate the logo at 90/120/600 browser frames per
second while preserving a fluid compositor-friendly transform animation.
Idempotent: safe to run repeatedly in the Docker build pipeline.
"""
from pathlib import Path
import re

HTML = Path('/app/monitor/templates/dashboard_v4.html')
CSS = Path('/app/monitor/static/dashboard_v4_reference_final.css')

html = HTML.read_text()
css = CSS.read_text()

if 'id="forgeCore"' not in html:
    raise RuntimeError('core perf patch: forgeCore anchor missing')

css_marker = '/* FIXCOIN CORE PERF v1 */'
if css_marker not in css:
    css += r'''

/* FIXCOIN CORE PERF v1 */
/* The FIX logo is driven by a capped compositor-friendly loop on mobile. */
@media (max-width:760px){
  .reference-dashboard .core-logo{
    animation:none!important;
    will-change:transform;
  }
  .reference-dashboard .core-logo::before{
    animation:none!important;
    transform:var(--cp-diamond-a,rotate(45deg) scale(.92))!important;
    will-change:transform;
  }
  .reference-dashboard .core-logo::after{
    animation:none!important;
    transform:var(--cp-diamond-b,rotate(45deg) scale(.92))!important;
    will-change:transform;
  }
}
@media (prefers-reduced-motion:reduce){
  .reference-dashboard .core-logo,
  .reference-dashboard .core-logo::before,
  .reference-dashboard .core-logo::after{
    animation:none!important;
  }
}
'''
    CSS.write_text(css)

js_marker = '/* FIXCOIN CORE PERF JS v1 */'
if js_marker not in html:
    script = r'''<script>
/* FIXCOIN CORE PERF JS v1 */
(function(){
  'use strict';
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (!window.matchMedia || !window.matchMedia('(max-width: 760px)').matches) return;

  var core = document.getElementById('forgeCore');
  if (!core) return;

  var root = document.documentElement;
  var last = 0;
  var start = 0;
  var refreshHz = 60;
  var targetFps = 30;
  var targetMs = 1000 / targetFps;
  var raf = 0;
  var samples = [];

  function median(values){
    var a = values.slice().sort(function(x,y){ return x-y; });
    return a[Math.floor(a.length / 2)] || 16.67;
  }

  function chooseRate(hz){
    /* Keep animation below physical refresh to avoid needless work. */
    if (hz <= 60) return 30;
    if (hz <= 90) return 45;
    return 60;
  }

  function setRefreshRate(hz){
    refreshHz = Math.max(30, Math.min(1000, hz || 60));
    targetFps = chooseRate(refreshHz);
    targetMs = 1000 / targetFps;
    root.style.setProperty('--cp-core-refresh', Math.round(refreshHz) + 'Hz');
    root.style.setProperty('--cp-core-fps', String(targetFps));
  }

  function measure(ts){
    if (!samples.length) samples.push(ts);
    else {
      var delta = ts - samples[samples.length - 1];
      if (delta > 0 && delta < 100) samples.push(ts);
    }
    if (samples.length < 25) {
      raf = requestAnimationFrame(measure);
      return;
    }
    var deltas = [];
    for (var i=1; i<samples.length; i++) deltas.push(samples[i] - samples[i-1]);
    setRefreshRate(1000 / median(deltas));
    start = performance.now();
    last = 0;
    raf = requestAnimationFrame(render);
  }

  function render(ts){
    if (document.hidden) {
      raf = requestAnimationFrame(render);
      return;
    }
    if (!last || ts - last >= targetMs - 0.5) {
      if (!start) start = ts;
      var elapsed = (ts - start) / 1000;
      var floatY = Math.sin((elapsed / 4.8) * Math.PI * 2) * 5;
      var angleA = (elapsed / 12) * 360 + 45;
      var angleB = -(elapsed / 17) * 360 + 45;
      var scaleA = 0.92 + ((Math.sin((elapsed / 12) * Math.PI * 2) + 1) * 0.5) * 0.12;
      var scaleB = 0.92 + ((Math.sin((elapsed / 17) * Math.PI * 2) + 1) * 0.5) * 0.12;

      core.style.transform = 'translateZ(70px) translateY(' + floatY.toFixed(2) + 'px)';
      core.style.setProperty('--cp-diamond-a', 'rotate(' + angleA.toFixed(2) + 'deg) scale(' + scaleA.toFixed(3) + ')');
      core.style.setProperty('--cp-diamond-b', 'rotate(' + angleB.toFixed(2) + 'deg) scale(' + scaleB.toFixed(3) + ')');
      last = ts;
    }
    raf = requestAnimationFrame(render);
  }

  core.style.setProperty('--cp-diamond-a', 'rotate(45deg) scale(.92)');
  core.style.setProperty('--cp-diamond-b', 'rotate(45deg) scale(.92)');
  raf = requestAnimationFrame(measure);

  document.addEventListener('visibilitychange', function(){
    if (!document.hidden) {
      start = performance.now();
      last = 0;
    }
  }, {passive:true});

  window.addEventListener('pagehide', function(){
    if (raf) cancelAnimationFrame(raf);
  }, {passive:true});
})();
</script>'''
    html = html.replace('</body>', script + '\n</body>')

# Keep the CSS cache bust in sync with the performance layer.
html = re.sub(r'(dashboard_v4_reference_final\.css\?v=)[^"\']+', r'\g<1>20260825-cp2', html)
HTML.write_text(html)
print('dashboard core mobile performance patch applied')
