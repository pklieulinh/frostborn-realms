import json
import os
from typing import Dict, Any, List

_CACHE = {}

def load_recipes() -> Dict[str, Any]:
    global _CACHE
    if "recipes" in _CACHE:
        return _CACHE["recipes"]
    base_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    path = os.path.join(base_dir, "crafting_recipes.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {"version": 1, "stations": {}, "recipes": []}
    recipes_by_id = {}
    station_index = {}
    for r in data.get("recipes", []):
        rid = r["id"]
        recipes_by_id[rid] = r
        st = r.get("station")
        if st:
            station_index.setdefault(st, []).append(rid)
    _CACHE["recipes"] = {
        "raw": data,
        "by_id": recipes_by_id,
        "by_station": station_index,
        "stations": data.get("stations", {})
    }
    return _CACHE["recipes"]

def get_station_recipes(station_type: str) -> List[str]:
    d = load_recipes()
    return d["by_station"].get(station_type, [])

def get_recipe(rid: str) -> Any:
    d = load_recipes()
    return d["by_id"].get(rid)