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
            if not entry.is_dir() and entry.filename not in EXCLUDED_BASE_ENTRIES
        }


def add_missing_slimefun_assets(entries: dict[str, bytes], asset_root: Path | None) -> None:
    """Fill only absent Slimefun textures from the canonical PortTextura tree."""
    if asset_root is None:
        return
    for path in sorted(asset_root.rglob("*")):
        if path.is_file():
            target = "assets/slimefun/" + path.relative_to(asset_root).as_posix()
            entries.setdefault(target, path.read_bytes())


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
    """Reject malformed JSON and unresolved custom Slimefun resource references."""
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
            if key in {"layer0", "layer1", "layer2", "particle"}:
                reference = parse_reference(value)
                if reference is not None:
                    namespace, path = reference
                    if namespace == "slimefun":
                        target = f"assets/slimefun/textures/{path}.png"
                        if target not in entries:
                            missing.add(target)
    if missing:
        raise ValueError("Missing custom assets:\n" + "\n".join(sorted(missing)))


def build(base_pack: Path, output: Path, slimefun_assets: Path | None) -> None:
    entries = read_base(base_pack)
    entries.update(dict(source_files()))
    add_missing_slimefun_assets(entries, slimefun_assets)
    validate(entries)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(entries):
            archive.writestr(name, entries[name])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path, help="Complete prior resource-pack ZIP")
    parser.add_argument(
        "--slimefun-assets",
        type=Path,
        help="Canonical assets/slimefun directory used only for missing files",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output ZIP path")
    args = parser.parse_args()
    build(args.base, args.output, args.slimefun_assets)
    print(f"Built {args.output}")


if __name__ == "__main__":
    main()
