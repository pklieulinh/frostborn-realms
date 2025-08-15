from ..ecs.world import World
from ..ecs.components import Movement, Position
from ..ai.pathfinding import a_star

def movement_system(world: World):
    em = world.entities
    move_store = em.get_component_store("Movement")
    pos_store = em.get_component_store("Position")
    for eid, mv in move_store.items():
        if eid not in pos_store:
            continue
        if not mv.path and mv.target:
            start = (pos_store[eid].x, pos_store[eid].y)
            path = a_star(world, start, mv.target)
            mv.path = path[1:] if path and len(path) > 1 else []
        if mv.path:
            nx, ny = mv.path[0]
            pos_store[eid].x = nx
            pos_store[eid].y = ny
            mv.path = mv.path[1:]
            if not mv.path:
                mv.target = None