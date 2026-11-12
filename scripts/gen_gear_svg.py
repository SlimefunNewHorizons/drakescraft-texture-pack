#!/usr/bin/env python3
"""Herramientas y armaduras DrakesCraft: paleta griega/dorada/morada/galactica.

Genera SVG (16x16, un rect por pixel, para poder editarlos) y los rasteriza con rsvg-convert.
Uso: gen_gear_svg.py [--out assets/minecraft/textures/item] [--svg assets/drakescraft/textures/gear/svg]
"""
import argparse
import subprocess
from pathlib import Path

MATS = {  # H principal, h luz, d sombra, E acento tecnologico
    "wooden":    ("#6b4a2b", "#9a7040", "#3f2a17", "#e8b84a"),
    "stone":     ("#5d6278", "#8a90ab", "#343749", "#8b5cf6"),
    "iron":      ("#aeb7c8", "#eef2fb", "#6b7488", "#38bdf8"),
    "golden":    ("#f2c14e", "#fff1a8", "#b8862a", "#fffbe0"),
    "diamond":   ("#3ed6e6", "#c2fbff", "#1b8fa0", "#a855f7"),
    "netherite": ("#2d2638", "#54466a", "#16121e", "#d946ef"),
    "chainmail": ("#8d93a6", "#c9cee0", "#4b5064", "#8b5cf6"),
}
OUTLINE = "#0d0a14"
HANDLE = ("#6b4a2b", "#8f6a3c")   # mango oscuro
GOLD = ("#e0ad3a", "#8f6a1c")     # dorado griego
PURPLE = "#7c3aed"


def diag(t, k=0):
    return (t + k, 15 - t + k)


def grid():
    return {}


def put(g, p, c):
    x, y = p
    if 0 <= x < 16 and 0 <= y < 16:
        g[(x, y)] = c


def handle(g, a, b):
    for i, t in enumerate(range(a, b + 1)):
        put(g, diag(t), "s" if i % 2 else "S")
    put(g, diag(a - 1 if a > 0 else a), "G")


def sword(g):
    handle(g, 2, 4)
    put(g, diag(1), "G")
    for k in range(-2, 3):
        put(g, diag(5, k), "G")
    for k in range(-1, 2):
        put(g, diag(6, k), "g")
    for t in range(7, 14):
        put(g, diag(t), "H")
        put(g, diag(t, -1) if False else (t - 1, 15 - t), "H")
    put(g, diag(14), "H")
    put(g, (13, 2), "H")
    put(g, diag(9), "E")
    put(g, diag(11), "E")


def pickaxe(g):
    handle(g, 1, 11)
    for k in range(-4, 5):
        put(g, diag(11, k), "H")
        put(g, (11 + k, 5 + k), "H")
    for k in (-4, -3, 4, 3):
        put(g, (11 + k, 6 + k), "H")
    put(g, (14, 8), "H"); put(g, (7, 1), "H")
    put(g, diag(11, 0), "G")
    put(g, diag(11, 1), "E"); put(g, diag(11, -1), "E")


def axe(g):
    handle(g, 1, 12)
    for p in [(7, 4), (8, 3), (9, 2), (10, 2), (11, 1), (8, 4), (9, 3), (10, 3), (11, 2), (12, 2),
              (9, 4), (10, 4), (11, 3), (12, 3), (10, 5), (11, 4), (12, 4), (11, 5)]:
        put(g, p, "H")
    put(g, diag(11), "G")
    put(g, (10, 3), "E")


def shovel(g):
    handle(g, 1, 11)
    for p in [(11, 3), (12, 2), (12, 3), (13, 3), (13, 2), (12, 4), (13, 1), (14, 2), (11, 4), (10, 5), (11, 5), (12, 5), (13, 4), (14, 3), (14, 1)]:
        put(g, p, "H")
    put(g, diag(11), "G")
    put(g, (13, 2), "E")


def hoe(g):
    handle(g, 1, 12)
    for p in [(10, 3), (11, 2), (12, 2), (13, 2), (14, 2), (14, 3), (13, 3), (12, 3), (11, 3), (10, 4), (9, 4), (14, 4)]:
        put(g, p, "H")
    put(g, diag(12), "G")
    put(g, (13, 2), "E")


TOOLS = {"sword": sword, "pickaxe": pickaxe, "axe": axe, "shovel": shovel, "hoe": hoe}

# Armaduras: mitad izquierda (8 col) x 16 filas; se espeja. Codigos: H D h cuerpo, G oro, P cresta, E acento, . vacio
ARMOR = {
    "helmet": [
        "........", ".......P", "....ooPP", "..ooHHhP", ".oHhHHHH", ".oHHHHHH", ".oHHHHHH",
        ".oGGGGGG", ".oHd.E..", ".oHd....", ".oHd....", ".ood....", "........", "........", "........", "........",
    ],
    "chestplate": [
        "........", "........", ".ooo..oo", ".oHHooHH", "oHhHHHHH", "oHHHGGGG", "oHHHGEEG", ".oHHGEEG",
        ".oHHGGGG", ".oHdHHHH", ".oHdHHHH", ".oHdHHHH", ".oHdHHHH", ".ooHdHHH", "..ooooDD", "........",
    ],
    "leggings": [
        "........", "........", ".ooooooo", ".oGGGGGG", ".oHHHhHH", ".oHHHHHH", ".oHHHHHo",
        ".oHHHHHo", ".oHHdoo.", ".oHHdo..", ".oHHdo..", ".oHHdo..", ".oHHdo..", ".oHhdo..", ".ooood..", "........",
    ],
    "boots": [
        "........", "........", "........", "........", "........", "..oooo..", "..oHho..", "..oHHo..",
        "..oGGo..", "..oHHo..", ".ooHHo..", "oHHHHo..", "oHEHHo..", "oDDDDo..", "ooooooo.", "........",
    ],
}
ARMOR_NAME = {"wooden": None, "stone": None, "iron": "iron", "golden": "golden", "diamond": "diamond",
              "netherite": "netherite", "chainmail": "chainmail"}


def shade_tool(g, mat):
    H, h, d, E = MATS[mat]
    out = {}
    filled = set(g)
    for (x, y), c in g.items():
        if c == "H":
            up = (x, y - 1) not in filled or g.get((x, y - 1)) not in ("H", "E")
            left = (x - 1, y) not in filled or g.get((x - 1, y)) not in ("H", "E")
            down = (x, y + 1) not in filled or g.get((x, y + 1)) not in ("H", "E")
            right = (x + 1, y) not in filled or g.get((x + 1, y)) not in ("H", "E")
            col = h if (up or left) and not (down and right) else d if (down or right) and not (up or left) else H
        else:
            col = {"S": HANDLE[0], "s": HANDLE[1], "G": GOLD[0], "g": GOLD[1], "E": E, "P": PURPLE}.get(c, c)
        out[(x, y)] = col
    return outline(out)


def outline(px):
    out = dict(px)
    for (x, y) in list(px):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if 0 <= p[0] < 16 and 0 <= p[1] < 16 and p not in px:
                    out[p] = OUTLINE
    return out


def armor_px(kind, mat):
    H, h, d, E = MATS[mat]
    px = {}
    for y, row in enumerate(ARMOR[kind]):
        full = row + row[::-1]
        for x, c in enumerate(full):
            if c == ".":
                continue
            px[(x, y)] = {"o": OUTLINE, "H": H, "h": h, "D": d, "d": d, "G": GOLD[0], "P": PURPLE, "E": E}[c]
    return px


def svg(px):
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>' for (x, y), c in sorted(px.items(), key=lambda i: (i[0][1], i[0][0])))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" shape-rendering="crispEdges">{rects}</svg>\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("assets/minecraft/textures/item"))
    ap.add_argument("--svg", type=Path, default=Path("assets/drakescraft/textures/gear/svg"))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    a.svg.mkdir(parents=True, exist_ok=True)
    jobs = {}
    for mat in ("wooden", "stone", "iron", "golden", "diamond", "netherite"):
        for tool, fn in TOOLS.items():
            g = grid(); fn(g)
            jobs[f"{mat}_{tool}"] = shade_tool(g, mat)
    for mat in ("chainmail", "iron", "golden", "diamond", "netherite"):
        for kind in ARMOR:
            jobs[f"{mat}_{kind}"] = outline_fix(armor_px(kind, mat))
    for name, px in jobs.items():
        s = a.svg / f"{name}.svg"
        s.write_text(svg(px))
        subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", str(s), "-o", str(a.out / f"{name}.png")], check=True)
    print(len(jobs), "texturas")


def outline_fix(px):
    return px


if __name__ == "__main__":
    main()
