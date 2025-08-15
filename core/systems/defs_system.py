import json, os
from ..ecs.world import World

DEF_FILES = {
    "items": "items.json",
    "materials": "materials.json",
    "buildings": "buildings.json",
    "storage_filters": "storage_filters.json"
}

def defs_system(world: World):
    meta = world.state.meta
    if meta.get("defs_loaded"): return
    base = os.path.join(os.path.dirname(__file__), "..", "data")
    loaded = {}
    for k, fn in DEF_FILES.items():
        path = os.path.join(base, fn)
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded[k] = json.load(f)
        except Exception:
            loaded[k] = []
    # index maps
    buildings_map = {b["id"]: b for b in loaded.get("buildings", [])}
    items_map = {i["id"]: i for i in loaded.get("items", [])}
    meta["defs"] = {
        "items": items_map,
        "materials": {m["id"]: m for m in loaded.get("materials", [])},
        "buildings": buildings_map,
        "storage_filters": {f["id"]: f for f in loaded.get("storage_filters", [])}
    }
    # categorize building ids by category
    cat_map = {}
    for bid, bdef in buildings_map.items():
        cat = bdef.get("category","Misc")
        cat_map.setdefault(cat, []).append(bid)
    meta["building_categories"] = cat_map
    meta["defs_loaded"] = True