from ..ecs.world import World
from ..ecs.components import Morale, Needs, EmotionState

def morale_system(world: World):
    em = world.entities
    morale_store = em.get_component_store("Morale")
    needs_store = em.get_component_store("Needs")
    emo_store = em.get_component_store("EmotionState")
    global_penalty = world.state.meta.get("recent_death_penalty", 0.0)
    if global_penalty > 0:
        global_penalty = max(0.0, global_penalty - 0.0005)
    for eid, morale in morale_store.items():
        needs = needs_store.get(eid)
        if needs:
            dht = needs.deficit_heat_ticks
            if dht > 40:
                morale.value = max(0.1, morale.value - 0.004)
            elif dht > 20:
                morale.value = max(0.1, morale.value - 0.002)
            else:
                morale.value = min(1.0, morale.value + 0.0015)
        # Emotion coupling
        if emo_store and eid in emo_store:
            mood = emo_store[eid].mood
            if mood < 0.5:
                morale.value = max(0.0, morale.value - (0.5 - mood)*0.002)
            elif mood > 0.8:
                morale.value = min(1.2, morale.value + (mood - 0.8)*0.003)
        if global_penalty > 0:
            morale.value = max(0.05, morale.value - global_penalty)
        morale.value = max(0.0, min(1.2, morale.value))
    world.state.meta["recent_death_penalty"] = global_penalty