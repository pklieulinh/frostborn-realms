from ..ecs.world import World
from ..ecs.components import (Position, Renderable, Identity, Profession, Role, Personality,
                              Traits, Authority, EmotionState, Needs, Attributes, TaskAgent,
                              ResourceInventory, Health, Morale, ThermalStatus, CombatTag,
                              Movement, WorkIntent, ActivityState, Dialogue, SkillProgress,
                              Skills, WorkStats, Demographics)
from ..util.id_gen import GLOBAL_ID_GEN
import random

NAMES_POOL = ["Arin","Bora","Cyril","Duna","Eryk","Fara","Galen","Hale","Iris","Jaro","Kael","Lia","Moro","Nila","Orin","Pia","Quill","Ryn","Sera","Tovin","Una","Varek","Wira","Xela","Yori","Zane"]

def colonist_growth_system(world: World):
    if world.state.meta.get("pregame", False): return
    tick = world.state.tick
    meta = world.state.meta
    growth_cd = meta.get("growth_cooldown_ticks",600)
    next_tick = meta.get("next_growth_tick", 300)
    if tick < next_tick: return
    pop = meta.get("population",0)
    housing_cap = meta.get("housing_capacity",0)
    pending = meta.get("pending_housing_capacity",0)
    food_ticks = meta.get("food_ticks",0)
    morale_avg = meta.get("morale_avg",0.8)
    food_threshold = meta.get("population_growth_food_threshold",80)
    if food_ticks <= food_threshold or (pop >= housing_cap + pending):
        meta["next_growth_tick"] = tick + 200
        return
    spawn_colonist(world)
    meta["births_total"] = meta.get("births_total",0)+1
    meta["last_birth_tick"] = tick
    meta["next_growth_tick"] = tick + growth_cd

def spawn_colonist(world: World):
    em = world.entities
    roles = em.get_component_store("Role")
    pos_store = em.get_component_store("Position")
    leader_pos = None
    for eid,r in roles.items():
        if r.type == "Leader":
            leader_pos = pos_store.get(eid)
            if leader_pos: break
    if not leader_pos: return
    rng = random.Random(world.state.tick ^ world.state.seed)
    eid = em.create(GLOBAL_ID_GEN.next())
    x = max(0,min(world.grid.width-1, leader_pos.x + rng.randint(-2,2)))
    y = max(0,min(world.grid.height-1, leader_pos.y + rng.randint(-2,2)))
    em.add_component(eid,"Position",Position(x,y))
    em.add_component(eid,"Renderable",Renderable("worker"))
    name = rng.choice(NAMES_POOL)
    em.add_component(eid,"Identity",Identity(name=name, code=f"N{eid}"))
    main_class, subclass = rng.choice([("Worker","General"),("Worker","Builder"),("Scout","Pathfinder"),("Engineer","Builder")])
    em.add_component(eid,"Profession",Profession(main_class=main_class, subclass=subclass))
    em.add_component(eid,"Role",Role("Worker"))
    p = Personality(
        openness=round(rng.random(),2),
        conscientiousness=round(rng.random(),2),
        extraversion=round(rng.random(),2),
        agreeableness=round(rng.random(),2),
        neuroticism=round(rng.random(),2)
    )
    em.add_component(eid,"Personality",p)
    em.add_component(eid,"Traits",Traits(items=[]))
    em.add_component(eid,"Authority",Authority(rank=1, leader=False))
    em.add_component(eid,"EmotionState",EmotionState())
    em.add_component(eid,"Needs",Needs())
    def ra():
        v = 0.52 + (rng.random()-0.5)*0.22
        return max(0.4,min(0.78,v))
    attrs = Attributes(
        strength=ra(), stamina=ra(), agility=ra(), intelligence=ra(),
        perception=ra(), resilience=ra(), craftsmanship=ra(),
        botany=ra(), mining=ra(), hunting=ra(), hauling=ra()
    )
    em.add_component(eid,"Attributes",attrs)
    em.add_component(eid,"TaskAgent",TaskAgent())
    capacity = int(26 + attrs.strength*24 + attrs.stamina*10)
    em.add_component(eid,"ResourceInventory",ResourceInventory(capacity=capacity, stored={}))
    em.add_component(eid,"Health",Health(hp=65, max_hp=65))
    em.add_component(eid,"Morale",Morale(value=1.0))
    em.add_component(eid,"ThermalStatus",ThermalStatus())
    em.add_component(eid,"CombatTag",CombatTag(faction="colony"))
    em.add_component(eid,"Movement",Movement(speed=1.0))
    em.add_component(eid,"WorkIntent",WorkIntent(job="Idle"))
    em.add_component(eid,"ActivityState",ActivityState())
    em.add_component(eid,"Dialogue",Dialogue(line="Gia nhập."))
    em.add_component(eid,"SkillProgress",SkillProgress())
    em.add_component(eid,"Skills",Skills(levels={},xp={},passions={}))
    em.add_component(eid,"WorkStats",WorkStats())
    gender = "M" if rng.random()<0.5 else "F"
    em.add_component(eid,"Demographics",Demographics(gender=gender, age=18 + rng.randint(0,5)))
    world.record_event({"tick": world.state.tick, "type":"ColonistArrived", "id": eid})