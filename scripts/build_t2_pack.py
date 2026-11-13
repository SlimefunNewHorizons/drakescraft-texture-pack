#!/usr/bin/env python3
"""Rebuild the T2 pack with legacy shaders restricted to pre-26.3 clients."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile


OVERLAY = "overlay_legacy_shaders"
MAX_LEGACY_FORMAT = 88  # Minecraft 26.2; 26.3 uses ShaderC/SPIR-V.
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[sd]|%%")


def patch_languages(source: zipfile.ZipFile, patches: dict) -> dict[str, bytes]:
    """Validate all patches before writing; preserve existing translation keys."""
    result = {}
    for name, replacements in patches.items():
        if not re.fullmatch(r"assets/[a-z0-9_.-]+/lang/[a-z]{2}_[a-z]{2}\.json", name):
            raise ValueError(f"Invalid language path: {name}")
        translations = json.loads(source.read(name))
        for key, value in replacements.items():
            if key not in translations or not isinstance(value, str) or not value.strip() or value == key:
                raise ValueError(f"Invalid translation: {name}: {key}")
            # A raw key has no reliable placeholders: compare against English.
            reference = translations[key]
            if reference == key:
                english = json.loads(source.read(name.rsplit('/', 1)[0] + '/en_us.json'))
                reference = english[key]
            if sorted(PLACEHOLDER.findall(reference)) != sorted(PLACEHOLDER.findall(value)):
                raise ValueError(f"Translation placeholders differ: {name}: {key}")
            translations[key] = value
        result[name] = (json.dumps(translations, ensure_ascii=False, indent=2) + "\n").encode()
    return result


def is_shader(name: str) -> bool:
    parts = name.split("/")
    return len(parts) >= 4 and parts[0] == "assets" and parts[2] == "shaders"


def patch_model_textures(source: zipfile.ZipFile, patches: dict) -> dict[str, bytes]:
    """Replace existing texture slots only when the target PNG is in the pack."""
    result = {}
    for name, replacements in patches.items():
        if (not re.fullmatch(r"assets/[a-z0-9_.-]+/models/[a-z0-9_./-]+\.json", name)
                or any(part in {".", "..", ""} for part in name.split("/"))):
            raise ValueError(f"Invalid model path: {name}")
        model = json.loads(source.read(name))
        textures = model.get("textures", {})
        for slot, reference in replacements.items():
            if slot not in textures or not isinstance(reference, str):
                raise ValueError(f"Invalid texture slot: {name}: {slot}")
            if not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", reference):
                raise ValueError(f"Invalid texture reference: {reference}")
            namespace, path = reference.split(":", 1)
            if any(part in {".", "..", ""} for part in path.split("/")):
                raise ValueError(f"Invalid texture reference: {reference}")
            target = f"assets/{namespace}/textures/{path}.png"
            if target not in source.namelist() or source.getinfo(target).is_dir():
                raise ValueError(f"Missing replacement texture: {target}")
            textures[slot] = reference
        result[name] = (json.dumps(model, ensure_ascii=False, indent=2) + "\n").encode()
    return result


def digest(path: Path, algorithm: str) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, algorithm).hexdigest()


def bridge_legacy_items(source: zipfile.ZipFile, carriers: list[str],
                        missing_model_fallbacks: dict[str, str] | None = None) -> dict[str, bytes]:
    """Retain CMD-only overrides in modern items, behind existing SF selections."""
    result = {}
    if (not isinstance(carriers, list) or not all(isinstance(c, str) for c in carriers)
            or len(carriers) != len(set(carriers))):
        raise ValueError("Expected unique legacy item carriers")
    names = set(source.namelist())
    fallbacks = missing_model_fallbacks if missing_model_fallbacks is not None else {}
    if not isinstance(fallbacks, dict):
        raise ValueError("Expected a mapping of missing models to existing models")
    def model_path(reference):
        if (not isinstance(reference, str)
                or not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", reference)):
            raise ValueError(f"Invalid fallback model reference: {reference}")
        namespace, path = reference.split(":", 1)
        if any(part in {".", "..", ""} for part in path.split("/")):
            raise ValueError(f"Invalid fallback model reference: {reference}")
        return f"assets/{namespace}/models/{path}.json"

    for missing, replacement in fallbacks.items():
        if model_path(missing) in names:
            raise ValueError(f"Fallback would replace an existing model: {missing}")
        target = model_path(replacement)
        if target not in names or source.getinfo(target).is_dir():
            raise ValueError(f"Missing fallback model: {target}")
    used_fallbacks = set()
    for carrier in carriers:
        if not isinstance(carrier, str) or not re.fullmatch(r"[a-z0-9_]+", carrier):
            raise ValueError(f"Invalid legacy item carrier: {carrier}")
        legacy_path = f"assets/minecraft/models/item/{carrier}.json"
        legacy = json.loads(source.read(legacy_path))
        entries = []
        previous = 0
        for override in legacy.get("overrides", []):
            predicate = override.get("predicate", {})
            threshold = predicate.get("custom_model_data")
            if (set(predicate) != {"custom_model_data"}
                    or type(threshold) not in (int, float)
                    or not math.isfinite(threshold) or threshold <= previous):
                raise ValueError(f"Unsupported legacy predicate or order: {legacy_path}")
            reference = override.get("model", "")
            if not isinstance(reference, str):
                raise ValueError(f"Invalid legacy model: {legacy_path}")
            if ":" not in reference:
                reference = "minecraft:" + reference
            if not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", reference):
                raise ValueError(f"Invalid legacy model reference: {reference}")
            namespace, path = reference.split(":", 1)
            if any(part in {".", "..", ""} for part in path.split("/")):
                raise ValueError(f"Invalid legacy model reference: {reference}")
            target = f"assets/{namespace}/models/{path}.json"
            if target not in names or source.getinfo(target).is_dir():
                if reference not in fallbacks:
                    raise ValueError(f"Missing legacy model: {target}")
                used_fallbacks.add(reference)
                reference = fallbacks[reference]
            entries.append({"threshold": threshold,
                            "model": {"type": "minecraft:model", "model": reference}})
            previous = threshold
        if not entries:
            raise ValueError(f"No legacy overrides: {legacy_path}")
        item_path = f"assets/minecraft/items/{carrier}.json"
        if any(name.endswith("/" + item_path) for name in names):
            raise ValueError(f"Audit modern item in existing overlays: {item_path}")
        vanilla = {"type": "minecraft:model", "model": f"minecraft:item/{carrier}"}
        definition = json.loads(source.read(item_path)) if item_path in names else {"model": vanilla}
        root = definition["model"]
        # Only the existing vanilla fallback is replaced: SF cases keep priority.
        selected = root
        if root.get("type") in {"select", "minecraft:select"}:
            if (root.get("property") != "minecraft:component"
                    or root.get("component") != "minecraft:custom_data"):
                raise ValueError(f"Audit modern item selector: {item_path}")
            selected = root.get("fallback", {})
        if (set(selected) != {"type", "model"}
                or selected["type"] not in {"model", "minecraft:model"}
                or selected["model"] not in {f"item/{carrier}", f"minecraft:item/{carrier}"}):
            raise ValueError(f"Audit modern item fallback: {item_path}")
        dispatch = {"type": "minecraft:range_dispatch", "property": "minecraft:custom_model_data",
                    "index": 0, "entries": entries, "fallback": selected}
        if selected is root:
            definition["model"] = dispatch
        else:
            root["fallback"] = dispatch
        result[item_path] = (json.dumps(definition, ensure_ascii=False, indent=2) + "\n").encode()
    if used_fallbacks != set(fallbacks):
        raise ValueError("Unused missing model fallbacks: audit the selected carriers")
    return result


def build(base: Path, output: Path, expected_sha256: str,
          language_patches: dict | None = None,
          model_patches: dict | None = None,
          legacy_item_bridges: list[str] | None = None,
          missing_model_fallbacks: dict[str, str] | None = None,
          extra_files: dict[str, bytes] | None = None) -> dict[str, object]:
    if base.resolve() == output.resolve():
        raise ValueError("The input pack must be preserved")
    if digest(base, "sha256") != expected_sha256:
        raise ValueError("Base pack SHA-256 does not match")
    with zipfile.ZipFile(base) as source:
        names = source.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries")
        languages = patch_languages(source, language_patches or {})
        models = patch_model_textures(source, model_patches or {})
        items = bridge_legacy_items(source, legacy_item_bridges if legacy_item_bridges is not None else [],
                                    missing_model_fallbacks)
        extra_files = extra_files or {}
        for name in extra_files:
            if (not re.fullmatch(r"assets/[a-z0-9_.-]+/[a-z0-9_./-]+", name)
                    or any(part in {".", "..", ""} for part in name.split("/"))):
                raise ValueError("Extra files must use safe resource paths under assets/")
            # These files are written after the base shader scan. Allowing one
            # here would bypass the overlay and expose legacy GLSL to 26.3.
            if is_shader(name):
                raise ValueError("Audit supplemental shaders before rebuilding")
        replacements = {**languages, **models, **items, **extra_files}
        metadata = json.loads(source.read("pack.mcmeta"))
        overlays = metadata.setdefault("overlays", {}).setdefault("entries", [])
        if any(entry["directory"] == OVERLAY for entry in overlays):
            raise ValueError("Base already contains the legacy shader overlay")
        # Refuse to silently leave a second legacy override active on 26.3.
        if any("/assets/" in name and is_shader("assets/" + name.split("/assets/", 1)[1])
               for name in names):
            raise ValueError("Audit shaders in existing overlays before rebuilding")
        shaders = sorted(name for name in names if is_shader(name) and not name.endswith("/"))
        if not shaders:
            raise ValueError("No legacy shaders found in the base pack")
        minimum = metadata["pack"].get("min_format", [metadata["pack"].get("pack_format", 0), 0])
        minimum_major = minimum[0] if isinstance(minimum, list) else minimum
        if minimum_major > MAX_LEGACY_FORMAT:
            raise ValueError("Base minimum is newer than the legacy shader range")
        overlays.append({
            "directory": OVERLAY,
            "formats": {"min_inclusive": minimum_major, "max_inclusive": MAX_LEGACY_FORMAT},
            "min_format": minimum,
            "max_format": [MAX_LEGACY_FORMAT, 65535],
        })
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for name in sorted(names):
                info = copy.copy(source.getinfo(name))
                if name in shaders:
                    info.filename = f"{OVERLAY}/{name}"
                content = (json.dumps(metadata, ensure_ascii=False, indent=2) + "\n").encode() \
                    if name == "pack.mcmeta" else replacements.get(name, source.read(name))
                target.writestr(info, content)
            for name in sorted((set(items) | set(extra_files)) - set(names)):
                info = zipfile.ZipInfo(name, date_time=source.getinfo("pack.mcmeta").date_time)
                info.compress_type = zipfile.ZIP_DEFLATED
                target.writestr(info, replacements[name])
    return {
        "base_sha256": expected_sha256,
        "sha256": digest(output, "sha256"),
        "sha1": digest(output, "sha1"),
        "bytes": output.stat().st_size,
        "legacy_shaders": shaders,
        "patched_languages": sorted(languages),
        "patched_models": sorted(models),
        "bridged_items": sorted(items),
        "missing_model_fallbacks": missing_model_fallbacks or {},
        "extra_files": sorted(extra_files),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--base-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--language-patches", type=Path,
                        help="Optional JSON mapping language paths to translation replacements")
    parser.add_argument("--model-patches", type=Path,
                        help="Optional JSON mapping model paths to existing texture-slot replacements")
    parser.add_argument("--legacy-item-bridges", type=Path,
                        help="Optional JSON list of CMD-only legacy carriers to bridge to modern items")
    parser.add_argument("--missing-model-fallbacks", type=Path,
                        help="Optional explicit substitutions for absent legacy models (modern items only)")
    parser.add_argument("--extra-dir", type=Path,
                        help="Directory whose files (relative to it, under assets/) are added or replace base files")
    parser.add_argument("--with-terralense", action="store_true",
                        help="Add the merged TerraLense minimap assets (see scripts/merge_terralense.py)")
    args = parser.parse_args()
    extra = {p.relative_to(args.extra_dir).as_posix(): p.read_bytes()
             for p in sorted(args.extra_dir.rglob("*")) if p.is_file()} if args.extra_dir else None
    if args.with_terralense:
        from merge_terralense import collect
        extra = {**(extra or {}), **collect()}
    patches = json.loads(args.language_patches.read_text()) if args.language_patches else None
    models = json.loads(args.model_patches.read_text()) if args.model_patches else None
    bridges = json.loads(args.legacy_item_bridges.read_text()) if args.legacy_item_bridges else None
    fallbacks = json.loads(args.missing_model_fallbacks.read_text()) if args.missing_model_fallbacks else None
    print(json.dumps(build(args.base, args.output, args.base_sha256, patches, models, bridges, fallbacks, extra), indent=2))


if __name__ == "__main__":
    main()
