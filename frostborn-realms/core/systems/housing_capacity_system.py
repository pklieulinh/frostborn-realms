from ..ecs.world import World
from ..ecs.components import HousingUnit, ConstructionSite
from ..ai.leader import HOUSING_DEF_CAPACITY

RECALC_INTERVAL = 25

def housing_capacity_system(world: World):
    if world.state.meta.get("pregame", False): return
    if world.state.tick % RECALC_INTERVAL != 0: return
    em = world.entities
    units = em.get_component_store("HousingUnit")
    total = 0
    for hu in units.values():
        total += hu.capacity
    world.state.meta["housing_capacity"] = total
    # Pending housing buffer (sites)
    sites = em.get_component_store("ConstructionSite")
    pending = 0
    for s in sites.values():
        def_id = s.meta.get("def_id")
        if def_id in HOUSING_DEF_CAPACITY:
            pending += HOUSING_DEF_CAPACITY[def_id]
    world.state.meta["pending_housing_capacity"] = pending