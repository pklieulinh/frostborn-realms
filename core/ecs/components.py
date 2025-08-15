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
class Identity:
    name: str
    code: str

@dataclass
class Traits:
    items: List[str] = field(default_factory=list)

@dataclass
class Personality:
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float

@dataclass
class Profession:
    main_class: str
    subclass: str

@dataclass
class Authority:
    rank: int = 1
    leader: bool = False

@dataclass
class EmotionState:
    mood: float = 0.7
    anger: float = 0.0
    fear: float = 0.0
    last_update_tick: int = 0

@dataclass
class Goals:
    current: Optional[Dict] = None
    queue: List[Dict] = field(default_factory=list)

@dataclass
class Relationships:
    affinity: Dict[int, float] = field(default_factory=dict)

@dataclass
class Memory:
    recent: List[Dict] = field(default_factory=list)

@dataclass
class ResourceInventory:
    capacity: int
    stored: Dict[str, int] = field(default_factory=dict)

@dataclass
class Movement:
    speed: float = 1.0
    target: Optional[tuple] = None
    path: List[tuple] = field(default_factory=list)

@dataclass
class TaskAgent:
    current: Optional[Dict] = None
    queue: List[Dict] = field(default_factory=list)
    stamina: float = 1.0

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
    meta: Dict[str, any] = field(default_factory=dict)

@dataclass
class HeatEmitter:
    radius: int
    output: int

@dataclass
class PortalGate:
    seed: int
    state: str
    quality: float
    biome: str = "Tundra"

@dataclass
class ExpeditionTeam:
    team_id: int
    portal_seed: int
    phase: str
    ticks_remaining: int
    log: List[Dict] = field(default_factory=list)
    result: Optional[Dict] = None
    loadout: Dict[str, int] = field(default_factory=dict)
    risk: float = 0.0
    base_duration: int = 0
    phase_index: int = 0

@dataclass
class LeaderAI:
    intervention_pending: List[Dict] = field(default_factory=list)
    last_decision_tick: int = -1

@dataclass
class Needs:
    food_timer: int = 0
    heat_timer: int = 0
    deficit_heat_ticks: int = 0

@dataclass
class Health:
    hp: float
    max_hp: float

@dataclass
class Morale:
    value: float = 1.0

@dataclass
class ThermalStatus:
    heat_value: float = 0.0
    comfortable: bool = True

@dataclass
class AttackStats:
    power: int
    cooldown_ticks: int
    cooldown: int = 0

@dataclass
class CombatTag:
    faction: str

@dataclass
class AICombat:
    target_id: Optional[int] = None
    pursue: bool = True

@dataclass
class ResearchStationTag:
    level: int = 1

@dataclass
class CraftingStation:
    station_type: str
    queue: List[Dict] = field(default_factory=list)
    active: bool = True
    auto: bool = True

@dataclass
class CraftingJob:
    recipe_id: str
    progress: int = 0
    time_required: int = 0
    inputs: Dict[str, int] = field(default_factory=dict)
    outputs: Dict[str, int] = field(default_factory=dict)

@dataclass
class VictoryState:
    achieved: bool = False
    tick: int = -1
    reason: str = ""

@dataclass
class HousingUnit:
    capacity: int = 4
    occupants: List[int] = field(default_factory=list)

@dataclass
class FarmField:
    crop: str = "ColdGrain"
    growth_progress: float = 0.0
    growth_rate: float = 0.35
    yield_amount: int = 3
    farmers_assigned: int = 0

@dataclass
class AnimalPen:
    species: str = "LivestockSmall"
    herd_size: int = 4
    husbandry_timer: int = 0
    production_interval: int = 220
    yield_amount: int = 2
    herders_assigned: int = 0

@dataclass
class WorkIntent:
    job: str = "Idle"
    priority: int = 0

@dataclass
class ActivityState:
    state: str = "Idle"
    target: Optional[int] = None
    target_pos: Optional[tuple] = None
    changed_tick: int = 0
    meta: Dict[str, any] = field(default_factory=dict)

@dataclass
class Dialogue:
    line: str = ""
    next_change_tick: int = 0

@dataclass
class ResourceDeposit:
    resource_type: str
    amount_remaining: int
    tier: int
    yield_per_cycle: int
    depletion_events: int = 0

@dataclass
class Sapling:
    ticks_to_mature: int
    wood_amount: int

@dataclass
class WorkStats:
    fatigue: float = 0.0
    stress: float = 0.0
    overwork_ticks: int = 0

@dataclass
class Storage:
    capacity: int
    used: int = 0
    accepted: Optional[List[str]] = None
    store: Dict[str,int] = field(default_factory=dict)

@dataclass
class ResourcePile:
    resources: Dict[str, int]
    decay_timer: int = 3000

@dataclass
class Attributes:
    strength: float
    stamina: float
    agility: float
    intelligence: float
    perception: float
    resilience: float
    craftsmanship: float
    botany: float
    mining: float
    hunting: float
    hauling: float

@dataclass
class SkillProgress:
    xp: Dict[str,float] = field(default_factory=dict)
    last_update_tick: int = 0

@dataclass
class Skills:
    levels: Dict[str,int] = field(default_factory=dict)
    xp: Dict[str,float] = field(default_factory=dict)
    passions: Dict[str,str] = field(default_factory=dict)

@dataclass
class WorkPriorities:
    priorities: Dict[str,int] = field(default_factory=dict)

@dataclass
class Item:
    def_id: str
    stack_count: int
    max_stack: int
    quality_tier: int = -1
    hp: int = 1
    max_hp: int = 1
    material_id: Optional[str] = None

@dataclass
class Quality:
    tier: int
    label: str
    multiplier: float

@dataclass
class Durability:
    hp: int
    max_hp: int
    outdoors: bool = False
    decay_rate: float = 0.0

@dataclass
class Blueprint:
    building_def: str
    cost_total: Dict[str,int]
    cost_remaining: Dict[str,int]
    placed_tick: int

@dataclass
class BuildFrame:
    building_def: str
    material_id: Optional[str]
    work_left: float
    hp_current: int
    hp_max: int

@dataclass
class MaterialTag:
    material_id: str

@dataclass
class StorageFilter:
    allow_categories: List[str] = field(default_factory=list)
    disallow_items: List[str] = field(default_factory=list)
    priority: int = 1

@dataclass
class Demographics:
    gender: str
    age: int
    fertile: bool = True
    pregnant_ticks: int = 0

COMPONENT_TYPES = {
    "Position": Position,
    "Renderable": Renderable,
    "Role": Role,
    "Identity": Identity,
    "Traits": Traits,
    "Personality": Personality,
    "Profession": Profession,
    "Authority": Authority,
    "EmotionState": EmotionState,
    "Goals": Goals,
    "Relationships": Relationships,
    "Memory": Memory,
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
    "Health": Health,
    "Morale": Morale,
    "ThermalStatus": ThermalStatus,
    "AttackStats": AttackStats,
    "CombatTag": CombatTag,
    "AICombat": AICombat,
    "ResearchStationTag": ResearchStationTag,
    "CraftingStation": CraftingStation,
    "CraftingJob": CraftingJob,
    "VictoryState": VictoryState,
    "HousingUnit": HousingUnit,
    "FarmField": FarmField,
    "AnimalPen": AnimalPen,
    "WorkIntent": WorkIntent,
    "ActivityState": ActivityState,
    "Dialogue": Dialogue,
    "ResourceDeposit": ResourceDeposit,
    "Sapling": Sapling,
    "WorkStats": WorkStats,
    "Storage": Storage,
    "ResourcePile": ResourcePile,
    "Attributes": Attributes,
    "SkillProgress": SkillProgress,
    "Skills": Skills,
    "WorkPriorities": WorkPriorities,
    "Item": Item,
    "Quality": Quality,
    "Durability": Durability,
    "Blueprint": Blueprint,
    "BuildFrame": BuildFrame,
    "MaterialTag": MaterialTag,
    "StorageFilter": StorageFilter,
    "Demographics": Demographics
}

def serialize_component(obj):
    if hasattr(obj, "__dict__"):
        return {k: v for k, v in obj.__dict__.items()}
    return obj