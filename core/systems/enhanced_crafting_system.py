from ..ecs.world import World
from ..ecs.components import ResourceInventory, Building, CraftingStation, WorkIntent, ActivityState, Skills
import random

# Enhanced crafting recipes for expanded content
CRAFTING_RECIPES = {
    # === BASIC PROCESSING === #
    "refine_wood": {
        "input": {"WoodCold": 3},
        "output": {"PlankWood": 2},
        "skill_req": {"crafting": 1},
        "time": 20,
        "station": ["workbench_crude", "workbench_crafting"]
    },
    "refine_hardwood": {
        "input": {"WoodHardwood": 2},
        "output": {"PlankHardwood": 2},
        "skill_req": {"crafting": 3},
        "time": 30,
        "station": ["workbench_crafting", "carpenter_shop"]
    },
    "make_bricks": {
        "input": {"Clay": 4, "WoodCold": 1},
        "output": {"BrickClay": 3},
        "skill_req": {"crafting": 2},
        "time": 25,
        "station": ["kiln"]
    },
    "make_glass": {
        "input": {"Sand": 3, "Coal": 1},
        "output": {"Glass": 2},
        "skill_req": {"crafting": 4},
        "time": 35,
        "station": ["glassworks"]
    },
    
    # === SMELTING === #
    "smelt_iron": {
        "input": {"OreIron": 2, "Coal": 1},
        "output": {"IngotIron": 1},
        "skill_req": {"crafting": 3},
        "time": 40,
        "station": ["foundry_basic", "foundry_advanced", "blast_furnace"]
    },
    "smelt_copper": {
        "input": {"OreCopper": 2, "Coal": 1},
        "output": {"IngotCopper": 1},
        "skill_req": {"crafting": 3},
        "time": 35,
        "station": ["foundry_basic", "foundry_advanced", "blast_furnace"]
    },
    "smelt_bronze": {
        "input": {"IngotCopper": 3, "IngotTin": 1},
        "output": {"IngotBronze": 2},
        "skill_req": {"crafting": 4},
        "time": 50,
        "station": ["foundry_advanced", "blast_furnace"]
    },
    "smelt_steel": {
        "input": {"IngotIron": 3, "Coal": 2},
        "output": {"IngotSteel": 2},
        "skill_req": {"crafting": 6},
        "time": 60,
        "station": ["foundry_advanced", "blast_furnace"]
    },
    "smelt_gold": {
        "input": {"OreGold": 2, "Coal": 1},
        "output": {"IngotGold": 1},
        "skill_req": {"crafting": 5},
        "time": 45,
        "station": ["foundry_advanced", "blast_furnace"]
    },
    
    # === ADVANCED ALLOYS === #
    "make_froststeel": {
        "input": {"IngotSteel": 2, "CrystalFrost": 1},
        "output": {"AlloyFroststeel": 1},
        "skill_req": {"crafting": 8},
        "time": 80,
        "station": ["master_forge"]
    },
    "make_voidmetal": {
        "input": {"IngotMithril": 1, "CrystalVoid": 2, "EssenceVoid": 1},
        "output": {"AlloyVoidmetal": 1},
        "skill_req": {"crafting": 10},
        "time": 120,
        "station": ["master_forge"]
    },
    
    # === TEXTILES === #
    "weave_cloth_rough": {
        "input": {"FiberPlant": 4},
        "output": {"ClothRough": 2},
        "skill_req": {"crafting": 2},
        "time": 30,
        "station": ["loom_simple", "loom_advanced"]
    },
    "weave_cloth_fine": {
        "input": {"FiberCotton": 3},
        "output": {"ClothFine": 2},
        "skill_req": {"crafting": 4},
        "time": 45,
        "station": ["loom_advanced", "tailor_workshop"]
    },
    "weave_cloth_silk": {
        "input": {"FiberSilk": 2},
        "output": {"ClothSilk": 1},
        "skill_req": {"crafting": 6},
        "time": 60,
        "station": ["luxury_tailor"]
    },
    "tan_leather": {
        "input": {"HideRaw": 2, "Salt": 1},
        "output": {"LeatherTanned": 1},
        "skill_req": {"crafting": 3},
        "time": 40,
        "station": ["tannery", "leather_workshop"]
    },
    "craft_quality_leather": {
        "input": {"HideThick": 1, "Salt": 1, "HerbsMedicinal": 1},
        "output": {"LeatherQuality": 1},
        "skill_req": {"crafting": 6},
        "time": 70,
        "station": ["leather_workshop"]
    },
    
    # === TOOLS & WEAPONS === #
    "craft_iron_axe": {
        "input": {"IngotIron": 2, "PlankWood": 1},
        "output": {"iron_axe": 1},
        "skill_req": {"crafting": 4},
        "time": 50,
        "station": ["smithy_basic", "smithy_advanced"]
    },
    "craft_steel_axe": {
        "input": {"IngotSteel": 2, "PlankHardwood": 1},
        "output": {"steel_axe": 1},
        "skill_req": {"crafting": 6},
        "time": 70,
        "station": ["smithy_advanced", "master_forge"]
    },
    "craft_iron_sword": {
        "input": {"IngotIron": 3, "LeatherTanned": 1},
        "output": {"sword_short": 1},
        "skill_req": {"crafting": 5},
        "time": 60,
        "station": ["smithy_basic", "smithy_advanced"]
    },
    "craft_steel_sword": {
        "input": {"IngotSteel": 3, "LeatherQuality": 1},
        "output": {"sword_long": 1},
        "skill_req": {"crafting": 7},
        "time": 90,
        "station": ["smithy_advanced", "master_forge"]
    },
    
    # === COMPONENTS === #
    "craft_mechanical_component": {
        "input": {"IngotIron": 2, "GearIron": 1},
        "output": {"ComponentMechanical": 1},
        "skill_req": {"crafting": 5},
        "time": 45,
        "station": ["workbench_precision", "machining_table"]
    },
    "craft_advanced_component": {
        "input": {"IngotSteel": 1, "ComponentMechanical": 2, "WireCopper": 3},
        "output": {"ComponentAdvanced": 1},
        "skill_req": {"crafting": 8},
        "time": 80,
        "station": ["fabrication_bench"]
    },
    
    # === FOOD PROCESSING === #
    "cook_simple_meal": {
        "input": {"MeatRaw": 1, "VegetablesRoot": 1},
        "output": {"MealSimple": 2},
        "skill_req": {"crafting": 1},
        "time": 25,
        "station": ["kitchen_basic", "kitchen_advanced"]
    },
    "cook_fine_meal": {
        "input": {"MeatPoultry": 1, "VegetablesFruit": 1, "SpicesCommon": 1},
        "output": {"MealFine": 2},
        "skill_req": {"crafting": 3},
        "time": 40,
        "station": ["kitchen_advanced", "restaurant"]
    },
    "cook_lavish_meal": {
        "input": {"MeatExotic": 1, "VegetablesFruit": 2, "SpicesExotic": 1, "DrinkWine": 1},
        "output": {"MealLavish": 1},
        "skill_req": {"crafting": 6},
        "time": 80,
        "station": ["restaurant"]
    },
    "brew_beer": {
        "input": {"GrainBarley": 3, "HerbsMedicinal": 1},
        "output": {"DrinkWine": 2},
        "skill_req": {"crafting": 4},
        "time": 100,
        "station": ["brewery"]
    },
    "distill_spirits": {
        "input": {"GrainWheat": 4, "DrinkWine": 1},
        "output": {"DrinkSpirits": 1},
        "skill_req": {"crafting": 6},
        "time": 120,
        "station": ["distillery"]
    }
}

def enhanced_crafting_system(world: World):
    """
    Enhanced crafting system supporting complex recipes, skill requirements, and quality bonuses
    """
    if world.state.meta.get("pregame", False):
        return
    
    em = world.entities
    buildings = em.get_component_store("Building")
    crafting_stations = em.get_component_store("CraftingStation")
    intents = em.get_component_store("WorkIntent")
    invs = em.get_component_store("ResourceInventory")
    acts = em.get_component_store("ActivityState")
    skills_store = em.get_component_store("Skills")
    
    for eid, intent in intents.items():
        if intent.job != "Crafter":
            continue
            
        act = acts.get(eid)
        if not act or act.state != "Working":
            continue
            
        station_id = act.target
        if not station_id or station_id not in buildings:
            continue
            
        building = buildings[station_id]
        station = crafting_stations.get(station_id)
        if not station:
            continue
            
        # Get current recipe being crafted
        current_recipe = getattr(station, 'current_recipe', None)
        if not current_recipe or current_recipe not in CRAFTING_RECIPES:
            continue
            
        recipe = CRAFTING_RECIPES[current_recipe]
        
        # Check skill requirements
        skills = skills_store.get(eid)
        can_craft = True
        if skills and recipe.get("skill_req"):
            for skill_name, required_level in recipe["skill_req"].items():
                current_level = getattr(skills, skill_name, 0)
                if current_level < required_level:
                    can_craft = False
                    break
        
        if not can_craft:
            continue
            
        # Check if station is appropriate
        if building.building_id not in recipe.get("station", []):
            continue
            
        # Progress crafting
        progress = getattr(station, 'progress', 0)
        progress += 1
        station.progress = progress
        
        # Check if crafting is complete
        if progress >= recipe["time"]:
            # Check if we have required inputs
            inv = invs.get(eid)
            if not inv:
                continue
                
            has_inputs = True
            for input_item, required_amount in recipe["input"].items():
                current_amount = inv.stored.get(input_item, 0)
                if current_amount < required_amount:
                    has_inputs = False
                    break
            
            if not has_inputs:
                station.progress = 0  # Reset progress if inputs missing
                continue
                
            # Consume inputs
            for input_item, required_amount in recipe["input"].items():
                inv.stored[input_item] -= required_amount
                if inv.stored[input_item] <= 0:
                    del inv.stored[input_item]
                    
            # Calculate quality bonus based on skill level
            quality_bonus = 1.0
            if skills and recipe.get("skill_req"):
                for skill_name, _ in recipe["skill_req"].items():
                    skill_level = getattr(skills, skill_name, 0)
                    quality_bonus += skill_level * 0.05  # 5% per skill level above requirement
            
            # Add outputs with quality bonus
            for output_item, base_amount in recipe["output"].items():
                final_amount = int(base_amount * quality_bonus)
                final_amount = max(1, final_amount)  # At least 1
                inv.stored[output_item] = inv.stored.get(output_item, 0) + final_amount
                
            # Grant skill experience
            if skills and recipe.get("skill_req"):
                for skill_name, _ in recipe["skill_req"].items():
                    current_level = getattr(skills, skill_name, 0)
                    # Gain more XP for higher tier recipes
                    xp_gain = recipe["time"] // 10 + 1
                    setattr(skills, f"{skill_name}_xp", getattr(skills, f"{skill_name}_xp", 0) + xp_gain)
                    
            # Reset crafting progress
            station.progress = 0
            station.current_recipe = None
            
            # Record crafting event
            world.record_event({
                "tick": world.state.tick,
                "type": "CraftingComplete",
                "recipe": current_recipe,
                "crafter": eid,
                "quality_bonus": quality_bonus,
                "outputs": recipe["output"]
            })