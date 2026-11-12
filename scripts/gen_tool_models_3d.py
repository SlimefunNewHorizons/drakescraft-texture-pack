#!/usr/bin/env python3
"""Modelos 3D (cuboides) de espada/pico/hacha de netherita y diamante, estilo kintsugi.

Genera:
  assets/drakescraft/textures/gear/svg/gear3d_<mat>.svg       (fuente)
  assets/drakescraft/textures/item/gear3d/<mat>.png            (16x16, SVG -> PNG con rsvg-convert, o PIL de respaldo)
  assets/drakescraft/models/item/gear3d/<mat>_<tool>.json      (modelos con display)
y engancha `drakescraft:item/gear3d/<id>` como fallback en assets/minecraft/items/<id>.json
(conserva los cases Slimefun). Termina validando JSON y rutas.
Las piezas se modelan verticales (eje Y) y cada elemento gira -45 grados en Z para quedar en la diagonal del handheld.
Uso: gen_tool_models_3d.py [--root .]
"""
import argparse
import json
import random
import subprocess
import sys
from pathlib import Path
from PIL import Image

NS = "drakescraft"
MATS = {  # base, luz, sombra (estilo contenido: oscuro, acento minimo)
    "wooden": ("#5a3d22", "#8a6838", "#33210f"),
    "stone": ("#4a4f63", "#7a809a", "#262938"),
    "iron": ("#6a7388", "#aeb7c8", "#2c3242"),
    "golden": ("#8a6a24", "#c9a24a", "#3a2c10"),
    "diamond": ("#1f6f7c", "#5fd6e4", "#0c2a33"),
    "netherite": ("#2d2638", "#54466a", "#16121e"),
    "copper": ("#8a4a2c", "#d2794a", "#3a1c10"),
    "mace": ("#2a1f3d", "#7c3aed", "#120b1e"),
}
TOOL_MATS = ["wooden", "stone", "iron", "golden", "diamond", "netherite", "copper"]
GOLD, GOLD_D, GOLD_L, WHITE, OUT = "#b08a30", "#684e1a", "#d6b860", "#e8e4f0", "#0d0a14"
HANDLE, HANDLE_L = "#6b4a2b", "#8f6a3c"
Q = {"plate": (0, 0), "edge": (8, 0), "gold": (0, 8), "grip": (8, 8)}  # cuadrantes 8x8 del atlas 16x16


def atlas(mat):
    b, l, d = MATS[mat]
    rng = random.Random("atlas-" + mat)
    px = {}
    for qn, (qx, qy) in Q.items():
        for j in range(8):
            for i in range(8):
                if qn == "plate":
                    c = b if (i + j) % 4 else d
                    if i in (0, 7) or j in (0, 7):
                        c = d
                elif qn == "edge":
                    c = l if i < 5 else b
                    if j == 7:
                        c = d
                elif qn == "gold":
                    c = GOLD if (i + j) % 5 else GOLD_L
                    if i == 7 or j == 7:
                        c = GOLD_D
                else:
                    c = HANDLE if (j // 2) % 2 == 0 else HANDLE_L
                    if j % 4 == 3:
                        c = GOLD_D
                px[(qx + i, qy + j)] = c
    # grieta de oro y estrellitas sobre la placa
    x = 2
    for y in range(1, 7):
        px[(x, y)] = GOLD
        x = max(1, min(6, x + rng.choice((-1, 0, 1))))
    px[(5, 2)] = WHITE
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        px[(5 + dx, 2 + dy)] = GOLD_L
    px[(1, 6)] = WHITE
    px[(9, 3)] = WHITE   # brillo en el filo
    px[(10, 5)] = WHITE
    return px


def write_svg_png(mat, root):
    px = atlas(mat)
    svg = root / f"assets/{NS}/textures/gear/svg/gear3d_{mat}.svg"
    png = root / f"assets/{NS}/textures/item/gear3d/{mat}.png"
    svg.parent.mkdir(parents=True, exist_ok=True)
    png.parent.mkdir(parents=True, exist_ok=True)
    rects = [f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>' for (x, y), c in sorted(px.items(), key=lambda t: (t[0][1], t[0][0]))]
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" shape-rendering="crispEdges">\n'
                   + "\n".join(rects) + "\n</svg>\n", encoding="utf-8")
    try:
        subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", "-o", str(png), str(svg)], check=True)
    except (OSError, subprocess.CalledProcessError):
        im = Image.new("RGBA", (16, 16))
        for (x, y), c in px.items():
            im.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,))
        im.save(png)


def el(frm, to, quad, rot=True):
    """Cuboide con las 6 caras mapeadas al cuadrante del atlas; gira -45 en Z sobre el centro (8,8,8)."""
    qx, qy = Q[quad]
    uv = [qx, qy, qx + 8, qy + 8]
    e = {"from": frm, "to": to, "faces": {f: {"uv": uv, "texture": "#0"} for f in ("north", "east", "south", "west", "up", "down")}}
    if rot:
        e["rotation"] = {"angle": -45, "axis": "z", "origin": [8, 8, 8]}
    return e


def sword():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),          # pomo
        el([7.5, 0.5, 7.5], [8.5, 4, 8.5], "grip"),              # empunadura
        el([4.5, 4, 7.0], [11.5, 5.2, 9.0], "gold"),            # guarda
        el([6.5, 5.2, 7.6], [9.5, 15.5, 8.4], "plate"),         # hoja
        el([7.5, 5.2, 7.2], [8.5, 15.5, 8.8], "edge"),          # lomo central
        el([7.0, 15.5, 7.7], [9.0, 17.5, 8.3], "plate"),        # punta
        el([7.6, 17.5, 7.8], [8.4, 18.8, 8.2], "edge"),
    ]


def pickaxe():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),
        el([7.5, 0.5, 7.5], [8.5, 14, 8.5], "grip"),            # mango largo
        el([7.0, 11.5, 7.0], [9.0, 12.5, 9.0], "gold"),         # collar
        el([1.5, 12.5, 7.0], [14.5, 14.2, 9.0], "plate"),       # cabeza
        el([0.0, 11.5, 7.3], [2.0, 13.5, 8.7], "edge"),         # punta izq
        el([14.0, 11.5, 7.3], [16.0, 13.5, 8.7], "edge"),       # punta der
        el([6.5, 14.2, 7.3], [9.5, 15.2, 8.7], "gold"),         # cresta
    ]


def axe():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),
        el([7.5, 0.5, 7.5], [8.5, 14, 8.5], "grip"),
        el([7.0, 11.5, 7.0], [9.0, 12.5, 9.0], "gold"),
        el([2.5, 10.0, 7.2], [8.5, 15.5, 8.8], "plate"),        # cuerpo de la hoja (hacia -X)
        el([0.5, 9.0, 7.5], [2.5, 16.5, 8.5], "edge"),          # filo
        el([8.5, 12.5, 7.3], [10.5, 15.0, 8.7], "gold"),        # contrapeso
    ]


def shovel():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),
        el([7.5, 0.5, 7.5], [8.5, 13, 8.5], "grip"),
        el([7.0, 11.5, 7.0], [9.0, 12.5, 9.0], "gold"),
        el([5.8, 12.5, 7.4], [10.2, 16.8, 8.6], "plate"),       # pala
        el([5.0, 12.5, 7.1], [5.8, 16.5, 8.9], "edge"),         # bordes elevados
        el([10.2, 12.5, 7.1], [11.0, 16.5, 8.9], "edge"),
        el([6.4, 16.8, 7.5], [9.6, 18.0, 8.5], "edge"),
    ]


def hoe():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),
        el([7.5, 0.5, 7.5], [8.5, 14, 8.5], "grip"),
        el([7.0, 11.5, 7.0], [9.0, 12.5, 9.0], "gold"),
        el([2.0, 12.6, 7.3], [9.0, 14.2, 8.7], "plate"),        # cuchilla hacia -X
        el([1.5, 10.6, 7.4], [3.5, 12.6, 8.6], "edge"),         # punta hacia abajo
        el([8.6, 14.2, 7.4], [10.0, 15.2, 8.6], "gold"),
    ]


def spear():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),
        el([7.5, 0.5, 7.5], [8.5, 14, 8.5], "grip"),
        el([6.8, 13.0, 6.8], [9.2, 14.2, 9.2], "gold"),
        el([6.3, 14.2, 7.6], [9.7, 16.6, 8.4], "plate"),        # hoja en hoja de laurel
        el([7.0, 16.6, 7.7], [9.0, 18.0, 8.3], "plate"),
        el([7.6, 18.0, 7.85], [8.4, 19.2, 8.15], "edge"),
    ]


def mace():
    return [
        el([7.2, -1.5, 7.2], [8.8, 0.5, 8.8], "gold"),
        el([7.5, 0.5, 7.5], [8.5, 11, 8.5], "grip"),
        el([6.8, 10.5, 6.8], [9.2, 11.7, 9.2], "gold"),
        el([5.0, 11.7, 5.5], [11.0, 17.0, 10.5], "plate"),      # cabeza
        el([4.4, 13.0, 6.8], [5.0, 15.8, 9.2], "edge"),         # pinchos
        el([11.0, 13.0, 6.8], [11.6, 15.8, 9.2], "edge"),
        el([6.8, 17.0, 6.8], [9.2, 18.4, 9.2], "edge"),
        el([6.8, 13.0, 4.9], [9.2, 15.8, 5.5], "edge"),
        el([6.8, 13.0, 10.5], [9.2, 15.8, 11.1], "edge"),
        el([5.0, 13.8, 5.5], [11.0, 14.6, 10.5], "gold"),       # banda
    ]


TOOLS = {"sword": sword, "pickaxe": pickaxe, "axe": axe, "shovel": shovel, "hoe": hoe, "spear": spear}

DISPLAY = {  # equivalente a item/handheld; la geometria ya lleva los 45 grados
    "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
    "thirdperson_lefthand": {"rotation": [0, 90, -55], "translation": [0, 4, 0.5], "scale": [0.85, 0.85, 0.85]},
    "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "firstperson_lefthand": {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
    "gui": {"rotation": [15, -30, 0], "translation": [0, 0, 0], "scale": [0.9, 0.9, 0.9]},
    "ground": {"rotation": [0, 0, 0], "translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
    "head": {"rotation": [0, 180, 0], "translation": [0, 13, 7], "scale": [1, 1, 1]},
    "fixed": {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
}
DISPLAY_MACE = dict(DISPLAY, thirdperson_righthand={"rotation": [0, -90, 55], "translation": [0, 4, 1], "scale": [1, 1, 1]},
                    thirdperson_lefthand={"rotation": [0, 90, -55], "translation": [0, 4, 1], "scale": [1, 1, 1]},
                    firstperson_righthand={"rotation": [0, -90, 25], "translation": [0, 3, 0.8], "scale": [0.9, 0.9, 0.9]},
                    firstperson_lefthand={"rotation": [0, 90, -25], "translation": [0, 3, 0.8], "scale": [0.9, 0.9, 0.9]})
DISPLAY_SPEAR_HAND = dict(DISPLAY,  # de item/spear_in_hand (jar 26.3)
                          firstperson_righthand={"rotation": [-20, 90, -35], "translation": [3.13, 2, 0.13], "scale": [1.36, 1.36, 0.68]},
                          firstperson_lefthand={"rotation": [-20, -90, 35], "translation": [3.13, 2, 0.13], "scale": [1.36, 1.36, 0.68]},
                          thirdperson_righthand={"rotation": [5, 270, -40], "translation": [0, 2, 2], "scale": [1.7, 1.7, 0.85]},
                          thirdperson_lefthand={"rotation": [5, -270, 40], "translation": [0, 2, 2], "scale": [1.7, 1.7, 0.85]})

MODELS = []  # (id_modelo, material, fn, display)
for _m in TOOL_MATS:
    for _t, _fn in TOOLS.items():
        _id = f"{_m}_{_t}"
        MODELS.append((_id, _m, _fn, DISPLAY))
        if _t == "spear":
            MODELS.append((_id + "_in_hand", _m, _fn, DISPLAY_SPEAR_HAND))
MODELS.append(("mace", "mace", mace, DISPLAY_MACE))


def item_json(mid):
    ref = f"{NS}:item/gear3d/{mid}"
    if mid.endswith("_spear"):  # misma estructura que el vanilla: gui/suelo/marco = modelo, mano = in_hand
        return {"model": {"type": "minecraft:select", "property": "minecraft:display_context",
                          "cases": [{"when": ["gui", "ground", "fixed", "on_shelf"], "model": {"type": "minecraft:model", "model": ref}}],
                          "fallback": {"type": "minecraft:model", "model": ref + "_in_hand"}}, "swap_animation_scale": 1.95}
    return {"model": {"type": "minecraft:model", "model": ref}}


def hook_items(root, mid):
    """items/<id>.json: si existe (con cases Slimefun) cambia el fallback minecraft:item/<id>; si no, lo crea."""
    if mid.endswith("_in_hand"):
        return
    p = root / f"assets/minecraft/items/{mid}.json"
    if p.exists():
        s = p.read_text(encoding="utf-8")
        s = s.replace(f'"minecraft:item/{mid}"', f'"{NS}:item/gear3d/{mid}"')
        if mid.endswith("_spear") and "gear3d" not in s:
            s = json.dumps(item_json(mid), indent=2) + "\n"
        p.write_text(s, encoding="utf-8")
    else:
        p.write_text(json.dumps(item_json(mid), indent=2) + "\n", encoding="utf-8")


def collect_models(node):
    """Todos los ids de modelo referenciados por un items/*.json (recursivo)."""
    if isinstance(node, dict):
        if node.get("type") == "minecraft:model" and "model" in node:
            yield node["model"]
        for v in node.values():
            yield from collect_models(v)
    elif isinstance(node, list):
        for v in node:
            yield from collect_models(v)


def validate(root):
    errs, warns, n = [], [], 0
    for mat in MATS:
        if not (root / f"assets/{NS}/textures/item/gear3d/{mat}.png").exists():
            errs.append(f"falta textura {mat}")
    for mid, mat, fn, _d in MODELS:
        mp = root / f"assets/{NS}/models/item/gear3d/{mid}.json"
        m = json.loads(mp.read_text(encoding="utf-8"))
        n += 1
        for k, v in m["textures"].items():
            ns, _, path = v.partition(":")
            if not (root / f"assets/{ns}/textures/{path}.png").exists():
                errs.append(f"{mp.name}: textura {v} no existe")
        for e in m["elements"]:
            if any(not -16 <= c <= 32 for c in e["from"] + e["to"]):
                errs.append(f"{mp.name}: elemento fuera de -16..32")
            if any(a >= b for a, b in zip(e["from"], e["to"])):
                errs.append(f"{mp.name}: from >= to")
            for f in e["faces"].values():
                if any(not 0 <= u <= 16 for u in f["uv"]):
                    errs.append(f"{mp.name}: uv fuera de 0..16")
        if mid.endswith("_in_hand"):
            continue
        ip = root / f"assets/minecraft/items/{mid}.json"
        items = json.loads(ip.read_text(encoding="utf-8"))
        refs = set(collect_models(items))
        if f"{NS}:item/gear3d/{mid}" not in refs:
            errs.append(f"{ip.name}: no usa el modelo 3D")
        for r in refs:
            ns, _, path = r.partition(":")
            if not (root / f"assets/{ns or 'minecraft'}/models/{path}.json").exists():
                # los cases Slimefun/jackstar existentes no son de este script: solo aviso
                (errs if ns == NS else warns).append(f"{ip.name}: modelo {r} no existe")
    print(f"aviso: {len(warns)} refs preexistentes (slimefun/jackstar) sin modelo en este worktree")
    return n, errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    root = Path(ap.parse_args().root)
    for mat in MATS:
        write_svg_png(mat, root)
    for mid, mat, fn, disp in MODELS:
        model = {"credit": "DrakesCraft kintsugi 3D (gen_tool_models_3d.py)", "texture_size": [16, 16],
                 "textures": {"0": f"{NS}:item/gear3d/{mat}", "particle": f"{NS}:item/gear3d/{mat}"},
                 "elements": fn(), "gui_light": "front", "display": disp}
        out = root / f"assets/{NS}/models/item/gear3d/{mid}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
        hook_items(root, mid)
    n, errs = validate(root)
    print(f"{n} modelos, {len(errs)} errores")
    for e in errs:
        print(" -", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
