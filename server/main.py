import sys
from pathlib import Path

# Ensure 'core' importable whether server/ is sibling or inside root
_THIS_FILE = Path(__file__).resolve()
_SEARCH_ROOTS = [_THIS_FILE.parent, _THIS_FILE.parent.parent, _THIS_FILE.parent.parent.parent]
for root in _SEARCH_ROOTS:
    if (root / "core").is_dir():
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        break

import asyncio
from fastapi import FastAPI
import uvicorn
from core.ecs.world import World
from core.simulation.tick_manager import TickManager
from core.config import WORLD_SEED, TICK_INTERVAL_SEC
from core.systems.movement import movement_system
from core.systems.needs import needs_system
from core.systems.tasks_exec import task_system
from core.systems.leader_decision import leader_system
from core.systems.events_tick import events_system
from core.systems.expedition_tick import expedition_system
from core.save_load import save_world, load_world
from core.ai.leader import confirm_pending, reject_pending
from core.expedition.sim import launch_expedition

app = FastAPI(title="BangPhongTheGioi-Server")

world = World(seed=WORLD_SEED)
world.bootstrap()
tick_manager = TickManager(TICK_INTERVAL_SEC)

def simulation_step(tick_index: int, dt: float):
    world.state.tick = tick_index
    events_system(world)
    leader_system(world, tick_index)
    task_system(world)
    movement_system(world)
    needs_system(world)
    expedition_system(world)

tick_manager.add_task(simulation_step)

@app.on_event("startup")
async def startup():
    async def loop():
        while True:
            tick_manager.step()
            await asyncio.sleep(0.005)
    asyncio.create_task(loop())

@app.get("/health")
def health():
    return {"status": "ok", "tick": world.state.tick}

@app.post("/save")
def save():
    save_world(world)
    return {"status": "ok"}

@app.post("/load")
def load():
    ok = load_world(world)
    return {"status": "ok" if ok else "error"}

@app.post("/toggle_intervention")
def toggle_intervention():
    world.state.intervention_mode = not world.state.intervention_mode
    return {"intervention": world.state.intervention_mode}

@app.post("/expedition/{seed}")
def expedition(seed: int):
    launch_expedition(world, seed)
    return {"status": "started"}

@app.post("/confirm/{idx}")
def confirm(idx: int):
    return {"ok": confirm_pending(world, idx)}

@app.post("/reject/{idx}")
def reject(idx: int):
    return {"ok": reject_pending(world, idx)}

if __name__ == "__main__":
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)
