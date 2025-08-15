from ..ecs.world import World
from ..expedition.sim import tick_expeditions

def expedition_system(world: World):
    tick_expeditions(world)