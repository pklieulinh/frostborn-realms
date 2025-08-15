from ..ecs.world import World
from ..ecs.components import Position, Renderable, Role, Health, AttackStats, CombatTag, AICombat
from ..util.id_gen import GLOBAL_ID_GEN

def predator_spawn_system(world: World):
    if "PredatorAttack" not in world.state.events_active:
        return
    threat = world.state.events_active["PredatorAttack"].get("threat", 0.2)
    max_predators = max(1, int(round(threat * 5)))
    em = world.entities
    role_store = em.get_component_store("Role")
    predators = [eid for eid, r in role_store.items() if r.type == "Predator"]
    if len(predators) >= max_predators:
        return
    # spawn one predator
    rng = world.rng
    attempts = 0
    while attempts < 40:
        x = rng.randint(0, world.grid.width - 1)
        y = rng.randint(0, world.grid.height - 1)
        if not world.grid.walkable(x, y):
            attempts += 1
            continue
        pid = em.create(GLOBAL_ID_GEN.next())
        em.add_component(pid, "Position", Position(x, y))
        em.add_component(pid, "Renderable", Renderable("predator"))
        em.add_component(pid, "Role", Role("Predator"))
        em.add_component(pid, "Health", Health(hp=50, max_hp=50))
        em.add_component(pid, "AttackStats", AttackStats(power=6, cooldown_ticks=8, cooldown=0))
        em.add_component(pid, "CombatTag", CombatTag(faction="predator"))
        em.add_component(pid, "AICombat", AICombat())
        world.record_event({"tick": world.state.tick, "type": "SpawnPredator", "id": pid})
        break
        attempts += 1