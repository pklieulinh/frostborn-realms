import random
import pygame
from typing import Dict, Tuple

class LocalWorld:
    def __init__(self, width: int, height: int, tile_size: int, asset_loader):
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.loader = asset_loader
        self.entities = []
        self.rng = random.Random(12345)

    def generate_initial(self):
        self.entities.append({"id": "leader", "pos": (5,5), "asset": "leader"})
        for i in range(6):
            self.entities.append({"id": f"worker{i}", "pos": (7+i, 7), "asset": "worker"})
        for _ in range(10):
            x = self.rng.randint(0, self.width-1)
            y = self.rng.randint(0, self.height-1)
            self.entities.append({"id": f"wood_{x}_{y}", "pos": (x,y), "asset": "wood_node"})

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        ts = self.tile_size
        for x in range(self.width):
            for y in range(self.height):
                rect = pygame.Rect(x*ts, y*ts, ts, ts)
                c = (30, 50, 70) if (x + y) % 2 == 0 else (35, 55, 80)
                pygame.draw.rect(surface, c, rect)
        for ent in self.entities:
            sx, sy = ent["pos"]
            spr = self.loader.resolve(ent["asset"]) if ent["asset"] in self.loader.images else None
            draw_rect = pygame.Rect(sx*ts+4, sy*ts+4, ts-8, ts-8)
            if spr:
                surf_scaled = pygame.transform.smoothscale(spr, (ts-6, ts-6))
                surface.blit(surf_scaled, (sx*ts+3, sy*ts+3))
            else:
                color = (255,215,0) if ent["asset"] == "leader" else (100,180,255)
                if ent["asset"].startswith("wood"):
                    color = (140,90,40)
                pygame.draw.rect(surface, color, draw_rect)