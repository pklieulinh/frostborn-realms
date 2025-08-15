import sys
import pygame
from pathlib import Path
from assets.loader.asset_loader import AssetLoader, AssetDefinitionError
from world.world import LocalWorld

WIDTH, HEIGHT = 960, 600
BG_COLOR = (15, 25, 40)
TILE = 32

def find_assets_dir(start: Path) -> Path:
    candidates = []
    for up in [start, *start.parents[:3]]:
        cand = up / "assets"
        if cand.is_dir():
            candidates.append(cand)
    for c in candidates:
        if (c / "assets_manifest.json").is_file() or (c / "assets_manifest.example.json").is_file():
            return c
    if candidates:
        return candidates[0]
    fallback = start / "assets"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

def load_assets():
    current_file_dir = Path(__file__).parent.resolve()
    assets_dir = find_assets_dir(current_file_dir)
    manifest = assets_dir / "assets_manifest.json"
    example = assets_dir / "assets_manifest.example.json"

    using_example = False
    chosen_manifest = None
    if manifest.is_file():
        chosen_manifest = manifest
        strict_missing = True
    elif example.is_file():
        chosen_manifest = example
        using_example = True
        # Khi dùng example: không strict => sinh placeholder thay vì crash
        strict_missing = False
        print(f"[WARN] Manifest not found, using example (placeholder mode): {example}")
    else:
        print(f"[WARN] No manifest found in {assets_dir}; starting empty placeholder asset set.")
        strict_missing = False

    loader = AssetLoader(
        base_dir=assets_dir,
        strict_missing_as_error=strict_missing,
        load_surfaces=True,
        load_mode="surfaces",
        placeholder_on_missing=True
    )

    if chosen_manifest:
        loader.add_images_from_manifest_file(chosen_manifest)

    loader.load_all()
    summary = loader.summary()
    print("[ASSETS]", summary)
    if using_example and summary.get("placeholders", 0) > 0:
        print("[INFO] Example manifest loaded with placeholders. Provide real sprites and create assets_manifest.json to enable strict mode.")
    return loader, assets_dir

def bootstrap():
    loader, assets_dir = load_assets()
    world = LocalWorld(width=40, height=30, tile_size=TILE, asset_loader=loader)
    world.generate_initial()
    return loader, world

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Frostborn Realms – Pygame Prototype")
    clock = pygame.time.Clock()
    try:
        loader, world = bootstrap()
    except AssetDefinitionError as e:
        print("[FATAL] Asset load error:", e)
        pygame.quit()
        sys.exit(1)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        world.update(dt)
        screen.fill(BG_COLOR)
        world.render(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()
