from ..ecs.world import World
from ..ecs.components import Health, Role, WorkStats, Position, HeatEmitter

def health_regen_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    healths = em.get_component_store("Health")
    if not healths: return
    roles = em.get_component_store("Role")
    workstats = em.get_component_store("WorkStats")
    heat_emitters = em.get_component_store("HeatEmitter")
    positions = em.get_component_store("Position")
    predators_present = any(r.type=="Predator" for r in roles.values())
    directive = world.state.meta.get("colony_directive","Normal")
    # Cho phép hồi: không có predator hoặc đang Retreat (coi là rút lui hồi sức)
    if predators_present and directive not in ("Retreat","Defend"):
        return
    base_rate = world.state.meta.get("regen_base_rate", 0.04)
    for eid, h in healths.items():
        if h.hp >= h.max_hp: continue
        if eid not in roles: continue
        rtype = roles[eid].type
        if rtype in ("Predator","Wildlife"): continue
        ws = workstats.get(eid)
        fatigue = ws.fatigue if ws else 0.0
        stress = ws.stress if ws else 0.0
        perf = (1 - 0.5*fatique_clamp(fatigue)) * (1 - 0.4*stress)
        if perf < 0.3: perf = 0.3
        regen = base_rate * perf
        # Bonus gần nguồn nhiệt
        if positions and eid in positions and heat_emitters:
            px, py = positions[eid].x, positions[eid].y
            for hid, he in heat_emitters.items():
                if hid in positions:
                    hp = positions[hid]
                    if abs(hp.x - px)+abs(hp.y - py) <= he.radius:
                        regen *= 1.5
                        break
        h.hp += regen
        if h.hp > h.max_hp: h.hp = h.max_hp
    world.state.meta["last_heal_tick"] = world.state.tick

def fatique_clamp(v):
    if v<0: return 0
    if v>1: return 1
    return v
