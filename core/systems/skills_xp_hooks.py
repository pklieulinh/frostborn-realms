from ..ecs.world import World
from ..ecs.components import Skills, ActivityState, WorkIntent

JOB_SKILL = {
    "Builder":"Construction",
    "Farmer":"Plants",
    "Gatherer":"Plants",
    "Miner":"Mining",
    "Hunter":"Shooting",
    "Herder":"Animals",
    "Forester":"Plants",
    "Hauler":"Construction",
}

def skills_xp_hooks(world: World):
    if world.state.meta.get("pregame", False): return
    em=world.entities
    skills=em.get_component_store("Skills")
    intents=em.get_component_store("WorkIntent")
    acts=em.get_component_store("ActivityState")
    if not skills: return
    tick=world.state.tick
    if tick % 30 != 0: return
    for eid,intent in intents.items():
        if eid not in skills: continue
        job=intent.job
        sk=JOB_SKILL.get(job)
        if not sk: continue
        # simple working state bonus
        act=acts.get(eid)
        if act and act.state in ("Working","Moving"):
            skills[eid].xp[sk]=skills[eid].xp.get(sk,0)+5