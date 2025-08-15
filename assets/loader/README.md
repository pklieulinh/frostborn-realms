# Asset Loader Usage

Example manifest (JSON):
```json
{
  "images": [
    { "id": "hero", "path": "sprites/hero.png", "tags": ["unit","player"] },
    { "id": "tree", "file": "env/tree.png", "category": "environment" }
  ]
}
```

Example manifest (YAML):
```yaml
images:
  - id: hero
    path: sprites/hero.png
    tags: [unit, player]
  - id: portal
    rel_path: effects/portal.png
    category: fx
```

Code:
```python
from assets.loader.asset_loader import AssetLoader

loader = AssetLoader(base_dir="assets")
loader.add_images_from_manifest_file("assets_manifest.json")
loader.load_all()
hero = loader.get("hero")
print(hero.abs_path)
```

Intervention for None path:
If a definition lacks 'path'/'file'/'rel_path', an AssetDefinitionError is raised with index or id context.