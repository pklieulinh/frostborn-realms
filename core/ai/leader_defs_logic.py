from typing import Dict, Any, List, Optional
from ..ecs.world import World
import math

# Priority layers controlled by metrics:
# food -> housing -> equipment (cold) -> recreation -> expansion/logistics -> portal

CRITICAL_ITEMS = ["wood_log","stone_block","iron_ingot","hide_tanned","cloth_roll","crystal_frost"]

def evaluate_colony_metrics(world: World) -> Dict[str,float]:
    meta = world.state.meta
    res = meta.get("resources_global", {})
    pop = meta.get("population",0)
    food_raw = sum(res.get(k,0) for k in ("food_ration","hearty_meal","grain_raw","raw_meat","berry_frozen"))
    food_need_rate = max(1, pop) * 0.5  # abstract
    food_ticks = food_raw / food_need_rate if food_need_rate>0 else 999
    housing_cap = meta.get("housing_capacity",0)
    housing_deficit = max(0, pop - housing_cap)
    apparel_warm = sum(res.get(k,0) for k in ("parka_fur","coat_leather","boots_fur","gloves_wool","hat_fur"))
    equip_cold_ratio = apparel_warm / max(1,pop*2.2)  # need ~2.2 warm pieces per colonist
    morale_avg = meta.get("morale_avg",0.8)
    recreation_need = 1.0 - min(1.0, morale_avg/1.0)
    distinct_resources = sum(1 for c in CRITICAL_ITEMS if res.get(c,0)>0)
    portal_need = 1 if distinct_resources < len(CRITICAL_ITEMS)//2 else 0
    expansion_need = 0.0
    if meta.get("storage_pressure",0)>0.8:
        expansion_need += 0.6
    if pop>8 and housing_deficit==0 and food_ticks>40 and equip_cold_ratio>0.6:
        expansion_need += 0.4
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
    meta = world.state.meta
    pop = meta.get("population",0)

    choices = []

    # FOOD
    if metrics["food_ticks"] < 30:
        for bid in ("farm_plot","greenhouse_basic","kitchen_basic","smokehouse"):
            if bid in buildings:
                score = (30 - metrics["food_ticks"])/30 + buildings[bid].get("tier",1)*0.05
                choices.append({"def_id":bid,"layer":"food","score":score})
    # HOUSING
    if metrics["housing_deficit"]>0:
        housing_chain = ["hut","cabin","lodge","dormitory","insulated_house"]
        for bid in housing_chain:
            if bid in buildings:
                tier = buildings[bid]["tier"]
                score = 0.9 + tier*0.1 + metrics["housing_deficit"]*0.15
                choices.append({"def_id":bid,"layer":"housing","score":score})

    # EQUIPMENT (cold)
    if metrics["equip_cold_ratio"] < 0.75 and metrics["food_ticks"] > 25 and metrics["housing_deficit"]==0:
        for bid in ("tailor_workshop","tannery","loom","forge_smithy"):
            if bid in buildings:
                gap = 0.75 - metrics["equip_cold_ratio"]
                score = 0.6 + gap*1.2
                choices.append({"def_id":bid,"layer":"equipment","score":score})

    # RECREATION
    if metrics["recreation_need"] > 0.25 and metrics["food_ticks"]>25 and metrics["housing_deficit"]==0:
        for bid in ("hearth_hall","music_stand","library_corner","shrine_small","bathhouse"):
            if bid in buildings:
                score = 0.4 + metrics["recreation_need"]*0.9
                choices.append({"def_id":bid,"layer":"recreation","score":score})

    # EXPANSION / LOGISTICS
    if metrics["expansion_need"] > 0.1:
        for bid in ("storage_crate","granary","cold_storage","stockyard","watchtower_wood","palisade_segment","stone_wall","armory_store"):
            if bid in buildings:
                score = 0.3 + metrics["expansion_need"]
                choices.append({"def_id":bid,"layer":"expansion","score":score})

    # PORTAL
    if metrics["portal_need"]>0 and metrics["food_ticks"]>15:
        for bid in ("portal_gate_t1","portal_gate_t2"):
            if bid in buildings:
                score = 0.55 + metrics["portal_need"]*0.5
                choices.append({"def_id":bid,"layer":"portal","score":score})

    # Tiebreak by tier preference early game
    for c in choices:
        bdef = buildings.get(c["def_id"],{})
        c["score"] += (5 - bdef.get("tier",1))*0.02  # prefer lower tier early
    return choices