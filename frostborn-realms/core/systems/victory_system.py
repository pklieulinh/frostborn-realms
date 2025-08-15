from ..ecs.world import World
from ..ecs.components import VictoryState

def victory_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    vs_store = em.get_component_store("VictoryState")
    if vs_store:
        # only one victory component expected
        for v in vs_store.values():
            if v.achieved:
                return
    # Conditions
    # 1. All portals built
    # 2. Enough FrostCrystal
    # 3. Survive minimal ticks
    invs = world.entities.get_component_store("ResourceInventory")
    frost_total = 0
    for inv in invs.values():
        frost_total += inv.stored.get("FrostCrystal", 0)
    if world.state.portal_count >= world.state.meta.get("victory_portal_req", world.state.meta.get("max_portals_req",  world.state.meta.get("MAX_PORTALS",  world.state.portal_count))) and \
       frost_total >= world.state.meta.get("victory_frost_req", 15) and \
       world.state.tick >= world.state.meta.get("victory_min_tick", 1500):
        # mark victory
        # attach component to world-level phantom entity
        wid = world.entities.create(-999999) if -999999 not in world.entities.entities else -999999
        world.entities.add_component(wid, "VictoryState", VictoryState(achieved=True, tick=world.state.tick, reason="StandardVictory"))
        world.state.meta["victory_state"] = {
            "tick": world.state.tick,
            "reason": "StandardVictory"
        }
        world.record_event({"tick": world.state.tick, "type": "Victory", "detail": "Conditions met"})