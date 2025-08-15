from dataclasses import dataclass, field
from typing import Dict, List, Optional

# --- Item / Building new components (isolated to reduce merge risk with existing components.py) ---

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
    priority: int = 1  # 0..4 similar RimWorld style