# LiveShare / Arcane Forge Dashboard

## Event flow

The dashboard consumes `/api/stream` SSE events.

Supported event classes include:

- `accept`
- `reject`
- `round`
- `block`

A `block` event triggers the visible Arcane Forge block-found FX.

## Block celebration

The block FX is intentionally separate from consensus. It is presentation only:

- Forge hit/pulse
- candidate core pulse
- particle burst
- `BLOCK CANDIDATE FOUND` banner
- browser event `fixedcoin:block`

The backend remains authoritative.

## UI rule

Never make a dashboard animation imply a block that the backend did not emit.

#dashboard #liveshare #arcane-forge
