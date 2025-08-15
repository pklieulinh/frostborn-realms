from typing import Dict, Any, List
from ..ecs.world import World
from ..ecs.components import LeaderAI, ResourceInventory, ConstructionSite
from ..util.id_gen import GLOBAL_ID_GEN
from ..ecs.components import Position, Renderable, ConstructionSite as CS
from ..config import MAX_PORTALS

BUILD_COSTS = {
    "Housing": {"WoodCold": 30},
    "Storage": {"WoodCold": 25},
    "HeatStation": {"WoodCold": 25},
    "Foundry": {"WoodCold": 40},
    "ResearchStation": {"WoodCold": 35},
    "PortalGate": {"WoodCold": 60},
}

def aggregate_resources(world: World) -> Dict[str,int]:
    em = world.entities
    invs = em.get_component_store("ResourceInventory")
    total: Dict[str,int] = {}
    for inv in invs.values():
        for k, v in inv.stored.items():
            total[k] = total.get(k, 0) + v
    return total

def leader_decide(world: World):
    em = world.entities
    leader_store = em.get_component_store("LeaderAI")
    if not leader_store:
        return
    leader_id = list(leader_store.keys())[0]
    leader = leader_store[leader_id]
    if world.state.intervention_mode and leader.intervention_pending:
        return
    resources = aggregate_resources(world)
    options: List[Dict[str, Any]] = []
    build_candidates = ["Housing", "Storage", "HeatStation", "PortalGate"]
    if world.state.portal_count >= MAX_PORTALS and "PortalGate" in build_candidates:
        build_candidates.remove("PortalGate")
    for b in build_candidates:
        cost = BUILD_COSTS[b]
        afford = all(resources.get(r, 0) >= c for r, c in cost.items())
        score = 0.0
        if b == "Housing":
            score = 0.4
        elif b == "Storage":
            score = 0.3
        elif b == "HeatStation":
            score = 0.25
        elif b == "PortalGate":
            score = 0.2
        if not afford:
            score *= 0.2
        options.append({"type": "build", "target": b, "score": score, "afford": afford})
    options.sort(key=lambda x: x["score"], reverse=True)
    if not options:
        return
    chosen = options[0]
    entry = {
        "tick": world.state.tick,
        "type": "LeaderDecision",
        "options": options,
        "chosen": chosen["target"],
    }
    world.record_decision(entry)
    leader.last_decision_tick = world.state.tick
    if world.state.intervention_mode:
        leader.intervention_pending.append(entry)
    else:
        enact_decision(world, chosen)

def enact_decision(world: World, option: Dict[str, Any]):
    if option["type"] == "build":
        em = world.entities
        leader_pos = None
        for eid, role in em.get_component_store("Role").items():
            if role.type == "Leader":
                leader_pos = em.get_component_store("Position")[eid]
                break
        if not leader_pos:
            return
        nx, ny = leader_pos.x + 2 + (world.rng.randint(-2,2)), leader_pos.y + 2 + (world.rng.randint(-2,2))
        nx = max(0, min(world.grid.width - 1, nx))
        ny = max(0, min(world.grid.height - 1, ny))
        site_id = em.create(GLOBAL_ID_GEN.next())
        em.add_component(site_id, "Position", Position(nx, ny))
        em.add_component(site_id, "Renderable", Renderable("site"))
        cost = BUILD_COSTS[option["target"]]
        em.add_component(site_id, "ConstructionSite", CS(option["target"], needed=cost))

def confirm_pending(world: World, index: int):
    em = world.entities
    leader_ai = list(em.get_component_store("LeaderAI").values())[0]
    if 0 <= index < len(leader_ai.intervention_pending):
        decision = leader_ai.intervention_pending.pop(index)
        for opt in decision["options"]:
            if opt["target"] == decision["chosen"]:
                enact_decision(world, opt)
                return True
    return False

def reject_pending(world: World, index: int):
    em = world.entities
    leader_ai = list(em.get_component_store("LeaderAI").values())[0]
    if 0 <= index < len(leader_ai.intervention_pending):
        leader_ai.intervention_pending.pop(index)
        return True
    return False