from ..ecs.world import World
from ..ecs.components import HousingUnit, Building, Role

def housing_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    housings = em.get_component_store("HousingUnit")
    buildings = em.get_component_store("Building")
    role_store = em.get_component_store("Role")
    if not buildings:
        return
    # Ensure every Housing building has HousingUnit
    for eid, b in buildings.items():
        if b.btype == "Housing" and eid not in housings:
            em.add_component(eid, "HousingUnit", HousingUnit())
    if not housings:
        return
    # Collect colonists
    colonists = [eid for eid, r in role_store.items() if r.type in ("Worker","Leader","Guard","Scholar","Engineer","Scout","Soldier")]
    # Flatten occupancy
    for hu in housings.values():
        hu.occupants = [c for c in hu.occupants if c in colonists]
    unassigned = [c for c in colonists if not any(c in hu.occupants for hu in housings.values())]
    # Assign round-robin
    if unassigned:
        ordered_units = sorted(housings.items(), key=lambda kv: kv[0])
        idx = 0
        for cid in unassigned:
            # find next unit with space
            placed = False
            for _ in range(len(ordered_units)):
                eid, unit = ordered_units[idx % len(ordered_units)]
                if len(unit.occupants) < unit.capacity:
                    unit.occupants.append(cid)
                    placed = True
                    idx += 1
                    break
                idx += 1
            if not placed:
                break
    # Update meta capacity info
    total_capacity = sum(hu.capacity for hu in housings.values())
    world.state.meta["housing_capacity"] = total_capacity
    world.state.meta["housing_occupied"] = sum(len(hu.occupants) for hu in housings.values())