import heapq
from typing import Dict, Tuple, List, Optional
from ..ecs.world import World

def heuristic(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(world: World, start: Tuple[int,int], goal: Tuple[int,int], limit: int = 800) -> Optional[List[Tuple[int,int]]]:
    if start == goal:
        return [start]
    open_set: List[Tuple[int, Tuple[int,int]]] = []
    heapq.heappush(open_set, (0, start))
    came: Dict[Tuple[int,int], Tuple[int,int]] = {}
    g: Dict[Tuple[int,int], int] = {start: 0}
    count = 0
    while open_set and count < limit:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came:
                current = came[current]
                path.append(current)
            path.reverse()
            return path
        for nx, ny in world.grid.neighbors(*current):
            ng = g[current] + 1
            if (nx, ny) not in g or ng < g[(nx, ny)]:
                g[(nx, ny)] = ng
                f = ng + heuristic((nx, ny), goal)
                came[(nx, ny)] = current
                heapq.heappush(open_set, (f, (nx, ny)))
        count += 1
    return None