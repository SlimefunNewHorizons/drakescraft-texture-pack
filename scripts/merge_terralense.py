#!/usr/bin/env python3
"""Fusiona los assets que TerraLense genera en el pack del repo (reproducible).

Entrada: TerraLense-Pack.zip generado una vez con `resource-pack.mode: generate`,
`self-host.enabled: false`, `url: ''` (plugins/TerraLense/pack/TerraLense-Pack.zip).
Salida: assets/minecraft/font/terralense_hud*.json y assets/terralense/** en este repo.
NUNCA copia pack.mcmeta ni shaders. Con --check solo compara, sin escribir.
Uso: merge_terralense.py --zip TerraLense-Pack.zip [--check]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FONT_DIR = "assets/minecraft/font/"
TEX_DIR = "assets/terralense/textures/font/"
FONTS = {FONT_DIR + "terralense_hud.json", FONT_DIR + "terralense_hud_top.json"}
EXPECTED = {"cell_": 24, "arrow_": 16, "marker_": 96}  # 136 PNG


def wanted(name: str) -> bool:
    return name in FONTS or (name.startswith(TEX_DIR) and name.endswith(".png"))


def validate(files: dict[str, bytes], default_font: Path | None = None) -> None:
    """Falla (SystemExit) si el conjunto no es el esperado o puede chocar con el pack."""
    missing = FONTS - files.keys()
    if missing:
        sys.exit(f"faltan fuentes: {sorted(missing)}")
    pngs = {n for n in files if n.startswith(TEX_DIR)}
    for prefix, count in EXPECTED.items():
        got = sum(1 for n in pngs if n[len(TEX_DIR):].startswith(prefix))
        if got != count:
            sys.exit(f"se esperaban {count} PNG '{prefix}*', hay {got}")
    if len(pngs) != sum(EXPECTED.values()):
        sys.exit(f"se esperaban {sum(EXPECTED.values())} PNG, hay {len(pngs)}")
    for name in FONTS:
        for prov in json.loads(files[name])["providers"]:
            ref = prov.get("file")
            if ref:
                ns, _, path = ref.partition(":")
                if ns != "terralense":
                    sys.exit(f"{name}: proveedor fuera del namespace terralense: {ref}")
                if f"assets/terralense/textures/{path}" not in files:
                    sys.exit(f"{name}: textura inexistente: {ref}")
    if default_font and default_font.exists():
        # default.json no debe referenciar terralense (no hay fusion ahi) y sus codepoints
        # viven en otra fuente: no hay colision posible, solo se comprueba que no los toquemos.
        if b"terralense" in default_font.read_bytes():
            sys.exit("default.json ya referencia terralense: revisar a mano")


def read_zip(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in sorted(z.namelist()) if wanted(n)}


def collect(repo: Path = REPO) -> dict[str, bytes]:
    """Ficheros fusionados del repo (rutas assets/...), para build_t2_pack.py --with-terralense."""
    files = {}
    for p in sorted(repo.joinpath("assets/terralense").rglob("*")):
        if p.is_file():
            files[p.relative_to(repo).as_posix()] = p.read_bytes()
    for name in sorted(FONTS):
        if (repo / name).is_file():
            files[name] = (repo / name).read_bytes()
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", required=True, type=Path)
    ap.add_argument("--repo", type=Path, default=REPO)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    files = read_zip(args.zip)
    validate(files, args.repo / FONT_DIR / "default.json")
    changed = [n for n, d in files.items()
               if not (args.repo / n).is_file() or (args.repo / n).read_bytes() != d]
    if args.check:
        sys.exit(f"{len(changed)} ficheros difieren" if changed else None)
    for n in changed:
        out = args.repo / n
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(files[n])
    sha1 = hashlib.sha1(args.zip.read_bytes()).hexdigest()
    print(json.dumps({"zip_sha1": sha1, "files": len(files), "written": len(changed)}))


if __name__ == "__main__":
    main()
