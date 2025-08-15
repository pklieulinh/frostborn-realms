from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Position:
    x: int
    y: int

@dataclass
class Renderable:
    sprite: str
    layer: int = 0

@dataclass
class Role:
    type: str

@dataclass
class ResourceInventory:
    capacity: int
    stored: Dict[str, int] = field(default_factory=dict)

@dataclass
class Movement:
    speed: float
    path: List[tuple] = field(default_factory=list)
    target: Optional[tuple] = None

@dataclass
class TaskAgent:
    current: Optional[Dict] = None
    queue: List[Dict] = field(default_factory=list)
    stamina: float = 1.0
    morale: float = 1.0

@dataclass
class ResourceNode:
    rtype: str
    amount: int

@dataclass
class Building:
    btype: str
    progress: float = 1.0
    level: int = 1
    active: bool = True

@dataclass
class ConstructionSite:
    btype: str
    needed: Dict[str, int]
    delivered: Dict[str, int] = field(default_factory=dict)
    progress: float = 0.0
    complete: bool = False

@dataclass
class HeatEmitter:
    radius: int
    output: int

@dataclass
class PortalGate:
    seed: int
    state: str
    quality: float

@dataclass
class ExpeditionTeam:
    team_id: int
    portal_seed: int
    phase: str
    ticks_remaining: int
    log: List[Dict] = field(default_factory=list)
    result: Optional[Dict] = None

@dataclass
class LeaderAI:
    intervention_pending: List[Dict] = field(default_factory=list)
    last_decision_tick: int = -1

@dataclass
class Needs:
    food_timer: int = 0
    heat_timer: int = 0
    deficit_heat_ticks: int = 0

COMPONENT_TYPES = {
    "Position": Position,
    "Renderable": Renderable,
    "Role": Role,
    "ResourceInventory": ResourceInventory,
    "Movement": Movement,
    "TaskAgent": TaskAgent,
    "ResourceNode": ResourceNode,
    "Building": Building,
    "ConstructionSite": ConstructionSite,
    "HeatEmitter": HeatEmitter,
    "PortalGate": PortalGate,
    "ExpeditionTeam": ExpeditionTeam,
    "LeaderAI": LeaderAI,
    "Needs": Needs,
}

def serialize_component(obj):
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items()}
    return obj