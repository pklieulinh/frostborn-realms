from assets.loader.asset_loader import AssetLoader, AssetDefinitionError
import pygame

def bootstrap_assets():
    loader = AssetLoader(
        base_dir="assets",
        strict=True,
        load_surfaces=True
    )
    loader.add_images_from_manifest_file("assets/assets_manifest.json")
    loader.load_all()
    print("Loaded assets:", loader.summary())
    return loader

def main():
    pygame.init()
    try:
        loader = bootstrap_assets()
    except AssetDefinitionError as e:
        print("[BOOT][FATAL] Asset load failed:", e)
        return
    screen = pygame.display.set_mode((800, 600))
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((15, 25, 40))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()