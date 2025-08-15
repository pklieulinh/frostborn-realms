from ..ecs.world import World
from ..ai.leader import leader_build_def_step

def leader_def_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    leader_build_def_step(world)
