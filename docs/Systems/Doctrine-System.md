# Doctrine System

## Purpose
Represents cultural / ideological modifiers influencing simulation (decay rates, yields, morale).

## Data
doctrines.alpha.json -> DoctrineRegistry.

## Current Implementation
DoctrineState component (two integer slots referencing doctrine IDs). NeedsDecaySystem queries DoctrineState to adjust morale decay (stoicism example).

## Future
- Doctrine drifting metrics (pressure from events)
- Unlock tree and prerequisites
- UI selection & conflict resolution
- Multi-slot typed categories (Faith, Efficiency, Social, Defense)

## Effects Mapping
Currently textual. Future: doctrine effects registered with effect handlers at bootstrap to apply stat modifiers and event weighting changes.