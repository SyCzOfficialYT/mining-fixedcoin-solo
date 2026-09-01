# Dragon asset status

The production dashboard uses the committed dragon artwork in `frontend/public/reference/`.

- `left-dragon.webp` is the canonical transparent purple dragon plate.
- `right-dragon.svg` is a valid wrapper around the canonical WebP; the dashboard mirrors and color-shifts it to produce the blue counterpart without embedding malformed Base64.
- `frontend/app/components.tsx` loads `/reference/left-dragon.webp` and `/reference/right-dragon.svg` directly.
- `frontend/app/reference-v8.css` controls the reference-scale placement and responsive composition.

The dashboard must not use the old malformed embedded-WebP payloads. Keep the artwork at native aspect ratio and avoid bitmap stretching that causes softness.
