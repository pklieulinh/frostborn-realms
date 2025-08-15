from ..ecs.world import World

def portal_upgrade_system(world: World):
    if world.state.meta.get("pregame", False):
        return
    em = world.entities
    portals = em.get_component_store("PortalGate")
    if not portals:
        return
    # simple upgrade: if have ModulePortalStabilizer item (as resource) consume to add +0.02 quality
    invs = em.get_component_store("ResourceInventory")
    target_inv = None
    for eid, inv in invs.items():
        target_inv = inv
        break
    if not target_inv:
        return
    count = target_inv.stored.get("ModulePortalStabilizer", 0)
    if count <= 0:
        return
    upgraded = 0
    for pid, pg in portals.items():
        if pg.quality < 1.0 and count > 0:
            pg.quality += 0.02
            count -= 1
            upgraded += 1
    target_inv.stored["ModulePortalStabilizer"] = count
    if upgraded > 0:
        world.record_event({"tick": world.state.tick, "type": "PortalUpgraded", "detail": f"{upgraded} portals improved"})