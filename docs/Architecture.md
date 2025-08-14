# Frostborn Realms – Architecture

## 1. Layer Overview
- Core: Bootstrap, Config, Time, Save/Load, Replay
- Simulation: ECS (Needs, Heat, Pathfinding, AI, Jobs, Economy, Diplomacy, Doctrine, Events, Monsters, Combat)
- Systems Extended: Trade, Caravan, Boss (Leviathan)
- Presentation: Overlays, HUD, Camera, Cinematics
- Data/Mod: Registries (Items, Events, Doctrines, Monsters, Buildings, Recipes, Palettes)
- Diagnostics: Profiler, Instrumentation, Soak Runner

## 2. ECS Partition (Planned Branch Implementation)
| Domain | Systems (Examples) |
|--------|--------------------|
| Needs | PackedNeedsSystem, MoraleModifierSystem |
| Heat  | HeatFrontierCollector, HeatDiffusionJobSystem |
| AI    | JobAssignmentSystem, ActionExecutionSystem, AnchorPrioritySystem |
| Events| EventLoaderSystem, TriggerEvaluator, ChoiceResolution |
| Doctrine | DoctrineModifierSystem, DriftSystem |
| Monsters | Spawn, Behavior, Combat, BossPhaseController |
| Trade | DemandSystem, RoutePlanner, CaravanMovement |
| Economy | PriceAdjustmentSystem, StockpileAnalysis |
| Boss | LeviathanPhaseController, AnchorSpawn, ColdPulse, Meteor |
| Overlay | PaletteLoader, ColorblindSwitcher, OverlayRenderer |
| Save/Replay | SnapshotWriter, DeltaEncoder, RestoreSystem |

## 3. Data Flow Examples
Event Trigger:
Telemetry Aggregators → TriggerEvaluator → PendingDecisionEvent → PlayerChoice/AutoResolve → EffectDispatcher → Components updated → Chronicle Log.

Leviathan Phase:
Boss HP/Shield monitor → Transition → (AnchorSpawnRequest) → Anchors Introduced (Suppression modifies Heat Diffusion penalty) → Anchor destruction events → Next Phase → Enrage & Pulses.

Heat:
HeatSources → Frontier Collector (Active flags) → Parallel Diffusion Job → Temperature Writeback → Overlays read & render.

Trade:
Daily Demand Calculation → Price Elasticity Update → Caravan Spawn (Route) → Travel (risk events) → Settlement Transaction → Inventory & Price Rebalance.

## 4. Parallelization Strategy
- Heat Diffusion: IJobParallelFor over active indices
- Pathfinding (later branch): batched jobs (flow field & micro A*)
- Replay Encoding: Background job for frame compression (optional)
- Price adjustments & aggregates on lower frequency scheduler (0.5–1 Hz)

## 5. Extensibility
- Effect DSL: string type → delegate mapping table
- Additional Bosses: Mirror Leviathan frameworks (Phase component + spawn triggers)
- Additional Biomes: Heat modifiers, resource spawn tables, monster pools
- Mod Hot Reload: Replace registries + broadcast EventRegistryReload

## 6. Save/Load (Later Branch)
Version header / chunk map:
- Header: Magic, Version, RNG Seeds
- Chunks: Entities (citizens), HeatCells (sparse active subset), BossState, Anchors, Caravans, Inventories
Serializer layering: Binary writer + optional JSON debug dump.

## 7. Risks & Mitigations
- Pathfinding spikes → hierarchical & cache TTL
- Heat memory footprint → compress inactive cells, store short (half) for low variance
- Event flood → cooldown enforced + weighted scheduler
- Replay divergence → deterministic RNG streams (AI, Spawns, Events)

## 8. Branch Roadmap (Execution)
See ROADMAP.md
