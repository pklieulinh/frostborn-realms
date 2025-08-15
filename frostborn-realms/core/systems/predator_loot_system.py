from ..ecs.world import World
from ..ecs.components import Health, Role, Position, Item, Renderable
from ..util.id_gen import GLOBAL_ID_GEN
import random

def predator_loot_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    healths = em.get_component_store("Health")
    roles = em.get_component_store("Role")
    positions = em.get_component_store("Position")
    to_remove = []
    for eid,h in healths.items():
        if h.hp > 0: continue
        r = roles.get(eid)
        if not r or r.type != "Predator": continue
        p = positions.get(eid)
        if p:
            meat = random.randint(2,5)
            hide = random.randint(1,3)
            _spawn_stack(world,p.x,p.y,"raw_meat",meat,60)
            _spawn_stack(world,p.x,p.y,"hide_raw",hide,70)
            world.record_event({"tick":world.state.tick,"type":"PredatorLoot","meat":meat,"hide":hide})
        to_remove.append(eid)
    for eid in to_remove:
        em.destroy(eid)

def _spawn_stack(world: World, x: int, y: int, def_id: str, amount: int, max_stack: int):
    em = world.entities
    while amount>0:
        stack = min(amount,max_stack)
        new_id = em.create(GLOBAL_ID_GEN.next())
        from ..ecs.components import Position as P
        em.add_component(new_id,"Position",P(x,y))
        em.add_component(new_id,"Renderable",Renderable("site"))
        em.add_component(new_id,"Item",Item(def_id=def_id, stack_count=stack, max_stack=max_stack))
        amount -= stack