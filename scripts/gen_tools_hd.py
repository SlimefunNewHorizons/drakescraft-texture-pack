#!/usr/bin/env python3
"""Herramientas DrakesCraft HD: arte vectorial (SVG 128x128) -> PNG 128x128 con rsvg-convert.

Cada herramienta se dibuja derecha (punta arriba, eje x=0) en coordenadas locales y se gira 45 grados (punta arriba-derecha),
como los items de Minecraft. Degradados metalicos, aristas de luz, runas, grabados, oxido tenue en hierro, patina en cobre.
Compatible 1.20-26.x: las texturas de item admiten cualquier tamano cuadrado.
Uso: gen_tools_hd.py [--out DIR] [--svg DIR] [--size 128]
"""
import argparse
import subprocess
from pathlib import Path

# (luz, medio, sombra, borde-oscuro, acento)
MATS = {
    "wooden":    ("#b0834a", "#7a5530", "#46301a", "#24160a", "#e0ad3a"),
    "stone":     ("#a3a8c2", "#686d86", "#3a3d52", "#1a1b27", "#8b5cf6"),
    "copper":    ("#f4b183", "#c2733f", "#7d4022", "#3d1d0d", "#3fd9b8"),
    "iron":      ("#e8edf8", "#a1abc0", "#5a6378", "#232733", "#38bdf8"),
    "golden":    ("#fff2a8", "#e6b83e", "#a5761b", "#503508", "#fffbe6"),
    "diamond":   ("#c6fbff", "#38cfe0", "#127a8c", "#06323b", "#c084fc"),
    "netherite": ("#6a5a84", "#3a3149", "#1b1624", "#07050b", "#e879f9"),
}
WOOD = ("#8f6a3c", "#6b4a2b", "#3d2915")
GOLD = ("#fff0a0", "#e0ad3a", "#8f6a1c")
GEM = ("#d8b4fe", "#7c3aed", "#3b1d7a")


def defs(mat, uid):
    l, m, d, o, e = MATS[mat]
    g = lambda i, stops, x2="1", y2="0": f'<linearGradient id="{i}{uid}" x1="0" y1="0" x2="{x2}" y2="{y2}">' + "".join(
        f'<stop offset="{p}" stop-color="{c}"/>' for p, c in stops) + "</linearGradient>"
    return (
        g("metal", [(0, l), (0.45, m), (1, d)])
        + g("metalv", [(0, l), (0.5, m), (1, d)], "0", "1")
        + g("wood", [(0, WOOD[0]), (0.5, WOOD[1]), (1, WOOD[2])])
        + g("gold", [(0, GOLD[0]), (0.5, GOLD[1]), (1, GOLD[2])])
        + g("goldv", [(0, GOLD[0]), (0.5, GOLD[1]), (1, GOLD[2])], "0", "1")
        + f'<radialGradient id="gem{uid}" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="{GEM[0]}"/><stop offset="0.5" stop-color="{GEM[1]}"/><stop offset="1" stop-color="{GEM[2]}"/></radialGradient>'
        + f'<radialGradient id="glow{uid}" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{e}" stop-opacity="0.9"/><stop offset="1" stop-color="{e}" stop-opacity="0"/></radialGradient>'
    )


def finishings(mat, uid):
    """oxido (hierro) o patina (cobre): manchas tenues dentro del metal"""
    if mat == "iron":
        c = "#8a4b2a"
    elif mat == "copper":
        c = "#3aa58f"
    else:
        return ""
    spots = [(-4, 40, 3), (5, 62, 2.5), (-6, 78, 2), (3, 30, 2), (-3, 56, 1.8)]
    return "".join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.7}" fill="{c}" opacity="0.55" clip-path="url(#clip{uid})"/>' for x, y, r in spots)


def S(mat, uid, shapes, clip):
    l, m, d, o, e = MATS[mat]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
            f'<defs>{defs(mat, uid)}<clipPath id="clip{uid}">{clip}</clipPath></defs>'
            f'<g transform="translate(64 66) rotate(45) scale(0.84) translate(0 -80)" stroke-linejoin="round" stroke-linecap="round">{shapes}</g></svg>\n')


def pal(mat):
    return MATS[mat]


def grip_wraps(x0, x1, y0, y1, uid, n=6, col="#3b2a5a"):
    out = f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="2" fill="url(#wood{uid})" stroke="#1b1008" stroke-width="1.2"/>'
    h = (y1 - y0) / n
    for i in range(n):
        y = y0 + i * h
        out += f'<path d="M{x0} {y+h*0.8:.1f} L{x1} {y:.1f}" stroke="{col}" stroke-width="2.4" opacity="0.9"/>'
    return out


def rune(x, y, c, h=5):
    return f'<path d="M{x-2} {y} L{x} {y-h} L{x+2} {y} M{x-2} {y+3} L{x+2} {y+3}" stroke="{c}" stroke-width="1" fill="none" opacity="0.95"/>'


def sword(mat, uid):
    l, m, d, o, e = pal(mat)
    blade = (f'<path d="M0 2 L10 22 L10 98 L-10 98 L-10 22 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2"/>'
             f'<path d="M0 8 L5 24 L5 94 L-5 94 L-5 24 Z" fill="url(#metalv{uid})" opacity="0.55"/>'
             f'<path d="M-9 24 L-9 97" stroke="{l}" stroke-width="1.6" opacity="0.9"/>'
             f'<path d="M0 12 L0 92" stroke="{o}" stroke-width="1" opacity="0.5"/>'
             + finishings(mat, uid) + rune(0, 40, e) + rune(0, 60, e) + rune(0, 80, e))
    guard = (f'<path d="M-32 100 Q-34 94 -24 96 L24 96 Q34 94 32 100 Q30 108 20 106 L-20 106 Q-30 108 -32 100 Z" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
             f'<circle cx="0" cy="101" r="5" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="1.2"/>')
    handle = grip_wraps(-5, 5, 108, 140, uid)
    pommel = f'<circle cx="0" cy="146" r="8" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="2"/><circle cx="0" cy="146" r="2.6" fill="url(#gem{uid})"/>'
    clip = '<path d="M0 2 L10 22 L10 98 L-10 98 L-10 22 Z"/>'
    return S(mat, uid, blade + guard + handle + pommel, clip)


def pickaxe(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 46, 156, uid, n=10)
    head = (f'<path d="M-62 74 C-58 36 -30 22 0 22 C30 22 58 36 62 74 C54 56 30 42 0 42 C-30 42 -54 56 -62 74 Z" fill="url(#metalv{uid})" stroke="{o}" stroke-width="2.2"/>'
            f'<path d="M-52 62 C-36 42 -14 36 0 36 C14 36 36 42 52 62" stroke="{l}" stroke-width="1.6" fill="none" opacity="0.85"/>'
            + finishings(mat, uid) + rune(-32, 52, e, 4) + rune(32, 52, e, 4))
    band = (f'<rect x="-10" y="30" width="20" height="20" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
            f'<circle cx="0" cy="40" r="4" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="1"/>')
    clip = '<path d="M-62 74 C-58 36 -30 22 0 22 C30 22 58 36 62 74 C54 56 30 42 0 42 C-30 42 -54 56 -62 74 Z"/>'
    return S(mat, uid, handle + head + band, clip)


def axe(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 30, 156, uid, n=11)
    head = (f'<path d="M4 24 C-14 14 -44 18 -56 36 C-62 50 -58 70 -50 82 C-34 78 -16 74 4 70 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
            f'<path d="M-52 40 C-48 56 -48 68 -44 78" stroke="{l}" stroke-width="2.2" fill="none" opacity="0.95"/>'
            f'<path d="M4 24 L16 28 L16 64 L4 70 Z" fill="url(#metalv{uid})" stroke="{o}" stroke-width="2"/>'
            + finishings(mat, uid) + rune(-22, 50, e, 5))
    band = f'<rect x="-9" y="22" width="18" height="52" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="1.8" opacity="0.0"/><rect x="-8" y="68" width="16" height="9" rx="2" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="1.8"/>'
    clip = '<path d="M4 24 C-14 14 -44 18 -56 36 C-62 50 -58 70 -50 82 C-34 78 -16 74 4 70 Z"/>'
    return S(mat, uid, handle + head + band, clip)


def shovel(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 66, 140, uid, n=8)
    loop = f'<path d="M-14 150 C-14 138 14 138 14 150 C14 160 -14 160 -14 150 Z M-8 150 C-8 144 8 144 8 150 C8 155 -8 155 -8 150 Z" fill="url(#wood{uid})" stroke="#1b1008" stroke-width="1.4" fill-rule="evenodd"/>'
    blade = (f'<path d="M0 2 C26 6 30 38 16 60 L-16 60 C-30 38 -26 6 0 2 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
             f'<path d="M0 8 L0 56" stroke="{o}" stroke-width="1.2" opacity="0.45"/>'
             f'<path d="M-18 14 C-24 30 -20 44 -12 56" stroke="{l}" stroke-width="2" fill="none" opacity="0.9"/>'
             + finishings(mat, uid) + rune(0, 30, e, 6))
    ferrule = f'<rect x="-11" y="58" width="22" height="12" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
    clip = '<path d="M0 2 C26 6 30 38 16 60 L-16 60 C-30 38 -26 6 0 2 Z"/>'
    return S(mat, uid, handle + loop + blade + ferrule, clip)


def hoe(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 40, 156, uid, n=10)
    head = (f'<path d="M4 28 L-52 28 C-60 28 -62 36 -60 44 L-58 66 L-44 66 L-44 46 L4 46 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
            f'<path d="M-52 31 L2 31" stroke="{l}" stroke-width="1.8" opacity="0.9"/>'
            + finishings(mat, uid) + rune(-26, 40, e, 4))
    band = f'<rect x="-8" y="26" width="16" height="22" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/><circle cx="0" cy="37" r="3.6" fill="url(#gem{uid})"/>'
    clip = '<path d="M4 28 L-52 28 C-60 28 -62 36 -60 44 L-58 66 L-44 66 L-44 46 L4 46 Z"/>'
    return S(mat, uid, handle + head + band, clip)


def spear(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-3.8, 3.8, 44, 160, uid, n=12)
    head = (f'<path d="M0 0 C18 16 20 40 0 58 C-20 40 -18 16 0 0 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
            f'<path d="M0 6 L0 54" stroke="{o}" stroke-width="1.4" opacity="0.55"/>'
            f'<path d="M-10 18 C-14 30 -10 42 -2 52" stroke="{l}" stroke-width="1.8" fill="none" opacity="0.9"/>'
            + finishings(mat, uid) + rune(0, 36, e, 5))
    collar = f'<rect x="-8" y="56" width="16" height="12" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
    tassel = (f'<path d="M0 70 C10 76 14 88 8 100 C6 92 2 82 0 78 Z" fill="#7c3aed" stroke="#2a1458" stroke-width="1.4"/>'
              f'<path d="M0 70 C-9 78 -12 90 -7 102 C-5 92 -2 82 0 78 Z" fill="#a855f7" stroke="#2a1458" stroke-width="1.4"/>')
    clip = '<path d="M0 0 C18 16 20 40 0 58 C-20 40 -18 16 0 0 Z"/>'
    return S(mat, uid, handle + tassel + head + collar, clip)


def mace(mat, uid):
    l, m, d, o, e = pal(mat)
    mat = "iron" if mat not in MATS else mat
    handle = grip_wraps(-4.5, 4.5, 56, 154, uid, n=10)
    spikes = "".join(f'<path d="M-4 0 L0 -13 L4 0 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="1.6" transform="translate(0 34) rotate({a}) translate(0 -22)"/>' for a in range(0, 360, 45))
    ball = (f'<circle cx="0" cy="34" r="22" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.4"/>'
            f'<path d="M-14 22 C-8 14 6 12 12 16" stroke="{l}" stroke-width="2.2" fill="none" opacity="0.9"/>'
            f'<circle cx="0" cy="34" r="6" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="1.2"/>')
    ring = f'<rect x="-10" y="54" width="20" height="9" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
    clip = '<circle cx="0" cy="34" r="22"/>'
    return S(mat, uid, handle + ring + spikes + ball + finishings(mat, uid), clip)


def trident(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-3.8, 3.8, 52, 156, uid, n=10, col="#145a66")
    prong = lambda x, y0: f'<path d="M{x} {y0} L{x+5} {y0+14} L{x+5} 58 L{x-5} 58 L{x-5} {y0+14} Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2"/>'
    head = (prong(0, 0) + prong(-22, 10) + prong(22, 10)
            + f'<path d="M-27 58 C-27 44 -22 40 -22 40 L-17 40 C-17 40 -10 40 0 40 C10 40 17 40 17 40 L22 40 C22 40 27 44 27 58 Z" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
            + f'<circle cx="0" cy="52" r="5" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="1.2"/>')
    return S(mat, uid, handle + head, '<rect x="-30" y="0" width="60" height="58"/>')


TOOLS = {"sword": sword, "pickaxe": pickaxe, "axe": axe, "shovel": shovel, "hoe": hoe, "spear": spear}
SOLO = {"mace": (mace, "iron"), "trident": (trident, "diamond")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("assets/minecraft/textures/item"))
    ap.add_argument("--svg", type=Path, default=Path("assets/drakescraft/textures/gear/svg_hd"))
    ap.add_argument("--size", type=int, default=128)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True); a.svg.mkdir(parents=True, exist_ok=True)
    jobs = {}
    for mat in MATS:
        for tool, fn in TOOLS.items():
            jobs[f"{mat}_{tool}"] = fn(mat, f"{mat}{tool}")
    for name, (fn, mat) in SOLO.items():
        jobs[name] = fn(mat, name)
    for name, doc in jobs.items():
        sp = a.svg / f"{name}.svg"; sp.write_text(doc)
        subprocess.run(["rsvg-convert", "-w", str(a.size), "-h", str(a.size), str(sp), "-o", str(a.out / f"{name}.png")], check=True)
    print(len(jobs), "texturas HD", a.size)


if __name__ == "__main__":
    main()
