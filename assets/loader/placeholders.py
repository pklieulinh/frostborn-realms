import pygame

def make_checker_surface(w: int, h: int) -> pygame.Surface:
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    c1 = (80, 90, 100, 255)
    c2 = (35, 40, 45, 255)
    tile = 4
    for y in range(0, h, tile):
        for x in range(0, w, tile):
            rect = (x, y, tile, tile)
            color = c1 if ((x//tile + y//tile) % 2 == 0) else c2
            surf.fill(color, rect)
    return surf