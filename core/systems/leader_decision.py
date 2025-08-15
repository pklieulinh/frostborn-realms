from ..ecs.world import World
from ..ai.leader import leader_decide

def leader_system(world: World, tick: int):
    leader_decide(world, tick)