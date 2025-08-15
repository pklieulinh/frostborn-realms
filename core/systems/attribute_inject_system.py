from ..ecs.world import World
from ..ecs.components import Attributes, SkillProgress, WorkStats, ResourceInventory, Role, Skills, WorkPriorities
import random

SKILL_LIST = ["Shooting","Melee","Construction","Mining","Cooking","Plants","Animals","Crafting","Artistic","Medicine","Social","Intellectual"]

def attribute_inject_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    roles = em.get_component_store("Role")
    attrs = em.get_component_store("Attributes")
    skills = em.get_component_store("Skills")
    sprogress = em.get_component_store("SkillProgress")
    wstats = em.get_component_store("WorkStats")
    invs = em.get_component_store("ResourceInventory")
    priorities = em.get_component_store("WorkPriorities")

    for eid, r in roles.items():
        if r.type not in ("Worker","Leader","Guard","Scholar","Engineer","Scout","Soldier"): continue
        if eid not in attrs:
            def rnd(): 
                v = 0.5 + (random.random()-0.5)*0.24 + (random.random()-0.5)*0.18
                return max(0.35,min(0.75,v))
            a = Attributes(
                strength=rnd(), stamina=rnd(), agility=rnd(), intelligence=rnd(), perception=rnd(),
                resilience=rnd(), craftsmanship=rnd(), botany=rnd(), mining=rnd(), hunting=rnd(), hauling=rnd()
            )
            em.add_component(eid, "Attributes", a)
            if eid in invs:
                invs[eid].capacity = int(25 + a.strength*22 + a.stamina*12)
        if eid not in sprogress:
            em.add_component(eid, "SkillProgress", SkillProgress())
        if eid not in wstats:
            em.add_component(eid, "WorkStats", WorkStats())
        if eid not in skills:
            lvl = {}
            xp = {}
            passions = {}
            for sk in SKILL_LIST:
                base = random.randint(0,4)
                lvl[sk] = base
                xp[sk] = 0
            # pick passions
            passion_candidates = random.sample(SKILL_LIST, k=min(3,len(SKILL_LIST)))
            for i, sk in enumerate(passion_candidates):
                passions[sk] = "Major" if i==0 else ("Minor" if i < 3 else "None")
            em.add_component(eid, "Skills", Skills(levels=lvl,xp=xp,passions=passions))
        if eid not in priorities:
            pr = {
                "Builder": 3,
                "Farmer": 3,
                "Gatherer": 4,
                "Miner": 2,
                "Hunter": 2,
                "Hauler": 3,
                "Forester": 3,
                "Herder": 2,
                "Research": 1
            }
            if r.type == "Leader":
                pr["Leader"] = 5
            em.add_component(eid, "WorkPriorities", WorkPriorities(priorities=pr))