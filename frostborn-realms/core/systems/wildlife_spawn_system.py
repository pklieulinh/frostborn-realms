# (đã ở trên – giữ nguyên; file này đã cung cấp)
from ..ecs.world import World
from ..ecs.components import Position, Renderable, Role, Health, CombatTag
from ..util.id_gen import GLOBAL_ID_GEN

import random

def wildlife_spawn_system(world: World):
    if world.state.meta.get("pregame", False): return
    meta = world.state.meta
    tick = world.state.tick
    nxt = meta.get("wildlife_next_tick", 0)
    if tick < nxt:
        return
    farms = world.entities.get_component_store("FarmField")
    base_interval = max(400, 900 - len(farms)*40)
    meta["wildlife_next_tick"] = tick + base_interval
    roles = world.entities.get_component_store("Role")
    existing = sum(1 for r in roles.values() if r.type=="Wildlife")
    if existing >= 10:
        return
    count = min(2, 10 - existing)
    for _ in range(count):
        _spawn_wildlife(world)

def _spawn_wildlife(world: World):
    g = world.grid
    for _ in range(30):
        x = world.rng.randint(0, g.width-1)
        y = world.rng.randint(0, g.height-1)
        if not g.walkable(x,y):
            continue
        eid = world.entities.create(GLOBAL_ID_GEN.next())
        world.entities.add_component(eid,"Position",Position(x,y))
        world.entities.add_component(eid,"Renderable",Renderable("wildlife"))
        world.entities.add_component(eid,"Role",Role("Wildlife"))
        world.entities.add_component(eid,"CombatTag",CombatTag(faction="wildlife"))
        world.entities.add_component(eid,"Health",Health(hp=20, max_hp=20))
        world.record_event({"tick": world.state.tick, "type":"WildlifeSpawn", "id": eid})
        return