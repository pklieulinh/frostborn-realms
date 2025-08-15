from ..ecs.world import World
from ..ecs.components import ResourceDeposit, Building
from ..ecs.components import ResourceInventory

def deposit_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    deposits = em.get_component_store("ResourceDeposit")
    if not deposits: return
    removed = []
    for eid, dep in deposits.items():
        if dep.amount_remaining <= 0:
            removed.append(eid)
    if not removed: return
    for eid in removed:
        # Remove building + deposit
        b = em.get_component_store("Building")
        if eid in b: del b[eid]
        del deposits[eid]
        world.record_event({"tick": world.state.tick, "type":"MineDepleted", "id": eid})