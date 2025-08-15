from ..ecs.world import World
from ..ecs.components import ExpeditionTeam, ResourceInventory, PortalGate
import random

PHASES = [
    ("travel_out", 180),
    ("explore", 240),
    ("return", 160),
]

# biome resource weights
BIOME_TABLE = {
    "Tundra":       (["OreIron","OreCopper","OreTin","CrystalFrost"],        [34,25,18,8]),
    "CrystalCavern":(["CrystalFrost","OreIron","OrichalcumShard","OreTin"],   [30,25,10,18]),
    "SulfurVent":   (["OreCopper","OreTin","OreIron","OrichalcumShard"],     [32,22,20,10]),
    "GlacialRift":  (["CrystalFrost","OreIron","OreCopper","OreTin"],        [40,20,18,10]),
    "MycelGroves":  (["OreTin","OreCopper","OreIron","CrystalFrost"],        [30,28,20,8]),
}

def expedition_system(world: World):
    if world.state.meta.get("pregame", False): return
    teams = world.entities.get_component_store("ExpeditionTeam")
    if not teams: return
    for eid, team in list(teams.items()):
        if team.ticks_remaining > 0:
            team.ticks_remaining -= 1
            if team.ticks_remaining % 60 == 0:
                world.record_event({"tick": world.state.tick,"type":"ExpeditionPhase","id":eid,"phase":team.phase,"remain":team.ticks_remaining})
            if team.ticks_remaining == 0:
                _advance_or_finish(world, eid, team)

def _advance_or_finish(world: World, eid: int, team):
    if team.phase_index < len(PHASES)-1:
        team.phase_index += 1
        name, dur = PHASES[team.phase_index]
        team.phase = name
        team.ticks_remaining = dur
        return
    _resolve_loot(world, eid, team)

def _resolve_loot(world: World, eid: int, team):
    em = world.entities
    invs = em.get_component_store("ResourceInventory")
    target_inv = None
    for iid, inv in invs.items():
        target_inv = inv
        break
    if not target_inv:
        del em.get_component_store("ExpeditionTeam")[eid]
        return
    portals = em.get_component_store("PortalGate")
    biome = "Tundra"
    if portals:
        biome = random.choice(list(portals.values())).biome
    table = BIOME_TABLE.get(biome, BIOME_TABLE["Tundra"])
    resource_choice = random.choices(table[0], weights=table[1], k=1)[0]
    base_loot = {"FoodRation": random.randint(2,4), resource_choice: random.randint(2,5)}
    if team.loadout.get("scouts",0)>0:
        base_loot["RuneFragment"] = random.randint(0,2)
    if team.loadout.get("guards",0)>0:
        base_loot["MeatRaw"] = random.randint(1,3)
    if random.random()<0.18:
        for k in list(base_loot.keys()):
            base_loot[k] = max(0, int(base_loot[k]*0.6))
    for k,v in base_loot.items():
        if v>0:
            target_inv.stored[k] = target_inv.stored.get(k,0)+v
    world.record_event({"tick": world.state.tick,"type":"ExpeditionComplete","id": eid,"loot":base_loot,"biome":biome})
    if random.random()<0.55:
        _create_mine_opportunity(world, biome)
    del em.get_component_store("ExpeditionTeam")[eid]

def _create_mine_opportunity(world: World, biome: str):
    meta = world.state.meta
    ops = meta.setdefault("pending_mine_ops", [])
    portal_count = world.state.portal_count
    max_tier = 5 + min(5, portal_count)
    tier = random.randint(1, max_tier)
    table = BIOME_TABLE.get(biome, BIOME_TABLE["Tundra"])
    resource_choice = random.choices(table[0], weights=table[1], k=1)[0]
    base = random.randint(90,150)
    amount = base * tier
    ops.append({"resource": resource_choice, "tier": tier, "amount": amount})
    world.record_event({"tick": world.state.tick, "type":"MineOpportunity", "resource":resource_choice,"tier":tier,"amt":amount,"biome":biome})