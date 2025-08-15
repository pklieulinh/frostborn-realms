from .leader import (
    leader_decide,
    load_research_tree,
    apply_research_by_id,
    create_construction_site,
    enact_decision,
    auto_expedition_loadout,
)

# Backwards compatibility stubs (legacy imports might expect these)
def assign_gather_task(*args, **kwargs):
    return None

def assign_construction_tasks(*args, **kwargs):
    return None

def process_task(*args, **kwargs):
    return None

__all__ = [
    "leader_decide",
    "load_research_tree",
    "apply_research_by_id",
    "create_construction_site",
    "enact_decision",
    "auto_expedition_loadout",
    "assign_gather_task",
    "assign_construction_tasks",
    "process_task",
]
