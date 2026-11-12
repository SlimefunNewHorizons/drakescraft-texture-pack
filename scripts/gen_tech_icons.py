#!/usr/bin/env python3
"""Iconos 128px + modelos + items de la armadura tecnologica (4 colores). Uso: gen_tech_icons.py"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import gen_tools_hd as g
ACC = {"cyan": "#35e4ff", "magenta": "#ff3fd8", "gold": "#ffc933", "green": "#4dff88"}
root = Path(".")
for c, e in ACC.items():
    g.MATS[f"tech_{c}"] = ("#7b88a6", "#3d475e", "#1a2030", "#05070d", e)
    for kind in ("helmet", "chestplate", "leggings", "boots"):
        nm = f"tech_{c}_{kind}"
        svg = g.armor_icon(f"tech_{c}", nm, kind)
        sp = root/"assets/drakescraft/textures/gear/svg_hd"/f"{nm}.svg"; sp.parent.mkdir(parents=True, exist_ok=True); sp.write_text(svg)
        png = root/"assets/drakescraft/textures/item"/f"{nm}.png"
        subprocess.run(["rsvg-convert", "-w", "128", "-h", "128", str(sp), "-o", str(png)], check=True)
        m = root/"assets/drakescraft/models/item"/f"{nm}.json"; m.write_text(json.dumps({"parent": "minecraft:item/generated", "textures": {"layer0": f"drakescraft:item/{nm}"}}, indent=2))
        i = root/"assets/drakescraft/items"/f"{nm}.json"; i.parent.mkdir(parents=True, exist_ok=True)
        i.write_text(json.dumps({"model": {"type": "minecraft:model", "model": f"drakescraft:item/{nm}"}}, indent=2))
print("ok")
