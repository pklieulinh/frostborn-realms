from ..ecs.world import World
from ..ecs.components import WorkIntent, ResourceNode, ResourceInventory, ActivityState, Position
import random

def gather_balance_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    meta = world.state.meta
    mult_wood = meta.get("gather_yield_multiplier_WoodCold",1.5)
    em = world.entities
    nodes = em.get_component_store("ResourceNode")
    intents = em.get_component_store("WorkIntent")
    invs = em.get_component_store("ResourceInventory")
    acts = em.get_component_store("ActivityState")
    for eid,intent in intents.items():
        if intent.job != "Gatherer":
            continue
        act = acts.get(eid)
        if not act or act.state != "Working":
            continue
        target_id = act.target
        if not target_id or target_id not in nodes:
            continue
        node = nodes[target_id]
        if node.amount <= 0:
            continue
        bonus = 0
        if node.rtype == "WoodCold":
            bonus = int(1 * (mult_wood-1))
        if bonus <= 0:
            continue
        inv = invs.get(eid)
        if inv:
            inv.stored[node.rtype] = inv.stored.get(node.rtype,0)+bonus
        node.amount = max(0,node.amount - bonus)
        world.record_event({"tick":world.state.tick,"type":"GatherBonus","rtype":node.rtype,"bonus":bonus})