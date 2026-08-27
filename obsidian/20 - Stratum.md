# Stratum

## Miner compatibility

Known low-hash families:

- NMMiner
- NerdMiner
- NerdQAxe / NerdQAxe++

Low-hash mode advertises a small **share difficulty** so these devices can produce useful shares. This does **not** alter the network target.

## Difficulty model

- `pool/share difficulty` = miner-facing work threshold
- `network difficulty` = consensus block threshold
- `share_work` = actual difficulty derived from the submitted hash

These values must never be conflated.

## Acceptance rule

A normal share must meet the current miner difficulty. A block candidate must additionally meet the network target.

## VarDiff

Low-hash VarDiff is allowed to tune share difficulty without touching network difficulty. It must not turn a miner's low share target into a block target.

#stratum #difficulty #nerdqaxe #nerdminer
