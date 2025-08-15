from ..ecs.world import World
from ..ecs.components import Storage, Position, Item

ABSORB_STACK_LIMIT_PER_TICK = 30

def storage_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    storages = em.get_component_store("Storage")
    if not storages:
        world.state.meta["storage_capacity"] = 0
        world.state.meta["storage_used"] = 0
        world.state.meta["storage_pressure"] = 0.0
        return
    pos_store = em.get_component_store("Position")
    items = em.get_component_store("Item") if "Item" in em._components else {}
    index = {}
    for sid, st in storages.items():
        if sid in pos_store:
            p = pos_store[sid]
            index[(p.x,p.y)] = sid
    absorb_count = 0
    for eid,it in list(items.items()):
        if absorb_count >= ABSORB_STACK_LIMIT_PER_TICK:
            break
        if eid not in pos_store:
            continue
        p = pos_store[eid]
        key = (p.x,p.y)
        if key not in index:
            continue
        sid = index[key]
        st = storages[sid]
        free = st.capacity - st.used
        if free <= 0:
            continue
        move = min(free, it.stack_count)
        st.store[it.def_id] = st.store.get(it.def_id,0)+move
        st.used += move
        it.stack_count -= move
        absorb_count += 1
        if it.stack_count <= 0:
            em.destroy(eid)
    total_cap = 0
    total_used = 0
    for st in storages.values():
        total_cap += st.capacity
        used_calc = sum(st.store.values())
        st.used = used_calc
        total_used += used_calc
    world.state.meta["storage_capacity"] = total_cap
    world.state.meta["storage_used"] = total_used
    world.state.meta["storage_pressure"] = (total_used/total_cap) if total_cap>0 else 0.0