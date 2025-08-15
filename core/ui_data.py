from .ecs.world import World
from .ai.leader import aggregate_resources, load_research_tree

def gather_ui_state(world: World):
    load_research_tree(world)
    res = aggregate_resources(world)
    meta = world.state.meta
    return {
        "tick": world.state.tick,
        "resources": res,
        "decisions": list(world.state.decision_feed)[-8:],
        "events": list(world.state.event_feed)[-8:],
        "expeditions": list(world.state.expedition_feed)[-6:],
        "portal_count": world.state.portal_count,
        "intervention": world.state.intervention_mode,
        "research_points": round(meta.get("research_points",0.0),2),
        "completed_research": meta.get("completed_research",[]),
        "modifiers": meta.get("modifiers",{}),
        "auto_research": meta.get("auto_research",False)
    }