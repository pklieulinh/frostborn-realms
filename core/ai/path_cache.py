from collections import OrderedDict
from .pathfinding import a_star

class PathCache:
    def __init__(self, limit=256):
        self.limit = limit
        self.store = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.enabled = True
    def get_path(self, grid, start, goal):
        if not self.enabled:
            self.misses += 1
            return a_star(grid, start, goal)
        key = (start, goal, getattr(grid, "rev", 0))
        if key in self.store:
            self.hits += 1
            self.store.move_to_end(key)
            return list(self.store[key])
        self.misses += 1
        path = a_star(grid, start, goal)
        self.store[key] = path
        if len(self.store) > self.limit:
            self.store.popitem(last=False)
        return list(path)
    def hit_rate(self):
        total = self.hits + self.misses
        if total == 0: return 0.0
        return self.hits / total
    def clear(self):
        self.store.clear()
        self.hits = 0
        self.misses = 0

GLOBAL_PATH_CACHE = PathCache()