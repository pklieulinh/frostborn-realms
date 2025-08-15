from ..ecs.world import World
from ..ai.tasks import assign_tasks, movement_step, process_work
from .gather_haul_system import gather_haul_finalize
from ..ai.path_cache import GLOBAL_PATH_CACHE

def task_system(world: World):
    assign_tasks(world)
    movement_step(world)
    process_work(world)
    gather_haul_finalize(world)
    world.state.meta["path_cache_hit"]=round(GLOBAL_PATH_CACHE.hit_rate()*100,2)