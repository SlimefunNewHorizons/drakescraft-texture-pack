#!/usr/bin/env python3
"""Rebuild the T2 pack with legacy shaders restricted to pre-26.3 clients."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import zipfile


OVERLAY = "overlay_legacy_shaders"
MAX_LEGACY_FORMAT = 88  # Minecraft 26.2; 26.3 uses ShaderC/SPIR-V.


def is_shader(name: str) -> bool:
    parts = name.split("/")
    return len(parts) >= 4 and parts[0] == "assets" and parts[2] == "shaders"


def digest(path: Path, algorithm: str) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, algorithm).hexdigest()


def build(base: Path, output: Path, expected_sha256: str) -> dict[str, object]:
    if base.resolve() == output.resolve():
        raise ValueError("The input pack must be preserved")
    if digest(base, "sha256") != expected_sha256:
        raise ValueError("Base pack SHA-256 does not match")
    with zipfile.ZipFile(base) as source:
        names = source.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries")
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
                    if name == "pack.mcmeta" else source.read(name)
                target.writestr(info, content)
    return {
        "base_sha256": expected_sha256,
        "sha256": digest(output, "sha256"),
        "sha1": digest(output, "sha1"),
        "bytes": output.stat().st_size,
        "legacy_shaders": shaders,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--base-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.base, args.output, args.base_sha256), indent=2))


if __name__ == "__main__":
    main()
