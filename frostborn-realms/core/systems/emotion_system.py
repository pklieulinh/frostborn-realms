import json
import os
from ..ecs.world import World
from ..ecs.components import EmotionState

def emotion_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    emostore = em.get_component_store("EmotionState")
    if not emostore:
        return
    meta = world.state.meta
    if "emotion_config" not in meta:
        meta["emotion_config"] = _load_emotion_config()
        meta["emotion_event_index"] = 0
    cfg = meta["emotion_config"]
    baseline_decay = cfg["baseline"].get("mood_decay", 0.001)
    anger_decay = cfg["baseline"].get("anger_decay", 0.003)
    fear_decay = cfg["baseline"].get("fear_decay", 0.002)
    events = world.state.event_feed
    start_idx = meta.get("emotion_event_index", 0)
    new_events = events[start_idx:]
    impacts = cfg.get("event_impacts", {})
    # Apply event impacts once
    for ev in new_events:
        etype = ev.get("type")
        imp = impacts.get(etype.lower()) or impacts.get(etype)  # case flexibility
        if imp:
            for eid, es in emostore.items():
                es.mood = clamp(es.mood + imp.get("mood", 0.0), 0.0, 1.0)
                es.anger = clamp(es.anger + imp.get("anger", 0.0), 0.0, 1.0)
                es.fear = clamp(es.fear + imp.get("fear", 0.0), 0.0, 1.0)
    if new_events:
        meta["emotion_event_index"] = len(events)
    # Natural decay toward neutral
    for eid, es in emostore.items():
        # mood toward 0.7 baseline
        delta = 0.7 - es.mood
        es.mood += delta * baseline_decay * 5
        if delta > 0:
            es.mood = min(1.0, es.mood)
        es.anger = max(0.0, es.anger - anger_decay)
        es.fear = max(0.0, es.fear - fear_decay)

def _load_emotion_config():
    path = os.path.join(os.path.dirname(__file__), "..","data","emotions_matrix.json")
    try:
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "baseline":{"mood_decay":0.001,"anger_decay":0.003,"fear_decay":0.002},
            "event_impacts":{
                "Death":{"mood":-0.1,"fear":0.05},
                "Victory":{"mood":0.15}
            }
        }

def clamp(v, a, b):
    return a if v < a else b if v > b else v