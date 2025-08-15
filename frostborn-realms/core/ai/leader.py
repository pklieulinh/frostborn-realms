from typing import Dict, Any, List, Optional
from math import ceil
from ..ecs.world import World
from ..config import MAX_PORTALS, BALANCE
from .colony_phase import ColonyPhase, determine_phase
from ..expedition.sim import launch_expedition

BUILD_COSTS = {
    "Housing": {"wood_log": 30},
    "Storage": {"wood_log": 25},
    "HeatStation": {"wood_log": 25},
    "FarmPlot": {"wood_log": 35},
    "Pasture": {"wood_log": 40},
    "ResearchStation": {"wood_log": 40},
    "Foundry": {"wood_log": 45},
    "PortalGate": {"wood_log": 60},
    "TreeNursery": {"wood_log": 30},
    "Mine": {"wood_log": 50}
}

PRIORITY_ORDER = [
    "Housing",
    "Storage",
    "PortalGate",
    "FarmPlot",
    "Pasture",
    "TreeNursery",
    "Foundry",
    "ResearchStation",
    "HeatStation",
]

FOOD_KEYS = ("FoodRation","MealHearty","BerriesFrozen","MeatRaw")
CRITICAL_ITEMS = ["wood_log","stone_block","iron_ingot","hide_tanned","cloth_roll","crystal_frost"]

FARMER_PLOTS_CAPACITY = 4
GLOBAL_FARM_CAP_PER_COLONIST = 2
MAX_CONSEC_FARM = 2
FARM_DEF_PREFIXES = ("farm_plot",)  # mở rộng nếu có thêm biến thể

HOUSING_DEF_CAPACITY = {
    "hut": 2,
    "cabin": 4,
    "lodge": 6,
    "dormitory": 10,
    "insulated_house": 6
}

def aggregate_resources(world: World) -> Dict[str,int]:
    global_res = world.state.meta.get("resources_global")
    if global_res:
        return dict(global_res)
    invs = world.entities.get_component_store("ResourceInventory")
    total: Dict[str,int] = {}
    for inv in invs.values():
        for k, v in inv.stored.items():
            total[k] = total.get(k, 0) + v
    return total

def existing_building_counts(world: World) -> Dict[str,int]:
    counts: Dict[str,int] = {}
    for b in world.entities.get_component_store("Building").values():
        counts[b.btype] = counts.get(b.btype,0)+1
    return counts

def morale_average(world: World) -> float:
    store = world.entities.get_component_store("Morale")
    if not store:
        return 1.0
    return sum(m.value for m in store.values())/len(store)

def threat_level(world: World) -> int:
    roles = world.entities.get_component_store("Role")
    return sum(1 for r in roles.values() if r.type == "Predator")

def research_gap(world: World) -> float:
    meta = world.state.meta
    tree = meta.get("research_tree_loaded", [])
    completed = meta.get("completed_research", [])
    if not tree:
        return 0.0
    return 1.0 - (len(completed)/len(tree)) if tree else 0.0

def population_info(world: World):
    roles = world.entities.get_component_store("Role")
    colonists = [eid for eid,r in roles.items()
                 if r.type in ("Worker","Leader","Guard","Scholar","Engineer","Scout","Soldier")]
    pop = len(colonists)
    capacity = world.state.meta.get("housing_capacity", 0)
    return pop, capacity

def food_days(world: World) -> float:
    pool = aggregate_resources(world)
    total_food = pool.get("FoodRationEq")
    if total_food is None:
        total_food = 0
        for k in FOOD_KEYS:
            total_food += pool.get(k,0)
    pop, _ = population_info(world)
    if pop == 0:
        return 9999
    consumption_per_tick = pop / BALANCE.food_need_interval
    if consumption_per_tick <= 0:
        return 9999
    return total_food / consumption_per_tick

def desired_farm_count(world: World, pop: int, food_ticks: float) -> int:
    if pop == 0:
        return 0
    if food_ticks > 800: return 0
    if food_ticks > 400: return 1
    base = ceil(pop/4)
    upper = pop*2
    return max(1, min(upper, base))

def recent_same_decisions_penalty(world: World, candidate: str) -> float:
    last = world.state.decision_feed[-MAX_CONSEC_FARM:]
    if not last: return 1.0
    if all(d.get("chosen") == candidate for d in last):
        return 0.55
    return 1.0

def build_cooldown_ok(world: World, btype: str) -> bool:
    cd_map = world.state.meta.setdefault("build_type_cooldowns", {})
    now = world.state.tick
    return now >= cd_map.get(btype, 0)

def set_build_cooldown(world: World, btype: str, first_portal: bool=False):
    cd_map = world.state.meta.setdefault("build_type_cooldowns", {})
    now = world.state.tick
    base_cd = {
        "FarmPlot": 80,
        "ResearchStation": 200,
        "Housing": 140,
        "Pasture": 140,
        "Foundry": 260,
        "PortalGate": 260 if first_portal else 420,
        "Storage": 180,
        "HeatStation": 140,
        "TreeNursery": 600,
        "Mine": 240
    }.get(btype, 140)
    cd_map[btype] = now + base_cd

# ---------- Build Governor ----------

def count_pending_sites(world: World):
    sites = world.entities.get_component_store("ConstructionSite")
    counts: Dict[str,int] = {}
    for s in sites.values():
        if s.complete: continue
        did = s.meta.get("def_id") or s.btype
        counts[did] = counts.get(did,0)+1
    return counts

def pending_category_counts(world: World):
    counts = count_pending_sites(world)
    cat = {"farm":0,"housing":0,"portal":0,"other":0}
    for did,c in counts.items():
        low = did.lower()
        if low.startswith("portal_gate"):
            cat["portal"] += c
        elif low in HOUSING_DEF_CAPACITY:
            cat["housing"] += c
        elif any(low.startswith(p) for p in FARM_DEF_PREFIXES) or low == "farmplot" or low == "farmplot".lower():
            cat["farm"] += c
        else:
            cat["other"] += c
    cat["total"] = sum(counts.values())
    return cat

def governor_limits(pop: int):
    if pop < 5:
        max_total = 3
    else:
        max_total = min(8, pop//2 + 2)
    return {
        "total": max_total,
        "farm": 1 if pop < 4 else min(2, ceil(pop/6)),
        "housing": 1,
        "portal": 1,
        "other": 2
    }

def consecutive_farm_decisions(world: World):
    feed = world.state.decision_feed
    c = 0
    for d in reversed(feed[-6:]):
        ch = d.get("chosen","").lower()
        if "farm" in ch:
            c += 1
        else:
            break
    return c

def governor_can_queue(world: World, def_or_type: str, category: str, pop: int, desired_farms: int,
                       farm_existing: int, food_ticks: float) -> bool:
    pc = pending_category_counts(world)
    limits = governor_limits(pop)
    if pc["total"] >= limits["total"]:
        return False
    if pc.get(category,0) >= limits[category]:
        return False
    # category specific rules
    if category == "farm":
        # hard caps
        pending_farm = pc["farm"]
        if farm_existing + pending_farm >= desired_farms and food_ticks >= 15:
            return False
        hard_cap = pop * GLOBAL_FARM_CAP_PER_COLONIST
        if hard_cap == 0: hard_cap = 2
        if farm_existing + pending_farm >= hard_cap and food_ticks >= 10:
            return False
        if food_ticks > 400:
            return False
        if consecutive_farm_decisions(world) >= MAX_CONSEC_FARM:
            return False
    return True

def classify_def(def_id: str) -> str:
    low = def_id.lower()
    if low.startswith("portal_gate"):
        return "portal"
    if low in HOUSING_DEF_CAPACITY:
        return "housing"
    if any(low.startswith(p) for p in FARM_DEF_PREFIXES) or low == "farmplot" or low == "farm_plot":
        return "farm"
    return "other"

# ---------- Scoring Legacy ----------

def score_build_option(world: World, b: str,
                       phase: ColonyPhase,
                       resources: Dict[str,int],
                       counts: Dict[str,int],
                       morale_avg: float,
                       predators: int,
                       r_gap: float,
                       food_ticks: float,
                       pop: int,
                       capacity: int,
                       desired_farms: int,
                       storage_pressure: float,
                       hauling_backlog: float) -> Optional[Dict[str,Any]]:
    cost = BUILD_COSTS[b]
    if not build_cooldown_ok(world, b):
        return None
    afford = all(resources.get(r,0) >= c or resources.get(r.lower(),0)>=c for r,c in cost.items())
    exist = counts.get(b,0)
    base = 0.0
    food_min = world.state.meta.get("phase_food_min", 800)
    food_goal = world.state.meta.get("phase_food_goal", 1200)
    housing_buffer = world.state.meta.get("housing_buffer",1)
    housing_required = pop + housing_buffer

    if b == "Housing":
        if capacity >= housing_required:
            return None
        deficit = pop - capacity
        base = 0.9 + max(0, deficit)*0.25
    elif b == "Storage":
        pressure_bonus = 0
        if storage_pressure > 0.7:
            pressure_bonus += min(0.6, (storage_pressure - 0.7)*2.0)
        base = 0.4 + pressure_bonus
        if base < 0.4: return None
    elif b == "PortalGate":
        if world.state.portal_count >= MAX_PORTALS: return None
        if resources.get("wood_log",0) < 40: return None
        if world.state.portal_count == 0:
            if food_ticks < food_min*0.55: return None
            base = 0.8
        else:
            base = 0.55
    elif b == "FarmPlot":
        farm_existing_real = counts.get("farm_plot",0) + counts.get("FarmPlot",0)
        pending = pending_category_counts(world)["farm"]
        if farm_existing_real + pending >= desired_farms and food_ticks >= food_min*0.25:
            return None
        hard_cap = min(pop*GLOBAL_FARM_CAP_PER_COLONIST, max(6, pop*2))
        if farm_existing_real + pending >= hard_cap and food_ticks >= 15:
            return None
        if food_ticks > 400:
            return None
        base = 0.6 if food_ticks < food_min else 0.2
        if farm_existing_real > 0:
            base /= (1 + farm_existing_real*0.5)
    elif b == "Pasture":
        if counts.get("FarmPlot",0) == 0 or food_ticks < food_min*0.5: return None
        base = 0.28
    elif b == "TreeNursery":
        if exist >= 1: return None
        base = 0.35
    elif b == "Foundry":
        if phase < ColonyPhase.INDUSTRY: return None
        base = 0.32 if exist==0 else 0.15
    elif b == "ResearchStation":
        cap_rs = max(1, pop//14 + 1)
        if exist >= cap_rs or food_ticks < food_min*0.6: return None
        base = 0.30 * (0.5 + research_gap(world))
    elif b == "HeatStation":
        base = 0.18 if exist < 2 else 0.1
    elif b == "Mine":
        ops = world.state.meta.get("pending_mine_ops", [])
        if not ops: return None
        active = counts.get("Mine",0)
        if active >= max(1, pop//5): return None
        base = 0.5
    else:
        return None

    if base <= 0: return None
    morale_factor = 0.5 + morale_avg/2
    if threat_level(world) > 0 and b not in ("PortalGate","Housing","Storage"):
        morale_factor *= 0.85
    score = base * morale_factor
    if not afford: score *= 0.25
    if b == "FarmPlot":
        if not governor_can_queue(world, "FarmPlot", "farm", pop,
                                   desired_farm_count(world,pop,world.state.meta.get("food_ticks",0)),
                                   counts.get("farm_plot",0)+counts.get("FarmPlot",0),
                                   world.state.meta.get("food_ticks",0)):
            return None
    score *= recent_same_decisions_penalty(world, b)
    return {
        "type":"build",
        "target": b,
        "score": score,
        "afford": afford,
        "factors":{},
        "cost": cost
    }

def auto_select_research(world: World):
    meta = world.state.meta
    tree = meta.get("research_tree_loaded", [])
    completed = set(meta.get("completed_research", []))
    pts = meta.get("research_points", 0.0)
    available = []
    for node in tree:
        if node["id"] in completed: continue
        prereq = node.get("prereq")
        if prereq and prereq not in completed: continue
        if pts >= node["cost"]:
            available.append(node)
    if not available: return None
    available.sort(key=lambda n: n["cost"])
    return available[0]

def load_research_tree(world: World):
    if "research_tree_loaded" in world.state.meta: return
    import json, os
    path = os.path.join(os.path.dirname(__file__), "..","data","research_tree.json")
    try:
        with open(path,"r",encoding="utf-8") as f:
            tree = json.load(f)
    except Exception:
        tree = [
            {"id":"gather1","name":"Sharper Axes","cost":8,"effects":{"gather_speed":0.15}},
            {"id":"build1","name":"Reinforced Tools","cost":10,"effects":{"build_speed":0.15},"prereq":"gather1"},
            {"id":"exp1","name":"Survival Drills","cost":12,"effects":{"expedition_risk_mult":-0.1},"prereq":"gather1"},
            {"id":"loot1","name":"Efficient Packing","cost":14,"effects":{"expedition_loot_mult":0.2},"prereq":"exp1"},
            {"id":"portal1","name":"Arcane Tuning","cost":16,"effects":{"portal_quality_bonus":0.1},"prereq":"build1"}
        ]
    world.state.meta["research_tree_loaded"] = tree
    world.state.meta.setdefault("completed_research", [])
    world.state.meta.setdefault("research_points", 0.0)
    world.state.meta.setdefault("modifiers", {
        "gather_speed":0.0,
        "build_speed":0.0,
        "expedition_loot_mult":0.0,
        "expedition_risk_mult":0.0,
        "portal_quality_bonus":0.0
    })
    world.state.meta.setdefault("auto_research", False)
    world.state.meta.setdefault("phase_food_min", 800)
    world.state.meta.setdefault("phase_food_goal", 1200)
    world.state.meta.setdefault("phase_food_bootstrap_exit", 400)
    world.state.meta.setdefault("leader_hands_on", True)

def apply_research_by_id(world: World, rid: str):
    load_research_tree(world)
    meta = world.state.meta
    if rid in meta.get("completed_research", []): return False
    node = next((n for n in meta["research_tree_loaded"] if n["id"]==rid), None)
    if not node: return False
    prereq = node.get("prereq")
    if prereq and prereq not in meta["completed_research"]: return False
    cost = node["cost"]
    if meta.get("research_points",0.0) < cost: return False
    meta["research_points"] -= cost
    for k,v in node.get("effects",{}).items():
        meta["modifiers"][k] = meta["modifiers"].get(k,0.0)+v
    meta["completed_research"].append(rid)
    world.record_event({"tick": world.state.tick, "type":"ResearchComplete", "id": rid})
    return True

def evaluate_colony_metrics(world: World) -> Dict[str,float]:
    meta = world.state.meta
    res = meta.get("resources_global", {})
    pop = meta.get("population",0)
    food_amount = res.get("FoodRationEq",0)
    food_need_rate = max(1,pop)*0.5
    food_ticks = food_amount/food_need_rate if food_need_rate>0 else 999
    housing_cap = meta.get("housing_capacity",0)
    housing_deficit = max(0,pop-housing_cap)
    apparel_warm = sum(res.get(k,0) for k in ("parka_fur","coat_leather","boots_fur","gloves_wool","hat_fur"))
    equip_cold_ratio = apparel_warm/max(1,pop*2.2)
    morale_avg = meta.get("morale_avg",0.8)
    recreation_need = 1 - min(1,morale_avg)
    distinct_resources = sum(1 for c in CRITICAL_ITEMS if res.get(c,0)>0)
    portal_need = 1 if distinct_resources < len(CRITICAL_ITEMS)//2 else 0
    expansion_need = 0.0
    if meta.get("storage_pressure",0)>0.8: expansion_need += 0.6
    if pop>8 and housing_deficit==0 and food_ticks>40 and equip_cold_ratio>0.6: expansion_need += 0.4
    meta["food_ticks"] = food_ticks
    meta["food_infra_score"] = round(food_ticks,2)
    meta["housing_need"] = housing_deficit
    meta["equip_cold_ratio"] = round(equip_cold_ratio,2)
    meta["recreation_need"] = recreation_need
    meta["portal_need_flag"] = portal_need
    meta["expansion_need"] = expansion_need
    return {
        "food_ticks":food_ticks,
        "housing_deficit":housing_deficit,
        "equip_cold_ratio":equip_cold_ratio,
        "recreation_need":recreation_need,
        "portal_need":portal_need,
        "expansion_need":expansion_need
    }

def suggest_build_targets(world: World) -> List[Dict[str,Any]]:
    defs = world.state.meta.get("defs",{})
    if not defs: return []
    buildings = defs.get("buildings",{})
    metrics = evaluate_colony_metrics(world)
    counts = existing_building_counts(world)
    pop,_ = population_info(world)
    choices = []
    if metrics["food_ticks"] < 30:
        farm_existing = counts.get("farm_plot",0)
        farmers_est = max(1,pop//6)
        farm_cap = max(farmers_est*FARMER_PLOTS_CAPACITY,pop*GLOBAL_FARM_CAP_PER_COLONIST)
        if farm_existing < farm_cap or metrics["food_ticks"] < 18:
            for bid in ("farm_plot","greenhouse_basic","kitchen_basic","smokehouse"):
                if bid in buildings:
                    score = (30 - metrics["food_ticks"])/30 + buildings[bid].get("tier",1)*0.05
                    if governor_can_queue(world,bid,"farm",pop,
                                           desired_farm_count(world,pop,metrics["food_ticks"]),
                                           counts.get("farm_plot",0),
                                           metrics["food_ticks"]):
                        choices.append({"def_id":bid,"layer":"food","score":score})
    if metrics["housing_deficit"]>0:
        for bid in ("hut","cabin","lodge","dormitory","insulated_house"):
            if bid in buildings:
                tier = buildings[bid]["tier"]
                score = 0.9 + tier*0.1 + metrics["housing_deficit"]*0.15
                if governor_can_queue(world,bid,"housing",pop,0,0,metrics["food_ticks"]):
                    choices.append({"def_id":bid,"layer":"housing","score":score})
    if metrics["equip_cold_ratio"] < 0.75 and metrics["food_ticks"]>25 and metrics["housing_deficit"]==0:
        for bid in ("tailor_workshop","tannery","loom","forge_smithy"):
            if bid in buildings:
                gap = 0.75 - metrics["equip_cold_ratio"]
                score = 0.6 + gap*1.2
                if governor_can_queue(world,bid,"other",pop,0,0,metrics["food_ticks"]):
                    choices.append({"def_id":bid,"layer":"equipment","score":score})
    if metrics["recreation_need"]>0.25 and metrics["food_ticks"]>25 and metrics["housing_deficit"]==0:
        for bid in ("hearth_hall","music_stand","library_corner","shrine_small","bathhouse"):
            if bid in buildings and governor_can_queue(world,bid,"other",pop,0,0,metrics["food_ticks"]):
                score = 0.4 + metrics["recreation_need"]*0.9
                choices.append({"def_id":bid,"layer":"recreation","score":score})
    if metrics["expansion_need"]>0.1:
        for bid in ("storage_crate","granary","cold_storage","stockyard","watchtower_wood","palisade_segment","stone_wall","armory_store"):
            if bid in buildings and governor_can_queue(world,bid,"other",pop,0,0,metrics["food_ticks"]):
                score = 0.3 + metrics["expansion_need"]
                choices.append({"def_id":bid,"layer":"expansion","score":score})
    if metrics["portal_need"]>0 and metrics["food_ticks"]>15:
        for bid in ("portal_gate_t1","portal_gate_t2"):
            if bid in buildings and governor_can_queue(world,bid,"portal",pop,0,0,metrics["food_ticks"]):
                score = 0.55 + metrics["portal_need"]*0.5
                choices.append({"def_id":bid,"layer":"portal","score":score})
    for c in choices:
        bdef = buildings.get(c["def_id"],{})
        c["score"] += (5 - bdef.get("tier",1))*0.02
    return choices

def leader_build_def_step(world: World):
    if world.state.meta.get("pregame", False): return
    if world.state.tick % 200 != 0: return
    sites = world.entities.get_component_store("ConstructionSite")
    if sites and any(s.meta.get("def_id") for s in sites.values()):
        return
    suggestions = suggest_build_targets(world)
    if not suggestions: return
    suggestions.sort(key=lambda x:x["score"], reverse=True)
    chosen = suggestions[0]
    last = world.state.decision_feed[-3:]
    if any(d.get("chosen")==chosen["def_id"] for d in last) and len(suggestions)>1:
        chosen = suggestions[1]
    create_construction_site(world, chosen["def_id"], def_id=chosen["def_id"])
    world.record_decision({
        "tick": world.state.tick,
        "type":"LeaderDecisionDef",
        "options":[{"def_id": s["def_id"], "score": round(s["score"],2)} for s in suggestions[:5]],
        "chosen": chosen["def_id"],
        "action_type":"build_def"
    })

def leader_decide(world: World, tick: Optional[int]=None):
    if world.state.meta.get("pregame", False): return
    em = world.entities
    leader_store = em.get_component_store("LeaderAI")
    if not leader_store: return
    leader_id = list(leader_store.keys())[0]
    leader = leader_store[leader_id]
    base_interval = world.state.meta.get("decision_interval_base", 90)
    acts = em.get_component_store("ActivityState")
    if acts.get(leader_id) and acts[leader_id].state in ("Working","Moving"): base_interval += 40
    if world.state.tick - leader.last_decision_tick < base_interval: return

    resources = aggregate_resources(world)
    counts = existing_building_counts(world)
    morale_avg = morale_average(world)
    predators = threat_level(world)
    r_gap = research_gap(world)
    pop, capacity = population_info(world)
    food_ticks = food_days(world)
    phase = determine_phase(world, counts, food_ticks, pop)
    world.state.meta["colony_phase"] = int(phase)
    desired_farms = desired_farm_count(world, pop, food_ticks)
    world.state.meta["desired_farms_calc"] = desired_farms
    world.state.meta["food_ticks"] = food_ticks

    unfinished = sum(1 for s in em.get_component_store("ConstructionSite").values() if not s.complete)
    world.state.meta["active_sites"] = max(unfinished,1)

    storage_pressure = world.state.meta.get("storage_pressure",0.0)
    hauling_backlog = world.state.meta.get("hauling_backlog",0.0)

    # Emergency housing (includes pending capacity)
    pending_caps = world.state.meta.get("pending_housing_capacity",0)
    housing_buffer = world.state.meta.get("housing_buffer",1)
    if pop + housing_buffer > capacity + pending_caps:
        # choose appropriate housing def
        hdef = select_housing_def(pop, food_ticks)
        if governor_can_queue(world,hdef,"housing",pop,desired_farms,
                               counts.get("farm_plot",0)+counts.get("FarmPlot",0),
                               food_ticks):
            create_construction_site(world, hdef, def_id=hdef)
            world.record_decision({
                "tick": world.state.tick,
                "type":"LeaderDecisionEmergencyHousing",
                "options":[{"target":"force_housing"}],
                "chosen": hdef,
                "action_type":"build_def"
            })
            leader.last_decision_tick = world.state.tick
            return

    # Forced early portal
    if world.state.portal_count == 0:
        portal_pending = any(s.meta.get("def_id","").startswith("portal_gate") for s in em.get_component_store("ConstructionSite").values())
        if not portal_pending and capacity >= pop and food_ticks >= min(350, world.state.meta.get("phase_food_min",800)*0.5) and resources.get("wood_log",0)>=40:
            if governor_can_queue(world,"portal_gate_t1","portal",pop,desired_farms,
                                   counts.get("farm_plot",0)+counts.get("FarmPlot",0),
                                   food_ticks):
                create_construction_site(world, "portal_gate_t1", def_id="portal_gate_t1")
                world.record_decision({
                    "tick": world.state.tick,
                    "type":"LeaderDecisionForcePortal",
                    "options":[{"target":"portal_gate_t1"}],
                    "chosen":"portal_gate_t1",
                    "action_type":"build_def"
                })
                leader.last_decision_tick = world.state.tick
                return

    options: List[Dict[str, Any]] = []
    for b in PRIORITY_ORDER:
        scored = score_build_option(world, b, phase, resources, counts, morale_avg,
                                    predators, r_gap, food_ticks, pop, capacity,
                                    desired_farms, storage_pressure, hauling_backlog)
        if scored:
            # governor re-check for legacy farm
            if b == "FarmPlot":
                if not governor_can_queue(world,"FarmPlot","farm",pop,desired_farms,
                                           counts.get("farm_plot",0)+counts.get("FarmPlot",0),
                                           food_ticks):
                    continue
            options.append(scored)

    auto_research = world.state.meta.get("auto_research", False)
    if auto_research and phase >= ColonyPhase.RESEARCH:
        purch = auto_select_research(world)
        if purch:
            options.append({
                "type":"research",
                "target": purch["id"],
                "score": 0.35,
                "factors":{},
                "cost": {"ResearchPoints": purch["cost"]}
            })

    options.sort(key=lambda x: x["score"], reverse=True)
    if not options:
        leader.last_decision_tick = world.state.tick
        return
    chosen = options[0]
    entry = {
        "tick": world.state.tick if tick is None else tick,
        "type": "LeaderDecisionLegacy",
        "options": [{"target": o["target"], "score": round(o["score"],3)} for o in options[:6]],
        "chosen": chosen["target"],
        "action_type": chosen["type"]
    }
    world.record_decision(entry)
    leader.last_decision_tick = world.state.tick
    if world.state.intervention_mode:
        leader.intervention_pending.append(entry)
    else:
        enact_decision(world, chosen)

def select_housing_def(pop: int, food_ticks: float) -> str:
    if pop < 6: return "hut"
    if pop < 10: return "cabin"
    if pop < 16: return "lodge"
    if pop < 26: return "dormitory"
    return "insulated_house" if food_ticks > 300 else "dormitory"

def enact_decision(world: World, option: Dict[str, Any]):
    t = option["type"]
    if t == "build":
        create_construction_site(world, option["target"])
    elif t == "research":
        apply_research_by_id(world, option["target"])
    elif t == "expedition":
        loadout = auto_expedition_loadout(world)
        seed = _first_portal_seed(world)
        if seed is not None:
            launch_expedition(world, seed, loadout=loadout)
            world.state.meta["expedition_next_tick"] = world.state.tick + 450
        else:
            world.record_event({"tick": world.state.tick, "type":"ExpeditionAbort", "detail":"NoPortal"})
    elif t == "mine":
        ops = world.state.meta.get("pending_mine_ops", [])
        if not ops: return
        op = ops.pop(0)
        create_construction_site(world, "Mine", deposit_op=op)

def _first_portal_seed(world: World):
    gates = world.entities.get_component_store("PortalGate")
    if not gates: return None
    return next(iter(gates.values())).seed

def auto_expedition_loadout(world: World):
    roles = world.entities.get_component_store("Role")
    scouts = any(r.type=="Scout" for r in roles.values())
    guards = any(r.type in ("Soldier","Guard") for r in roles.values())
    pool = aggregate_resources(world)
    food_total = sum(pool.get(k,0) for k in FOOD_KEYS)
    supplies = min(4, int(food_total//12))
    return {"guards": 1 if guards else 0,"scouts": 1 if scouts else 0,"supplies": supplies}

def create_construction_site(world: World, btype: str, deposit_op: Optional[Dict[str,Any]]=None, def_id: Optional[str]=None):
    em = world.entities
    leader_pos = None
    pos_store = em.get_component_store("Position")
    role_store = em.get_component_store("Role")
    for eid, role in role_store.items():
        if role.type == "Leader":
            leader_pos = pos_store.get(eid)
            if leader_pos: break
    if not leader_pos: return
    used = {(p.x,p.y) for p in pos_store.values()}
    found = None
    for radius in range(2,8):
        for dx in range(-radius,radius+1):
            for dy in (-radius,radius):
                x = leader_pos.x + dx
                y = leader_pos.y + dy
                if world.grid.in_bounds(x,y) and world.grid.walkable(x,y) and (x,y) not in used:
                    found = (x,y); break
            if found: break
        if found: break
    if not found:
        found = (min(world.grid.width-1, leader_pos.x+2),
                 min(world.grid.height-1, leader_pos.y+2))
    from ..util.id_gen import GLOBAL_ID_GEN
    site_id = em.create(GLOBAL_ID_GEN.next())
    from ..ecs.components import Position as CPos, Renderable, ConstructionSite as CS
    em.add_component(site_id,"Position",CPos(found[0],found[1]))
    em.add_component(site_id,"Renderable",Renderable("site"))
    if def_id:
        defs = world.state.meta.get("defs",{})
        bmap = defs.get("buildings",{})
        bdef = bmap.get(def_id)
        if not bdef: return
        cost_map = {c["item"]: c["amount"] for c in bdef.get("cost",[])}
        em.add_component(site_id,"ConstructionSite",CS(def_id, needed=cost_map, meta={"def_id":def_id}))
    else:
        cost = BUILD_COSTS.get(btype, {"wood_log":25})
        meta_obj = {}
        if btype == "Mine" and deposit_op:
            meta_obj["deposit"] = deposit_op
        em.add_component(site_id,"ConstructionSite",CS(btype, needed=cost, meta=meta_obj))
        set_build_cooldown(world, btype, first_portal=(btype=="PortalGate" and world.state.portal_count==0))

__all__ = [
    "leader_decide",
    "load_research_tree",
    "apply_research_by_id",
    "create_construction_site",
    "evaluate_colony_metrics",
    "suggest_build_targets",
    "leader_build_def_step"
]