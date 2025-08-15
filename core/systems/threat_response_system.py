from ..ecs.world import World
from ..ecs.components import Position, Role

THREAT_RADIUS = 12

def threat_response_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    roles = em.get_component_store("Role")
    pos = em.get_component_store("Position")
    leader_pos = None
    for eid,r in roles.items():
        if r.type=="Leader":
            leader_pos = pos.get(eid)
            break
    if not leader_pos:
        return
    predator_near = False
    for eid,r in roles.items():
        if r.type=="Predator":
            p = pos.get(eid)
            if not p: continue
            if abs(p.x - leader_pos.x) + abs(p.y - leader_pos.y) <= THREAT_RADIUS:
                predator_near = True
                break
    if predator_near:
        world.state.meta["colony_directive"] = "Defend"
    else:
        if world.state.meta.get("colony_directive") == "Defend":
            world.state.meta["colony_directive"] = "Normal"