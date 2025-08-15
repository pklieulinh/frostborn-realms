from ..ecs.world import World
from ..ecs.components import Role, AttackStats, CombatTag
from ..ecs.components import Health

def guard_system(world: World):
    # If predator present and no guard, convert a worker to guard
    em = world.entities
    role_store = em.get_component_store("Role")
    predators_exist = any(r.type == "Predator" for r in role_store.values())
    if not predators_exist:
        return
    guard_exist = any(r.type == "Guard" for r in role_store.values())
    if guard_exist:
        return
    # pick a worker with highest hp
    healths = em.get_component_store("Health")
    candidates = [(eid, healths[eid].hp) for eid, r in role_store.items() if r.type == "Worker" and eid in healths]
    if not candidates:
        return
    candidates.sort(key=lambda x: x[1], reverse=True)
    chosen = candidates[0][0]
    role_store[chosen].type = "Guard"
    if chosen not in em.get_component_store("AttackStats"):
        em.add_component(chosen, "AttackStats", AttackStats(power=5, cooldown_ticks=7, cooldown=0))
    if chosen not in em.get_component_store("CombatTag"):
        em.add_component(chosen, "CombatTag", CombatTag(faction="colony"))