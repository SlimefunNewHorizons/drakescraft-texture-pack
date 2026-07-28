#!/usr/bin/env python3
"""Build a verified DrakesCraft resource pack from a complete base pack."""

from __future__ import annotations

import argparse
import json
import zipfile
from collections.abc import Iterator, Mapping
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_BASE_ENTRIES = {"assets/minecraft/template.json"}
EXCLUDED_BASE_PREFIXES = ("assets/minecraft/models/slimefun/coronalis/",)


def source_files() -> Iterator[tuple[str, bytes]]:
    """Yield the tracked overrides which replace entries from the base pack."""
    for path in sorted((ROOT / "assets").rglob("*")):
        if path.is_file():
            yield path.relative_to(ROOT).as_posix(), path.read_bytes()
    for name in ("pack.mcmeta", "pack.png"):
        path = ROOT / name
        if path.is_file():
            yield name, path.read_bytes()


def read_base(base_pack: Path) -> dict[str, bytes]:
    """Load the complete base pack, omitting known invalid legacy metadata."""
    with zipfile.ZipFile(base_pack) as archive:
        return {
            entry.filename: archive.read(entry)
            for entry in archive.infolist()
            if not entry.is_dir()
            and entry.filename not in EXCLUDED_BASE_ENTRIES
            and not entry.filename.startswith(EXCLUDED_BASE_PREFIXES)
        }


def add_missing_slimefun_assets(entries: dict[str, bytes], asset_root: Path | None) -> None:
    """Fill only absent Slimefun textures from the canonical PortTextura tree."""
    if asset_root is None:
        return
    for path in sorted(asset_root.rglob("*")):
        if path.is_file():
            target = "assets/slimefun/" + path.relative_to(asset_root).as_posix()
            entries.setdefault(target, path.read_bytes())


def add_flat_item_models(entries: dict[str, bytes]) -> None:
    """Generate standard item models for namespace textures without a model file.

    Legacy DrakesCraft assets ship several UI textures but no 1.21 item-model
    documents. The new item definitions resolve ``namespace:item/path`` and
    therefore need a small generated model for each texture.
    """
    texture_prefix = "assets/"
    texture_marker = "/textures/item/"
    for name in sorted(tuple(entries)):
        if not name.startswith(texture_prefix) or texture_marker not in name or not name.endswith(".png"):
            continue
        namespace = name[len(texture_prefix) :].split("/", 1)[0]
        if namespace in {"minecraft", "slimefun"}:
            continue
        item_path = name.split(texture_marker, 1)[1][:-4]
        model_name = f"assets/{namespace}/models/item/{item_path}.json"
        entries.setdefault(
            model_name,
            json.dumps(
                {
                    "parent": "minecraft:item/generated",
                    "textures": {"layer0": f"{namespace}:item/{item_path}"},
                },
                separators=(",", ":"),
            ).encode("utf-8"),
        )


def references_slimefun_model(value: object) -> bool:
    """Return whether a definition branch points to a Slimefun model."""
    if isinstance(value, Mapping):
        return any(
            key == "model"
            and isinstance(child, str)
            and (child.startswith("slimefun/") or child.startswith("minecraft:slimefun/"))
            or references_slimefun_model(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(references_slimefun_model(child) for child in value)
    return False


def keep_slimefun_cases(value: object) -> object:
    """Drop item-definition selector cases that are not Slimefun entries."""
    if isinstance(value, Mapping):
        filtered: dict[str, object] = {}
        for key, child in value.items():
            if key == "cases" and isinstance(child, list):
                filtered[key] = [
                    keep_slimefun_cases(case)
                    for case in child
                    if references_slimefun_model(case)
                ]
            else:
                filtered[key] = keep_slimefun_cases(child)
        return filtered
    if isinstance(value, list):
        return [keep_slimefun_cases(child) for child in value]
    return value


def sf_only_source_files() -> Iterator[tuple[str, bytes]]:
    """Yield a minimal pack: Slimefun assets plus its required item selectors."""
    for name in ("pack.mcmeta", "pack.png"):
        path = ROOT / name
        if path.is_file():
            yield name, path.read_bytes()

    for directory in (
        ROOT / "assets" / "minecraft" / "models" / "slimefun",
        ROOT / "assets" / "slimefun",
    ):
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                yield path.relative_to(ROOT).as_posix(), path.read_bytes()

    item_root = ROOT / "assets" / "minecraft" / "items"
    for path in sorted(item_root.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        if not references_slimefun_model(document):
            continue
        filtered = keep_slimefun_cases(document)
        yield (
            path.relative_to(ROOT).as_posix(),
            json.dumps(filtered, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
        )


def parse_reference(value: object, default_namespace: str = "minecraft") -> tuple[str, str] | None:
    if not isinstance(value, str) or value.startswith("#"):
        return None
    if ":" in value:
        namespace, path = value.split(":", 1)
    else:
        namespace, path = default_namespace, value
    return namespace, path


def walk_mapping(value: object) -> Iterator[tuple[str, object]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield key, child
            yield from walk_mapping(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_mapping(child)


def validate(entries: Mapping[str, bytes]) -> None:
    """Reject malformed JSON and unresolved resource references owned by this pack."""
    documents: dict[str, object] = {}
    for name, content in entries.items():
        if name.startswith("assets/") and name.endswith(".json"):
            try:
                documents[name] = json.loads(content.decode("utf-8-sig"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid JSON in {name}: {exc}") from exc

    missing: set[str] = set()
    for name, document in documents.items():
        if "/models/" not in name and "/items/" not in name:
            continue
        for key, value in walk_mapping(document):
            if key in {"model", "parent"}:
                reference = parse_reference(value)
                if reference is not None:
                    namespace, path = reference
                    if namespace == "minecraft" and path.startswith("slimefun/"):
                        target = f"assets/minecraft/models/{path}.json"
                        if target not in entries:
                            missing.add(target)
                    # The legacy Slimefun model tree is namespaced as
                    # minecraft/slimefun while its textures use slimefun.
                    # Some historical base-pack entries still use the latter
                    # in model metadata, so only validate external namespaces.
                    elif namespace not in {"minecraft", "slimefun"}:
                        target = f"assets/{namespace}/models/{path}.json"
                        if target not in entries:
                            missing.add(target)
            if key in {"layer0", "layer1", "layer2", "particle"}:
                reference = parse_reference(value)
                if reference is not None:
                    namespace, path = reference
                    if namespace == "slimefun":
                        target = f"assets/slimefun/textures/{path}.png"
                        if target not in entries:
                            missing.add(target)
                    elif namespace != "minecraft":
                        target = f"assets/{namespace}/textures/{path}.png"
                        if target not in entries:
                            missing.add(target)
    if missing:
        raise ValueError("Missing custom assets:\n" + "\n".join(sorted(missing)))


def build(base_pack: Path, output: Path, slimefun_assets: Path | None) -> None:
    entries = read_base(base_pack)
    entries.update(dict(source_files()))
    add_missing_slimefun_assets(entries, slimefun_assets)
    add_flat_item_models(entries)
    validate(entries)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            archive.writestr(name, entries[name])


def build_sf_only(output: Path, slimefun_assets: Path) -> None:
    """Build a pack that changes only Slimefun items and their guide assets."""
    entries = dict(sf_only_source_files())
    add_missing_slimefun_assets(entries, slimefun_assets)
    validate(entries)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            archive.writestr(name, entries[name])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, help="Complete prior resource-pack ZIP")
    parser.add_argument(
        "--slimefun-assets",
        type=Path,
        help="Canonical assets/slimefun directory used only for missing files",
    )
    parser.add_argument(
        "--sf-only",
        action="store_true",
        help="Build only Slimefun models, textures and item selectors",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output ZIP path")
    args = parser.parse_args()
    if args.sf_only:
        if args.slimefun_assets is None:
            parser.error("--sf-only requires --slimefun-assets")
        build_sf_only(args.output, args.slimefun_assets)
    elif args.base is None:
        parser.error("--base is required unless --sf-only is used")
    else:
        build(args.base, args.output, args.slimefun_assets)
    print(f"Built {args.output}")


if __name__ == "__main__":
    main()
