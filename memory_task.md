# FixedCoin Dashboard Agent Task

**Mode:** agent / execute-to-completion
**Scope:** `dashboard_v4`, realtime forge, block-candidate particles, animation performance, responsive reference layout, Docker build integrity.
**Date:** 2026-08-25

## Objective

Bring the dashboard to the reference layout while keeping realtime telemetry intact and moving animation work onto low-overhead canvas compositor layers. The block-candidate area must have its own particle treatment, and Docker builds must not fail because a validator expects post-build DOM that is intentionally injected later.

## Task Queue

- [x] Keep `dashboard_v4` as the canonical dashboard template.
- [x] Preserve realtime SSE, authoritative round/timer state, accepted/rejected share telemetry and FIXCORE forge primitives.
- [x] Keep the canonical `.particle-canvas` realtime primitive available to the v4 validator.
- [x] Add a dedicated block-candidate particle canvas layer.
- [x] Add a dedicated candidate-core particle layer for the block-candidate HUD.
- [x] Move high-frequency forge particles/events to a single compositor canvas with visibility/FPS throttling.
- [x] Pause animation work when the forge is outside the viewport.
- [x] Respect `prefers-reduced-motion` and `navigator.connection.saveData`.
- [x] Apply the reference three-column desktop forge layout and responsive mobile compositor layout.
- [x] Keep the reference layout and animation CSS version-pinned in the generated dashboard.
- [x] Run the animation performance patch after the canonical v4 primitives exist.
- [x] Make the v4 validator validate canonical source primitives instead of requiring post-build canvas injection.
- [x] Ensure Docker runs the reference-layout patch and animation-performance patch during image build.
- [ ] **LOCAL VERIFICATION:** pull `main`, rebuild the image, start the container, then verify `/`, static asset versions, dashboard particle layers and clean startup logs on the target host.

## Known Failure That Triggered This Task

The Docker build previously stopped in `fixcoin_dashboard_v4_js_patch.py` with:

`RuntimeError: dashboard v4 is missing required realtime/FIXCORE primitives: .particle-canvas|modern compositor canvas`

The root cause was validator/build-order coupling: the performance compositor creates some canvases dynamically, so the validator must not require those post-build DOM nodes. The canonical `particleCanvas` primitive is validated in the dashboard layer, while the performance patch owns the dynamically created compositor layers.

## Current Repository State

The repository already contains the corresponding repair chain on `main`, including:

- v4 validator build-order repair
- candidate particle canvas
- modern compositor acceptance
- reference forge layout/responsive compositor CSS
- animation performance compositor pinned to `v20260825-3`

The latest `main` commit is expected to be used as the source of truth. The remaining unchecked item is deliberately a host-side verification step because this agent cannot execute Docker on the user's CachyOS workstation.

## Verification Commands

```bash
git pull --ff-only
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d
sudo docker logs --tail=200 fixedcoin-solo
curl -s http://127.0.0.1:5050/ | grep -oE 'dashboard_v4_animation_perf\\.(css|js)[^" ]*|dashboard_v4_reference_layout\\.css[^" ]*' | sort -u
sudo docker exec fixedcoin-solo sh -c 'grep -oE "particle-canvas|candidate-particle-canvas|candidate-core-particle-canvas|fx-animation-canvas" /app/monitor/templates/dashboard_v4.html | sort -u'
```

## Exit Criteria

1. Docker build reaches completion without the v4 primitive validator error.
2. Container starts with FixedCoin Solo online.
3. Dashboard serves the pinned animation/reference assets.
4. Forge particles remain animated without a runaway per-element animation workload.
5. Block Candidate visibly receives its own particle treatment.
6. Mobile layout retains the central FIXCORE/HUD instead of simply hiding it.
7. Realtime share counters/events continue to work.
