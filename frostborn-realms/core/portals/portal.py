from typing import Dict, Any
import random
from ..ecs.world import World
from ..ecs.components import PortalGate

def portal_biome(seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    return {
        "temperature": -30 - rng.randint(0, 30),
        "predator_density": rng.choice(["low", "mid", "high"]),
        "resource_richness": rng.uniform(0.5, 1.5),
        "hazard": rng.choice(["none", "ice_spike", "storm"]),
    }

def assign_portal_gate_component(world: World, entity_id: int):
    em = world.entities
    seed = world.rng.randint(1, 10_000_000)
    quality = 1.0
    if "PortalSurge" in world.state.events_active:
        quality += world.state.events_active["PortalSurge"].get("boost", 0)
    em.add_component(entity_id, "PortalGate", PortalGate(seed=seed, state="idle", quality=quality))
    world.state.portal_count += 1