import pygame
import time

class UISystem:
    def __init__(self, font: pygame.font.Font):
        self.font = font
        self.frame_count = 0
        self.accum_time = 0.0
        self.fps = 0.0
        self.last_mark = time.perf_counter()

    def update(self, surface: pygame.Surface, dt: float, ctx):
        self.frame_count += 1
        self.accum_time += dt
        if self.accum_time >= 0.5:
            self.fps = self.frame_count / self.accum_time
            self.accum_time = 0.0
            self.frame_count = 0
        text = f"FPS {self.fps:05.1f}  Entities {len(list(ctx.em.alive.keys()))}"
        img = self.font.render(text, True, (190, 210, 225))
        surface.blit(img, (8, 6))