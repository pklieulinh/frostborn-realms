from ..ecs.world import World
from ..ecs.components import Role, Position, AICombat, CombatTag

def predator_ai_system(world: World):
    em = world.entities
    role_store = em.get_component_store("Role")
    pos_store = em.get_component_store("Position")
    ai_store = em.get_component_store("AICombat")
    faction_store = em.get_component_store("CombatTag")

    # Build lists
    colony_targets = [eid for eid, ct in faction_store.items() if ct.faction == "colony" and eid in pos_store]
    predator_targets = [eid for eid, ct in faction_store.items() if ct.faction == "predator" and eid in pos_store]

    # Predator chooses colony target
    for eid in predator_targets:
        if eid not in ai_store or eid not in pos_store:
            continue
        ai = ai_store[eid]
        if not colony_targets:
            ai.target_id = None
            continue
        # prefer leader if exists
        leader_candidates = [cid for cid in colony_targets if role_store.get(cid) and role_store[cid].type == "Leader"]
        chosen_candidates = leader_candidates if leader_candidates else colony_targets
        ex = pos_store[eid].x
        ey = pos_store[eid].y
        best = None
        best_dist = 9999
        for cid in chosen_candidates:
            cx = pos_store[cid].x
            cy = pos_store[cid].y
            d = abs(cx - ex) + abs(cy - ey)
            if d < best_dist:
                best_dist = d
                best = cid
        ai.target_id = best

    # Guards choose predator
    guards = [eid for eid, r in role_store.items() if r.type == "Guard"]
    for gid in guards:
        if gid not in ai_store:
            ai_store[gid] = world.entities.get_component_store("AICombat").setdefault(gid, AICombat())
        if gid not in pos_store:
            continue
        ai = ai_store[gid]
        if not predator_targets:
            ai.target_id = None
            continue
        gx = pos_store[gid].x
        gy = pos_store[gid].y
        best = None
        best_dist = 9999
        for pid in predator_targets:
            px = pos_store[pid].x
            py = pos_store[pid].y
            d = abs(px - gx) + abs(py - gy)
            if d < best_dist:
                best_dist = d
                best = pid
        ai.target_id = best

    # Simple chase movement: step one tile toward target for predators and guards
    for eid, ai in ai_store.items():
        if ai.target_id is None:
            continue
        if eid not in pos_store or ai.target_id not in pos_store:
            continue
        sx, sy = pos_store[eid].x, pos_store[eid].y
        tx, ty = pos_store[ai.target_id].x, pos_store[ai.target_id].y
        if abs(sx - tx) + abs(sy - ty) <= 1:
            continue  # already adjacent for combat
        # Greedy step
        nx, ny = sx, sy
        if sx < tx:
            nx += 1
        elif sx > tx:
            nx -= 1
        elif sy < ty:
            ny += 1
        elif sy > ty:
            ny -= 1
        # Bound & walkable check
        if world.grid.walkable(nx, ny):
            pos_store[eid].x = nx
            pos_store[eid].y = ny