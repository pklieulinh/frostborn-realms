from heapq import heappush, heappop

def a_star(grid, start, goal):
    if start == goal:
        return []
    open_set = []
    heappush(open_set, (0, start))
    came = {}
    g = {start: 0}
    sx, sy = start
    gx, gy = goal
    while open_set:
        _, current = heappop(open_set)
        if current == goal:
            return _reconstruct(came, current)
        cx, cy = current
        for nx, ny in ((cx+1,cy),(cx-1,cy),(cx,cy+1),(cx,cy-1)):
            if not grid.in_bounds(nx, ny): continue
            if not grid.walkable(nx, ny): continue
            ng = g[current] + 1
            if ng < g.get((nx,ny), 1e9):
                g[(nx,ny)] = ng
                came[(nx,ny)] = current
                h = abs(nx-gx)+abs(ny-gy)
                heappush(open_set, (ng + h, (nx,ny)))
    return []

def _reconstruct(came, cur):
    path = []
    while cur in came:
        path.append(cur)
        cur = came[cur]
    path.reverse()
    return path[:180]