from ..ecs.world import World
from ..ecs.components import ConstructionSite, Position, Renderable
from ..ecs.components_items_build import Blueprint
from ..util.id_gen import GLOBAL_ID_GEN

def create_def_construction_site(world: World, def_id: str, near_pos):
    defs = world.state.meta.get("defs",{})
    bdef = defs.get("buildings",{}).get(def_id)
    if not bdef: return
    em = world.entities
    from random import randint
    x = max(0, min(world.grid.width-1, near_pos[0] + randint(-4,4)))
    y = max(0, min(world.grid.height-1, near_pos[1] + randint(-4,4)))
    sid = em.create(GLOBAL_ID_GEN.next())
    em.add_component(sid,"Position",Position(x,y))
    em.add_component(sid,"Renderable",Renderable("site"))
    cost_map = {c["item"]: c["amount"] for c in bdef.get("cost",[])}
    em.add_component(sid,"ConstructionSite",ConstructionSite("DEF", needed=cost_map, meta={"def_id":def_id}))
    return sid