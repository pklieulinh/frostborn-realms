from __future__ import annotations

import json
import os
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

try:
    import pygame
    _HAS_PYGAME = True
except ImportError:
    _HAS_PYGAME = False


class AssetDefinitionError(Exception):
    pass


@dataclass
class AssetRecord:
    id: str
    rel_path: str
    abs_path: Path
    meta: Dict[str, Any]
    surface: Any = None
    placeholder: bool = False
    dynamic: bool = False  # created at runtime (not from manifest)


def extract_rel_path(img_def: Dict[str, Any]) -> Optional[str]:
    for key in ("path", "file", "rel_path"):
        if key in img_def:
            val = img_def[key]
            if val is not None:
                return str(val)
    return None


def validate_image_def(img_def: Dict[str, Any], idx: int) -> None:
    if not isinstance(img_def, dict):
        raise AssetDefinitionError(f"Image definition at index {idx} is not a dict")
    if "id" not in img_def:
        raise AssetDefinitionError(f"Image definition at index {idx} missing 'id'")
    if not isinstance(img_def["id"], str) or not img_def["id"].strip():
        raise AssetDefinitionError(f"Image definition at index {idx} has invalid 'id'")
    if not any(k in img_def for k in ("path", "file", "rel_path")):
        raise AssetDefinitionError(f"Image id='{img_def['id']}' index={idx} missing one of path|file|rel_path")


class AssetLoader:
    """
    Backward & forward compatible AssetLoader + Dynamic Placeholders.

    Key behaviors:
      - strict_missing_as_error controls raising on missing files (if placeholder_on_missing False).
      - placeholder_on_missing allows runtime surface generation for entries in manifest whose files are missing.
      - allow_dynamic_placeholders enables on-demand creation of placeholder assets for ids never declared in manifest.
    """

    def __init__(
        self,
        base_dir: Union[str, Path],
        images: Optional[Sequence[Dict[str, Any]]] = None,
        strict: bool = True,
        strict_missing_as_error: Optional[bool] = None,
        root_override: Optional[Union[str, Path]] = None,
        load_surfaces: bool = True,
        load_mode: str = "surfaces",
        default_convert_alpha: bool = True,
        placeholder_on_missing: bool = True,
        default_placeholder_size: int = 32,
        allow_dynamic_placeholders: bool = True,
    ):
        self.base_dir = Path(base_dir).resolve()
        self._images_raw = list(images) if images else []
        if strict_missing_as_error is None:
            self.strict_missing_as_error = strict
        else:
            self.strict_missing_as_error = strict_missing_as_error
        self.root_override = Path(root_override).resolve() if root_override else None
        self._image_cache: Dict[str, AssetRecord] = {}
        self._loaded = False
        self.load_mode = load_mode
        self.default_convert_alpha = default_convert_alpha
        self.placeholder_on_missing = placeholder_on_missing
        self.default_placeholder_size = default_placeholder_size
        self.allow_dynamic_placeholders = allow_dynamic_placeholders
        self.load_surfaces = (load_surfaces and _HAS_PYGAME and load_mode in ("surfaces", "eager"))

    @property
    def images(self) -> Dict[str, AssetRecord]:
        if not self._loaded:
            raise RuntimeError("Assets not loaded yet. Call load_all() first.")
        return self._image_cache

    def add_images_from_manifest_file(self, manifest_path: Union[str, Path]) -> None:
        p = Path(manifest_path)
        if not p.is_file():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        text = p.read_text(encoding="utf-8")
        manifest_str = str(p)
        if manifest_str.lower().endswith((".yaml", ".yml")):
            try:
                import yaml  # type: ignore
            except ImportError as e:
                raise RuntimeError("PyYAML not installed; pip install pyyaml") from e
            data = yaml.safe_load(text)
        else:
            try:
                data = json.loads(text)
            except json.JSONDecodeError as e:
                raise AssetDefinitionError(f"Invalid JSON in manifest '{manifest_path}': {e}") from e
        if not isinstance(data, dict):
            raise AssetDefinitionError("Manifest root must be an object/dict")
        images = data.get("images")
        if not isinstance(images, list):
            raise AssetDefinitionError("Manifest missing 'images' list")
        self._images_raw.extend(images)

    def load_all(self) -> None:
        if self._loaded:
            return
        for idx, img_def in enumerate(self._images_raw):
            rec = self._process_entry(img_def, idx)
            if rec.id in self._image_cache:
                raise AssetDefinitionError(f"Duplicate asset id '{rec.id}' at index {idx}")
            self._image_cache[rec.id] = rec
        self._loaded = True

    def _process_entry(self, img_def: Dict[str, Any], idx: int) -> AssetRecord:
        validate_image_def(img_def, idx)
        asset_id: str = img_def["id"]
        rel_path = extract_rel_path(img_def)
        if rel_path is None:
            raise AssetDefinitionError(f"Image id='{asset_id}' index={idx} missing path/file/rel_path value (was None)")
        rel_path = rel_path.strip()
        if not rel_path:
            raise AssetDefinitionError(f"Image id='{asset_id}' index={idx} has empty path value")
        is_abs = Path(rel_path).is_absolute()
        if is_abs:
            abs_path = Path(rel_path).resolve()
            normalized_rel = os.path.relpath(abs_path, self.base_dir) if abs_path.exists() else rel_path
        else:
            root = self.root_override if self.root_override else self.base_dir
            normalized_rel = rel_path.lstrip("/").replace("\\", "/")
            abs_path = (root / normalized_rel).resolve()
        meta = {k: v for k, v in img_def.items() if k not in ("id", "path", "file", "rel_path")}
        file_exists = abs_path.exists()
        surface = None
        placeholder = False
        if not file_exists:
            msg = f"Asset file not found id='{asset_id}' resolved='{abs_path}'"
            if self.strict_missing_as_error and not self.placeholder_on_missing:
                raise AssetDefinitionError(msg)
            else:
                print(f"[AssetLoader][WARN] {msg} - using placeholder")
                if self.load_surfaces and self.placeholder_on_missing:
                    surface = self._make_placeholder_surface(asset_id, meta)
                    placeholder = True
        else:
            if self.load_surfaces:
                surface = self._load_surface(asset_id, abs_path)
        return AssetRecord(id=asset_id, rel_path=normalized_rel, abs_path=abs_path, meta=meta, surface=surface, placeholder=placeholder)

    def _load_surface(self, asset_id: str, abs_path: Path):
        if not _HAS_PYGAME:
            return None
        try:
            surf = pygame.image.load(str(abs_path))
            if self.default_convert_alpha and surf.get_alpha() is not None:
                surf = surf.convert_alpha()
            elif self.default_convert_alpha:
                surf = surf.convert()
            return surf
        except Exception as e:
            if self.strict_missing_as_error and not self.placeholder_on_missing:
                raise AssetDefinitionError(f"Failed to load surface id='{asset_id}' path='{abs_path}': {e}") from e
            else:
                print(f"[AssetLoader][WARN] Surface load failed id='{asset_id}': {e} - placeholder")
                return self._make_placeholder_surface(asset_id, {})

    def _color_from_id(self, asset_id: str):
        h = hashlib.md5(asset_id.encode()).hexdigest()
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return (64 + r // 2, 64 + g // 2, 64 + b // 2)

    def _make_placeholder_surface(self, asset_id: str, meta: Dict[str, Any]):
        if not _HAS_PYGAME:
            return None
        w = int(meta.get("w", self.default_placeholder_size))
        h = int(meta.get("h", self.default_placeholder_size))
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = meta.get("placeholder_color")
        if isinstance(color, list) and len(color) == 3:
            base_color = tuple(int(c) for c in color)
        else:
            base_color = self._color_from_id(asset_id)
        surf.fill(base_color)
        pygame.draw.rect(surf, (20, 20, 20), surf.get_rect(), 2)
        try:
            font = pygame.font.SysFont("Arial", max(10, w // 3))
            letter = asset_id[0].upper()
            txt = font.render(letter, True, (255, 255, 255))
            rect = txt.get_rect(center=surf.get_rect().center)
            surf.blit(txt, rect)
        except Exception:
            pass
        return surf

    def register_placeholder(self, asset_id: str, meta: Optional[Dict[str, Any]] = None, overwrite: bool = False):
        if not overwrite and asset_id in self._image_cache:
            return self._image_cache[asset_id]
        meta = meta or {}
        rel_path = f"dynamic/{asset_id}.png"
        abs_path = self.base_dir / rel_path
        surface = None
        if self.load_surfaces and self.placeholder_on_missing:
            surface = self._make_placeholder_surface(asset_id, meta)
        rec = AssetRecord(
            id=asset_id,
            rel_path=rel_path,
            abs_path=abs_path,
            meta=meta,
            surface=surface,
            placeholder=True,
            dynamic=True
        )
        self._image_cache[asset_id] = rec
        return rec

    def ensure_ids(self, asset_ids: Sequence[str]):
        for aid in asset_ids:
            if aid not in self._image_cache and self.allow_dynamic_placeholders:
                print(f"[AssetLoader][INFO] Auto-register placeholder asset id='{aid}'")
                self.register_placeholder(aid)

    def ensure_surface(self, asset_id: str, reload: bool = False):
        rec = self.get(asset_id)
        if rec.surface is None or reload:
            if rec.abs_path.exists():
                rec.surface = self._load_surface(asset_id, rec.abs_path)
            else:
                if self.placeholder_on_missing or rec.dynamic:
                    rec.surface = self._make_placeholder_surface(asset_id, rec.meta)
                    rec.placeholder = True
                else:
                    raise AssetDefinitionError(f"Cannot load surface; file missing id='{asset_id}' path='{rec.abs_path}'")
        return rec.surface

    def resolve(self, asset_id: str, want_record: bool = False, lazy: bool = True):
        if asset_id not in self._image_cache:
            if self.allow_dynamic_placeholders:
                self.register_placeholder(asset_id)
            else:
                raise KeyError(f"Asset id '{asset_id}' not loaded")
        rec = self._image_cache[asset_id]
        if want_record:
            return rec
        if rec.surface is None and lazy and _HAS_PYGAME:
            self.ensure_surface(asset_id)
        return rec.surface

    def resolve_path(self, asset_id: str) -> Path:
        rec = self.get(asset_id)
        return rec.abs_path

    def get(self, asset_id: str) -> AssetRecord:
        if not self._loaded:
            raise RuntimeError("Assets not loaded yet. Call load_all() first.")
        if asset_id not in self._image_cache:
            if self.allow_dynamic_placeholders:
                return self.register_placeholder(asset_id)
            raise KeyError(f"Asset id '{asset_id}' not loaded")
        return self._image_cache[asset_id]

    def get_surface(self, asset_id: str):
        return self.resolve(asset_id, want_record=False, lazy=True)

    def summary(self) -> Dict[str, Any]:
        return {
            "count": len(self._image_cache),
            "base_dir": str(self.base_dir),
            "ids": sorted(self._image_cache.keys()),
            "loaded_surfaces": sum(1 for r in self._image_cache.values() if r.surface is not None),
            "placeholders": sum(1 for r in self._image_cache.values() if r.placeholder),
            "dynamic_placeholders": sum(1 for r in self._image_cache.values() if r.dynamic),
            "mode": self.load_mode,
            "strict_missing_as_error": self.strict_missing_as_error,
            "allow_dynamic_placeholders": self.allow_dynamic_placeholders,
        }


def load_images(
    base_dir: Union[str, Path],
    manifest: Optional[Union[str, Path]] = None,
    images: Optional[List[Dict[str, Any]]] = None,
    strict: bool = True,
    strict_missing_as_error: Optional[bool] = None,
    load_surfaces: bool = True,
    load_mode: str = "surfaces",
    placeholder_on_missing: bool = True,
    allow_dynamic_placeholders: bool = True,
) -> AssetLoader:
    loader = AssetLoader(
        base_dir,
        images=images,
        strict=strict,
        strict_missing_as_error=strict_missing_as_error,
        load_surfaces=load_surfaces,
        load_mode=load_mode,
        placeholder_on_missing=placeholder_on_missing,
        allow_dynamic_placeholders=allow_dynamic_placeholders,
    )
    if manifest:
        loader.add_images_from_manifest_file(manifest)
    loader.load_all()
    return loader
