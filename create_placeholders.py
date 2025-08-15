import pygame
import sys
from pathlib import Path
import argparse
import hashlib

DEFAULT_IDS = ["leader", "worker", "wood_node"]

def color_from_id(asset_id: str):
    h = hashlib.md5(asset_id.encode()).hexdigest()
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (64 + r // 2, 64 + g // 2, 64 + b // 2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="frostborn-realms/assets/sprites", help="Output sprites directory")
    parser.add_argument("--size", type=int, default=32)
    parser.add_argument("--ids", nargs="*", default=DEFAULT_IDS)
    args = parser.parse_args()

    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pygame.init()
    for aid in args.ids:
        surf = pygame.Surface((args.size, args.size), pygame.SRCALPHA)
        surf.fill(color_from_id(aid))
        pygame.draw.rect(surf, (20,20,20), surf.get_rect(), 2)
        try:
            font = pygame.font.SysFont("Arial", max(8, args.size // 3))
            txt = font.render(aid[0].upper(), True, (255,255,255))
            rect = txt.get_rect(center=surf.get_rect().center)
            surf.blit(txt, rect)
        except Exception:
            pass
        path = out_dir / f"{aid}.png"
        pygame.image.save(surf, str(path))
        print("Created", path)

    print("Done placeholder generation.")
    pygame.quit()

if __name__ == "__main__":
    main()
