from ..ecs.world import World
from ..ecs.components import Role, HousingUnit, Position, Renderable, Identity, Profession, Personality, Traits, Authority, EmotionState, Needs, TaskAgent, ResourceInventory, Health, Morale, ThermalStatus, CombatTag, Movement, WorkIntent, ActivityState, Dialogue
from ..characters.traits import random_trait_set
from ..util.id_gen import GLOBAL_ID_GEN
import random
NAMES = ["Ael","Bran","Cira","Dax","Eryn","Fynn","Gav","Hale","Ina","Joss","Kara","Lun","Merr","Nyx","Orin","Perr","Quill","Rin","Sera","Tor"]
PROF = [("Worker","General"), ("Worker","Builder"), ("Worker","Lumberjack"), ("Scout","Pathfinder")]

def population_system(world: World):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    roles = em.get_component_store("Role")
    housings = em.get_component_store("HousingUnit")
    if not roles or not housings: return
    pop = sum(1 for r in roles.values() if r.type in ("Worker","Leader","Guard","Scholar","Engineer","Scout","Soldier"))
    capacity = sum(h.capacity for h in housings.values())
    free = capacity - pop
    world.state.meta["population"] = pop
    world.state.meta["housing_capacity"] = capacity
    world.state.meta["housing_occupied"] = pop
    # growth control
    interval = world.state.meta.get("growth_interval_ticks", 600)
    next_tick = world.state.meta.get("next_growth_check", 0)
    if world.state.tick < next_tick: return
    world.state.meta["next_growth_check"] = world.state.tick + interval
    # conditions
    if free <= 0: return
    food_ticks = world.state.meta.get("food_ticks",0)
    if food_ticks < world.state.meta.get("phase_food_min",800)*0.85: return
    morale_avg = _morale_avg(world)
    if morale_avg < 0.55: return
    # spawn
    _spawn_colonist(world)
    world.record_event({"tick": world.state.tick, "type":"ImmigrantArrived"})
    # update projection
    world.state.meta["pop_growth_projection"] = max(1, (pop+1)//6 + (1 if world.state.portal_count>0 else 0))

def _morale_avg(world: World):
    store = world.entities.get_component_store("Morale")
    if not store: return 1.0
    return sum(m.value for m in store.values())/len(store)

def _spawn_colonist(world: World):
    em = world.entities
    leader_pos = None
    pos_store = em.get_component_store("Position")
    for eid, r in em.get_component_store("Role").items():
        if r.type == "Leader":
            leader_pos = pos_store.get(eid)
            break
    x = leader_pos.x+1 if leader_pos else 5
    y = leader_pos.y+1 if leader_pos else 5
    eid = em.create(GLOBAL_ID_GEN.next())
    em.add_component(eid,"Position",Position(x,y))
    em.add_component(eid,"Renderable",Renderable("worker"))
    name = random.choice(NAMES)
    em.add_component(eid,"Identity",Identity(name=name, code=f"NEW{eid}"))
    main, sub = random.choice(PROF)
    em.add_component(eid,"Profession",Profession(main_class=main, subclass=sub))
    em.add_component(eid,"Role",Role("Worker"))
    p = Personality(
        openness=round(random.random(),2),
        conscientiousness=round(random.random(),2),
        extraversion=round(random.random(),2),
        agreeableness=round(random.random(),2),
        neuroticism=round(random.random(),2),
    )
    em.add_component(eid,"Personality",p)
    catalog = world.state.meta.get("trait_catalog",{})
    tset = random_trait_set(random, catalog, max_traits=2)
    em.add_component(eid,"Traits",Traits(items=tset))
    em.add_component(eid,"Authority",Authority(rank=1, leader=False))
    em.add_component(eid,"EmotionState",EmotionState())
    em.add_component(eid,"Needs",Needs())
    em.add_component(eid,"TaskAgent",TaskAgent())
    em.add_component(eid,"ResourceInventory",ResourceInventory(capacity=20, stored={}))
    em.add_component(eid,"Health",Health(hp=55,max_hp=55))
    em.add_component(eid,"Morale",Morale(value=1.0))
    em.add_component(eid,"ThermalStatus",ThermalStatus())
    em.add_component(eid,"CombatTag",CombatTag(faction="colony"))
    em.add_component(eid,"Movement",Movement(speed=1.0))
    em.add_component(eid,"WorkIntent",WorkIntent(job="Idle"))
    em.add_component(eid,"ActivityState",ActivityState())
    em.add_component(eid,"Dialogue",Dialogue(line="Tôi đã đến!"))