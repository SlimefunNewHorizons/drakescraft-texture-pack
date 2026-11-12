#!/usr/bin/env python3
"""Herramientas DrakesCraft v2 (SVG 16x16 -> PNG): mas produccion, todas las armas/herramientas.

Coordenadas del eje: pix(t,k) = (t+k, 15-t+k). t avanza del mango (abajo-izq) a la punta (arriba-der); k es perpendicular
(k<0 = arriba-izq = luz, k>0 = abajo-der = sombra). Salida: svg + png en textures/item.
Uso: gen_tools_v2.py [--out DIR] [--svg DIR]
"""
import argparse
import math
import subprocess
from pathlib import Path

# H principal, h luz, d sombra, E rune/acento
MATS = {
    "wooden":    ("#6e4c2c", "#9a7040", "#3f2a17", "#e0ad3a"),
    "stone":     ("#5f647a", "#8e94b0", "#33364a", "#8b5cf6"),
    "copper":    ("#c0703d", "#f0a672", "#7a3f22", "#3fd0b0"),
    "iron":      ("#9aa3b6", "#dfe6f4", "#5b6478", "#38bdf8"),
    "golden":    ("#e8b83f", "#fff0a0", "#a8791f", "#fff7d0"),
    "diamond":   ("#35c9d9", "#bff8ff", "#17808f", "#a855f7"),
    "netherite": ("#322a3e", "#5a4b72", "#16121e", "#d946ef"),
}
OUT = "#0d0a14"
S, s_ = "#6b4a2b", "#93693a"      # mango
WRAP, WRAP2 = "#3b2a5a", "#5a43888"[:7]
GOLD, GOLD_D = "#e0ad3a", "#8f6a1c"
GEM = "#7c3aed"
STRING = "#d9d2ea"
RUST = "#8a4b2a"


def pix(t, k):
    return (t + k, 15 - t + k)


class Canvas(dict):
    def put(self, p, c):
        x, y = p
        if 0 <= x < 16 and 0 <= y < 16:
            self[(x, y)] = c

    def pt(self, t, k, c):
        self.put(pix(t, k), c)


def finish(cv, mat):
    H, h, d, E = MATS[mat]
    for (x, y), c in list(cv.items()):  # rellena la paridad vacia de cabezas/hojas; los mangos quedan en diagonal
        if c in "hHdEGgP" and (x + 1, y) not in cv:
            cv.put((x + 1, y), c)
    pal = {"H": H, "h": h, "d": d, "E": E, "S": S, "s": s_, "W": WRAP, "w": "#5b46a0", "G": GOLD, "g": GOLD_D, "P": GEM, "T": STRING}
    px = {p: pal.get(c, c) for p, c in cv.items()}
    if mat == "iron":  # oxido tenue, determinista
        for (x, y), c in list(px.items()):
            if c in (H, d) and (x * 7 + y * 13) % 11 == 0:
                px[(x, y)] = RUST
    if mat == "copper":  # pátina verdeazulada
        for (x, y), c in list(px.items()):
            if c in (H, d) and (x * 5 + y * 11) % 13 == 0:
                px[(x, y)] = "#3aa58f"
    out = dict(px)
    for (x, y) in px:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                p = (x + dx, y + dy)
                if 0 <= p[0] < 16 and 0 <= p[1] < 16 and p not in px:
                    out[p] = OUT
    return out


def rows(cv, spec):
    for y, x0, text in spec:
        for i, c in enumerate(text):
            if c != ".":
                cv.put((x0 + i, y), c)


def diag_handle(cv, x0, y0, n):
    """mango en diagonal de (x0,y0) hacia abajo-izquierda, n pixeles"""
    for i in range(n):
        cv.put((x0 - i, y0 + i), "W" if i % 4 == 2 else ("s" if i % 2 else "S"))


def grip(cv, a, b, wrap_every=3):
    for t in range(a, b + 1):
        cv.pt(t, 0, ("W" if (t - a) % wrap_every == 1 else ("s" if t % 2 else "S")))


def band(cv, t, k0, k1, edge_l="h", mid="H", edge_r="d"):
    """Franja perpendicular t con k0..k1: luz a la izquierda, sombra a la derecha."""
    for k in range(k0, k1 + 1):
        cv.pt(t, k, edge_l if k == k0 else edge_r if k == k1 else mid)


def sword(cv):
    grip(cv, 2, 4)
    cv.pt(1, 0, "G"); cv.pt(0, 0, "g")
    for k in range(-2, 3):
        cv.pt(5, k, "g" if abs(k) == 2 else "G")
    cv.pt(5, 0, "P")
    for t in range(6, 14):
        band(cv, t, -1, 1)
        if t in (8, 10, 12):
            cv.pt(t, 0, "E")
    band(cv, 14, -1, 0)
    cv.pt(15, -1, "h")


def pickaxe(cv):
    grip(cv, 0, 12, 4)
    for k in range(-5, 6):
        t = 13 - (abs(k) + 1) // 2
        cv.pt(t, k, "h" if k < 0 else "d" if k > 0 else "H")
        cv.pt(t - 1, k, "d" if abs(k) > 1 else "H")
        if abs(k) >= 4:
            cv.pt(t - 2, k, "d")
    for k in (-1, 0, 1):
        cv.pt(12, k, "G"); cv.pt(13, k, "G")
    cv.pt(13, 0, "P")
    cv.pt(13, -3, "E"); cv.pt(13, 3, "E")


def axe(cv):
    diag_handle(cv, 12, 3, 13)
    cv.put((1, 15), "G"); cv.put((9, 6), "G")
    rows(cv, [(0, 8, "hhhH"), (1, 6, "hhHHHd"), (2, 5, "hhHHHHHd"), (3, 5, "hhHHEHHHd"), (4, 6, "hhHHHHHd"),
              (5, 7, "hHHHHd"), (6, 8, "hHHd"), (7, 8, "hd")])
    rows(cv, [(1, 12, "d"), (2, 13, "d"), (3, 14, "d")])
    cv.put((11, 4), "g")


def shovel(cv):
    diag_handle(cv, 11, 6, 10)
    rows(cv, [(0, 12, "hHd"), (1, 11, "hhHHd"), (2, 11, "hHEHd"), (3, 11, "hHHHd"), (4, 12, "hHHd"), (5, 12, "GGG")])
    cv.put((10, 7), "G"); cv.put((11, 6), "g")
    cv.put((1, 15), "G")


def hoe(cv):
    grip(cv, 0, 12, 4)
    for t in (12,):
        for k in (-1, 0, 1):
            cv.pt(t, k, "G")
    for k in range(-5, 1):
        cv.pt(13, k, "h" if k < 0 else "H")
        cv.pt(14, k, "h") if -4 <= k <= -1 else None
        cv.pt(12, k, "d") if k <= -2 else None
    for t in (11, 10):
        cv.pt(t, -5, "d"); cv.pt(t, -4, "d") if t == 11 else None
    cv.pt(13, -3, "E")


def spear(cv):
    diag_handle(cv, 10, 5, 11)
    cv.put((1, 15), "G"); cv.put((0, 15), "g")
    cv.put((7, 8), "w"); cv.put((6, 9), "W"); cv.put((7, 9), "w")
    rows(cv, [(0, 15, "h"), (1, 13, "hHd"), (2, 11, "hhHEd"), (3, 10, "hhHHd"), (4, 10, "hHHd"), (5, 9, "GGg")])
    cv.put((10, 5), "P")


def mace(cv):
    grip(cv, 0, 9, 4)
    for k in (-1, 0, 1):
        cv.pt(10, k, "G")
    cv.pt(10, 0, "P")
    for t in range(11, 15):
        for k in range(-2, 3):
            if abs(k) == 2 and t in (11, 14):
                continue
            cv.pt(t, k, "h" if k <= -1 and t >= 12 else "d" if k >= 1 else "H")
    for (t, k) in ((12, -3), (13, 3), (15, 0), (11, 3), (14, -3), (10, -2), (15, -1)):
        cv.pt(t, k, "h")
    cv.pt(12, 0, "E"); cv.pt(13, 0, "E")


def trident(cv):
    grip(cv, 0, 9, 4)
    for k in (-1, 0, 1):
        cv.pt(10, k, "G")
    for k in (-3, -2, -1, 0, 1, 2, 3):
        cv.pt(11, k, "H" if abs(k) < 3 else "h")
    for k in (-3, 0, 3):
        for t in (12, 13, 14):
            cv.pt(t, k, "h" if k < 0 else "d" if k > 0 else "H")
    cv.pt(15, 0, "h"); cv.pt(14, -3, "h"); cv.pt(14, 3, "h")
    cv.pt(12, -2, "d") if False else None
    cv.pt(15, -3, "E"); cv.pt(15, 3, "E"); cv.pt(12, 0, "E")


def arc_points(cx, cy, r, a0, a1, n=40):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((round(cx + r * math.cos(a)), round(cy + r * math.sin(a))))
    return list(dict.fromkeys(pts))


def line(p, q):
    (x0, y0), (x1, y1) = p, q
    n = max(abs(x1 - x0), abs(y1 - y0)) or 1
    return list(dict.fromkeys((round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)))


def bow(cv, pull=0):
    limb = arc_points(14, 14, 12.5, 188, 262)
    for i, p in enumerate(limb):
        cv.put(p, "h" if i % 3 == 0 else "H")
        cv.put((p[0] + 1, p[1]), "d")
    mid = limb[len(limb) // 2]
    for dx in (-1, 0, 1):
        cv.put((mid[0] + dx, mid[1] + dx), "W")
    a, b = limb[0], limb[-1]
    cv.put(a, "G"); cv.put(b, "G")
    m = ((a[0] + b[0]) // 2 + 1 + pull, (a[1] + b[1]) // 2 + 1 + pull)
    for p in line((a[0] + 1, a[1]), m) + line(m, (b[0], b[1] + 1)):
        cv.put(p, "T")
    if pull:
        for p in line((m[0], m[1]), (m[0] - 6 - pull, m[1] - 6 - pull)):
            cv.put(p, "S")
        cv.put((m[0] - 7 - pull, m[1] - 7 - pull), "h")
        cv.put((m[0] - 1, m[1] + 1 - 0), "w") if False else None


def crossbow(cv, state="standby"):
    for p in line((1, 14), (11, 4)):  # culata
        cv.put(p, "S"); cv.put((p[0], p[1] + 1), "s")
    for p in line((8, 0), (15, 7)):  # arco transversal
        cv.put(p, "H"); cv.put((p[0], p[1] + 1), "d")
    cv.put((8, 0), "G"); cv.put((15, 7), "G"); cv.put((11, 3), "G"); cv.put((12, 4), "G")
    tip = (11, 4) if state == "standby" else (10, 5)
    for p in line((8, 1), tip) + line(tip, (15, 8)):
        cv.put(p, "T")
    if state in ("arrow", "firework"):
        for p in line((5, 10), (14, 1)):
            cv.put(p, "S")
        cv.put((15, 0), "h" if state == "arrow" else "E"); cv.put((14, 1), "h" if state == "arrow" else "E")
    cv.put((5, 10), "P") if state == "standby" else None


def shears(cv):
    for t in range(2, 9):
        cv.pt(t, -1, "h"); cv.pt(t, 1, "d")
    for t in range(8, 15):
        cv.pt(t, -2 + (t - 8) // 3, "H"); cv.pt(t, 2 - (t - 8) // 3, "H")
    cv.pt(1, -2, "G"); cv.pt(1, 2, "G"); cv.pt(0, -3, "g"); cv.pt(0, 3, "g")
    cv.pt(8, 0, "P")


def brush(cv):
    grip(cv, 0, 8, 4)
    for k in (-1, 0, 1):
        cv.pt(9, k, "G")
    for t in range(10, 14):
        for k in range(-2, 3):
            cv.pt(t, k, "h" if k < 0 else "d" if k > 0 else "H")
    for k in range(-2, 3):
        cv.pt(14, k, "E" if k % 2 == 0 else "H")


def flint_and_steel(cv):
    for t in range(3, 9):
        cv.pt(t, -1, "H"); cv.pt(t, 0, "d")
    for k in (-3, -2, 2, 3):
        cv.pt(2, k, "d"); cv.pt(9, k, "d")
    for k in range(-3, 4):
        cv.pt(1, k, "d") if abs(k) == 3 else None
    for p in ((11, 4), (12, 3), (11, 2), (13, 2), (12, 5)):
        cv.put(p, "E")
    cv.pt(10, 0, "G"); cv.pt(10, 1, "g")


def fishing_rod(cv, cast=False):
    for t in range(0, 14):
        cv.pt(t, 0, "s" if t % 2 else "S")
    cv.pt(13, 0, "G")
    if not cast:
        for y in range(2, 12):
            cv.put((15, y), "T") if y % 1 == 0 else None
        cv.put((14, 12), "E"); cv.put((15, 12), "E")
    else:
        for p in line((14, 1), (14, 10)):
            cv.put(p, "T")
        cv.put((14, 11), "E")


TOOLS = {"sword": sword, "pickaxe": pickaxe, "axe": axe, "shovel": shovel, "hoe": hoe, "spear": spear}
SOLO = {  # nombre -> (func, material de paleta)
    "mace": (mace, "iron"), "trident": (trident, "diamond"),
    "bow": (lambda c: bow(c, 0), "wooden"), "bow_pulling_0": (lambda c: bow(c, 1), "wooden"),
    "bow_pulling_1": (lambda c: bow(c, 2), "wooden"), "bow_pulling_2": (lambda c: bow(c, 3), "wooden"),
    "crossbow_standby": (lambda c: crossbow(c, "standby"), "wooden"),
    "crossbow_arrow": (lambda c: crossbow(c, "arrow"), "wooden"),
    "crossbow_firework": (lambda c: crossbow(c, "firework"), "wooden"),
    "crossbow_pulling_0": (lambda c: crossbow(c, "standby"), "wooden"),
    "crossbow_pulling_1": (lambda c: crossbow(c, "standby"), "wooden"),
    "crossbow_pulling_2": (lambda c: crossbow(c, "arrow"), "wooden"),
    "shears": (shears, "iron"), "brush": (brush, "copper"), "flint_and_steel": (flint_and_steel, "iron"),
    "fishing_rod": (lambda c: fishing_rod(c, False), "wooden"), "fishing_rod_cast": (lambda c: fishing_rod(c, True), "wooden"),
}


def svg(px):
    r = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>' for (x, y), c in sorted(px.items(), key=lambda i: (i[0][1], i[0][0])))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" shape-rendering="crispEdges">{r}</svg>\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("assets/minecraft/textures/item"))
    ap.add_argument("--svg", type=Path, default=Path("assets/drakescraft/textures/gear/svg"))
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True); a.svg.mkdir(parents=True, exist_ok=True)
    jobs = {}
    for mat in ("wooden", "stone", "copper", "iron", "golden", "diamond", "netherite"):
        for tool, fn in TOOLS.items():
            cv = Canvas(); fn(cv); jobs[f"{mat}_{tool}"] = finish(cv, mat)
    for name, (fn, mat) in SOLO.items():
        cv = Canvas(); fn(cv); jobs[name] = finish(cv, mat)
    for name, px in jobs.items():
        sp = a.svg / f"{name}.svg"; sp.write_text(svg(px))
        subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", str(sp), "-o", str(a.out / f"{name}.png")], check=True)
    print(len(jobs), "texturas")


if __name__ == "__main__":
    main()
