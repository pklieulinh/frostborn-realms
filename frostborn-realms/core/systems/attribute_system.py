from ..ecs.world import World
from ..ecs.components import Attributes, SkillProgress, ResourceInventory, Movement, WorkStats
ATTR_KEYS = ["strength","stamina","agility","intelligence","perception","resilience","craftsmanship","botany","mining","hunting","hauling"]

def attribute_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    attrs = em.get_component_store("Attributes")
    if not attrs: return
    sprog = em.get_component_store("SkillProgress")
    invs = em.get_component_store("ResourceInventory")
    movs = em.get_component_store("Movement")
    wstats = em.get_component_store("WorkStats")
    tick = world.state.tick

    for eid, ws in wstats.items():
        a = attrs.get(eid)
        if not a: continue
        ws.fatigue = max(0, ws.fatigue - a.stamina * 0.0009)
        ws.stress = max(0, ws.stress - a.resilience * 0.0006)

    if tick % 120 != 0: return

    for eid, a in attrs.items():
        sp = sprog.get(eid)
        if sp:
            for key in ATTR_KEYS:
                xp = sp.xp.get(key,0.0)
                if xp <= 0: continue
                current = getattr(a,key)
                inc = (1 - current) * (xp / (100 + xp)) * 0.15
                if inc > 0:
                    setattr(a,key, min(0.99, current + inc))
                sp.xp[key] = xp * 0.35
        if eid in invs:
            inv = invs[eid]
            inv.capacity = int(25 + a.strength*22 + a.stamina*12)
            if inv.capacity < 15: inv.capacity = 15
        if eid in movs:
            mv = movs[eid]
            load_ratio = 0.0
            if eid in invs and invs[eid].capacity>0:
                load_ratio = sum(invs[eid].stored.values())/invs[eid].capacity
            base_speed = 1.0 + a.agility*0.25
            mv.speed = base_speed * (1 - (load_ratio**2) * (0.18 - a.agility*0.06))
            if mv.speed < 0.45: mv.speed = 0.45
            if mv.speed > 2.0: mv.speed = 2.0

    if attrs:
        col_avg = sum(a.strength for a in attrs.values())/len(attrs)
        col_ag = sum(a.agility for a in attrs.values())/len(attrs)
        col_st = sum(a.stamina for a in attrs.values())/len(attrs)
        world.state.meta["attr_avg_strength"]=round(col_avg,3)
        world.state.meta["attr_avg_agility"]=round(col_ag,3)
        world.state.meta["attr_avg_stamina"]=round(col_st,3)