# Asset Integration Layer

## Goals
- Centralize all references (prefabs, audio, materials, sprites) in a single manifest.
- Provide graceful fallback (procedural primitive + colored material) if asset missing.
- Ensure licensing compliance with quick scan.

## Folder Structure
Assets/
  External/           (3rd-party imported)
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
- Prefab keys: building_hearth, creature_ice_wolf, fx_cold_burst
- Audio keys: sfx_ui_click, sfx_wind_loop, sfx_event_chime
- Material keys (for AssetManifest & MaterialLibrary bridging): mat_ice, mat_rock...

## Runtime Flow
1. GameBootstrap loads `AssetManifest` (serialized field or Resources.Load).
2. AssetResolver.Initialize(manifest) populates dictionaries.
3. Systems or dev tools spawn by key; missing keys -> placeholder.
4. Optional: In milestone 4, migrate to Addressables for memory locality.

## Fallback Philosophy
We always prefer simulation continuity over content perfection. Missing asset must not break run; placeholder makes issues visible but non-fatal.

## Future Enhancements
- Add hash validation / size budget checker.
- Add BuildReport guard: fail CI if missing license in added External folder.
- Addressables label auto-generation from manifest keys.