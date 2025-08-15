import json
from pathlib import Path
from typing import Dict, Any
from .ecs.world import World
from .ecs.components import COMPONENT_TYPES

SAVE_FILE = Path("save_slot.json")
SCHEMA_VERSION = 2

META_WHITELIST = {
    "research_points",
    "completed_research",
    "modifiers",
    "auto_research",
    "recent_death_penalty",
    "victory_state"
}

def save_world(world: World):
    data: Dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "tick": world.state.tick,
        "seed": world.state.seed,
        "portal_count": world.state.portal_count,
        "intervention_mode": world.state.intervention_mode,
        "events_active": world.state.events_active,
        "meta": {k: v for k, v in world.state.meta.items() if k in META_WHITELIST},
        "entities": [],
    }
    for eid in world.entities.entities:
        comp_map = world.entities.serialize_entity(eid)
        data["entities"].append({"id": eid, "components": comp_map})
    SAVE_FILE.write_text(json.dumps(data))

def load_world(world: World):
    if not SAVE_FILE.exists():
        return False
    raw = json.loads(SAVE_FILE.read_text())
    schema = raw.get("schema",1)
    for eid in list(world.entities.entities):
        world.entities.destroy(eid)
    world.state.tick = raw.get("tick",0)
    world.state.portal_count = raw.get("portal_count",0)
    world.state.intervention_mode = raw.get("intervention_mode",False)
    world.state.events_active = raw.get("events_active",{})
    meta_in = raw.get("meta",{}) if schema >=2 else {}
    for k,v in meta_in.items():
        world.state.meta[k] = v
    for e in raw.get("entities",[]):
        eid = e["id"]
        world.entities.create(eid)
        for cname, cval in e["components"].items():
            if cname in COMPONENT_TYPES:
                ctype = COMPONENT_TYPES[cname]
                obj = ctype(**cval)
                world.entities.add_component(eid, cname, obj)
    return True