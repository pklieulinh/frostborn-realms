from ..ecs.world import World
from ..ecs.components import Traits, Health
from ..characters.traits import load_trait_catalog
import math

def trait_effects_system(world: World):
    # Catalog cached
    if "trait_catalog" not in world.state.meta:
        world.state.meta["trait_catalog"] = load_trait_catalog()
    catalog = world.state.meta["trait_catalog"]
    em = world.entities
    traits_store = em.get_component_store("Traits")
    health_store = em.get_component_store("Health")
    entity_mods = world.state.meta.setdefault("entity_mods", {})
    research_points_accum = 0.0
    for eid, tr_comp in traits_store.items():
        mods = {
            "gather_speed":0.0,
            "build_speed":0.0,
            "expedition_risk_mult":0.0,
            "morale_decay":0.0,
            "hp_max_mult":0.0,
            "research_points":0.0,
            "aura_morale":0.0
        }
        for tid in tr_comp.items:
            data = catalog.get(tid)
            if not data:
                continue
            eff = data.get("effects",{})
            for k,v in eff.items():
                if k in mods and isinstance(v,(int,float)):
                    mods[k] += v
        # apply hp max change
        if eid in health_store and mods["hp_max_mult"] != 0.0:
            h = health_store[eid]
            base_max = h.max_hp / (1 + mods["hp_max_mult"]) if (1+mods["hp_max_mult"])!=0 else h.max_hp
            # recalc new max
            new_max = int(math.ceil(base_max * (1 + mods["hp_max_mult"])))
            new_max = max(1, new_max)
            # Adjust hp proportionally
            ratio = h.hp / h.max_hp if h.max_hp>0 else 1.0
            h.max_hp = new_max
            h.hp = min(new_max, int(round(ratio * new_max)))
        if mods["research_points"]>0:
            research_points_accum += mods["research_points"]
        entity_mods[eid] = mods
    # Add accumulated research points
    if research_points_accum>0:
        meta = world.state.meta
        meta["research_points"] = meta.get("research_points",0.0) + research_points_accum