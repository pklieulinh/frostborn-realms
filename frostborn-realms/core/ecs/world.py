from dataclasses import dataclass, field
from typing import Dict, Any
import random
from .entity_manager import EntityManager
from ..util.id_gen import GLOBAL_ID_GEN
from .components import (
    Position, Renderable, Role, ResourceInventory, TaskAgent, Needs,
    ResourceNode, Building, HeatEmitter, Health, Morale, ThermalStatus,
    CombatTag, Identity, Traits, Personality, Profession, Authority,
    EmotionState, Movement, WorkIntent, ActivityState, Dialogue,
    HousingUnit, Storage, Attributes
)
from ..config import MAX_PORTALS

NAMES = ["Arlen","Brakka","Cyra","Daren","Elwen","Faela","Gorin","Hilda","Iskar","Joran","Kaela","Lorin","Mira","Noren","Olia","Pyrr","Quen","Raska","Selva","Torin"]
PROFESSIONS = [
    ("Worker","Builder"),
    ("Worker","Lumberjack"),
    ("Scholar","Researcher"),
    ("Scout","Pathfinder"),
    ("Engineer","Builder"),
    ("Worker","General")
]

@dataclass
class WorldState:
    tick: int = 0
    seed: int = 0
    portal_count: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)
    intervention_mode: bool = False
    events_active: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    decision_feed: list = field(default_factory=list)
    event_feed: list = field(default_factory=list)
    expedition_feed: list = field(default_factory=list)

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
        if not self.in_bounds(x, y): return False
        return self.tiles[x][y]["walk"]

class World:
    def __init__(self, seed: int):
        self.state = WorldState(seed=seed)
        self.entities = EntityManager()
        self.grid = GridMap(40, 30, seed)
        self.rng = random.Random(seed)

    def bootstrap(self, candidates: int = 9):
        self.state.meta["pregame"] = True
        from ..characters.traits import load_trait_catalog, random_trait_set
        catalog = load_trait_catalog()
        self.state.meta["trait_catalog"] = catalog
        for i in range(candidates):
            eid = self.entities.create(GLOBAL_ID_GEN.next())
            x = 5 + (i % 5)
            y = 5 + (i // 5)
            self.entities.add_component(eid, "Position", Position(x, y))
            self.entities.add_component(eid, "Renderable", Renderable("worker"))
            name = self.rng.choice(NAMES)
            code = f"C{i+1:02d}"
            self.entities.add_component(eid, "Identity", Identity(name=name, code=code))
            main_class, subclass = self.rng.choice(PROFESSIONS)
            self.entities.add_component(eid, "Profession", Profession(main_class=main_class, subclass=subclass))
            self.entities.add_component(eid, "Role", Role("Worker"))
            p = Personality(
                openness=round(self.rng.random(),2),
                conscientiousness=round(self.rng.random(),2),
                extraversion=round(self.rng.random(),2),
                agreeableness=round(self.rng.random(),2),
                neuroticism=round(self.rng.random(),2),
            )
            self.entities.add_component(eid, "Personality", p)
            tset = random_trait_set(self.rng, catalog, max_traits=3)
            self.entities.add_component(eid, "Traits", Traits(items=tset))
            self.entities.add_component(eid, "Authority", Authority(rank=1, leader=False))
            self.entities.add_component(eid, "EmotionState", EmotionState())
            self.entities.add_component(eid, "Needs", Needs())
            base_strength = 0.4 + self.rng.random()*0.3
            attrs = Attributes(
                strength=base_strength,
                stamina=0.4 + self.rng.random()*0.3,
                agility=0.4 + self.rng.random()*0.3,
                intelligence=0.4 + self.rng.random()*0.3,
                perception=0.4 + self.rng.random()*0.3,
                resilience=0.4 + self.rng.random()*0.3,
                craftsmanship=0.4 + self.rng.random()*0.3,
                botany=0.4 + self.rng.random()*0.3,
                mining=0.4 + self.rng.random()*0.3,
                hunting=0.4 + self.rng.random()*0.3,
                hauling=0.4 + self.rng.random()*0.3
            )
            self.entities.add_component(eid, "Attributes", attrs)
            capacity = int(30 + attrs.strength*20 + attrs.stamina*10)
            self.entities.add_component(eid, "TaskAgent", TaskAgent())
            self.entities.add_component(eid, "ResourceInventory", ResourceInventory(capacity=capacity, stored={}))
            self.entities.add_component(eid, "Health", Health(hp=60, max_hp=60))
            self.entities.add_component(eid, "Morale", Morale(value=1.0))
            self.entities.add_component(eid, "ThermalStatus", ThermalStatus())
            self.entities.add_component(eid, "CombatTag", CombatTag(faction="colony"))
            self.entities.add_component(eid, "Movement", Movement(speed=1.0))
            self.entities.add_component(eid, "WorkIntent", WorkIntent(job="Idle"))
            self.entities.add_component(eid, "ActivityState", ActivityState())
            self.entities.add_component(eid, "Dialogue", Dialogue(line="..."))
        for _ in range(15):
            rx, ry = self.rng.randint(0, self.grid.width - 1), self.rng.randint(0, self.grid.height - 1)
            if not self.grid.walkable(rx, ry): continue
            rid = self.entities.create(GLOBAL_ID_GEN.next())
            self.entities.add_component(rid, "Position", Position(rx, ry))
            self.entities.add_component(rid, "Renderable", Renderable("wood_node"))
            self.entities.add_component(rid, "ResourceNode", ResourceNode("WoodCold", self.rng.randint(30, 70)))
        # Initial Storage
        store_id = self.entities.create(GLOBAL_ID_GEN.next())
        self.entities.add_component(store_id, "Position", Position(4, 5))
        self.entities.add_component(store_id, "Renderable", Renderable("storage"))
        self.entities.add_component(store_id, "Building", Building("Storage"))
        self.entities.add_component(store_id, "Storage", Storage(capacity=300))
        heat_id = self.entities.create(GLOBAL_ID_GEN.next())
        self.entities.add_component(heat_id, "Position", Position(6, 5))
        self.entities.add_component(heat_id, "Renderable", Renderable("heat"))
        self.entities.add_component(heat_id, "Building", Building("HeatStation"))
        self.entities.add_component(heat_id, "HeatEmitter", HeatEmitter(radius=6, output=120))
        self.state.meta["bootstrap_complete"] = True

    def start_game_with_leader(self, eid: int):
        em = self.entities
        if self.state.meta.get("pregame", False):
            self.state.meta["pregame"] = False
        role_store = em.get_component_store("Role")
        if eid in role_store:
            role_store[eid].type = "Leader"
        invs = em.get_component_store("ResourceInventory")
        if eid in invs:
            invs[eid].capacity = max(invs[eid].capacity, 140)
            invs[eid].stored.setdefault("FoodRation", 20)
            invs[eid].stored.setdefault("WoodCold", 60)
        lai = em.get_component_store("LeaderAI")
        if eid not in lai:
            from .components import LeaderAI
            em.add_component(eid, "LeaderAI", LeaderAI())
        auths = em.get_component_store("Authority")
        if eid in auths:
            auths[eid].rank = 3
            auths[eid].leader = True
        if eid not in em.get_component_store("Movement"):
            em.add_component(eid, "Movement", Movement(speed=1.0))
        if eid not in em.get_component_store("WorkIntent"):
            em.add_component(eid, "WorkIntent", WorkIntent(job="Leader"))
        if eid not in em.get_component_store("ActivityState"):
            em.add_component(eid, "ActivityState", ActivityState())
        if eid not in em.get_component_store("Dialogue"):
            em.add_component(eid, "Dialogue", Dialogue(line="Ta sẽ dẫn dắt."))
        self.record_event({"tick": self.state.tick, "type": "LeaderChosen", "id": eid})
        self.record_decision({"tick": self.state.tick, "type":"LeaderDecisionInit","options":[],"chosen":"<init>","action_type":"init"})

    def can_build_portal(self) -> bool:
        return self.state.portal_count < MAX_PORTALS

    def record_decision(self, entry):
        self.state.decision_feed.append(entry)
        self.state.decision_feed = self.state.decision_feed[-120:]

    def record_event(self, entry):
        self.state.event_feed.append(entry)
        self.state.event_feed = self.state.event_feed[-140:]

    def record_expedition(self, entry):
        self.state.expedition_feed.append(entry)
        self.state.expedition_feed = self.state.expedition_feed[-100:]