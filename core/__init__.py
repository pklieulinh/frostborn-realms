# Core package: chỉ xuất những hằng số cấu hình cấp cao, tránh import sâu gây vòng lặp.
from .config import (
    TICK_RATE,
    TICK_INTERVAL_SEC,
    WORLD_SEED,
    MAX_PORTALS,
    PROTOCOL_VERSION,
    GAME_TITLE,
    BALANCE,
)
