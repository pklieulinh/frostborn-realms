import json
import os
from typing import Dict, Any, List

DEFAULT_TRAITS = [
    {"id":"Stoic","effects":{"emotion_stability":0.2},"desc":"Ổn định cảm xúc."},
    {"id":"Hotheaded","effects":{"anger_gain":0.3,"morale_decay":0.1},"desc":"Dễ nóng."},
    {"id":"Efficient","effects":{"gather_speed":0.15,"build_speed":0.1},"desc":"Làm việc hiệu quả."},
    {"id":"Fragile","effects":{"hp_max_mult":-0.1},"desc":"Thể chất yếu."},
    {"id":"LeaderAura","effects":{"aura_morale":0.05},"desc":"Tỏa khí chất lãnh đạo."},
    {"id":"Scholar","effects":{"research_points":0.05},"desc":"Sinh điểm nghiên cứu."},
    {"id":"ScoutAdept","effects":{"expedition_risk_mult":-0.05},"desc":"Tinh thông thám hiểm."},
    {"id":"Engineer","effects":{"build_speed":0.15},"desc":"Xây dựng nhanh."}
]

def load_trait_catalog() -> Dict[str, Dict[str, Any]]:
    path = os.path.join(os.path.dirname(__file__), "..","data","traits.json")
    catalog: Dict[str, Dict[str, Any]] = {}
    try:
        with open(path,"r",encoding="utf-8") as f:
            arr = json.load(f)
    except Exception:
        arr = DEFAULT_TRAITS
    for t in arr:
        catalog[t["id"]] = t
    return catalog

def summarize_effects(effects: Dict[str, Any]) -> str:
    parts = []
    for k,v in effects.items():
        if isinstance(v,(int,float)):
            sign = "+" if v>=0 else ""
            parts.append(f"{k}:{sign}{v}")
        else:
            parts.append(f"{k}:{v}")
    return ", ".join(parts)

def random_trait_set(rng, catalog, max_traits=3):
    keys = list(catalog.keys())
    rng.shuffle(keys)
    chosen = []
    for k in keys:
        if len(chosen) >= max_traits:
            break
        # simple probability
        if rng.random() < 0.5:
            chosen.append(k)
    if not chosen:
        chosen.append(rng.choice(keys))
    return chosen[:max_traits]