#!/usr/bin/env python3
"""Valida los cases por id de gen_slimefun_svg.py: JSON valido, modelo y texturas existentes, PNG 128x128 con alfa."""
import glob
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
KEY = "slimefun:slimefun_item"
err, ids, modelos = [], 0, set()


def walk(o):
    global ids
    if isinstance(o, dict):
        if o.get("type") == "minecraft:model" and str(o.get("model", "")).startswith("slimefun/drakes_proc/"):
            modelos.add(o["model"])
        w = o.get("when")
        if isinstance(w, dict) and KEY in w.get("PublicBukkitValues", {}):
            ids += 1
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


for f in glob.glob(str(ROOT / "assets/minecraft/items/*.json")):
    try:
        walk(json.loads(Path(f).read_text(encoding="utf-8")))
    except Exception as e:  # noqa: BLE001
        err.append(f"JSON {f}: {e}")
tex = set()
for m in sorted(modelos):
    p = ROOT / "assets/minecraft/models" / f"{m}.json"
    if not p.exists():
        err.append(f"falta modelo {m}")
        continue
    for ref in json.loads(p.read_text())["textures"].values():
        tex.add(ref.split(":")[1])
for t in sorted(tex):
    p = ROOT / "assets/slimefun/textures" / f"{t}.png"
    if not p.exists():
        err.append(f"falta textura {t}")
        continue
    im = Image.open(p)
    if im.size != (128, 128) or im.convert("RGBA").getchannel("A").getextrema()[0] == 255:
        err.append(f"{t}: {im.size} {im.mode} (se espera 128x128 con transparencia)")
tam = sum(Path(f).stat().st_size for f in glob.glob(str(ROOT / "assets/slimefun/textures/item/drakes_proc/**/*.png"), recursive=True))
print(f"{ids} cases por id, {len(modelos)} modelos, {len(tex)} texturas ({tam / 1024:.0f} KiB PNG), {len(err)} errores")
for e in err[:30]:
    print(e)
sys.exit(1 if err else 0)
