from dataclasses import dataclass, field
from typing import Dict, Any
import random
from .entity_manager import EntityManager
from ..util.id_gen import GLOBAL_ID_GEN
from .components import (
    Position, Renderable, Role, ResourceInventory, TaskAgent, Needs,
    ResourceNode, Building, LeaderAI
)
from ..config import MAX_PORTALS

@dataclass
class WorldState:
    tick: int = 0
    seed: int = 0
    portal_count: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)
    intervention_mode: bool = False
    events_active: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    decision_feed: Dict[str, Any] = field(default_factory=list)
    event_feed: Dict[str, Any] = field(default_factory=list)
    expedition_feed: Dict[str, Any] = field(default_factory=list)

class GridMap:
    def __init__(self, w: int, h: int, seed: int):
        self.width = w
        self.height = h
        random.seed(seed)
        self.tiles = [[{"walk": True, "type": "snow"} for _ in range(h)] for _ in range(w)]
        for _ in range(int(w * h * 0.03)):
            rx = random.randint(0, w - 1)
            ry = random.randint(0, h - 1)
            self.tiles[rx][ry]["walk"] = False
            self.tiles[rx][ry]["type"] = "rock"

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        return self.tiles[x][y]["walk"]

    def neighbors(self, x: int, y: int):
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if self.walkable(nx, ny):
                yield nx, ny

class World:
    def __init__(self, seed: int):
        self.state = WorldState(seed=seed)
        self.entities = EntityManager()
        self.grid = GridMap(40, 30, seed)
        self.rng = random.Random(seed)
        self._hash_cache: Dict[int, int] = {}

    def bootstrap(self):
        leader_id = self.entities.create(GLOBAL_ID_GEN.next())
        self.entities.add_component(leader_id, "Position", Position(5, 5))
        self.entities.add_component(leader_id, "Renderable", Renderable("npc_leader"))
        self.entities.add_component(leader_id, "Role", Role("Leader"))
        self.entities.add_component(leader_id, "ResourceInventory", ResourceInventory(capacity=80, stored={"Food": 20, "WoodCold": 30}))
        self.entities.add_component(leader_id, "TaskAgent", TaskAgent())
        self.entities.add_component(leader_id, "Needs", Needs())
        self.entities.add_component(leader_id, "LeaderAI", LeaderAI())
        for i in range(6):
            wid = self.entities.create(GLOBAL_ID_GEN.next())
            self.entities.add_component(wid, "Position", Position(7 + i, 7))
            self.entities.add_component(wid, "Renderable", Renderable("npc_worker"))
            self.entities.add_component(wid, "Role", Role("Worker"))
            self.entities.add_component(wid, "TaskAgent", TaskAgent())
            self.entities.add_component(wid, "Needs", Needs())
            self.entities.add_component(wid, "ResourceInventory", ResourceInventory(capacity=30, stored={}))
        for _ in range(12):
            rx, ry = self.rng.randint(0, self.grid.width - 1), self.rng.randint(0, self.grid.height - 1)
            if not self.grid.walkable(rx, ry):
                continue
            rid = self.entities.create(GLOBAL_ID_GEN.next())
            self.entities.add_component(rid, "Position", Position(rx, ry))
            self.entities.add_component(rid, "Renderable", Renderable("wood"))
            self.entities.add_component(rid, "ResourceNode", ResourceNode("WoodCold", self.rng.randint(30, 60)))
        store_id = self.entities.create(GLOBAL_ID_GEN.next())
        self.entities.add_component(store_id, "Position", Position(4, 5))
        self.entities.add_component(store_id, "Renderable", Renderable("storage"))
        self.entities.add_component(store_id, "Building", Building("Storage"))
        heat_id = self.entities.create(GLOBAL_ID_GEN.next())
        self.entities.add_component(heat_id, "Position", Position(6, 5))
        self.entities.add_component(heat_id, "Renderable", Renderable("heat"))
        self.entities.add_component(heat_id, "Building", Building("HeatStation"))
        self.state.meta["bootstrap_complete"] = True

    def can_build_portal(self) -> bool:
        return self.state.portal_count < MAX_PORTALS

    def record_decision(self, entry):
        feed = self.state.decision_feed
        feed.append(entry)
        while len(feed) > 50:
            feed.pop(0)

    def record_event(self, entry):
        feed = self.state.event_feed
        feed.append(entry)
        while len(feed) > 50:
            feed.pop(0)

    def record_expedition(self, entry):
        feed = self.state.expedition_feed
        feed.append(entry)
        while len(feed) > 50:
            feed.pop(0)