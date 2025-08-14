# Events System

## Data Flow
JSON (events.beta.json) -> RegistryBootstrap -> EventRegistry (List<EventDef>).
An EventDef has multiple EventChoice, each with textual effects (string tokens).

## Current Runtime
1. EventTriggerScanSystem periodically (config interval) and RNG probability spawns an empty entity tagged EventPendingTag.
2. EventResolutionSystem picks a random event from registry, auto-selects first choice (placeholder).
3. Effects are textual stubs only; no parser yet.

## Planned Effect DSL
Syntax examples:
- morale+2, warmth-3, hunger+5
- add_item:Raw Meat:2
- doctrine_progress:stoicism:5
- spawn_monster:ice_wolf:1

Will parse into structured actions (enum opcode + payload).

## Milestone 3 Additions
- Deterministic event selection weighting
- Conditional triggers (needs thresholds, doctrine state)
- Player choice resolution pipeline (UI integration hook)