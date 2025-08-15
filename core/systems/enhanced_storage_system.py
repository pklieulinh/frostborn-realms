from ..ecs.world import World
from ..ecs.components import ResourceInventory, Storage, Building, Position
import random

# Enhanced storage priorities and logistics
STORAGE_PRIORITIES = {
    # Food storage priorities
    "food": {
        "categories": ["FoodRaw", "Food", "consumable"],
        "decay_rate": 0.02,  # 2% decay per day for perishables
        "priority_buildings": ["granary", "cold_storage", "freezer", "silo"],
        "temperature_bonus": {"cold_storage": 0.5, "freezer": 0.1}  # Reduced decay
    },
    # Material storage
    "materials": {
        "categories": ["Raw", "Material", "refined", "component"],
        "decay_rate": 0.0,  # No decay
        "priority_buildings": ["storage_crate", "warehouse", "storage_cabinet"],
        "organization_bonus": {"warehouse": 1.5, "storage_cabinet": 1.2}  # Capacity multiplier
    },
    # Weapons and equipment
    "equipment": {
        "categories": ["Tool", "Weapon", "Apparel", "Jewelry"],
        "decay_rate": 0.001,  # Very slow decay from rust/wear
        "priority_buildings": ["armory_basic", "armory_vault", "equipment_rack"],
        "maintenance_bonus": {"armory_vault": 0.1}  # Reduced decay
    },
    # Valuable items
    "valuables": {
        "categories": ["Special", "artifact", "arcane", "Art"],
        "decay_rate": 0.0,
        "priority_buildings": ["armory_vault", "storage_cabinet"],
        "security_bonus": {"armory_vault": 2.0}  # Theft protection
    }
}

# Resource spoilage and aging system
RESOURCE_AGING = {
    "MeatRaw": {"max_age": 100, "spoil_product": None},
    "MeatFish": {"max_age": 80, "spoil_product": None},
    "MeatPoultry": {"max_age": 90, "spoil_product": None},
    "VegetablesLeafy": {"max_age": 60, "spoil_product": None},
    "VegetablesFruit": {"max_age": 120, "spoil_product": None},
    "BerriesFrozen": {"max_age": 200, "spoil_product": None},
    "DrinkWine": {"max_age": 1000, "improve_with_age": True},
    "DrinkSpirits": {"max_age": 2000, "improve_with_age": True},
}

# Auto-distribution rules for efficient logistics
AUTO_DISTRIBUTION = {
    "food_to_kitchen": {
        "from_items": ["MeatRaw", "MeatFish", "VegetablesRoot", "GrainWheat"],
        "to_buildings": ["kitchen_basic", "kitchen_advanced", "restaurant"],
        "max_distance": 20,
        "priority": 8
    },
    "materials_to_workshops": {
        "from_items": ["IngotIron", "IngotSteel", "PlankWood", "LeatherTanned"],
        "to_buildings": ["smithy_basic", "smithy_advanced", "tailor_workshop"],
        "max_distance": 15,
        "priority": 7
    },
    "ores_to_foundry": {
        "from_items": ["OreIron", "OreCopper", "OreTin", "Coal"],
        "to_buildings": ["foundry_basic", "foundry_advanced", "blast_furnace"],
        "max_distance": 25,
        "priority": 6
    }
}

def enhanced_storage_system(world: World):
    """
    Enhanced storage system with decay, auto-distribution, and intelligent logistics
    """
    if world.state.meta.get("pregame", False):
        return
    
    em = world.entities
    storages = em.get_component_store("Storage")
    buildings = em.get_component_store("Building")
    inventories = em.get_component_store("ResourceInventory")
    positions = em.get_component_store("Position")
    
    # Process resource aging and decay
    process_resource_aging(world, inventories)
    
    # Auto-distribute resources based on need
    auto_distribute_resources(world, inventories, buildings, positions)
    
    # Optimize storage efficiency
    optimize_storage_efficiency(world, storages, buildings)

def process_resource_aging(world: World, inventories):
    """
    Handle resource aging, spoilage, and improvement over time
    """
    tick = world.state.tick
    
    for eid, inv in inventories.items():
        if not hasattr(inv, 'resource_ages'):
            inv.resource_ages = {}
            
        resources_to_remove = []
        resources_to_improve = []
        
        for resource_id, amount in inv.stored.items():
            if resource_id in RESOURCE_AGING:
                aging_info = RESOURCE_AGING[resource_id]
                
                # Age the resource
                current_age = inv.resource_ages.get(resource_id, 0)
                inv.resource_ages[resource_id] = current_age + 1
                
                # Check for spoilage
                if current_age > aging_info["max_age"]:
                    spoil_amount = min(amount, max(1, amount // 10))  # Spoil 10% or 1, whichever is more
                    inv.stored[resource_id] -= spoil_amount
                    
                    if inv.stored[resource_id] <= 0:
                        resources_to_remove.append(resource_id)
                    
                    world.record_event({
                        "tick": tick,
                        "type": "ResourceSpoiled",
                        "resource": resource_id,
                        "amount": spoil_amount,
                        "entity": eid
                    })
                
                # Check for improvement with age (wine, spirits)
                elif aging_info.get("improve_with_age") and current_age > aging_info["max_age"] // 4:
                    if random.random() < 0.01:  # 1% chance per tick after 1/4 max age
                        quality_bonus = min(amount, 1)
                        if quality_bonus > 0:
                            resources_to_improve.append((resource_id, quality_bonus))
        
        # Remove spoiled resources
        for resource_id in resources_to_remove:
            if resource_id in inv.stored:
                del inv.stored[resource_id]
            if resource_id in inv.resource_ages:
                del inv.resource_ages[resource_id]
        
        # Handle quality improvements
        for resource_id, improvement in resources_to_improve:
            # Could create higher quality versions or provide bonuses
            pass

def auto_distribute_resources(world: World, inventories, buildings, positions):
    """
    Automatically distribute resources to where they're needed most
    """
    if world.state.tick % 20 != 0:  # Run every 20 ticks to reduce performance impact
        return
    
    em = world.entities
    
    # Find all storage locations
    storage_locations = {}
    workshop_locations = {}
    
    for eid, building in buildings.items():
        pos = positions.get(eid)
        if not pos:
            continue
            
        building_id = building.building_id
        
        # Categorize buildings
        if any(tag in building.get("tags", []) for tag in ["store_", "storage"]):
            storage_locations[eid] = {
                "building_id": building_id,
                "position": pos,
                "inventory": inventories.get(eid)
            }
        elif any(tag in building.get("tags", []) for tag in ["prod_", "food_"]):
            workshop_locations[eid] = {
                "building_id": building_id,
                "position": pos,
                "inventory": inventories.get(eid)
            }
    
    # Execute distribution rules
    for rule_name, rule in AUTO_DISTRIBUTION.items():
        execute_distribution_rule(world, rule, storage_locations, workshop_locations, positions)

def execute_distribution_rule(world, rule, storage_locations, workshop_locations, positions):
    """
    Execute a specific auto-distribution rule
    """
    # Find sources (storages with required items)
    sources = []
    for storage_id, storage_info in storage_locations.items():
        if not storage_info["inventory"]:
            continue
            
        for item_id in rule["from_items"]:
            amount = storage_info["inventory"].stored.get(item_id, 0)
            if amount > 5:  # Only distribute if we have excess (>5)
                sources.append({
                    "entity_id": storage_id,
                    "item_id": item_id,
                    "amount": amount - 2,  # Keep 2 as reserve
                    "position": storage_info["position"]
                })
    
    # Find destinations (workshops that need these items)
    destinations = []
    for workshop_id, workshop_info in workshop_locations.items():
        if workshop_info["building_id"] in rule["to_buildings"]:
            inv = workshop_info["inventory"]
            if not inv:
                continue
                
            for item_id in rule["from_items"]:
                current_amount = inv.stored.get(item_id, 0)
                if current_amount < 10:  # Need more if less than 10
                    destinations.append({
                        "entity_id": workshop_id,
                        "item_id": item_id,
                        "needed": 10 - current_amount,
                        "position": workshop_info["position"]
                    })
    
    # Match sources to destinations
    for dest in destinations:
        best_source = None
        best_distance = float('inf')
        
        for source in sources:
            if source["item_id"] != dest["item_id"]:
                continue
                
            # Calculate distance
            dx = abs(source["position"].x - dest["position"].x)
            dy = abs(source["position"].y - dest["position"].y)
            distance = dx + dy
            
            if distance <= rule["max_distance"] and distance < best_distance:
                best_distance = distance
                best_source = source
        
        # Transfer resources
        if best_source:
            transfer_amount = min(best_source["amount"], dest["needed"])
            if transfer_amount > 0:
                # Remove from source
                source_inv = storage_locations[best_source["entity_id"]]["inventory"]
                source_inv.stored[best_source["item_id"]] -= transfer_amount
                
                # Add to destination
                dest_inv = workshop_locations[dest["entity_id"]]["inventory"]
                dest_inv.stored[dest["item_id"]] = dest_inv.stored.get(dest["item_id"], 0) + transfer_amount
                
                # Update source amount for future transfers
                best_source["amount"] -= transfer_amount
                
                world.record_event({
                    "tick": world.state.tick,
                    "type": "AutoDistribution",
                    "rule": rule,
                    "item": dest["item_id"],
                    "amount": transfer_amount,
                    "from": best_source["entity_id"],
                    "to": dest["entity_id"]
                })

def optimize_storage_efficiency(world: World, storages, buildings):
    """
    Optimize storage efficiency based on storage type and contents
    """
    for storage_id, storage in storages.items():
        building = buildings.get(storage_id)
        if not building:
            continue
            
        building_id = building.building_id
        
        # Apply storage bonuses based on building type
        base_capacity = getattr(storage, 'base_capacity', 100)
        efficiency_bonus = 1.0
        
        # Check for organization bonuses
        for category, rules in STORAGE_PRIORITIES.items():
            if building_id in rules["priority_buildings"]:
                bonus = rules.get("organization_bonus", {}).get(building_id, 1.0)
                efficiency_bonus = max(efficiency_bonus, bonus)
        
        # Apply the efficiency bonus
        storage.capacity = int(base_capacity * efficiency_bonus)
        
        # Handle overflow if needed
        current_total = sum(storage.stored.values()) if hasattr(storage, 'stored') else 0
        if current_total > storage.capacity:
            # Need to handle overflow - could trigger hauling jobs or warnings
            pass