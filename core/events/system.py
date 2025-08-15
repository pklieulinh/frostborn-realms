from ..ecs.world import World
from ..config import BALANCE
import random

def tick_events(world: World):
    # ColdSnap
    if "ColdSnap" not in world.state.events_active and random.random() < 0.001:
        world.state.events_active["ColdSnap"] = {"until": world.state.tick + 120}
        world.record_event({"tick": world.state.tick, "type": "ColdSnap", "detail": "Nhiệt độ giảm sâu"})
    # PredatorAttack
    if "PredatorAttack" not in world.state.events_active and random.random() < 0.0012:
        intensity = random.choice([0.15, 0.2, 0.3])  # scale of threat
        world.state.events_active["PredatorAttack"] = {"until": world.state.tick + 90, "threat": intensity}
        world.record_event({"tick": world.state.tick, "type": "PredatorAttack", "detail": f"Quái thú tấn công (intensity={intensity})"})
    # PortalSurge
    if "PortalSurge" not in world.state.events_active and random.random() < 0.0008:
        world.state.events_active["PortalSurge"] = {"until": world.state.tick + 80, "boost": BALANCE.portal_surged_quality_boost}
        world.record_event({"tick": world.state.tick, "type": "PortalSurge", "detail": "Dòng chảy không gian hỗn loạn"})
    # Expire
    expired = []
    for k, v in world.state.events_active.items():
        if world.state.tick >= v["until"]:
            expired.append(k)
    for k in expired:
        del world.state.events_active[k]