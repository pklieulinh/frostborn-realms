from ..ecs.world import World
from ..ecs.components import WorkIntent, ActivityState, WorkStats, EmotionState, Morale

JOB_FATIGUE_FACTOR = {
    "Builder": 1.1,
    "Farmer": 0.9,
    "Herder": 0.8,
    "Gatherer": 1.0,
    "Hunter": 1.2,
    "Miner": 1.15,
    "Forester": 0.95,
    "Explorer": 1.05,
    "Leader": 1.0,
    "Idle": 0.2
}

def stress_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    intents = em.get_component_store("WorkIntent")
    acts = em.get_component_store("ActivityState")
    emos = em.get_component_store("EmotionState")
    morals = em.get_component_store("Morale")
    ws = em.get_component_store("WorkStats")
    tick = world.state.tick
    if not intents: return
    for eid, intent in intents.items():
        act = acts.get(eid)
        w = ws.get(eid)
        if not w:
            from ..ecs.components import WorkStats
            w = WorkStats()
            em.add_component(eid, "WorkStats", w)
        state = act.state if act else "Idle"
        job = intent.job
        base_gain = 0.003
        factor = JOB_FATIGUE_FACTOR.get(job, 1.0)
        working = state == "Working"
        if working:
            w.fatigue += base_gain * factor * (1 + w.stress*0.5)
            w.overwork_ticks += 1
        else:
            # recovery
            rec = 0.0025 if state == "Idle" else 0.0012
            w.fatigue -= rec
            if w.overwork_ticks > 0:
                w.overwork_ticks -= 1
        # clamp fatigue
        if w.fatigue < 0: w.fatigue = 0
        if w.fatigue > 1: w.fatigue = 1
        # stress adjustments
        mood = emos[eid].mood if eid in emos else 0.7
        morale = morals[eid].value if eid in morals else 1.0
        if w.fatigue > 0.75:
            w.stress += 0.0025 + (w.fatigue - 0.75)*0.01
        elif w.fatigue < 0.4:
            w.stress -= 0.002
        if mood < 0.45:
            w.stress += (0.45 - mood)*0.004
        if morale < 0.5:
            w.stress += (0.5 - morale)*0.003
        else:
            w.stress -= 0.001
        if w.overwork_ticks > 1200:
            w.stress += 0.004
        # clamp stress
        if w.stress < 0: w.stress = 0
        if w.stress > 1: w.stress = 1
    # meta averages
    if ws:
        avg_f = sum(w.fatigue for w in ws.values())/len(ws)
        avg_s = sum(w.stress for w in ws.values())/len(ws)
        world.state.meta["fatigue_avg"] = avg_f
        world.state.meta["stress_avg"] = avg_s