# Frostborn Realms

Autonomous God-Survival Colony Simulation (Cold Apocalypse) – Developed by GeminiForge AI (Game Dev Autonomous System).

## Status
Phase: Beta Pass Content Integration (Foundations laid, full event set of 55, Leviathan multi-phase design, trade & caravan framework, heat diffusion jobified design queued for implementation branch).

Next Immediate Step After Initial Commit:
- Create branch `2-ecs-core` → add ECS component set + core systems.
- Sequential branches (documented in ROADMAP).

## High-Level Vision
Guide a frozen colony balancing Heat, Morale, Doctrine, Logistics, Arcane risks, and escalating monstrosities culminating in a multi-phase Leviathan boss encounter. Player interventions are *light-touch*: law/doctrine, edicts, strategic decisions. Emergent simulation drives day-to-day outcomes.

## Key Feature Pillars
- Data-Driven ECS (Unity DOTS) simulation: needs, heat, AI utility, hierarchical pathfinding, frontier heat diffusion.
- Full Event System (55 curated events) with branching outcomes & effect DSL.
- Doctrine System influencing resource efficiency, morale stability, risk.
- Multi-Phase Boss (Leviathan) with anchors & environmental suppression.
- Trade & Caravan economy: dynamic demand & price elasticity.
- Inventory, crafting tiers, item decay (temperature aware).
- Modding: JSON registries (items, events, doctrines, monsters, buildings, recipes, palettes).
- Overlays + Colorblind palettes (Deuteranopia / Protanopia / Tritanopia / High Contrast).
- Replay (snapshot / delta) & Save/Load (versioned schema – to be added in later branch).
- Profiling & instrumentation hooks.

## Repository Structure (Initial)
```
frostborn-realms/
  .gitignore
  .gitattributes
  README.md
  LICENSE
  docs/
    Architecture.md
    GDD.md
    ROADMAP.md
    Systems/
       (placeholder - detailed docs added in subsequent branches)
  Mods/
    items.alpha.json
    events.beta.json
    monsters.alpha.json
    doctrines.alpha.json
    buildings.alpha.json
    recipes.alpha.json
  Data/
    balance_needs.csv
    balance_monsters.csv
    balance_doctrines.csv
  Assets/
    Scripts/        (will be populated in ecs-core branch)
    ArtPlaceholders/
    Resources/
    Scenes/
```

## Build (Future Branch)
- Unity 2022.3 LTS + Entities 1.x, Burst, Collections.
- Define Symbols (beta later): `ENABLE_REPLAY;MOD_LOADER;BETA_PASS`

## License
Code: MIT  
Data JSON / Balancing: CC0 (Attribution list in LICENSE section “Attributions”).  
Third-party free assets (when integrated) remain under their original CC0 or permissive licenses.

See `docs/Architecture.md` & `docs/GDD.md` for deep detail.

-- GeminiForge