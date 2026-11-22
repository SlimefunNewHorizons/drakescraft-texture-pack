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
import tempfile
import zipfile


OVERLAY = "overlay_legacy_shaders"
MAX_LEGACY_FORMAT = 88  # Minecraft 26.2; 26.3 uses ShaderC/SPIR-V.
PLACEHOLDER = re.compile(r"%(?:\d+\$)?[sd]|%%")
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CUBE_FACES = {"down", "up", "north", "south", "west", "east"}


def valid_number_list(value: object, length: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == length
        and all(type(item) in {int, float} and math.isfinite(item) for item in value)
    )


def valid_resource_reference(value: object) -> str | None:
    if not isinstance(value, str) or not re.fullmatch(r"(?:[a-z0-9_.-]+:)?[a-z0-9_./-]+", value):
        return None
    reference = value if ":" in value else "minecraft:" + value
    _, path = reference.split(":", 1)
    if any(part in {".", "..", ""} for part in path.split("/")):
        return None
    return reference


def valid_texture_mcmeta(payload: bytes) -> bool:
    try:
        node = json.loads(payload)
    except (ValueError, UnicodeError):
        return False
    if not isinstance(node, dict) or not node:
        return False
    if "animation" in node:
        anim = node["animation"]
        if not isinstance(anim, dict):
            return False
        for key in ("frametime", "width", "height"):
            if key in anim and (type(anim[key]) is not int or anim[key] <= 0):
                return False
        if "interpolate" in anim and type(anim["interpolate"]) is not bool:
            return False
        if "frames" in anim:
            frames = anim["frames"]
            if not isinstance(frames, list):
                return False
            for frame in frames:
                if type(frame) is int:
                    if frame < 0:
                        return False
                elif isinstance(frame, dict):
                    if type(frame.get("index")) is not int or frame["index"] < 0:
                        return False
                    if "time" in frame and (type(frame["time"]) is not int or frame["time"] <= 0):
                        return False
                else:
                    return False
    return True


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


def required_model_references(source, replacements, metadata, required):
    """Find incoming model/parent references in the planned loadable resources."""
    found = {reference: set() for reference in required}
    if not found:
        return {}
    prefixes = [""] + [entry["directory"] + "/"
                         for entry in metadata.get("overlays", {}).get("entries", [])]

    def references(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"model", "parent"} and isinstance(value, str):
                    yield value if ":" in value else "minecraft:" + value
                yield from references(value)
        elif isinstance(node, list):
            for value in node:
                yield from references(value)

    for name in sorted(set(source.namelist()) | set(replacements)):
        logical = next((name[len(prefix):] for prefix in prefixes
                        if name.startswith(prefix) and re.fullmatch(
                            r"assets/[a-z0-9_.-]+/(?:items|models)/[a-z0-9_./-]+\.json",
                            name[len(prefix):])), None)
        if logical is None or any(part in {".", "..", ""} for part in logical.split("/")):
            continue
        content = replacements[name] if name in replacements else source.read(name)
        try:
            node = json.loads(content)
        except (ValueError, UnicodeError):
            continue
        for reference in references(node):
            if reference in found:
                namespace, path = reference.split(":", 1)
                if logical != f"assets/{namespace}/models/{path}.json":
                    found[reference].add(name)
    for reference, sources in found.items():
        if not sources:
            raise ValueError(f"Unreferenced required model: {reference}")
    return {reference: sorted(sources) for reference, sources in found.items()}


def required_model_parent_chains(source, replacements, required, metadata):
    """Reject root parent cycles and unaudited overlay substitutions."""
    names = set(source.namelist()) | set(replacements)
    prefixes = [entry["directory"] + "/"
                for entry in metadata.get("overlays", {}).get("entries", [])]
    chains = {}
    for reference in required:
        chain = []
        seen = set()
        current = reference
        while current is not None:
            if current in seen:
                raise ValueError("Required model parent cycle: " + " -> ".join(chain + [current]))
            seen.add(current)
            chain.append(current)
            namespace, path = current.split(":", 1)
            name = f"assets/{namespace}/models/{path}.json"
            content = (replacements[name] if name in replacements else source.read(name)) \
                if name in names else None
            # A declared overlay can replace the checked model or any parent,
            # including a vanilla parent absent from this ZIP. Require review
            # of differing bytes even if its range may currently be inactive.
            for prefix in prefixes:
                overlay_name = prefix + name
                if overlay_name in names:
                    overlay_content = replacements[overlay_name] if overlay_name in replacements \
                        else source.read(overlay_name)
                    if overlay_content != content:
                        raise ValueError(f"Audit required model parent in overlay: {overlay_name}")
            # Vanilla/builtin resources may be supplied by the client. This
            # check detects local cycles; it does not certify dependencies.
            if name not in names:
                break
            try:
                node = json.loads(content)
            except (ValueError, UnicodeError) as exc:
                raise ValueError(f"Invalid required model parent JSON: {name}") from exc
            if not isinstance(node, dict):
                raise ValueError(f"Expected required model parent object: {name}")
            current = node.get("parent")
            if current is not None:
                if (not isinstance(current, str)
                        or not re.fullmatch(r"(?:[a-z0-9_.-]+:)?[a-z0-9_./-]+", current)
                        or any(part in {".", "..", ""} for part in current.split(":")[-1].split("/"))):
                    raise ValueError(f"Invalid required model parent: {name}")
                if ":" not in current:
                    current = "minecraft:" + current
        chains[reference] = chain
    return chains


def audit_required_model_reference_overlays(source, replacements, metadata, incoming):
    """Reject overlay variants that can shadow an incoming reference source."""
    names = set(source.namelist()) | set(replacements)
    prefixes = [""] + [entry["directory"] + "/"
                       for entry in metadata.get("overlays", {}).get("entries", [])]
    checked = set()
    for sources in incoming.values():
        for name in sources:
            # Incoming sources already passed the loadable-resource path check.
            logical = next(name[len(prefix):] for prefix in prefixes
                           if name.startswith(prefix) and re.fullmatch(
                               r"assets/[a-z0-9_.-]+/(?:items|models)/[a-z0-9_./-]+\.json",
                               name[len(prefix):]))
            if logical in checked:
                continue
            checked.add(logical)
            variants = [prefix + logical for prefix in prefixes if prefix + logical in names]
            content = replacements[name] if name in replacements else source.read(name)
            for variant in variants:
                other = replacements[variant] if variant in replacements else source.read(variant)
                if other != content:
                    raise ValueError(f"Audit required model reference in overlay: {variant}")


def required_model_textures(source, replacements, metadata, parent_chains):
    """Validate geometry, texture slots, PNG/mcmeta files and overlay variants for required models."""
    names = set(source.namelist()) | set(replacements)
    overlay_prefixes = [entry["directory"] + "/"
                        for entry in metadata.get("overlays", {}).get("entries", [])]
    result = {}
    for reference, chain in parent_chains.items():
        merged_textures = {}
        face_slots = []
        for current in reversed(chain):
            namespace, model_path = current.split(":", 1)
            root_model = f"assets/{namespace}/models/{model_path}.json"
            if root_model not in names:
                continue
            content = replacements[root_model] if root_model in replacements else source.read(root_model)
            node = json.loads(content)
            if "textures" in node:
                textures = node["textures"]
                if not isinstance(textures, dict):
                    raise ValueError(f"Invalid required model textures: {root_model}")
                for slot, raw_ref in textures.items():
                    if (not isinstance(slot, str)
                            or not re.fullmatch(r"[a-zA-Z0-9_.-]+", slot)
                            or not isinstance(raw_ref, str)):
                        raise ValueError(f"Invalid required model texture slot: {root_model}")
                    if raw_ref.startswith("#"):
                        if not re.fullmatch(r"#[a-zA-Z0-9_.-]+", raw_ref):
                            raise ValueError(f"Invalid required model texture alias: {root_model}")
                        merged_textures[slot] = raw_ref
                    else:
                        normalized = valid_resource_reference(raw_ref)
                        if normalized is None:
                            raise ValueError(f"Invalid required model texture reference: {root_model}")
                        merged_textures[slot] = normalized
            if "elements" in node:
                elements = node["elements"]
                if not isinstance(elements, list):
                    raise ValueError(f"Invalid required model elements: {root_model}")
                current_slots = []
                for element in elements:
                    if not isinstance(element, dict):
                        raise ValueError(f"Invalid required model element: {root_model}")
                    for coord_key in ("from", "to"):
                        if coord_key in element and not valid_number_list(element[coord_key], 3):
                            raise ValueError(f"Invalid required model element {coord_key}: {root_model}")
                    faces = element.get("faces")
                    if not isinstance(faces, dict) or not faces:
                        raise ValueError(f"Invalid required model element faces: {root_model}")
                    for direction, face in faces.items():
                        if direction not in CUBE_FACES or not isinstance(face, dict):
                            raise ValueError(f"Invalid required model face: {root_model}")
                        if "uv" in face and not valid_number_list(face["uv"], 4):
                            raise ValueError(f"Invalid required model face uv: {root_model}")
                        if "cullface" in face and face["cullface"] not in CUBE_FACES:
                            raise ValueError(f"Invalid required model face cullface: {root_model}")
                        if "rotation" in face and (
                            type(face["rotation"]) is not int
                            or face["rotation"] not in {0, 90, 180, 270}
                        ):
                            raise ValueError(f"Invalid required model face rotation: {root_model}")
                        tex = face.get("texture")
                        if not isinstance(tex, str) or not re.fullmatch(r"#[a-zA-Z0-9_.-]+", tex):
                            raise ValueError(f"Invalid required model face texture: {root_model}")
                        current_slots.append(tex[1:])
                face_slots = current_slots
        for slot in face_slots:
            if slot not in merged_textures:
                raise ValueError(f"Undefined required model face texture slot: {reference}: #{slot}")
        resolved_refs = set()
        for slot in sorted(merged_textures):
            visited = {slot}
            target = merged_textures[slot]
            while isinstance(target, str) and target.startswith("#"):
                next_slot = target[1:]
                if next_slot in visited:
                    raise ValueError(f"Required model texture slot cycle: {reference}: #{slot}")
                if next_slot not in merged_textures:
                    raise ValueError(f"Undefined required model texture slot: {reference}: #{next_slot}")
                visited.add(next_slot)
                target = merged_textures[next_slot]
            if isinstance(target, str) and not target.startswith("#"):
                resolved_refs.add(target)
        textures_report = []
        for texture_ref in sorted(resolved_refs):
            tex_ns, tex_path = texture_ref.split(":", 1)
            root_png = f"assets/{tex_ns}/textures/{tex_path}.png"
            root_mcmeta = root_png + ".mcmeta"
            custom_required = (
                tex_ns != "minecraft"
                or tex_path == "custom"
                or tex_path.startswith("custom/")
                or "/custom/" in tex_path
            )
            png_bytes = None
            root_sha256 = None
            if root_png in replacements:
                png_bytes = replacements[root_png]
            elif root_png in names and not source.getinfo(root_png).is_dir():
                png_bytes = source.read(root_png)
            if png_bytes is not None:
                if not png_bytes.startswith(PNG_SIGNATURE):
                    raise ValueError(f"Invalid required model texture PNG signature: {root_png}")
                root_sha256 = hashlib.sha256(png_bytes).hexdigest()
            elif custom_required:
                raise ValueError(f"Missing required model texture: {root_png}")
            mcmeta_bytes = None
            root_mcmeta_sha256 = None
            if root_mcmeta in replacements:
                mcmeta_bytes = replacements[root_mcmeta]
            elif root_mcmeta in names and not source.getinfo(root_mcmeta).is_dir():
                mcmeta_bytes = source.read(root_mcmeta)
            if mcmeta_bytes is not None:
                if not valid_texture_mcmeta(mcmeta_bytes):
                    raise ValueError(f"Invalid required model texture mcmeta: {root_mcmeta}")
                root_mcmeta_sha256 = hashlib.sha256(mcmeta_bytes).hexdigest()
            for prefix in overlay_prefixes:
                overlay_png = prefix + root_png
                if overlay_png in names:
                    ov_png = replacements[overlay_png] if overlay_png in replacements else source.read(overlay_png)
                    if ov_png != png_bytes:
                        raise ValueError(f"Audit required model texture in overlay: {overlay_png}")
                overlay_mcmeta = prefix + root_mcmeta
                if overlay_mcmeta in names:
                    ov_mcmeta = (replacements[overlay_mcmeta]
                                 if overlay_mcmeta in replacements else source.read(overlay_mcmeta))
                    if ov_mcmeta != mcmeta_bytes:
                        raise ValueError(f"Audit required model texture mcmeta in overlay: {overlay_mcmeta}")
            textures_report.append({
                "texture": texture_ref,
                "path": root_png,
                "present": root_sha256 is not None,
                "sha256": root_sha256,
                "mcmeta_sha256": root_mcmeta_sha256,
            })
        result[reference] = textures_report
    return result


def build(base: Path, output: Path, expected_sha256: str,
          language_patches: dict | None = None,
          model_patches: dict | None = None,
          legacy_item_bridges: list[str] | None = None,
          missing_model_fallbacks: dict[str, str] | None = None,
          extra_files: dict[str, bytes] | None = None,
          required_models: list[str] | None = None) -> dict[str, object]:
    if base.resolve() == output.resolve():
        raise ValueError("The input pack must be preserved")
    if digest(base, "sha256") != expected_sha256:
        raise ValueError("Base pack SHA-256 does not match")
    with zipfile.ZipFile(base) as source:
        names = source.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP entries")
        # Read every member before opening the output. A matching archive hash
        # does not guarantee valid member CRCs; a late failure would truncate an
        # existing candidate after some entries had already been written.
        if source.testzip() is not None:
            raise ValueError("Base pack CRC check failed")
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
        # Check the planned output, including replacements, before touching the
        # destination. A fallback or a model in an overlay cannot satisfy a
        # requirement for the original root resource.
        checked_models = {}
        for reference in required_models or []:
            if (not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_./-]+", reference)
                    or any(part in {".", "..", ""} for part in reference.split(":", 1)[1].split("/"))):
                raise ValueError(f"Invalid required model reference: {reference}")
            namespace, path = reference.split(":", 1)
            name = f"assets/{namespace}/models/{path}.json"
            if name in replacements:
                content = replacements[name]
            elif name in names and not source.getinfo(name).is_dir():
                content = source.read(name)
            else:
                raise ValueError(f"Missing required model: {name}")
            try:
                model = json.loads(content)
            except (ValueError, UnicodeDecodeError) as exc:
                raise ValueError(f"Invalid required model JSON: {name}") from exc
            if not isinstance(model, dict) or not model:
                raise ValueError(f"Expected a nonempty required model object: {name}")
            checked_models[reference] = hashlib.sha256(content).hexdigest()
        metadata = json.loads(source.read("pack.mcmeta"))
        incoming = required_model_references(source, replacements, metadata, checked_models)
        parent_chains = required_model_parent_chains(source, replacements, checked_models, metadata)
        model_textures = required_model_textures(source, replacements, metadata, parent_chains)
        audit_required_model_reference_overlays(source, replacements, metadata, incoming)
        overlays = metadata.setdefault("overlays", {}).setdefault("entries", [])
        if any(entry["directory"] == OVERLAY for entry in overlays):
            raise ValueError("Base already contains the legacy shader overlay")
        if any(name.startswith(f"{OVERLAY}/") for name in names):
            raise ValueError("Base contains files in the legacy shader overlay directory")
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
        # Stage on the destination filesystem so replacement is atomic. CRC
        # preflight cannot protect an earlier candidate from a write failure.
        with tempfile.TemporaryDirectory(prefix=f".{output.name}.", dir=output.parent) as directory:
            candidate = Path(directory) / "candidate.zip"
            with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED) as target:
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
            candidate.replace(output)
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
        "required_models_sha256": checked_models,
        "required_model_references": incoming,
        "required_model_parent_chains": parent_chains,
        "required_model_textures": model_textures,
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
    parser.add_argument("--require-model", action="append", default=[], metavar="NAMESPACE:PATH",
                        help="Require a nonempty root model JSON, an incoming reference, no local root parent cycle and no differing declared overlay parent or reference source before writing (repeatable; does not verify provenance or render)")
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
    print(json.dumps(build(args.base, args.output, args.base_sha256, patches, models, bridges, fallbacks,
                           extra, args.require_model), indent=2))


if __name__ == "__main__":
    main()
