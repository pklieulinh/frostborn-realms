from ..ecs.world import World
from ..ecs.components import Skills, WorkStats
import math

PASSION_MULT = {"None":1.0, "Minor":1.5, "Major":2.2}

def skills_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    skills = em.get_component_store("Skills")
    if not skills: return
    wstats = em.get_component_store("WorkStats")
    tick = world.state.tick
    if tick % 150 != 0: return
    for eid, sk in skills.items():
        fatigue_mod = 1.0
        stress_mod = 1.0
        ws = wstats.get(eid)
        if ws:
            fatigue_mod -= ws.fatigue*0.35
            stress_mod -= ws.stress*0.25
            if fatigue_mod < 0.4: fatigue_mod = 0.4
            if stress_mod < 0.5: stress_mod = 0.5
        for name, xp in list(sk.xp.items()):
            if xp <= 0: continue
            lvl = sk.levels.get(name,0)
            needed = 100 + (lvl**1.55)*45
            passion = sk.passions.get(name, "None")
            pm = PASSION_MULT.get(passion,1.0)
            gain_pool = xp * pm * fatigue_mod * stress_mod
            while gain_pool >= needed and lvl < 20:
                gain_pool -= needed
                lvl += 1
                needed = 100 + (lvl**1.55)*45
            sk.levels[name] = lvl
            sk.xp[name] = gain_pool*0.4  # partial retention

    # colony skill averages
    c=0; sum_con=0; sum_pl=0; sum_shoot=0
    for sk in skills.values():
        sum_con += sk.levels.get("Construction",0)
        sum_pl += sk.levels.get("Plants",0)
        sum_shoot += sk.levels.get("Shooting",0)
        c+=1
    if c>0:
        world.state.meta["skills_avg_construction"]=round(sum_con/c,2)
        world.state.meta["skills_avg_plants"]=round(sum_pl/c,2)
        world.state.meta["skills_avg_shooting"]=round(sum_shoot/c,2)