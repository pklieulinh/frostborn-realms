from ..ecs.world import World
from ..ecs.components import Dialogue, ActivityState, WorkIntent, ResourceInventory, LeaderAI

BASE_LINES = {
    "Idle":["Rảnh.","Chờ lệnh.","..."],
    "Moving":["Đang đi.","Tới nơi.","Nhanh nào."],
    "Working":["Làm việc.","Tập trung.","Tiếp tục."],
    "Delivering":["Vận chuyển.","Mang vật liệu."],
    "Harvesting":["Thu hoạch."],
    "Combat":["Chiến đấu!"],
}

JOB_LINES = {
    "Farmer":["Chăm ruộng.","Tưới nhẹ.","Lo vụ mùa."],
    "Herder":["Chăn nuôi.","Kiểm chuồng."],
    "Hunter":["Đi săn.","Rình mồi."],
    "Builder":["Xây dựng.","Cố định khung."],
    "Gatherer":["Gom gỗ.","Khai thác."],
    "Explorer":["Thăm dò.","Quan sát."],
    "Miner":["Khai mỏ.","Đục quặng."],
    "Forester":["Trồng cây.","Gieo mầm."]
}

def dialogue_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    dlg = em.get_component_store("Dialogue")
    acts = em.get_component_store("ActivityState")
    intents = em.get_component_store("WorkIntent")
    tick = world.state.tick
    invs = em.get_component_store("ResourceInventory")
    leader_ai = em.get_component_store("LeaderAI")
    leader_id = None
    if leader_ai:
        leader_id = list(leader_ai.keys())[0]

    low_wood = False
    total_wood = 0
    for inv in invs.values():
        total_wood += inv.stored.get("WoodCold",0)
    if total_wood < world.state.meta.get("wood_reserve",20):
        low_wood = True

    for eid, d in dlg.items():
        act = acts.get(eid)
        intent = intents.get(eid)
        if not act or not intent:
            continue
        if world.state.tick < d.next_change_tick and act.changed_tick != tick:
            continue
        pool = JOB_LINES.get(intent.job)
        if eid == leader_id:
            # Leader dynamic lines
            if low_wood and intent.job in ("Gatherer","Builder"):
                pool = ["Ta dẫn đầu.","Nhanh lên.","Ưu tiên gỗ."]
            elif intent.job in JOB_LINES:
                pool = [f"Làm {intent.job.lower()}."]
            else:
                pool = ["Chỉ huy & hỗ trợ.","Giám sát."]
        if not pool:
            pool = BASE_LINES.get(act.state, ["..."])
        import random
        d.line = random.choice(pool)
        d.next_change_tick = tick + 160