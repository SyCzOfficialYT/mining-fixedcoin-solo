# Dragon asset status

The current `left-dragon.svg` on `main` contains an embedded WebP data URI that is malformed and does not decode as valid Base64. The exact generated artwork binary is not available to the repository write API from the current chat context, so this checkpoint intentionally does not replace the artwork with a fabricated approximation.

Required production action: add the actual generated dragon artwork as a real binary asset (preferably `left-dragon.webp` / `right-dragon.webp`) and reference those files directly from the dashboard. Do not continue patching the malformed Base64 URI.
