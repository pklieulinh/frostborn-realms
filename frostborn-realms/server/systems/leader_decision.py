from ..ecs.world import World
from ..ai.leader import leader_decide

def leader_system(world: World, tick: int):
    if tick % 20 == 0:
        leader_decide(world)