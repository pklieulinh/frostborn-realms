from ..ecs.world import World
from ..events.system import tick_events

def events_system(world: World):
    tick_events(world)