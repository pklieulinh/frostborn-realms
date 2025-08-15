from ..ecs.world import World
from ..ecs.components import Needs, ResourceInventory
from ..config import BALANCE

def needs_system(world: World):
    em = world.entities
    needs_store = em.get_component_store("Needs")
    inv_store = em.get_component_store("ResourceInventory")
    for eid, needs in needs_store.items():
        needs.food_timer += 1
        if needs.food_timer >= BALANCE.food_need_interval:
            inv = inv_store.get(eid)
            if inv and inv.stored.get("Food", 0) > 0:
                inv.stored["Food"] -= 1
            needs.food_timer = 0