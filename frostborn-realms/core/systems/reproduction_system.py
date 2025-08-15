from ..ecs.world import World
from ..ecs.components import Demographics, Role
from .colonist_growth_system import spawn_colonist

REPRO_INTERVAL = 300

def reproduction_system(world: World):
    if world.state.meta.get("pregame", False): return
    tick = world.state.tick
    if tick % REPRO_INTERVAL != 0: return
    meta = world.state.meta
    food_ticks = meta.get("food_ticks",0)
    morale_avg = meta.get("morale_avg",0.8)
    housing_cap = meta.get("housing_capacity",0)
    pending = meta.get("pending_housing_capacity",0)
    pop = meta.get("population",0)
    if pop >= housing_cap + pending: return
    if food_ticks < 50 or morale_avg < 0.5: return
    em = world.entities
    demos = em.get_component_store("Demographics")
    roles = em.get_component_store("Role")
    males = any(d.gender=="M" and eid in roles and roles[eid].type in WORK_TYPES for eid,d in demos.items())
    females = any(d.gender=="F" and eid in roles and roles[eid].type in WORK_TYPES for eid,d in demos.items())
    if not males or not females: return
    spawn_colonist(world)
    meta["births_total"] = meta.get("births_total",0)+1
    meta["last_birth_tick"] = tick

WORK_TYPES = ("Worker","Leader","Guard","Scholar","Engineer","Scout","Soldier")