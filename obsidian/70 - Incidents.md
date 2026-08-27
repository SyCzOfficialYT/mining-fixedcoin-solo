# Incidents

## 2026-08-27 — Block candidate had no dashboard animation

### Symptom

The dashboard reached `100.00%` but did not visibly celebrate a block candidate.

### Cause

The backend emitted a `type=block` SSE event, while the v4 dashboard live-event handler only reacted to accept/reject events.

### Fix

Added the repository-owned block FX patch. The `block` event now triggers the Forge celebration and dispatches `fixedcoin:block`.

### Lesson

Every backend event that represents a meaningful operator event needs an explicit frontend consumer and a documented event contract.

## 2026-08-27 — Low-hash VarDiff overshot too aggressively

### Observation

NerdQAxe/NMMiner low-hash shares were accepted, but the pool-side share difficulty could climb rapidly while network difficulty remained much higher.

### Rule

Low-hash share difficulty is an accounting/compatibility threshold. It must remain separate from network difficulty and never become the block target.

#incidents #postmortem #debugging
