from ..ecs.world import World
from ..ecs.components import AttackStats, Position, Health, CombatTag, AICombat, Role

def combat_system(world: World):
    em = world.entities
    atk_store = em.get_component_store("AttackStats")
    pos_store = em.get_component_store("Position")
    hp_store = em.get_component_store("Health")
    tag_store = em.get_component_store("CombatTag")
    ai_store = em.get_component_store("AICombat")
    role_store = em.get_component_store("Role")
    if not atk_store:
        return
    for eid, atk in atk_store.items():
        if atk.cooldown > 0:
            atk.cooldown -= 1
    pending_damage = {}
    for eid, atk in atk_store.items():
        if atk.cooldown > 0:
            continue
        if eid not in pos_store or eid not in tag_store:
            continue
        faction = tag_store[eid].faction
        tx_id = None
        if eid in ai_store:
            tgt = ai_store[eid].target_id
            if tgt and tgt in pos_store and tgt in tag_store and tag_store[tgt].faction != faction:
                if abs(pos_store[eid].x - pos_store[tgt].x) + abs(pos_store[eid].y - pos_store[tgt].y) <= 1:
                    tx_id = tgt
        if tx_id is None:
            ex, ey = pos_store[eid].x, pos_store[eid].y
            for other, other_pos in pos_store.items():
                if other == eid or other not in tag_store:
                    continue
                if tag_store[other].faction == faction:
                    continue
                if abs(other_pos.x - ex) + abs(other_pos.y - ey) <= 1:
                    tx_id = other
                    break
        if tx_id is not None:
            pending_damage[tx_id] = pending_damage.get(tx_id, 0) + atk.power
            atk.cooldown = atk.cooldown_ticks
    any_colonist_death = False
    for target, dmg in pending_damage.items():
        if target not in hp_store:
            continue
        hp_store[target].hp -= dmg
        if hp_store[target].hp <= 0:
            rtype = role_store[target].type if target in role_store else "Unknown"
            if rtype in ("Worker","Leader","Guard"):
                any_colonist_death = True
            world.record_event({"tick": world.state.tick, "type": "Death", "id": target, "role": rtype})
            em.destroy(target)
    if any_colonist_death:
        pen = world.state.meta.get("recent_death_penalty",0.0)
        world.state.meta["recent_death_penalty"] = min(0.2, pen + 0.02)