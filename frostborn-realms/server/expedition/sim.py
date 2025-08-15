from ..ecs.world import World
from ..ecs.components import ExpeditionTeam
from ..util.id_gen import GLOBAL_ID_GEN
from ..portals.portal import portal_biome

def launch_expedition(world: World, portal_seed: int):
    em = world.entities
    team_id = GLOBAL_ID_GEN.next()
    eid = em.create(team_id)
    portal_biome(portal_seed)
    duration = 40
    em.add_component(eid, "ExpeditionTeam", ExpeditionTeam(team_id=team_id, portal_seed=portal_seed, phase="travel", ticks_remaining=duration))
    world.record_expedition({"tick": world.state.tick, "id": team_id, "portal_seed": portal_seed, "status": "launched"})

def tick_expeditions(world: World):
    em = world.entities
    teams = em.get_component_store("ExpeditionTeam")
    remove = []
    for eid, team in teams.items():
        team.ticks_remaining -= 1
        if team.ticks_remaining % 10 == 0 and team.phase == "travel":
            team.log.append({"tick": world.state.tick, "msg": "Encounter minor"})
        if team.ticks_remaining <= 0:
            team.phase = "returning"
            team.result = {"loot": {"FrostCrystal": 1}}
            world.record_expedition({"tick": world.state.tick, "id": team.team_id, "portal_seed": team.portal_seed, "status": "completed", "result": team.result})
            remove.append(eid)
    for r in remove:
        em.destroy(r)