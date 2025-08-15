from ..ecs.world import World
from ..ecs.components import CraftingStation, CraftingJob, ResourceInventory, Building
from ..crafting.recipes import load_recipes, get_recipe, get_station_recipes

AUTO_TARGETS = [
    # (station_type, recipe_id, maintain_stock)
    ("Foundry", "IngotIron", 30),
    ("Foundry", "IngotBronze", 25),
    ("Foundry", "AlloyFroststeel", 12),
    ("Foundry", "PlateAlloy", 12),
    ("Workshop", "GearCog", 20),
    ("Workshop", "MeshInsulate", 16),
    ("RuneForge", "CircuitRune", 8),
    ("RuneForge", "LensRunic", 6),
    ("TailorBench", "ClothWoven", 30),
    ("TailorBench", "LeatherTreated", 25),
    ("AlchemyTable", "PowderFrost", 25),
    ("AlchemyTable", "CatalystArcane", 10),
]

def _ensure_station_components(world: World):
    em = world.entities
    buildings = em.get_component_store("Building")
    cs_store = em.get_component_store("CraftingStation")
    for eid, b in buildings.items():
        if b.btype in ("Foundry","Workshop","TailorBench","AlchemyTable","RuneForge","PortalLab"):
            if eid not in cs_store:
                em.add_component(eid, "CraftingStation", CraftingStation(station_type=b.btype))

def _aggregate_resources(world: World):
    em = world.entities
    invs = em.get_component_store("ResourceInventory")
    total = {}
    for inv in invs.values():
        for k, v in inv.stored.items():
            total[k] = total.get(k, 0) + v
    return total

def _try_queue_auto(world: World, eid: int, station: CraftingStation, totals):
    if not station.auto:
        return
    for stype, rid, want in AUTO_TARGETS:
        if stype != station.station_type:
            continue
        cur = totals.get(_primary_output_of(rid), 0)
        if cur >= want:
            continue
        recipe = get_recipe(rid)
        if not recipe:
            continue
        if not _have_inputs(totals, recipe["inputs"]):
            continue
        # queue
        job = CraftingJob(
            recipe_id=rid,
            progress=0,
            time_required=recipe.get("time", 10),
            inputs=recipe["inputs"],
            outputs=recipe["outputs"]
        )
        station.queue.append(job.__dict__)
        break

def _have_inputs(totals, reqs):
    for k, v in reqs.items():
        if totals.get(k, 0) < v:
            return False
    return True

def _primary_output_of(rid: str):
    r = get_recipe(rid)
    if not r:
        return ""
    outs = r.get("outputs", {})
    if outs:
        return next(iter(outs.keys()))
    return ""

def _consume_inputs(world: World, inputs: dict) -> bool:
    # simple global consumption from leader (or first inventory)
    em = world.entities
    invs = em.get_component_store("ResourceInventory")
    # check aggregated first
    total = {}
    for inv in invs.values():
        for k, v in inv.stored.items():
            total[k] = total.get(k, 0) + v
    for k, v in inputs.items():
        if total.get(k, 0) < v:
            return False
    # deduct greedily
    for k, v in inputs.items():
        rem = v
        for inv in invs.values():
            have = inv.stored.get(k, 0)
            if have <= 0:
                continue
            take = min(have, rem)
            inv.stored[k] = have - take
            rem -= take
            if rem <= 0:
                break
    return True

def _deposit_outputs(world: World, outputs: dict):
    em = world.entities
    # deposit to leader or first inventory
    invs = em.get_component_store("ResourceInventory")
    target = None
    role_store = em.get_component_store("Role")
    for eid, inv in invs.items():
        if eid in role_store and role_store[eid].type == "Leader":
            target = inv
            break
    if not target and invs:
        target = next(iter(invs.values()))
    if not target:
        return
    for k, v in outputs.items():
        target.stored[k] = target.stored.get(k, 0) + v

def crafting_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    _ensure_station_components(world)
    em = world.entities
    stations = em.get_component_store("CraftingStation")
    if not stations:
        return
    totals = _aggregate_resources(world)
    jobs_store = em.get_component_store("CraftingJob")
    # Auto queue
    for eid, st in stations.items():
        if not st.active:
            continue
        if len(st.queue) == 0:
            _try_queue_auto(world, eid, st, totals)
    # Process first job each station
    for eid, st in stations.items():
        if not st.queue:
            continue
        job_data = st.queue[0]
        # Promote to component if not present
        if eid not in jobs_store:
            em.add_component(eid, "CraftingJob", CraftingJob(
                recipe_id=job_data["recipe_id"],
                progress=0,
                time_required=job_data["time_required"] if "time_required" in job_data else job_data.get("time_required", job_data.get("time", 10)),
                inputs=job_data["inputs"],
                outputs=job_data["outputs"]
            ))
        job = jobs_store[eid]
        if job.progress == 0:
            ok = _consume_inputs(world, job.inputs)
            if not ok:
                # cannot start, drop job
                st.queue.pop(0)
                del jobs_store[eid]
                continue
        job.progress += 1
        if job.progress >= job.time_required:
            _deposit_outputs(world, job.outputs)
            st.queue.pop(0)
            del jobs_store[eid]