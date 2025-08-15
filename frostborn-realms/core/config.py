from pydantic import BaseModel
from typing import Literal

TICK_RATE = 10
TICK_INTERVAL_SEC = 1 / TICK_RATE
WORLD_SEED = 123456789
MAX_PORTALS = 9
PROTOCOL_VERSION = "0.3.0"
GAME_TITLE = "BangPhongTheGioi"
BUILD_ENV: Literal["dev", "prod"] = "dev"

class Balance(BaseModel):
    food_need_interval: int = 30
    heat_need_interval: int = 40
    base_gather_ticks: int = 4
    morale_penalty_heat_delay: int = 50
    expedition_base_duration: int = 40
    portal_surged_quality_boost: float = 0.25
    expedition_loot_crystal: int = 1

BALANCE = Balance()