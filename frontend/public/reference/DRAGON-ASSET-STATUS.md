# Dragon asset status

The production dashboard now uses the generated dragon artwork from `frontend/public/reference/`.

- `left-dragon.svg` — embedded WebP artwork, committed on `main`.
- `right-dragon.svg` — embedded WebP artwork, committed on `main`.
- `frontend/app/components.tsx` resolves the artwork to `/reference/left-dragon.svg` and `/reference/right-dragon.svg`.

Do not replace these assets with CSS/SVG approximations or malformed Base64. If the artwork is regenerated, replace the complete SVG asset with a valid embedded WebP and verify that the Base64 payload decodes before committing.
