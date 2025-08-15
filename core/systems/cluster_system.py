from ..ecs.world import World
from ..ecs.components import ResourceNode, Position
from collections import deque

def cluster_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    nodes = em.get_component_store("ResourceNode")
    if not nodes: return
    tick = world.state.tick
    interval = world.state.meta.get("cluster_rebuild_interval", 120)
    next_tick = world.state.meta.get("cluster_next_tick", 0)
    if tick < next_tick:
        return
    world.state.meta["cluster_next_tick"] = tick + interval
    # snapshot previous hash to skip if unchanged
    total_amt = 0
    key_acc = []
    for eid, rn in nodes.items():
        total_amt += rn.amount
        key_acc.append((eid, rn.rtype, rn.amount))
    snap_hash = hash(tuple(key_acc))
    prev_hash = world.state.meta.get("cluster_prev_hash")
    if prev_hash == snap_hash:
        return
    world.state.meta["cluster_prev_hash"] = snap_hash
    # build clusters
    pos = em.get_component_store("Position")
    visited = set()
    clusters = {}
    cid_counter = 1
    for eid, rn in nodes.items():
        if eid in visited: continue
        if rn.rtype != "WoodCold":  # hiện tại chỉ cluster gỗ
            rn.cluster_id = None
            continue
        if eid not in pos: continue
        queue = deque([eid])
        cluster_nodes = []
        rtype = rn.rtype
        while queue:
            nid = queue.popleft()
            if nid in visited: continue
            if nid not in nodes: continue
            nn = nodes[nid]
            if nn.rtype != rtype: continue
            visited.add(nid)
            cluster_nodes.append(nid)
            if nid not in pos: continue
            px, py = pos[nid].x, pos[nid].y
            # BFS radius=6
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = px+dx, py+dy
                for oid, on in nodes.items():
                    if oid in visited: continue
                    if on.rtype!=rtype: continue
                    if oid not in pos: continue
                    op = pos[oid]
                    if abs(op.x - px)+abs(op.y - py) == 1:
                        queue.append(oid)
        if not cluster_nodes:
            continue
        total = sum(nodes[nid].amount for nid in cluster_nodes)
        cx = sum(pos[nid].x for nid in cluster_nodes)//len(cluster_nodes)
        cy = sum(pos[nid].y for nid in cluster_nodes)//len(cluster_nodes)
        for nid in cluster_nodes:
            nodes[nid].cluster_id = cid_counter
        clusters[cid_counter] = {
            "rtype": rtype,
            "nodes": cluster_nodes,
            "total": total,
            "centroid": (cx, cy)
        }
        cid_counter += 1
    world.state.meta["clusters"] = clusters