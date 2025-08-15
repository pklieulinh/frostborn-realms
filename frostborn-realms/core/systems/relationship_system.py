from ..ecs.world import World
from ..ecs.components import Relationships, HousingUnit

def relationship_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    rels = em.get_component_store("Relationships")
    housings = em.get_component_store("HousingUnit")
    if not rels or not housings:
        return
    # Simple affinity boost: co-housing synergy
    for hu in housings.values():
        occ = hu.occupants
        for i in range(len(occ)):
            for j in range(i+1, len(occ)):
                a = occ[i]; b = occ[j]
                if a not in rels:
                    continue
                rels[a].affinity[b] = min(1.0, rels[a].affinity.get(b, 0.0) + 0.0005)
                if b in rels:
                    rels[b].affinity[a] = min(1.0, rels[b].affinity.get(a, 0.0) + 0.0005)