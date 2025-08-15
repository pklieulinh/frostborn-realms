from .sim import launch_expedition

def tick_expeditions(world):
    # Backward compatibility stub: delegate to current expedition system.
    from ..systems.expedition_tick import expedition_system
    expedition_system(world)

__all__ = ["launch_expedition", "tick_expeditions"]
