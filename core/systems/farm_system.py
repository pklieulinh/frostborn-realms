from ..ecs.world import World
from ..ecs.components import FarmField, Position, Item, Renderable, ConstructionSite
from ..util.id_gen import GLOBAL_ID_GEN

def farm_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    fields = em.get_component_store("FarmField")
    sites = em.get_component_store("ConstructionSite")
    pending = 0
    for s in sites.values():
        if s.complete: continue
        did = (s.meta.get("def_id") or s.btype).lower()
        if "farm_plot" in did:
            pending += 1
    farm_count = 0
    tick = world.state.tick
    for fid, field in list(fields.items()):
        farm_count += 1
        field.growth_progress += field.growth_rate
        if field.growth_progress >= 100.0:
            yield_amt = field.yield_amount
            field.growth_progress = 0.0
            world.record_event({"tick":tick,"type":"FarmHarvest","amount":yield_amt})
            pos_store = em.get_component_store("Position")
            p = pos_store.get(fid)
            if p:
                _spawn_stack(world, p.x, p.y, "grain_raw", yield_amt, 90)
    world.state.meta["farm_count"] = farm_count
    world.state.meta["farm_sites_pending"] = pending

def _spawn_stack(world: World, x: int, y: int, def_id: str, amount: int, max_stack: int):
    em = world.entities
    while amount>0:
        stack = min(amount, max_stack)
        new_id = em.create(GLOBAL_ID_GEN.next())
        from ..ecs.components import Position as P
        em.add_component(new_id,"Position",P(x,y))
        em.add_component(new_id,"Renderable",Renderable("site"))
        em.add_component(new_id,"Item",Item(def_id=def_id, stack_count=stack, max_stack=max_stack))
        amount -= stack