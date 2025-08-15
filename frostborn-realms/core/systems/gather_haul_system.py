from ..ecs.world import World
from ..ecs.components import (WorkIntent, ActivityState, Position, ResourceNode,
                              ResourceInventory, Storage, ResourcePile, Movement,
                              Attributes, SkillProgress)
from ..ai.path_cache import GLOBAL_PATH_CACHE
from ..ai.pathfinding import a_star
from ..util.id_gen import GLOBAL_ID_GEN
from collections import deque

CLUSTER_RADIUS = 6
CLUSTER_MAX_NODES = 9
CLUSTER_MAX_MANHATTAN = 8

def gather_haul_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    intents = em.get_component_store("WorkIntent")
    acts = em.get_component_store("ActivityState")
    pos = em.get_component_store("Position")
    nodes = em.get_component_store("ResourceNode")
    invs = em.get_component_store("ResourceInventory")
    storages = em.get_component_store("Storage")
    piles = em.get_component_store("ResourcePile")
    attrs = em.get_component_store("Attributes")
    skills = em.get_component_store("SkillProgress")

    if not intents:
        return

    storage_list = []
    for sid, st in storages.items():
        if sid not in pos:
            continue
        storage_list.append((sid, st, pos[sid].x, pos[sid].y))

    total_pile_amount = 0
    for pile in piles.values():
        total_pile_amount += sum(pile.resources.values())

    avg_capacity = 1
    if invs:
        avg_capacity = sum(inv.capacity for inv in invs.values()) / len(invs)

    hauling_backlog = total_pile_amount / max(1, avg_capacity)
    world.state.meta["hauling_backlog"] = hauling_backlog

    cluster_stats = []

    for eid, intent in intents.items():
        if eid not in pos or eid not in invs:
            continue
        if intent.job not in ("Gatherer", "Hauler"):
            continue
        act = acts.setdefault(eid, ActivityState())
        if intent.job == "Gatherer":
            _run_gatherer(world, eid, act, invs[eid], pos, nodes, storage_list, attrs.get(eid), skills.get(eid))
        elif intent.job == "Hauler":
            _run_hauler(world, eid, act, invs[eid], pos, piles, storage_list, attrs.get(eid), skills.get(eid))

        if "cluster_nodes" in act.meta:
            cluster_stats.append(len(act.meta["cluster_nodes"]))

    if cluster_stats:
        world.state.meta["cluster_active_count"] = len(cluster_stats)
        world.state.meta["cluster_avg_size"] = round(sum(cluster_stats) / len(cluster_stats), 2)

def _run_gatherer(world, eid, act, inv, pos_store, nodes, storage_list, attr, sp):
    em = world.entities
    if act.state == "Idle":
        if "cluster_nodes" not in act.meta or not act.meta["cluster_nodes"]:
            cluster = _build_cluster(world, eid, pos_store, nodes)
            if cluster:
                act.meta["cluster_nodes"] = cluster
                act.meta["cluster_index"] = 0
        if "cluster_nodes" in act.meta and act.meta["cluster_nodes"]:
            idx = act.meta.get("cluster_index", 0)
            if idx < len(act.meta["cluster_nodes"]):
                target_node = act.meta["cluster_nodes"][idx]
                if target_node in nodes:
                    _move_to(world, eid, target_node)
                    act.state = "Moving"
                    act.changed_tick = world.state.tick
                else:
                    act.meta["cluster_index"] += 1
        else:
            target = _pick_richest_node(world, eid, pos_store, nodes)
            if target:
                act.meta["single_node"] = target
                _move_to(world, eid, target)
                act.state = "Moving"
                act.changed_tick = world.state.tick

    elif act.state == "Working":
        gather_factor = 1.0
        if attr:
            gather_factor = 0.55 + attr.strength * 0.25 + attr.agility * 0.15 + attr.botany * 0.05
        amount = max(1, int(gather_factor))
        node_id = None
        if "cluster_nodes" in act.meta and act.meta.get("cluster_nodes"):
            idx = act.meta.get("cluster_index", 0)
            cnodes = act.meta["cluster_nodes"]
            if idx < len(cnodes):
                node_id = cnodes[idx]
        elif "single_node" in act.meta:
            node_id = act.meta["single_node"]

        if node_id and node_id in nodes:
            node = nodes[node_id]
            harvested = min(amount, node.amount)
            node.amount -= harvested
            inv.stored[node.rtype] = inv.stored.get(node.rtype, 0) + harvested
            if sp:
                sp.xp["strength"] = sp.xp.get("strength", 0) + 0.5
                sp.xp["hauling"] = sp.xp.get("hauling", 0) + 0.2
                sp.xp["botany"] = sp.xp.get("botany", 0) + 0.25
                sp.xp["agility"] = sp.xp.get("agility", 0) + 0.1
            if node.amount <= 0:
                del nodes[node_id]
                if "cluster_nodes" in act.meta and node_id in act.meta["cluster_nodes"]:
                    act.meta["cluster_index"] += 1
                else:
                    act.meta.pop("single_node", None)

            load = sum(inv.stored.values())
            if load >= inv.capacity:
                _deliver_or_drop(world, eid, inv, storage_list, pos_store)
                act.state = "Moving"
                act.changed_tick = world.state.tick
            else:
                if "cluster_nodes" in act.meta:
                    idx = act.meta.get("cluster_index", 0)
                    cnodes = act.meta["cluster_nodes"]
                    while idx < len(cnodes) and cnodes[idx] not in nodes:
                        idx += 1
                        act.meta["cluster_index"] = idx
                    if idx < len(cnodes):
                        nxt = cnodes[idx]
                        _move_to(world, eid, nxt)
                        act.state = "Moving"
                        act.changed_tick = world.state.tick
                    else:
                        _deliver_or_drop(world, eid, inv, storage_list, pos_store)
                        act.state = "Moving"
                        act.changed_tick = world.state.tick
        else:
            act.state = "Idle"

def _run_hauler(world, eid, act, inv, pos_store, piles, storage_list, attr, sp):
    if act.state == "Idle":
        if sum(inv.stored.values()) > 0:
            _deliver_or_drop(world, eid, inv, storage_list, pos_store)
            act.state = "Moving"
            act.changed_tick = world.state.tick
            return
        target = _nearest_pile(eid, pos_store, piles)
        if target:
            act.meta["haul_pile"] = target
            _move_to(world, eid, target)
            act.state = "Moving"
            act.changed_tick = world.state.tick

    elif act.state == "Working":
        if sum(inv.stored.values()) < inv.capacity:
            pile_id = act.meta.get("haul_pile")
            if pile_id and pile_id in piles:
                pile = piles[pile_id]
                pulled = _pull_from_pile(pile, inv)
                if sp and pulled > 0:
                    sp.xp["hauling"] = sp.xp.get("hauling", 0) + 0.6
                    sp.xp["stamina"] = sp.xp.get("stamina", 0) + 0.25
                if not pile.resources:
                    del piles[pile_id]
                    act.meta.pop("haul_pile", None)
                if sum(inv.stored.values()) < inv.capacity * 0.85:
                    nxt = _adjacent_pile_cluster(eid, pos_store, piles)
                    if nxt:
                        act.meta["haul_pile"] = nxt
                        _move_to(world, eid, nxt)
                        act.state = "Moving"
                        act.changed_tick = world.state.tick
                        return
                if sum(inv.stored.values()) >= inv.capacity or "haul_pile" not in act.meta:
                    _deliver_or_drop(world, eid, inv, storage_list, pos_store)
                    act.state = "Moving"
                    act.changed_tick = world.state.tick
            else:
                _deliver_or_drop(world, eid, inv, storage_list, pos_store)
                act.state = "Moving"
                act.changed_tick = world.state.tick
        else:
            _deliver_or_drop(world, eid, inv, storage_list, pos_store)
            act.state = "Moving"
            act.changed_tick = world.state.tick

def _pull_from_pile(pile, inv):
    pulled = 0
    for rk, rv in list(pile.resources.items()):
        if rv <= 0:
            continue
        room = inv.capacity - sum(inv.stored.values())
        if room <= 0:
            break
        take = min(rv, max(1, int(room * 0.5)))
        pile.resources[rk] -= take
        inv.stored[rk] = inv.stored.get(rk, 0) + take
        pulled += take
        if pile.resources[rk] <= 0:
            del pile.resources[rk]
    return pulled

def _adjacent_pile_cluster(eid, pos_store, piles):
    if eid not in pos_store:
        return None
    px, py = pos_store[eid].x, pos_store[eid].y
    best = None
    best_amt = 0
    for pid, pile in piles.items():
        if pid not in pos_store:
            continue
        pp = pos_store[pid]
        if abs(pp.x - px) + abs(pp.y - py) <= 2:
            amt = sum(pile.resources.values())
            if amt > best_amt:
                best_amt = amt
                best = pid
    return best

def _nearest_pile(eid, pos_store, piles):
    if eid not in pos_store:
        return None
    px, py = pos_store[eid].x, pos_store[eid].y
    best = None
    best_dist = 999
    for pid, pile in piles.items():
        if pid not in pos_store:
            continue
        pp = pos_store[pid]
        dist = abs(pp.x - px) + abs(pp.y - py)
        if dist < best_dist:
            best_dist = dist
            best = pid
    return best

def _build_cluster(world, eid, pos_store, nodes):
    if eid not in pos_store:
        return None
    sx, sy = pos_store[eid].x, pos_store[eid].y
    seed_id = None
    best_amt = 0
    for nid, node in nodes.items():
        if nid not in pos_store:
            continue
        p = pos_store[nid]
        d = abs(p.x - sx) + abs(p.y - sy)
        if d <= CLUSTER_RADIUS and node.amount > best_amt:
            best_amt = node.amount
            seed_id = nid
    if not seed_id:
        return None
    seed_type = nodes[seed_id].rtype
    cluster = [seed_id]
    visited = {seed_id}
    q = deque([seed_id])
    while q and len(cluster) < CLUSTER_MAX_NODES:
        cur = q.popleft()
        if cur not in pos_store:
            continue
        cp = pos_store[cur]
        for nid, node in nodes.items():
            if nid in visited:
                continue
            if node.rtype != seed_type:
                continue
            if nid not in pos_store:
                continue
            np = pos_store[nid]
            if abs(np.x - sx) + abs(np.y - sy) > CLUSTER_MAX_MANHATTAN:
                continue
            dist = abs(np.x - cp.x) + abs(np.y - cp.y)
            if dist <= 4:
                visited.add(nid)
                cluster.append(nid)
                q.append(nid)
            if len(cluster) >= CLUSTER_MAX_NODES:
                break
    return cluster

def _pick_richest_node(world, eid, pos_store, nodes):
    if eid not in pos_store:
        return None
    px, py = pos_store[eid].x, pos_store[eid].y
    best = None
    best_amt = 0
    for nid, node in nodes.items():
        if nid not in pos_store:
            continue
        np = pos_store[nid]
        d = abs(np.x - px) + abs(np.y - py)
        if d > 18:
            continue
        if node.amount > best_amt:
            best_amt = node.amount
            best = nid
    return best

def _move_to(world, eid, target_eid):
    em = world.entities
    pos = em.get_component_store("Position")
    mov = em.get_component_store("Movement")
    acts = em.get_component_store("ActivityState")
    if eid not in pos or target_eid not in pos:
        return
    if eid not in mov:
        from ..ecs.components import Movement
        em.add_component(eid, "Movement", Movement(speed=1.0))
    start = (pos[eid].x, pos[eid].y)
    goal = (pos[target_eid].x, pos[target_eid].y)
    if hasattr(GLOBAL_PATH_CACHE, "get_path"):
        path = GLOBAL_PATH_CACHE.get_path(world.grid, start, goal)
    else:
        path = a_star(world.grid, start, goal)
    mv = mov[eid]
    mv.target = goal
    mv.path = path
    act = acts[eid]
    act.state = "Moving"
    act.target = target_eid
    act.target_pos = goal
    act.changed_tick = world.state.tick

def _deliver_or_drop(world, eid, inv, storage_list, pos_store):
    load = sum(inv.stored.values())
    if load == 0:
        return
    if eid not in pos_store:
        return
    px, py = pos_store[eid].x, pos_store[eid].y
    best = None
    best_dist = 999
    for sid, st, sx, sy in storage_list:
        free = st.capacity - st.used
        if free <= 0:
            continue
        dist = abs(sx - px) + abs(sy - py)
        if dist < best_dist:
            best_dist = dist
            best = sid
    acts = world.entities.get_component_store("ActivityState")
    if best is not None:
        _move_to(world, eid, best)
        acts[eid].meta["deliver_to"] = best
    else:
        pid = world.entities.create(GLOBAL_ID_GEN.next())
        from ..ecs.components import Position, Renderable, ResourcePile
        world.entities.add_component(pid, "Position", Position(px, py))
        world.entities.add_component(pid, "Renderable", Renderable("site"))
        world.entities.add_component(pid, "ResourcePile", ResourcePile(resources=inv.stored.copy()))
        inv.stored.clear()

def gather_haul_finalize(world: World):
    em = world.entities
    acts = em.get_component_store("ActivityState")
    storages = em.get_component_store("Storage")
    pos = em.get_component_store("Position")
    invs = em.get_component_store("ResourceInventory")
    skills = em.get_component_store("SkillProgress")
    for eid, act in acts.items():
        if act.state == "Working" and "deliver_to" in act.meta:
            sid = act.meta.get("deliver_to")
            if sid in storages and eid in pos and eid in invs:
                st = storages[sid]
                inv = invs[eid]
                for rk, rv in list(inv.stored.items()):
                    if rv <= 0:
                        continue
                    free = st.capacity - st.used
                    if free <= 0:
                        break
                    move = min(rv, free)
                    st.store[rk] = st.store.get(rk, 0) + move
                    st.used += move
                    inv.stored[rk] -= move
                    if inv.stored[rk] <= 0:
                        del inv.stored[rk]
                if not inv.stored:
                    act.meta.pop("deliver_to", None)
                    act.state = "Idle"
                    sp = skills.get(eid)
                    if sp:
                        sp.xp["hauling"] = sp.xp.get("hauling", 0) + 1.2
                        sp.xp["stamina"] = sp.xp.get("stamina", 0) + 0.4
            else:
                act.meta.pop("deliver_to", None)
                act.state = "Idle"