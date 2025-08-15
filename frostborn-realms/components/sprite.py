from dataclasses import dataclass
from typing import Optional

@dataclass
class SpriteComponent:
    image_id: str
    frame_width: int = 0
    frame_height: int = 0
    frame_count: int = 1
    frame_time: float = 0.08
    accum: float = 0.0
    current_frame: int = 0
    loop: bool = True
    active: bool = True

    def has_animation(self) -> bool:
        return self.frame_count > 1 and self.frame_width > 0 and self.frame_height > 0