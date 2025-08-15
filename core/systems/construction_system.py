from ..ecs.world import World
from ..ecs.components import ConstructionSite, Building, FarmField, AnimalPen, ResourceDeposit, PortalGate, Storage
from ..portals.portal import assign_portal_gate_component

def construction_system(world: World):
    if world.state.meta.get("pregame", False): return
    em=world.entities
    sites=list(em.get_component_store("ConstructionSite").items())
    for sid, site in sites:
        if not site.complete: continue
        cs=em.get_component_store("ConstructionSite")
        em.add_component(sid,"Building",Building(site.btype))
        if site.btype=="FarmPlot":
            em.add_component(sid,"FarmField",FarmField())
        elif site.btype=="Pasture":
            em.add_component(sid,"AnimalPen",AnimalPen())
        elif site.btype=="PortalGate" and world.can_build_portal():
            biome="Tundra"
            assign_portal_gate_component(world,sid, biome=biome)
        elif site.btype=="Mine":
            depo=site.meta.get("deposit")
            if depo:
                em.add_component(sid,"ResourceDeposit",ResourceDeposit(
                    resource_type=depo["resource"],
                    amount_remaining=depo["amount"],
                    tier=depo["tier"],
                    yield_per_cycle=max(1,2*depo["tier"])
                ))
        elif site.btype=="Storage":
            em.add_component(sid,"Storage",Storage(capacity=260))
        del cs[sid]