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
        + f'<filter id="noise{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1.4 -0.45"/></filter>'
        + f'<radialGradient id="glow{uid}" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{e}" stop-opacity="0.9"/><stop offset="1" stop-color="{e}" stop-opacity="0"/></radialGradient>'
    )


def shine(d, mat, uid, tag=""):
    """bisel (luz arriba-izq, sombra abajo-der), grano fino y rayitas, recortado al contorno d"""
    l, m, dk, o, e = MATS[mat]
    cid = f"bv{uid}{tag}"
    return (f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'
            f'<g clip-path="url(#{cid})">'
            f'<path d="{d}" fill="none" stroke="{l}" stroke-width="3.4" opacity="0.55" transform="translate(1.7 1.7)"/>'
            f'<path d="{d}" fill="none" stroke="{o}" stroke-width="3.4" opacity="0.5" transform="translate(-1.7 -1.7)"/>'
            f'<rect x="-80" y="-10" width="160" height="200" filter="url(#noise{uid})" opacity="0.22"/>'
            f'</g>')


def star(x, y, r, c="#ffffff", op=0.9):
    return f'<path d="M{x} {y-r} L{x+r*0.28} {y-r*0.28} L{x+r} {y} L{x+r*0.28} {y+r*0.28} L{x} {y+r} L{x-r*0.28} {y+r*0.28} L{x-r} {y} L{x-r*0.28} {y-r*0.28} Z" fill="{c}" opacity="{op}"/>'


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
             + shine("M0 2 L10 22 L10 98 L-10 98 L-10 22 Z", mat, uid)
             + finishings(mat, uid) + rune(0, 40, e) + rune(0, 60, e) + rune(0, 80, e)
             + star(0, 30, 2.6, e) + star(0, 50, 2, e) + star(0, 70, 2.6, e) + star(0, 88, 2, e)
             + f'<path d="M-7 98 L-7 104 M7 98 L7 104" stroke="{o}" stroke-width="2" opacity="0.6"/>')
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
            + shine("M-62 74 C-58 36 -30 22 0 22 C30 22 58 36 62 74 C54 56 30 42 0 42 C-30 42 -54 56 -62 74 Z", mat, uid)
            + finishings(mat, uid) + rune(-32, 52, e, 4) + rune(32, 52, e, 4) + star(-46, 56, 2.4, e) + star(46, 56, 2.4, e) + star(0, 30, 2.4, e))
    band = (f'<rect x="-10" y="30" width="20" height="20" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
            f'<circle cx="0" cy="40" r="4" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="1"/>')
    clip = '<path d="M-62 74 C-58 36 -30 22 0 22 C30 22 58 36 62 74 C54 56 30 42 0 42 C-30 42 -54 56 -62 74 Z"/>'
    return S(mat, uid, handle + head + band, clip)


def axe(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 34, 156, uid, n=11)
    hd = "M3 30 C-8 22 -26 22 -38 34 C-46 44 -44 58 -38 68 C-26 66 -12 62 3 58 Z"
    head = (f'<path d="{hd}" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
            + shine(hd, mat, uid)
            + f'<path d="M-36 36 C-40 48 -40 58 -36 66" stroke="{l}" stroke-width="2.4" fill="none" opacity="0.95"/>'
            f'<path d="M-4 30 L-4 58" stroke="{o}" stroke-width="1" opacity="0.5"/>'
            f'<path d="M3 36 L11 38 L11 50 L3 52 Z" fill="url(#metalv{uid})" stroke="{o}" stroke-width="1.8"/>'
            + finishings(mat, uid) + rune(-20, 48, e, 5) + star(-30, 40, 3, e))
    band = f'<rect x="-8" y="56" width="16" height="9" rx="2" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="1.8"/>'
    clip = f'<path d="{hd}"/>'
    return S(mat, uid, handle + head + band, clip)


def shovel(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 66, 140, uid, n=8)
    loop = f'<path d="M-14 150 C-14 138 14 138 14 150 C14 160 -14 160 -14 150 Z M-8 150 C-8 144 8 144 8 150 C8 155 -8 155 -8 150 Z" fill="url(#wood{uid})" stroke="#1b1008" stroke-width="1.4" fill-rule="evenodd"/>'
    blade = (f'<path d="M0 2 C26 6 30 38 16 60 L-16 60 C-30 38 -26 6 0 2 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
             f'<path d="M0 8 L0 56" stroke="{o}" stroke-width="1.2" opacity="0.45"/>'
             f'<path d="M-18 14 C-24 30 -20 44 -12 56" stroke="{l}" stroke-width="2" fill="none" opacity="0.9"/>'
             + shine("M0 2 C26 6 30 38 16 60 L-16 60 C-30 38 -26 6 0 2 Z", mat, uid)
             + finishings(mat, uid) + rune(0, 30, e, 6) + star(0, 14, 2.4, e) + star(-9, 40, 2, e) + star(9, 40, 2, e)
             + f'<path d="M-14 50 C-6 44 6 44 14 50" stroke="{o}" stroke-width="1.2" fill="none" opacity="0.5"/>')
    ferrule = f'<rect x="-11" y="58" width="22" height="12" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
    clip = '<path d="M0 2 C26 6 30 38 16 60 L-16 60 C-30 38 -26 6 0 2 Z"/>'
    return S(mat, uid, handle + loop + blade + ferrule, clip)


def hoe(mat, uid):
    l, m, d, o, e = pal(mat)
    handle = grip_wraps(-4.5, 4.5, 40, 156, uid, n=10)
    neck = "M4 28 L-46 28 L-46 40 L4 42 Z"
    blade = "M-62 28 L-40 28 L-38 62 L-48 84 L-60 74 L-64 50 Z"
    head = (f'<path d="{neck}" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
            f'<path d="{blade}" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
            + shine(neck, mat, uid, "n") + shine(blade, mat, uid, "b")
            + f'<path d="M-60 34 L-62 50 L-58 70" stroke="{l}" stroke-width="2.2" fill="none" opacity="0.95"/>'
            + finishings(mat, uid) + rune(-50, 54, e, 4) + star(-20, 35, 2.4, e))
    band = f'<rect x="-8" y="30" width="16" height="22" rx="3" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/><circle cx="0" cy="41" r="3.6" fill="url(#gem{uid})"/>'
    clip = f'<path d="{neck} {blade}"/>'
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


def S_flat(mat, uid, shapes, clip=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128">'
            f'<defs>{defs(mat, uid)}<clipPath id="clip{uid}">{clip}</clipPath></defs>'
            f'<g stroke-linejoin="round" stroke-linecap="round">{shapes}</g></svg>\n')


def bow(mat, uid, pull=-1):
    """pull=-1 reposo; 0..2 tensando (con flecha)"""
    l, m, d, o, e = pal("wooden")
    stave = "M8 8 C-34 32 -34 128 8 152"
    px = [8, 14, 22, 30][pull + 1] if pull >= 0 else 8
    body = (f'<path d="{stave}" fill="none" stroke="{o}" stroke-width="13"/>'
            f'<path d="{stave}" fill="none" stroke="url(#wood{uid})" stroke-width="9"/>'
            f'<path d="M6 12 C-30 34 -30 124 6 148" fill="none" stroke="{l}" stroke-width="2.4" opacity="0.8" transform="translate(-1.4 0)"/>'
            f'<rect x="-30" y="66" width="12" height="28" rx="3" fill="#3b2a5a" stroke="#1b1008" stroke-width="1.6" transform="rotate(-6 -24 80)"/>'
            f'<circle cx="8" cy="8" r="5" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="1.6"/>'
            f'<circle cx="8" cy="152" r="5" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="1.6"/>'
            + star(-26, 44, 2.6, "#c084fc") + star(-26, 116, 2.6, "#c084fc"))
    string = f'<path d="M8 8 L{px} 80 L8 152" fill="none" stroke="#e8e2f6" stroke-width="2"/>'
    arrow = ""
    if pull >= 0:
        arrow = (f'<path d="M{px} 80 L-44 80" stroke="#7a5530" stroke-width="3.6"/><path d="M-44 80 L-58 80" stroke="{o}" stroke-width="0"/>'
                 f'<path d="M-44 74 L-62 80 L-44 86 Z" fill="url(#metal{uid})" stroke="{MATS["iron"][3]}" stroke-width="1.6"/>'
                 f'<path d="M{px} 80 L{px+6} 74 L{px+12} 74 L{px+8} 80 L{px+12} 86 L{px+6} 86 Z" fill="#e8e2f6" stroke="{o}" stroke-width="1.2"/>')
    return S(mat, uid, string + arrow + body, "")


def crossbow(mat, uid, state="standby", string_y=66):
    l, m, d, o, e = pal("wooden")
    stock = (f'<path d="M-8 52 L8 52 L10 150 L-10 150 Z" fill="url(#wood{uid})" stroke="{o}" stroke-width="2.2"/>'
             f'<path d="M-5 56 L-6 148" stroke="{l}" stroke-width="2" opacity="0.7"/>'
             f'<rect x="-8" y="96" width="16" height="9" rx="2" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="1.6"/>'
             f'<path d="M-3 104 L-3 118 L3 118 L3 104" fill="#1b1008" opacity="0.75"/>'
             + star(0, 134, 2.6, "#c084fc"))
    prod = (f'<path d="M-62 50 C-34 30 34 30 62 50" fill="none" stroke="{o}" stroke-width="13"/>'
            f'<path d="M-62 50 C-34 30 34 30 62 50" fill="none" stroke="url(#metalv{uid})" stroke-width="8"/>'
            f'<path d="M-58 48 C-32 31 32 31 58 48" fill="none" stroke="{MATS["iron"][0]}" stroke-width="1.8" opacity="0.85"/>'
            f'<circle cx="-62" cy="50" r="5" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="1.6"/><circle cx="62" cy="50" r="5" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="1.6"/>')
    string = f'<path d="M-62 50 L0 {string_y} L62 50" fill="none" stroke="#e8e2f6" stroke-width="2"/>'
    extra = ""
    if state == "arrow":
        extra = (f'<path d="M0 {string_y} L0 14" stroke="#7a5530" stroke-width="4"/><path d="M-8 22 L0 -2 L8 22 Z" fill="url(#metal{uid})" stroke="{MATS["iron"][3]}" stroke-width="1.6"/>'
                 f'<path d="M0 {string_y} L-6 {string_y+10} M0 {string_y} L6 {string_y+10}" stroke="#e8e2f6" stroke-width="5" opacity="0.9"/>')
    if state == "firework":
        extra = (f'<rect x="-6" y="14" width="12" height="52" rx="3" fill="#b3261e" stroke="#4a0f0b" stroke-width="2"/>'
                 f'<path d="M-6 14 L0 -4 L6 14 Z" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="1.6"/>'
                 f'<rect x="-6" y="34" width="12" height="6" fill="url(#gold{uid})"/>' + star(0, 52, 3, "#ffe08a"))
    return S(mat, uid, stock + extra + string + prod, "")


def arrow(mat, uid, kind="arrow"):
    l, m, d, o, e = pal("iron")
    head_fill = {"arrow": f"url(#metal{uid})", "spectral": f"url(#gold{uid})", "tipped_head": "#f4f1fb", "tipped_base": "none"}[kind]
    head_stroke = {"tipped_base": "none"}.get(kind, o)
    shaft = "" if kind == "tipped_head" else (f'<rect x="-3" y="26" width="6" height="104" rx="1.5" fill="url(#wood{uid})" stroke="#1b1008" stroke-width="1.6"/>')
    feath_col = {"arrow": "#e8e2f6", "spectral": "#ffe08a", "tipped_base": "#e8e2f6", "tipped_head": "none"}[kind]
    feathers = "" if kind == "tipped_head" else "".join(
        f'<path d="M-3 {y} L-16 {y+14} L-16 {y+28} L-3 {y+16} Z M3 {y} L16 {y+14} L16 {y+28} L3 {y+16} Z" fill="{feath_col}" stroke="#2a2438" stroke-width="1.4"/>'
        for y in (104, 118))
    head = (f'<path d="M0 0 L12 28 L0 22 L-12 28 Z" fill="{head_fill}" stroke="{head_stroke}" stroke-width="2"/>'
            + ('' if kind in ("tipped_head", "tipped_base") else f'<path d="M0 4 L0 22" stroke="{o}" stroke-width="1.2" opacity="0.6"/>'))
    if kind == "spectral":
        head += star(0, 14, 4, "#ffffff", 0.95) + f'<circle cx="0" cy="14" r="14" fill="url(#glow{uid})" opacity="0.7"/>'
    return S(mat, uid, shaft + feathers + head, "")


def elytra(mat, uid, broken=False):
    wing = ("M-4 18 C-38 4 -76 20 -92 68 C-80 96 -52 112 -20 122 C-12 84 -10 50 -4 18 Z")
    grad = (f'<linearGradient id="ely{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6b4fa0"/><stop offset="0.55" stop-color="#3b2a63"/><stop offset="1" stop-color="#17101f"/></linearGradient>')
    ribs = "".join(f'<path d="M-6 {20+i*3} C-{34+i*8} {20+i*18} -{56+i*10} {52+i*14} -{18+i*22} {118-i*4}" fill="none" stroke="#bfa6ff" stroke-width="1.4" opacity="0.55"/>' for i in range(4))
    tear = ('<path d="M-60 40 L-48 56 L-60 62 L-46 78 L-62 86" fill="none" stroke="#0d0a14" stroke-width="3"/>' if broken else "")
    one = (f'<path d="{wing}" fill="url(#ely{uid})" stroke="#0d0a14" stroke-width="2.6"/>'
           f'<path d="{wing}" fill="none" stroke="#d4c3ff" stroke-width="2" opacity="0.7" transform="translate(1.6 1.6)" clip-path="url(#ewc{uid})"/>'
           + ribs + tear
           + f'<circle cx="-14" cy="30" r="3.6" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="1.2"/><circle cx="-16" cy="56" r="3.2" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="1.2"/>'
           + star(-48, 62, 3.4, "#e9d5ff") + star(-30, 90, 2.4, "#c084fc") + star(-70, 74, 2, "#ffffff"))
    body = (f'<defs>{grad}<clipPath id="ewc{uid}"><path d="{wing}"/></clipPath></defs>'
            f'<g transform="translate(64 14) scale(0.62)">{one}<g transform="scale(-1 1)">{one}</g></g>'
            f'<path d="M64 24 L64 120" stroke="#0d0a14" stroke-width="3"/>')
    doc = S_flat(mat, uid, body.replace("<defs>", "<defs>", 1))
    return doc.replace("</defs><g", "</defs><g", 1)


def totem(mat, uid):
    body = (f'<circle cx="64" cy="64" r="58" fill="url(#glow{uid})" opacity="0.55"/>'
            f'<path d="M64 8 C84 8 88 26 84 38 L112 52 L104 68 L84 62 L84 112 L44 112 L44 62 L24 68 L16 52 L44 38 C40 26 44 8 64 8 Z" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="3"/>'
            f'<path d="M64 12 C80 12 82 26 79 36 L100 48" fill="none" stroke="#fff6c2" stroke-width="2.4" opacity="0.8" transform="translate(1 1)"/>'
            f'<path d="M50 26 L58 24 L58 32 L52 32 Z M78 26 L70 24 L70 32 L76 32 Z" fill="#1b1008"/>'
            f'<path d="M64 34 L64 42" stroke="#1b1008" stroke-width="2.4"/>'
            f'<path d="M64 56 L74 70 L64 92 L54 70 Z" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="2"/>'
            f'<path d="M50 100 L78 100 M50 106 L78 106" stroke="#8f6a1c" stroke-width="2"/>'
            + star(64, 74, 4, "#ffffff") + star(30, 54, 2.6, "#c084fc") + star(98, 54, 2.6, "#c084fc") + star(64, 12, 2.4, "#fff6c2"))
    return S_flat(mat, uid, body)


def shears(mat, uid):
    l, m, d, o, e = pal("iron")
    blade = lambda sx: (f'<g transform="rotate({sx*-9} 0 90) scale({sx} 1)">'
                        f'<path d="M0 4 C10 20 12 50 4 92 L-6 92 C-2 56 -4 24 0 4 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.2"/>'
                        f'<path d="M-1 12 C3 30 4 56 0 86" stroke="{l}" stroke-width="2" fill="none" opacity="0.9"/></g>')
    loops = (f'<path d="M-4 92 C-30 96 -34 128 -12 140 C-2 144 6 136 6 126 L0 92 Z" fill="url(#wood{uid})" stroke="#1b1008" stroke-width="2.2"/>'
             f'<path d="M4 92 C30 96 34 128 12 140 C2 144 -6 136 -6 126 L0 92 Z" fill="url(#wood{uid})" stroke="#1b1008" stroke-width="2.2" transform="translate(0 0)"/>'
             f'<ellipse cx="-14" cy="122" rx="7" ry="10" fill="#1b1424" opacity="0.8"/><ellipse cx="14" cy="122" rx="7" ry="10" fill="#1b1424" opacity="0.8"/>')
    pivot = f'<circle cx="0" cy="90" r="6" fill="url(#gold{uid})" stroke="#3a2a08" stroke-width="2"/><circle cx="0" cy="90" r="2.2" fill="url(#gem{uid})"/>'
    return S("iron", uid, blade(1) + blade(-1) + loops + pivot + star(0, 40, 2.4, MATS["iron"][4]), "")


def brush(mat, uid):
    l, m, d, o, e = pal("copper")
    handle = grip_wraps(-6, 6, 70, 150, uid, n=7, col="#145a66")
    ferrule = f'<rect x="-11" y="56" width="22" height="18" rx="3" fill="url(#metalv{uid})" stroke="{o}" stroke-width="2.2"/><path d="M-11 64 L11 64" stroke="{o}" stroke-width="1.4" opacity="0.6"/>'
    bristles = "".join(f'<path d="M{x} 58 C{x+(x/6)} 36 {x+(x/3)} 20 {x+(x/2)} {8+abs(x)}" fill="none" stroke="{c}" stroke-width="5" opacity="0.95"/>' for x, c in ((-8, "#7a5530"), (-4, "#b0834a"), (0, "#e0c08a"), (4, "#b0834a"), (8, "#7a5530")))
    return S("copper", uid, handle + bristles + ferrule + star(0, 90, 2.6, "#3fd9b8"), "")


def flint_and_steel(mat, uid):
    l, m, d, o, e = pal("iron")
    steel = (f'<path d="M-36 120 C-36 80 -10 70 18 74 C44 78 46 112 20 118 C4 122 -4 112 6 102 C16 92 4 88 -14 94 C-22 100 -20 118 -22 128 Z" fill="url(#metal{uid})" stroke="{o}" stroke-width="2.4"/>'
             f'<path d="M-30 118 C-30 88 -10 78 16 80" stroke="{l}" stroke-width="2.2" fill="none" opacity="0.9"/>')
    flint = (f'<path d="M30 40 L56 30 L74 54 L60 78 L34 70 Z" fill="#3a3a48" stroke="#0d0a14" stroke-width="2.4"/>'
             f'<path d="M36 44 L56 36 L66 52" stroke="#9aa0b8" stroke-width="2" fill="none" opacity="0.85"/>')
    sparks = star(26, 50, 7, "#ffd35a") + star(16, 34, 4.2, "#fff0a8") + star(40, 24, 3.4, "#ff9d3a")
    return S_flat("iron", uid, f'<g transform="translate(26 14) scale(0.78)">{steel}{flint}{sparks}</g>')


def fishing_rod(mat, uid, cast=False):
    l, m, d, o, e = pal("wooden")
    rod = grip_wraps(-3.4, 3.4, 8, 152, uid, n=16)
    guides = "".join(f'<circle cx="0" cy="{y}" r="4" fill="none" stroke="url(#gold{uid})" stroke-width="2"/>' for y in (30, 62, 94))
    reel = f'<rect x="-10" y="116" width="20" height="14" rx="3" fill="url(#metalv{uid})" stroke="#232733" stroke-width="2"/><circle cx="0" cy="123" r="3" fill="url(#gem{uid})"/>'
    if cast:
        line = f'<path d="M0 8 C40 30 70 70 70 150" fill="none" stroke="#e8e2f6" stroke-width="2.4"/>'
    else:
        line = f'<path d="M0 8 C30 10 44 40 44 76" fill="none" stroke="#e8e2f6" stroke-width="2.4"/><circle cx="44" cy="82" r="6" fill="#b3261e" stroke="#4a0f0b" stroke-width="1.8"/>'
    return S("wooden", uid, line + rod + guides + reel, "")


ARMOR_MATS = ("chainmail", "iron", "golden", "diamond", "netherite", "copper")
MATS["chainmail"] = ("#c3c8d8", "#7d8398", "#40445a", "#1a1b27", "#8b5cf6")


def armor_icon(mat, uid, kind):
    l, m, d, o, e = pal(mat)
    chain = mat == "chainmail"
    fillm = f"url(#metalv{uid})"
    if kind == "helmet":
        sh = "M18 78 C14 40 34 16 64 16 C94 16 114 40 110 78 L110 104 L88 104 L88 84 C88 74 80 70 72 70 L56 70 C48 70 40 74 40 84 L40 104 L18 104 Z"
        extra = (f'<path d="M58 16 C60 6 68 6 70 16 L70 44 L58 44 Z" fill="#7c3aed" stroke="#2a1458" stroke-width="2"/>'
                 f'<path d="M24 62 L104 62 L104 70 L24 70 Z" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
                 f'<path d="M64 70 L64 92" stroke="{o}" stroke-width="3" opacity="0.7"/>' + star(36, 40, 3, e) + star(92, 40, 3, e))
    elif kind == "chestplate":
        sh = "M10 40 L36 22 L50 28 C58 36 70 36 78 28 L92 22 L118 40 L110 76 L98 70 L96 112 L32 112 L30 70 L18 76 Z"
        extra = (f'<path d="M64 40 L64 108" stroke="{o}" stroke-width="2.4" opacity="0.6"/>'
                 f'<path d="M64 52 L74 68 L64 88 L54 68 Z" fill="url(#gem{uid})" stroke="#2a1458" stroke-width="2"/>'
                 f'<path d="M34 100 L94 100" stroke="url(#gold{uid})" stroke-width="5"/>' + star(40, 56, 3, e) + star(88, 56, 3, e))
    elif kind == "leggings":
        sh = "M30 20 L98 20 L102 112 L74 112 L68 54 L60 54 L54 112 L26 112 Z"
        extra = (f'<path d="M30 20 L98 20 L98 34 L30 34 Z" fill="url(#goldv{uid})" stroke="#3a2a08" stroke-width="2"/>'
                 f'<circle cx="64" cy="27" r="4" fill="url(#gem{uid})"/>' + star(40, 72, 3, e) + star(88, 72, 3, e))
    else:
        sh = "M12 26 L46 26 L46 66 L60 74 C66 78 66 90 60 98 L60 106 L12 106 Z"
        sh2 = "M116 26 L82 26 L82 66 L68 74 C62 78 62 90 68 98 L68 106 L116 106 Z"
        extra = (f'<path d="M12 40 L46 40 M82 40 L116 40" stroke="url(#gold{uid})" stroke-width="5"/>' + star(28, 80, 3, e) + star(100, 80, 3, e))
    shapes = f'<path d="{sh}" fill="{fillm}" stroke="{o}" stroke-width="3"/>'
    if kind == "boots":
        shapes += f'<path d="{sh2}" fill="{fillm}" stroke="{o}" stroke-width="3"/>'
    shapes += shine(sh, mat, uid, "a") + (shine(sh2, mat, uid, "b") if kind == "boots" else "")
    if chain:
        shapes += f'<g clip-path="url(#bv{uid}a)" opacity="0.45">' + "".join(f'<circle cx="{x}" cy="{y}" r="4.2" fill="none" stroke="{o}" stroke-width="1.4"/>' for y in range(20, 116, 8) for x in range(10 + (y // 8 % 2) * 4, 120, 8)) + '</g>'
    shapes += finishings(mat, uid) + extra
    return S_flat(mat, uid, shapes, f'<path d="{sh}"/>')


TOOLS = {"sword": sword, "pickaxe": pickaxe, "axe": axe, "shovel": shovel, "hoe": hoe, "spear": spear}
SOLO = {"mace": (mace, "iron"), "trident": (trident, "diamond"),
        "bow": (lambda m, u: bow(m, u, -1), "wooden"), "bow_pulling_0": (lambda m, u: bow(m, u, 0), "wooden"),
        "bow_pulling_1": (lambda m, u: bow(m, u, 1), "wooden"), "bow_pulling_2": (lambda m, u: bow(m, u, 2), "wooden"),
        "crossbow_standby": (lambda m, u: crossbow(m, u, "standby", 66), "wooden"),
        "crossbow_pulling_0": (lambda m, u: crossbow(m, u, "standby", 58), "wooden"),
        "crossbow_pulling_1": (lambda m, u: crossbow(m, u, "standby", 62), "wooden"),
        "crossbow_pulling_2": (lambda m, u: crossbow(m, u, "standby", 68), "wooden"),
        "crossbow_arrow": (lambda m, u: crossbow(m, u, "arrow", 66), "wooden"),
        "crossbow_firework": (lambda m, u: crossbow(m, u, "firework", 66), "wooden"),
        "arrow": (lambda m, u: arrow(m, u, "arrow"), "iron"), "spectral_arrow": (lambda m, u: arrow(m, u, "spectral"), "golden"),
        "tipped_arrow_base": (lambda m, u: arrow(m, u, "tipped_base"), "iron"), "tipped_arrow_head": (lambda m, u: arrow(m, u, "tipped_head"), "iron"),
        "elytra": (lambda m, u: elytra(m, u), "netherite"), "broken_elytra": (lambda m, u: elytra(m, u, True), "netherite"),
        "totem_of_undying": (totem, "golden"),
        "shears": (shears, "iron"), "brush": (brush, "copper"), "flint_and_steel": (flint_and_steel, "iron"),
        "fishing_rod": (lambda m, u: fishing_rod(m, u, False), "wooden"), "fishing_rod_cast": (lambda m, u: fishing_rod(m, u, True), "wooden")}
for _m in MATS:
    if _m not in ("iron", "chainmail"):
        SOLO[f"{_m}_mace"] = (mace, _m)


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
    for mat in ARMOR_MATS:
        for kind in ("helmet", "chestplate", "leggings", "boots"):
            nm = f"{mat}_{kind}"
            jobs[nm] = armor_icon(mat, nm, kind)
    for name, doc in jobs.items():
        sp = a.svg / f"{name}.svg"; sp.write_text(doc)
        subprocess.run(["rsvg-convert", "-w", str(a.size), "-h", str(a.size), str(sp), "-o", str(a.out / f"{name}.png")], check=True)
    print(len(jobs), "texturas HD", a.size)


if __name__ == "__main__":
    main()
