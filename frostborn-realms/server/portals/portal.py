from typing import Dict, Any
import random
from ..ecs.world import World
from ..ecs.components import PortalGate

def spawn_portal_building(world: World, site_eid: int):
    em = world.entities
    pos = em.get_component_store("Position")[site_eid]
    pos.x += 0
    seed = world.rng.randint(1, 10_000_000)
    quality = 1.0
    if "PortalSurge" in world.state.events_active:
        quality += world.state.events_active["PortalSurge"].get("boost", 0)
    em.add_component(site_eid, "PortalGate", PortalGate(seed=seed, state="idle", quality=quality))

def open_portal(world: World, eid: int):
    gates = world.entities.get_component_store("PortalGate")
    gate = gates[eid]
    if gate.state == "idle":
        gate.state = "active"

def portal_biome(seed: int) -> Dict[str, Any]:
    rng = random.Random(seed)
    return {
        "temperature": -30 - rng.randint(0, 30),
        "predator_density": rng.choice(["low", "mid", "high"]),
        "resource_richness": rng.uniform(0.5, 1.5),
        "hazard": rng.choice(["none", "ice_spike", "storm"]),
    }