# Asset Integration Layer

## Goals
- Centralize all references (prefabs, audio, materials, sprites) in a single manifest.
- Provide graceful fallback (procedural primitive + colored material) if asset missing.
- Ensure licensing compliance with quick scan.

## Folder Structure
Assets/
  External/
    Environment/
    Creatures/
    Audio/
    UI/
    FX/
  Game/
    Prefabs/
  Materials/
  Scripts/
  ScriptableObjects/

## Steps to Add a New Asset
1. Import pack into `Assets/External/<Category>/<PackName>`.
2. Add LICENSE / attribution if required.
3. Run menu: Tools/Frostborn/Scan Asset Licenses.
4. Create prefab for gameplay usage under `Assets/Game/Prefabs`.
5. Open `AssetManifest` and drag the prefab / audio / material in.
6. Reference by string key from systems or dev spawners.

## Naming Conventions
Prefab keys: building_hearth, creature_ice_wolf, fx_cold_burst
Audio keys: sfx_ui_click, sfx_wind_loop, sfx_event_chime
Material keys: mat_ice, mat_rock...

## Runtime Flow
1. GameBootstrap loads `AssetManifest`.
2. AssetResolver.Initialize(manifest) populates dictionaries.
3. Systems or dev tools spawn by key; missing keys -> placeholder.
4. Optional future: Addressables.

## Fallback Philosophy
Missing asset never breaks run; placeholder signals gap.

## Future Enhancements
- License scan CI fail on missing license.
- Addressables / memory budgets.
- Codegen enums for keys.

