# FixedCoin Dashboard Agent Task

**Mode:** agent / execute-to-completion
**Scope:** `dashboard_v4`, realtime forge, block-candidate HUD, animation performance, responsive reference layout, Docker build integrity, final visual polish.
**Date:** 2026-08-25

## Objective

Rebuild the dashboard against the supplied reference image instead of merely stacking small CSS overrides. The live dashboard must retain realtime mining telemetry while presenting the cyberpunk/industrial HUD composition: visible central FIX hexagon, 3D card depth/parallax, forge particle volume, particles on progress bars, integrated block-candidate HUD, and five balance/ETA cards.

## Task Queue

- [x] Keep `dashboard_v4` as the canonical dashboard template.
- [x] Preserve realtime status/log rendering and existing mining/Stratum telemetry IDs.
- [x] Preserve the canonical `.particle-canvas` primitive used by the existing v4 renderer.
- [x] Add a dedicated block-candidate particle lane on the progress bar.
- [x] Add a dedicated network-target particle lane on the progress bar.
- [x] Add a dedicated forge particle volume using one Canvas compositor layer.
- [x] Keep the central FIXCORE/HUD visible instead of allowing mobile/reference overrides to hide it.
- [x] Apply the reference three-zone forge composition: left metrics / center core / right accepted-rejected telemetry.
- [x] Add physical 3D card shells and bounded pointer parallax.
- [x] Add the reference block-candidate core with rings, cube logo, status labels and depth grid.
- [x] Restore the five balance/ETA cards and bind them to the live wallet values returned by `/api/status`.
- [x] Make live VarDiff visible in the center HUD from the active worker difficulty.
- [x] Keep responsive mobile composition structurally faithful instead of collapsing the forge into a single column.
- [x] Keep mining/consensus/Stratum logic untouched by the visual rebuild.
- [x] Make `dashboard_v4.html` the persistent monitor route target in `monitor/app.py`.
- [x] Version-pin the final reference CSS/JS assets to avoid stale browser cache.
- [x] Create a dedicated final visual layer instead of continuing to mutate unrelated historical v4 CSS files.
- [x] Document the work in this memory task.
- [ ] **LOCAL VERIFICATION:** on the target CachyOS host, pull `main`, rebuild/restart Docker, verify `/`, static asset versions, console/runtime errors, and visually compare desktop + mobile against the supplied reference.

## Implemented in this pass

- `monitor/templates/dashboard_v4.html` was rebuilt around the reference composition and now contains the center FIX HUD, explicit bar-particle canvases, candidate HUD, three primary share cards, five balance/ETA cards and the existing block-history surface.
- `monitor/static/dashboard_v4_reference_final.css` is the final visual composition layer. It owns the reference geometry, 3D physical card shells, depth grid, core rings/logo, candidate core, responsive scaling and five-card balance row.
- `monitor/static/dashboard_v4_reference_final.js` adds live wallet/VarDiff binding, a single forge particle field, progress-bar particle streams and bounded pointer parallax.
- `monitor/app.py` now serves `dashboard_v4.html` at `/`.

## Acceptance Criteria

1. Central FIX logo is visible on desktop and mobile.
2. Forge remains a three-zone composition: left telemetry / center core / right share telemetry.
3. 3D card depth/parallax is visibly present without breaking scrolling.
4. Both progress bars show animated particles near the actual best-share position.
5. Five balance/ETA cards are visible and update from `/api/status`.
6. Block history and existing live counters continue to render.
7. No Stratum/consensus behavior is changed by the visual pass.
8. Docker/browser verification remains the final unchecked step because it must be performed against the user's running node.

## Verification Commands

```bash
git pull --ff-only
sudo docker compose down
sudo docker compose up -d --build
sudo docker logs --tail=200 fixedcoin-solo
curl -s http://127.0.0.1:5050/ | grep -oE 'dashboard_v4_reference_final\.(css|js)[^" ]*' | sort -u
sudo docker exec fixedcoin-solo sh -c 'grep -oE "forgeParticles|targetParticles|candidateParticles|liveVarDiff|confirmedBalance|unconfirmedBalance|immatureBalance|totalBalance" /app/monitor/templates/dashboard_v4.html | sort -u'
```
