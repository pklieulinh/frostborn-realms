from ..ecs.world import World
from ..ecs.components import ExpeditionTeam, Position, Renderable
from ..util.id_gen import GLOBAL_ID_GEN
from ..systems.expedition_tick import PHASES

def launch_expedition(world: World, portal_seed: int, loadout=None):
    if loadout is None:
        loadout = {"guards":0,"scouts":1,"supplies":1}
    em = world.entities
    team_id = em.create(GLOBAL_ID_GEN.next())
    phase_name, phase_dur = PHASES[0]
    team = ExpeditionTeam(
        team_id=team_id,
        portal_seed=portal_seed,
        phase=phase_name,
        ticks_remaining=phase_dur,
        loadout=loadout,
        risk=0.1,
        base_duration=sum(p[1] for p in PHASES),
        phase_index=0
    )
    em.add_component(team_id, "ExpeditionTeam", team)
    # Optional render anchor (off-map)
    em.add_component(team_id, "Position", Position(0,0))
    em.add_component(team_id, "Renderable", Renderable("expedition_team"))
    world.record_event({"tick": world.state.tick, "type":"ExpeditionLaunched", "id": team_id, "loadout": loadout})