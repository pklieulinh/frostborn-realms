from assets.loader.asset_loader import load_images, AssetDefinitionError

def main():
    try:
        loader = load_images(
            base_dir="assets",
            manifest="assets/assets_manifest.json",
            strict=True,
            load_surfaces=False
        )
        print("Asset validation OK:", loader.summary())
    except AssetDefinitionError as e:
        print("Asset validation FAILED:", e)
        raise SystemExit(1)
    except Exception as e:
        print("Unexpected error:", e)
        raise

if __name__ == "__main__":
    main()