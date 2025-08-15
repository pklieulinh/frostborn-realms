from ..ecs.world import World
from ..ecs.components import WorkIntent, ResourceNode, ResourceInventory, ActivityState, Position, Skills
import random

# Enhanced gathering multipliers for balanced progression
GATHER_MULTIPLIERS = {
    "WoodCold": 1.5,
    "WoodHardwood": 1.3,
    "WoodIronbark": 1.2,
    "Stone": 1.4,
    "StoneGranite": 1.3,
    "StoneMarble": 1.1,
    "OreIron": 1.3,
    "OreCopper": 1.3,
    "OreTin": 1.3,
    "OreGold": 1.2,
    "OreSilver": 1.2,
    "Coal": 1.4,
    "CrystalFrost": 1.1,
    "CrystalFire": 1.1
}

# Skill-based gathering bonuses
SKILL_BONUSES = {
    "mining": ["OreIron", "OreCopper", "OreTin", "OreGold", "OreSilver", "Stone", "StoneGranite", "Coal"],
    "forestry": ["WoodCold", "WoodHardwood", "WoodIronbark"],
    "research": ["CrystalFrost", "CrystalFire", "RuneStone"],
    "crafting": ["Stone", "Clay", "Sand"]
}

def gather_balance_system(world: World):
    """
    Enhanced gathering system with skill bonuses, tool quality effects, and balanced progression
    """
    if world.state.meta.get("pregame", False):
        return
    
    meta = world.state.meta
    em = world.entities
    nodes = em.get_component_store("ResourceNode")
    intents = em.get_component_store("WorkIntent")
    invs = em.get_component_store("ResourceInventory")
    acts = em.get_component_store("ActivityState")
    skills_store = em.get_component_store("Skills")
    
    for eid, intent in intents.items():
        if intent.job != "Gatherer":
            continue
            
        act = acts.get(eid)
        if not act or act.state != "Working":
            continue
            
        target_id = act.target
        if not target_id or target_id not in nodes:
            continue
            
        node = nodes[target_id]
        if node.amount <= 0:
            continue
            
        # Base gathering multiplier
        base_mult = GATHER_MULTIPLIERS.get(node.rtype, 1.0)
        
        # Skill-based bonus
        skill_bonus = 0.0
        skills = skills_store.get(eid)
        if skills:
            for skill_name, resource_types in SKILL_BONUSES.items():
                if node.rtype in resource_types:
                    skill_level = getattr(skills, skill_name, 0)
                    skill_bonus += skill_level * 0.1  # 10% per skill level
                    break
        
        # Quality and tool bonuses (simplified)
        tool_bonus = random.uniform(0.0, 0.3)  # Random tool quality effect
        
        # Calculate final bonus
        total_multiplier = base_mult + skill_bonus + tool_bonus
        bonus = max(0, int(random.uniform(0.5, 1.5) * (total_multiplier - 1.0)))
        
        if bonus <= 0:
            continue
            
        # Apply gathering bonus
        inv = invs.get(eid)
        if inv:
            inv.stored[node.rtype] = inv.stored.get(node.rtype, 0) + bonus
            
        # Reduce node resources
        node.amount = max(0, node.amount - bonus)
        
        # Record event for analytics
        world.record_event({
            "tick": world.state.tick,
            "type": "GatherBonus",
            "rtype": node.rtype,
            "bonus": bonus,
            "multiplier": total_multiplier,
            "skill_bonus": skill_bonus,
            "tool_bonus": tool_bonus
        })