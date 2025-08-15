from ..ecs.world import World
from .trait_effects_system import trait_effects_system

def traits_system(world: World):
    trait_effects_system(world)