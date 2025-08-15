import pygame
from components.sprite import SpriteComponent
from components.position import Position

class RenderingSystem:
    def __init__(self, screen: pygame.Surface, loader):
        self.screen = screen
        self.loader = loader
        self.bg_color = (12, 16, 20)

    def update(self, ctx, dt: float):
        self.screen.fill(self.bg_color)
        pos_store = ctx.store("position")
        spr_store = ctx.store("sprite")

        for eid, spr in spr_store.items():
            pos = pos_store.get(eid)
            if not pos:
                continue
            image = self.loader.resolve(spr.image_id)
            frame_surface = image
            if spr.has_animation():
                spr.accum += dt
                while spr.accum >= spr.frame_time:
                    spr.accum -= spr.frame_time
                    spr.current_frame = (spr.current_frame + 1) % spr.frame_count
                fw, fh = spr.frame_width, spr.frame_height
                fx = spr.current_frame * fw
                rect = pygame.Rect(fx, 0, fw, fh)
                frame_surface = image.subsurface(rect)
            self.screen.blit(frame_surface, (pos.x, pos.y))
