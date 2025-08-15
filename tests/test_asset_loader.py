from pathlib import Path
import pytest
from assets.loader.asset_loader import AssetLoader, AssetDefinitionError, extract_rel_path, validate_image_def

def test_valid_load(tmp_path: Path):
    (tmp_path / "img").mkdir()
    (tmp_path / "img" / "hero.png").write_bytes(b"x")
    images = [
        {"id": "hero", "path": "img/hero.png"},
        {"id": "tree", "file": "img/hero.png"},
    ]
    loader = AssetLoader(tmp_path, images, strict=True, load_surfaces=False)
    loader.load_all()
    assert "hero" in loader.images
    assert loader.get("hero").abs_path.exists()

def test_missing_path_value(tmp_path: Path):
    images = [{"id": "broken", "path": None}]
    loader = AssetLoader(tmp_path, images, strict=True, load_surfaces=False)
    with pytest.raises(AssetDefinitionError):
        loader.load_all()

def test_missing_any_path_key(tmp_path: Path):
    images = [{"id": "nop"}]
    loader = AssetLoader(tmp_path, images, strict=True, load_surfaces=False)
    with pytest.raises(AssetDefinitionError):
        loader.load_all()

def test_duplicate_id(tmp_path: Path):
    (tmp_path / "a.png").write_bytes(b"x")
    images = [
        {"id": "dup", "path": "a.png"},
        {"id": "dup", "path": "a.png"},
    ]
    loader = AssetLoader(tmp_path, images, strict=True, load_surfaces=False)
    with pytest.raises(AssetDefinitionError):
        loader.load_all()

def test_extract_rel_path():
    assert extract_rel_path({"id": "a", "path": "x.png"}) == "x.png"
    assert extract_rel_path({"id": "a", "file": "y.png"}) == "y.png"
    assert extract_rel_path({"id": "a", "rel_path": "z.png"}) == "z.png"
    assert extract_rel_path({"id": "a"}) is None

def test_validate_requires_key():
    with pytest.raises(AssetDefinitionError):
        validate_image_def({"id": "a"}, 0)