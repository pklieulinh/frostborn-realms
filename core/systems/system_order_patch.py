# Integrates newly added systems into main loop (import in main runtime)
from ..ecs.world import World
from .defs_system import defs_system
from .item_stack_system import item_stack_system
from .blueprint_system import blueprint_system
from .construction_def_system import construction_def_system
from .leader_def_system import leader_def_system

def early_defs_phase(world: World):
    defs_system(world)

def items_phase(world: World):
    item_stack_system(world)

def construction_phase(world: World):
    blueprint_system(world)
    construction_def_system(world)

def leader_def_phase(world: World):
    leader_def_system(world)