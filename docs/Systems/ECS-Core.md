# ECS Core

## Goal
Provide a minimal, extensible Entities (DOTS) architecture for simulation loops (needs decay, movement, events trigger) with clear expansion points.

## Components
- Position: float3 location
- Needs: survival metrics (Hunger, Warmth, Morale, Fatigue)
- Movement: path target + speed
- DoctrineState: active doctrine slots
- InventoryRef: pointer to inventory entity (future)
- ActionRequest: generic action with time remaining (future extension)
- EventPendingTag: marks transient global/local events
- CitizenTag / MonsterTag: role filters

## Systems (Phase 1)
- NeedsDecaySystem: applies decays scaled by config and doctrines.
- MovementSystem: linear movement toward target.
- JobAssignmentSystem: placeholder hook for AI task assignment.
- EventTriggerScanSystem: time/cooldown-based injection of event entities.
- EventResolutionSystem: pulls a random event, auto-resolves first choice.
- DoctrineDriftSystem: placeholder, future social evolution.
- InventoryAggregationSystem: placeholder for global stock roll-up.

All are stateless or near-stateless; future scheduling will group by update frequency.

## Ordering (Future)
Will introduce system groups: SimulationTickGroup, EventGroup, AIGroup, PostResolveGroup to manage dependency order.

## Next Steps
- Add Effect DSL interpreter
- Proper event queue with priorities
- Save/Load world serialization