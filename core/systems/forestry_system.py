from ..ecs.world import World
from ..ecs.components import Sapling, Position, ResourceNode
import random

def forestry_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    saplings = em.get_component_store("Sapling")
    if not saplings: return
    for eid, s in list(saplings.items()):
        s.ticks_to_mature -= 1
        if s.ticks_to_mature <=0:
            # mature into wood node
            pos = em.get_component_store("Position").get(eid)
            if pos:
                em.add_component(eid, "ResourceNode", ResourceNode("WoodCold", s.wood_amount))
            del saplings[eid]
            world.record_event({"tick": world.state.tick, "type":"TreeMature", "id": eid})