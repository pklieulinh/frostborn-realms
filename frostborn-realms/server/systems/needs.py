from ..ecs.world import World
from ..ecs.components import Needs, ResourceInventory
from ..config import BALANCE

def needs_system(world: World):
    em = world.entities
    needs_store = em.get_component_store("Needs")
    inv_store = em.get_component_store("ResourceInventory")
    events = world.state.events_active
    for eid, needs in needs_store.items():
        needs.food_timer += 1
        needs.heat_timer += 1
        if needs.food_timer >= BALANCE.food_need_interval:
            inv = inv_store.get(eid)
            if inv and inv.stored.get("Food", 0) > 0:
                inv.stored["Food"] -= 1
            needs.food_timer = 0
        heat_interval = BALANCE.heat_need_interval
        if "ColdSnap" in events:
            heat_interval = max(10, heat_interval // 2)
        if needs.heat_timer >= heat_interval:
            heatstations = [bid for bid, b in em.get_component_store("Building").items() if b.btype == "HeatStation"]
            if not heatstations:
                needs.deficit_heat_ticks += 1
            else:
                needs.deficit_heat_ticks = max(0, needs.deficit_heat_ticks - 1)
            needs.heat_timer = 0