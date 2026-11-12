#!/usr/bin/env python3
"""Capas de armadura DrakesCraft estilo KINTSUGI (26.x): placas oscuras, grietas de oro, estrellitas y brillos.

Genera por material (netherite, diamond, iron, gold, chainmail):
  assets/minecraft/textures/entity/equipment/humanoid/<mat>.png          (capa 1: casco/peto/botas, 64x32)
  assets/minecraft/textures/entity/equipment/humanoid_leggings/<mat>.png (capa 2: pantalones, 64x32)
  assets/minecraft/equipment/<mat>.json                                   (asset vanilla sobrescrito)
  assets/drakescraft/textures/gear/svg/armor_<mat>_layer{1,2}.svg         (fuente SVG, 1 rect por run de pixeles)
y la variante propia drakescraft:kintsugi (para equippable.asset_id).
Sin shader: los brillos son pixeles claros pintados. Determinista (semilla fija).
Uso: gen_armor_layers.py [--root .]
"""
import argparse
import json
import random
from pathlib import Path
from PIL import Image

OUTLINE = (13, 10, 20)
GOLD = (224, 173, 58)
GOLD_D = (143, 106, 28)
GOLD_L = (255, 241, 168)
WHITE = (255, 255, 255)


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


# base, luz, sombra, brillo propio del material, estilo
MATS = {
    "netherite": dict(H="#2d2638", h="#54466a", d="#16121e", sp="#e9d5ff", crack=GOLD, mesh=False),
    "diamond":   dict(H="#1d5360", h="#3ed6e6", d="#0c2a33", sp="#c2fbff", crack=GOLD, mesh=False),
    "iron":      dict(H="#5b6478", h="#aeb7c8", d="#2c3242", sp="#eef2fb", crack=GOLD, mesh=False),
    "gold":      dict(H="#7a5a1a", h="#c99a2e", d="#3f2c0a", sp="#fffbe0", crack=GOLD_L, mesh=False),
    "chainmail": dict(H="#4b5064", h="#8d93a6", d="#262a38", sp="#c9cee0", crack=GOLD, mesh=True),
    "kintsugi":  dict(H="#241c30", h="#7c3aed", d="#0f0b17", sp="#e9d5ff", crack=GOLD, mesh=False),
}
VANILLA = ["netherite", "diamond", "iron", "gold", "chainmail"]


def box(u, v, w, h, d):
    """Caras de un cuboide en el UV vanilla (top, bottom, right, front, left, back)."""
    return {
        "top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d),
        "right": (u, v + d, d, h), "front": (u + d, v + d, w, h),
        "left": (u + d + w, v + d, d, h), "back": (u + d + w + d, v + d, w, h),
    }


# partes del mapa 64x32: cabeza, torso, brazo (el izquierdo reutiliza el derecho), pierna (idem)
HEAD, BODY, ARM, LEG = box(0, 0, 8, 8, 8), box(16, 16, 8, 12, 4), box(40, 16, 4, 12, 4), box(0, 16, 4, 12, 4)
LAYER1 = {"head": HEAD, "body": BODY, "arm": ARM, "leg": LEG}
LAYER2 = {"body": BODY, "leg": LEG}


def paint_face(px, rect, m, rng, belt=False):
    x0, y0, w, h = rect
    H, hl, d = hx(m["H"]), hx(m["h"]), hx(m["d"])
    sp, crack = hx(m["sp"]), m["crack"]
    ox, oy = rng.randrange(4), rng.randrange(4)
    for j in range(h):
        for i in range(w):
            if m["mesh"]:
                c = hl if (i + j) % 2 == 0 and rng.random() < .15 else (H if (i + j) % 2 == 0 else d)
            else:
                px_, py_ = (i + ox) % 4, (j + oy) % 4
                if px_ == 0 and py_ == 0:
                    c = OUTLINE          # juntura entre placas
                elif px_ == 0 or py_ == 0:
                    c = d
                elif px_ == 1 or py_ == 1:
                    c = hl if (px_ == 1 and py_ == 1) else H
                else:
                    c = H
            px[(x0 + i, y0 + j)] = c
    # bordes de la cara mas oscuros: da volumen
    for i in range(w):
        px[(x0 + i, y0 + h - 1)] = d
    # grietas de oro (kintsugi): paseo aleatorio descendente
    for _ in range(1 + (w * h > 90)):
        x, y = x0 + rng.randrange(w), y0
        for _s in range(h + 2):
            if not (x0 <= x < x0 + w and y0 <= y < y0 + h):
                break
            px[(x, y)] = crack if rng.random() > .15 else GOLD_D
            if rng.random() < .08:
                px[(x, y)] = GOLD_L
            y += 1
            x += rng.choice((-1, 0, 0, 1))
            x = max(x0, min(x0 + w - 1, x))
    # estrellitas (cruz) y brillos sueltos
    if w >= 4 and h >= 4:
        for _ in range(1 if w * h > 40 else 0):
            cx, cy = x0 + 1 + rng.randrange(w - 2), y0 + 1 + rng.randrange(h - 2)
            px[(cx, cy)] = WHITE
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px[(cx + dx, cy + dy)] = GOLD_L
    for _ in range(w * h // 36):
        px[(x0 + rng.randrange(w), y0 + rng.randrange(h))] = sp
    if belt:  # cinturon / ribete dorado en las 2 primeras filas
        for i in range(w):
            px[(x0 + i, y0)] = GOLD_L if i % 3 == 0 else GOLD
            px[(x0 + i, y0 + 1)] = GOLD_D


def build_layer(mat, layer, seed):
    m = MATS[mat]
    rng = random.Random(f"{mat}-{layer}-{seed}")
    px = {}
    parts = LAYER1 if layer == 1 else LAYER2
    for pname, faces in parts.items():
        for fname, rect in faces.items():
            belt = (layer == 2 and pname == "body" and fname in ("front", "back", "left", "right")) or \
                   (layer == 1 and pname == "head" and False)
            paint_face(px, rect, m, rng, belt)
    if layer == 1:  # ribete dorado en el borde inferior del casco (caras laterales)
        for f in ("right", "front", "left", "back"):
            x0, y0, w, h = HEAD[f]
            for i in range(w):
                px[(x0 + i, y0 + h - 1)] = GOLD if i % 2 else GOLD_D
    return px


def save_png(px, path):
    im = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    for (x, y), c in px.items():
        im.putpixel((x, y), tuple(c) + (255,))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)


def save_svg(px, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 32" width="512" height="256" shape-rendering="crispEdges">']
    for y in range(32):
        x = 0
        while x < 64:
            c = px.get((x, y))
            if c is None:
                x += 1
                continue
            e = x
            while e + 1 < 64 and px.get((e + 1, y)) == c:
                e += 1
            out.append(f'<rect x="{x}" y="{y}" width="{e - x + 1}" height="1" fill="#{c[0]:02x}{c[1]:02x}{c[2]:02x}"/>')
            x = e + 1
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    root = Path(ap.parse_args().root)
    mc = root / "assets/minecraft"
    dk = root / "assets/drakescraft"
    svg = dk / "textures/gear/svg"
    for mat in VANILLA + ["kintsugi"]:
        for layer, sub in ((1, "humanoid"), (2, "humanoid_leggings")):
            px = build_layer(mat, layer, 26)
            base = (dk if mat == "kintsugi" else mc) / "textures/entity/equipment" / sub / f"{mat}.png"
            save_png(px, base)
            save_svg(px, svg / f"armor_{mat}_layer{layer}.svg")
        ns = "drakescraft" if mat == "kintsugi" else "minecraft"
        layers = {"humanoid": [{"texture": f"{ns}:{mat}"}], "humanoid_leggings": [{"texture": f"{ns}:{mat}"}]}
        if mat in ("netherite", "diamond", "iron", "gold"):
            # conserva las capas no humanoides que trae el asset vanilla (se resuelven a texturas vanilla)
            layers["horse_body"] = [{"texture": f"minecraft:{mat}"}]
            layers["nautilus_body"] = [{"texture": f"minecraft:{mat}"}]
        out = (dk if mat == "kintsugi" else mc) / "equipment" / f"{mat}.json"
        write_json(out, {"layers": layers})
        print("ok", mat)


if __name__ == "__main__":
    main()
