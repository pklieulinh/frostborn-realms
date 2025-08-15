from ..ecs.world import World
from ..ecs.components import Position, Storage

FOOD_ALIAS = {
    "grain_raw": 1.0,
    "raw_meat": 1.0,
    "food_ration": 1.2,
    "hearty_meal": 1.8,
    "berry_frozen": 0.8
}

def item_stack_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    try:
        items_store = em.get_component_store("Item")
    except KeyError:
        items_store = {}
    if items_store:
        pos_store = em.get_component_store("Position")
        grouped = {}
        for eid, it in list(items_store.items()):
            if eid not in pos_store:
                continue
            p = pos_store[eid]
            key = (p.x, p.y, it.def_id, it.quality_tier, it.material_id)
            if key not in grouped:
                grouped[key] = eid
            else:
                tgt = grouped[key]
                if tgt == eid:
                    continue
                base = items_store[tgt]
                space = base.max_stack - base.stack_count
                if space <= 0:
                    continue
                take = min(space, it.stack_count)
                base.stack_count += take
                it.stack_count -= take
                if it.stack_count <= 0:
                    em.destroy(eid)
    aggregate = world.state.meta.setdefault("resources_global", {})
    aggregate.clear()
    food_eq = 0.0
    for it in items_store.values():
        aggregate[it.def_id] = aggregate.get(it.def_id,0) + it.stack_count
        if it.def_id in FOOD_ALIAS:
            food_eq += it.stack_count * FOOD_ALIAS[it.def_id]
    storages = em.get_component_store("Storage")
    for st in storages.values():
        for k,v in st.store.items():
            aggregate[k] = aggregate.get(k,0)+v
            if k in FOOD_ALIAS:
                food_eq += v * FOOD_ALIAS[k]
    if food_eq > 0:
        aggregate["FoodRationEq"] = int(food_eq)