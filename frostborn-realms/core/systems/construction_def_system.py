from ..ecs.world import World
from ..ecs.components import ConstructionSite, Building, FarmField, Storage, PortalGate, HeatEmitter, HousingUnit
from ..ai.leader import HOUSING_DEF_CAPACITY

EXTRA_DEF_BEHAVIOR = {
    "farm_plot": {"farm_field": True},
    "greenhouse_basic": {"farm_field": True},
    "storage_crate": {"storage_cap":500},
    "granary": {"storage_cap":700},
    "cold_storage": {"storage_cap":650},
    "stockyard": {"storage_cap":800},
    "armory_store": {"storage_cap":400},
    "portal_gate_t1": {"portal": True},
    "portal_gate_t2": {"portal": True},
    "portal_gate_t3": {"portal": True},
    "portal_gate_t4": {"portal": True},
    "hearth_fire": {"heat":120,"radius":5},
    "furnace_stone": {"heat":200,"radius":6},
    "boiler_heater": {"heat":320,"radius":7}
}

def construction_def_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    sites = em.get_component_store("ConstructionSite")
    if not sites: return
    for sid, site in list(sites.items()):
        def_id = site.meta.get("def_id")
        if not def_id:
            if site.complete and site.progress >= 1.0:
                em.add_component(sid,"Building",Building(site.btype))
                del sites[sid]
            continue
        if not site.complete and site.progress < 1.0:
            continue
        em.add_component(sid,"Building",Building(def_id))
        if def_id in HOUSING_DEF_CAPACITY:
            cap = HOUSING_DEF_CAPACITY[def_id]
            em.add_component(sid,"HousingUnit",HousingUnit(capacity=cap))
        behavior = EXTRA_DEF_BEHAVIOR.get(def_id)
        if behavior:
            if behavior.get("farm_field"):
                em.add_component(sid,"FarmField",FarmField())
            if "storage_cap" in behavior:
                em.add_component(sid,"Storage",Storage(capacity=behavior["storage_cap"]))
            if behavior.get("portal"):
                _ensure_portal(world, sid)
            if "heat" in behavior:
                em.add_component(sid,"HeatEmitter",HeatEmitter(radius=behavior.get("radius",5), output=behavior["heat"]))
        del sites[sid]

def _ensure_portal(world: World, eid: int):
    em = world.entities
    gates = em.get_component_store("PortalGate")
    if eid not in gates:
        em.add_component(eid,"PortalGate",PortalGate(seed=world.state.seed ^ eid, state="Idle", quality=1.0))
    world.state.portal_count += 1
    world.record_event({"tick":world.state.tick,"type":"PortalBuilt","id":eid})