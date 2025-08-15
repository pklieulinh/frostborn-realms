from ..ecs.world import World
from ..ecs.components import ResourceInventory, Storage, ConstructionSite

LEGACY_MAP = {
    "WoodCold": "wood_log",
    "FoodRation": "food_ration",
    "MealHearty": "hearty_meal",
    "MeatRaw": "raw_meat"
}

CHECK_INTERVAL = 30

def legacy_resource_convert_system(world: World):
    if world.state.meta.get("pregame", False): return
    if world.state.tick % CHECK_INTERVAL != 0: return
    em = world.entities
    invs = em.get_component_store("ResourceInventory")
    stor = em.get_component_store("Storage")
    sites = em.get_component_store("ConstructionSite")
    for inv in invs.values():
        _convert_dict(inv.stored)
    for st in stor.values():
        _convert_dict(st.store)
    for s in sites.values():
        _convert_dict(s.needed)
        _convert_dict(s.delivered)

def _convert_dict(d: dict):
    for old, new in list(LEGACY_MAP.items()):
        if old in d:
            d[new] = d.get(new, 0) + d.pop(old)