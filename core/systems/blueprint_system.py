from ..ecs.world import World
from ..ecs.components import ConstructionSite, Building, FarmField, Storage, PortalGate, HeatEmitter

# This simplified blueprint system now only ensures immediate conversion if legacy site.complete is already true
def blueprint_system(world: World):
    if world.state.meta.get("pregame", False): return
    # Actual conversion handled in construction_def_system
    return