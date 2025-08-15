from ..ecs.world import World
from ..ecs.components import ResourceNode, ResourceInventory, ConstructionSite, Building

def assign_gather_task(world: World, eid: int):
    em = world.entities
    agent = em.get_component_store("TaskAgent")[eid]
    if agent.current:
        return
    nodes = em.get_component_store("ResourceNode")
    pos_store = em.get_component_store("Position")
    best = None
    best_dist = 9999
    ep = pos_store[eid]
    for nid, node in nodes.items():
        if node.amount <= 0:
            continue
        np = pos_store[nid]
        dist = abs(np.x - ep.x) + abs(np.y - ep.y)
        if dist < best_dist:
            best_dist = dist
            best = nid
    if best is not None:
        agent.current = {"type": "gather", "target": best, "progress": 0}

def process_task(world: World, eid: int):
    em = world.entities
    agent = em.get_component_store("TaskAgent")[eid]
    if not agent.current:
        return
    t = agent.current
    if t["type"] == "gather":
        target = t["target"]
        if target not in em.get_component_store("ResourceNode"):
            agent.current = None
            return
        t["progress"] += 1
        if t["progress"] >= 4:
            node = em.get_component_store("ResourceNode")[target]
            if node.amount > 0:
                node.amount -= 1
                inv = em.get_component_store("ResourceInventory").get(eid)
                if inv:
                    inv.stored["WoodCold"] = inv.stored.get("WoodCold", 0) + 1
            t["progress"] = 0
            if node.amount <= 0:
                agent.current = None
    elif t["type"] == "build_deliver":
        site_id = t["site"]
        sites = em.get_component_store("ConstructionSite")
        if site_id not in sites:
            agent.current = None
            return
        site = sites[site_id]
        inv = em.get_component_store("ResourceInventory").get(eid)
        if not inv:
            agent.current = None
            return
        needed_type = None
        needed_amt = 0
        for r, amt in site.needed.items():
            delivered = site.delivered.get(r, 0)
            if delivered < amt:
                needed_type = r
                needed_amt = amt - delivered
                break
        if not needed_type:
            agent.current = None
            return
        have = inv.stored.get(needed_type, 0)
        if have <= 0:
            agent.current = None
            return
        take = min(1, have, needed_amt)
        inv.stored[needed_type] -= take
        site.delivered[needed_type] = site.delivered.get(needed_type, 0) + take
        agent.current = None
    elif t["type"] == "build_work":
        site_id = t["site"]
        sites = em.get_component_store("ConstructionSite")
        if site_id not in sites:
            agent.current = None
            return
        site = sites[site_id]
        all_met = all(site.delivered.get(r, 0) >= v for r, v in site.needed.items())
        if not all_met:
            agent.current = None
            return
        site.progress += 0.1
        if site.progress >= 1.0:
            site.complete = True
            agent.current = None

def assign_construction_tasks(world: World, eid: int):
    em = world.entities
    sites = em.get_component_store("ConstructionSite")
    if not sites:
        return
    agent = em.get_component_store("TaskAgent")[eid]
    if agent.current:
        return
    pos_store = em.get_component_store("Position")
    pos_store[eid]
    for sid, site in sites.items():
        if site.complete:
            continue
        all_met = all(site.delivered.get(r, 0) >= v for r, v in site.needed.items())
        if not all_met:
            agent.current = {"type": "build_deliver", "site": sid}
            return
        else:
            agent.current = {"type": "build_work", "site": sid}
            return

def convert_completed_sites(world: World):
    em = world.entities
    sites = list(em.get_component_store("ConstructionSite").items())
    for sid, site in sites:
        if site.complete:
            cs = em.get_component_store("ConstructionSite")
            em.add_component(sid, "Building", Building(site.btype))
            del cs[sid]
            if site.btype == "PortalGate":
                world.state.portal_count += 1