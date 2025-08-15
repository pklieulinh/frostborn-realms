# Frozen Dominion / Frostborn Realms – Combined Workspace

This workspace contains:
1. Web Simulation Stack (Python FastAPI server + TypeScript client) – authoritative ECS, portals, leader AI.
2. Local Pygame Prototype – basic world render using the AssetLoader.

## 1. Web Simulation
Run:
```
pip install fastapi uvicorn pydantic
cd server_root_directory (where server/main.py resides)
python -m uvicorn server.main:app --reload
```
Open client: Serve /client via a simple static server (or open index.html with a live server extension); ensure it connects to ws://localhost:8000/ws.

## 2. Pygame Prototype
Install:
```
pip install pygame
```
Prepare assets:
Rename `assets/assets_manifest.example.json` to `assets/assets_manifest.json` and adjust paths to your actual images (PNG files). Ensure each image entry has at least one of: path | file | rel_path.

Run:
```
python frostborn-realms/main.py
```

If an asset is missing, the loader (strict mode) raises AssetDefinitionError.

## 3. Validation
Run asset validation before launching:
```
python frostborn-realms/validate_assets.py
```

## 4. Save/Load (Web ECS)
Endpoints:
- POST /save
- POST /load

## 5. Portal Cap
Server enforces MAX_PORTALS=9. Leader AI will not plan further PortalGate buildings beyond this cap.

## 6. Extending
- To unify both (pygame + server ECS), redirect Pygame render loop to subscribe to the websocket diff stream instead of its own local simplified world (future step).
- For asset automation, request "SCAN DIR".

## 7. License / Attribution
Placeholder – add your license.
