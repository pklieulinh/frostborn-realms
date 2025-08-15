from ..ecs.world import World
from .leader_defs_logic import suggest_build_targets
from ..ai.leader import create_construction_site

def leader_build_def_step(world: World):
    if world.state.meta.get("pregame", False): return
    suggestions = suggest_build_targets(world)
    if not suggestions: return
    suggestions.sort(key=lambda x:x["score"], reverse=True)
    chosen = suggestions[0]
    # prevent spamming same def consecutively
    last = world.state.decision_feed[-3:]
    if any(d.get("chosen")==chosen["def_id"] for d in last):
        if len(suggestions)>1:
            chosen = suggestions[1]
    # create construction site (def-based)
    create_construction_site(world, "GenericDef", def_id=chosen["def_id"])
    world.record_decision({
        "tick": world.state.tick,
        "type":"LeaderDecisionDef",
        "options":[{"def_id": s["def_id"], "score": round(s["score"],2)} for s in suggestions[:5]],
        "chosen": chosen["def_id"],
        "action_type":"build_def"
    })