from ..ecs.world import World

def movement_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    pos_store = em.get_component_store("Position")
    mov_store = em.get_component_store("Movement")
    acts = em.get_component_store("ActivityState")
    attrs = em.get_component_store("Attributes")
    invs = em.get_component_store("ResourceInventory")
    for eid, mv in mov_store.items():
        if eid not in pos_store: continue
        act = acts.get(eid)
        if not act or act.state != "Moving":
            continue
        speed_factor = 1.0
        if eid in attrs:
            at = attrs[eid]
            load_ratio = 0.0
            if eid in invs:
                inv = invs[eid]
                load_ratio = sum(inv.stored.values())/max(1, inv.capacity)
            speed_factor = 1 + at.agility*0.35 + at.stamina*0.15 - load_ratio*0.25
            if speed_factor < 0.5: speed_factor = 0.5
            if speed_factor > 2.2: speed_factor = 2.2
        steps = int(speed_factor)
        if steps < 1: steps = 1
        while steps > 0 and mv.path:
            nx, ny = mv.path[0]
            if pos_store[eid].x == nx and pos_store[eid].y == ny:
                mv.path.pop(0)
            else:
                if world.grid.walkable(nx, ny):
                    pos_store[eid].x = nx
                    pos_store[eid].y = ny
                mv.path.pop(0)
            steps -= 1
        if not mv.path:
            act.state = "Working"
            act.changed_tick = world.state.tick