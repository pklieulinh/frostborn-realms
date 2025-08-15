from ..ecs.world import World
from ..ecs.components import HeatEmitter, Position, ThermalStatus, Needs

def heat_system(world: World):
    em = world.entities
    emitters = em.get_component_store("HeatEmitter")
    pos_store = em.get_component_store("Position")
    if not emitters:
        world.state.meta["heat_map"] = None
        return
    g = world.grid
    # Build heat map
    heat_map = [[0.0 for _ in range(g.height)] for _ in range(g.width)]
    for eid, emitter in emitters.items():
        if eid not in pos_store:
            continue
        p = pos_store[eid]
        r = emitter.radius
        base_output = emitter.output
        for x in range(max(0, p.x - r), min(g.width, p.x + r + 1)):
            dx = abs(x - p.x)
            max_dy = r - dx
            for y in range(max(0, p.y - max_dy), min(g.height, p.y + max_dy + 1)):
                dy = abs(y - p.y)
                dist = dx + dy
                if dist > r:
                    continue
                # linear falloff
                contrib = max(0.0, base_output * (1 - dist / (r + 0.0001)))
                heat_map[x][y] += contrib
    # Normalize to 0..255 for rendering
    max_val = 0.0
    for x in range(g.width):
        for y in range(g.height):
            if heat_map[x][y] > max_val:
                max_val = heat_map[x][y]
    scale = 255.0 / max_val if max_val > 0 else 0
    heat_map_int = [[int(min(255, heat_map[x][y] * scale)) for y in range(g.height)] for x in range(g.width)]
    world.state.meta["heat_map"] = heat_map_int
    # Update ThermalStatus + Needs deficit logic
    ts_store = em.get_component_store("ThermalStatus")
    needs_store = em.get_component_store("Needs")
    for eid in list(ts_store.keys()):
        if eid not in pos_store:
            continue
        p = pos_store[eid]
        hv = heat_map_int[p.x][p.y]
        ts = ts_store[eid]
        ts.heat_value = hv
        comfortable_threshold = 90
        ts.comfortable = hv >= comfortable_threshold
        # Adjust deficit_heat_ticks based on comfort
        if eid in needs_store:
            n = needs_store[eid]
            if ts.comfortable:
                n.deficit_heat_ticks = max(0, n.deficit_heat_ticks - 1)
            else:
                n.deficit_heat_ticks += 1