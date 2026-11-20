#!/usr/bin/env python3
"""Placas de rango con 7 niveles visuales (0 sobrio .. 6 apice). Reusa icon_svg/svg_to_png de
Slimefun-Texture-Drake/tools/gen_greek_badges_and_auras.py. Alto 44 px (height 11 en el font)."""
import importlib.util
from pathlib import Path
GEN = Path.home() / "Documentos/Desarrollo/Repositorios/drakescraft/Slimefun-Texture-Drake/tools/gen_greek_badges_and_auras.py"
_s = importlib.util.spec_from_file_location("gb", GEN); gb = importlib.util.module_from_spec(_s); _s.loader.exec_module(gb)
svg_to_png = gb.svg_to_png

FRAME = {  # stops (top->bottom) del marco por nivel
    0: ("#D9A066", "#B08D57", "#6B4F2A"), 1: ("#F8FAFC", "#CBD5E1", "#64748B"),
    2: ("#FFF2A6", "#D4AF37", "#8C6414"), 3: ("#FFF2A6", "#FFD700", "#8C6414"),
    4: ("#FFFFFF", "#FFD700", "#B8860B"), 5: None, 6: None}
PRISM = '<stop offset="0" stop-color="#FF4D6D"/><stop offset=".2" stop-color="#FFD60A"/><stop offset=".4" stop-color="#4ADE80"/><stop offset=".6" stop-color="#22D3EE"/><stop offset=".8" stop-color="#818CF8"/><stop offset="1" stop-color="#F472B6"/>'
SPARK = '<path d="M0,-4 L1,-1 L4,0 L1,1 L0,4 L-1,1 L-4,0 L-1,-1 Z" fill="#FFFFFF"/>'

def badge(label, c1, c2, icon, bg1, bg2, level):
    H = 44; W = ((max(124, 52 + int(len(label) * 16.5) + 26) + 3) // 4) * 4
    fr = FRAME[level]
    frame_fill = "url(#fr)"
    fdef = (f'<linearGradient id="fr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{fr[0]}"/><stop offset=".5" stop-color="{fr[1]}"/><stop offset="1" stop-color="{fr[2]}"/></linearGradient>'
            if fr else f'<linearGradient id="fr" x1="0" y1="0" x2="1" y2="0">{PRISM}</linearGradient>')
    pl_top, pl_bot = (("#2A1B3D", "#150A22") if level == 0 else ("#334155", "#0F172A") if level == 1 else (bg1, bg2))
    o = []
    if level >= 3:  # halo del color del rango
        o.append(f'<rect x="5" y="2" width="{W-10}" height="{H-4}" rx="8" fill="none" stroke="{c1}" stroke-width="3" opacity="{0.35 + 0.1*(level-3)}" filter="url(#bl)"/>')
    o.append(f'<rect x="6" y="2" width="{W-12}" height="{H-4}" rx="7" fill="#0B0213"/>')
    o.append(f'<rect x="8" y="3.5" width="{W-16}" height="{H-7}" rx="6" fill="{frame_fill}"/>')
    inset = 3 if level >= 1 else 2
    o.append(f'<rect x="{8+inset}" y="{3.5+inset}" width="{W-16-2*inset}" height="{H-7-2*inset}" rx="4" fill="url(#pl)"/>')
    o.append(f'<rect x="{9+inset}" y="{4+inset}" width="{W-18-2*inset}" height="10" rx="3" fill="#FFFFFF" opacity="0.10"/>')
    if level >= 2:
        o += [f'<rect x="{x}" y="5" width="6" height="2" fill="#FFD700" opacity=".5"/><rect x="{x}" y="{H-7}" width="6" height="2" fill="#FFD700" opacity=".5"/>' for x in range(18, W - 22, 12)]
    if level >= 3:  # laureles
        o.append(f'<path d="M5,22 C2,17 4,11 9,9 C7,14 7,17 8,22 C7,27 7,30 9,35 C4,33 2,27 5,22 Z" fill="url(#fr)" stroke="#1A0529"/><path d="M{W-5},22 C{W-2},17 {W-4},11 {W-9},9 C{W-7},14 {W-7},17 {W-8},22 C{W-7},27 {W-7},30 {W-9},35 C{W-4},33 {W-2},27 {W-5},22 Z" fill="url(#fr)" stroke="#1A0529"/>')
        o += [f'<circle cx="{x}" cy="{y}" r="1.6" fill="{c2}" stroke="#1A0529" stroke-width=".6"/>' for x in (14, W - 14) for y in (9, H - 9)]
    if level >= 4:  # linea interior de acento + destellos
        o.append(f'<rect x="{13}" y="9" width="{W-26}" height="{H-18}" rx="3" fill="none" stroke="{c1}" stroke-width=".8" opacity=".7"/>')
        o += [f'<g transform="translate({W-20},{y}) scale(.9)">{SPARK}</g>' for y in (12,)]
    if level >= 5:  # rayos tras el medallón + destellos
        o.append('<g opacity=".55" transform="translate(27,22)">' + "".join(f'<path d="M0,0 L{14*__import__("math").cos(a):.1f},{14*__import__("math").sin(a):.1f}" stroke="{c2}" stroke-width="1.2"/>' for a in [k*0.5236 for k in range(12)]) + '</g>')
        o += [f'<g transform="translate({x},{y}) scale({s})">{SPARK}</g>' for x, y, s in ((W - 30, 33, .8), (44, 10, .7), (W // 2 + 20, 38, .6))]
    if level >= 6:  # corona + doble marco
        o.append(f'<rect x="10" y="5" width="{W-20}" height="{H-10}" rx="5" fill="none" stroke="#FFFFFF" stroke-width=".7" opacity=".6"/>')
        o.append(f'<g transform="translate({W//2-6},-.5) scale(.75)">{gb.icon_svg("crown", "#FFD700", "#FFF3A1")}</g>')
    o.append(f'<circle cx="27" cy="22" r="11" fill="#150523" stroke="url(#fr)" stroke-width="1.6"/>')
    o.append(f'<g transform="translate(17.5,12.5) scale(1.18)">{gb.icon_svg(icon, c1, c2)}</g>')
    tx = 40 + (W - 56) // 2
    tf = f'font-family="DejaVu Sans, Liberation Sans, sans-serif" font-weight="900" font-size="21" letter-spacing="1.2" text-anchor="middle"'
    txtfill = "#FFFFFF" if level < 2 else "url(#tg)"
    o.append(f'<text x="{tx}" y="29.5" {tf} fill="#12031F">{label}</text>')
    if level >= 5: o.append(f'<text x="{tx}" y="28" {tf} fill="none" stroke="{c1}" stroke-width="1.6" opacity=".55">{label}</text>')
    o.append(f'<text x="{tx}" y="28" {tf} fill="{txtfill}">{label}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><defs>{fdef}'
           f'<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{pl_top}"/><stop offset="1" stop-color="{pl_bot}"/></linearGradient>'
           f'<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="{c2}"/><stop offset="1" stop-color="{c1}"/></linearGradient>'
           f'<filter id="bl" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="1.6"/></filter></defs>{"".join(o)}</svg>')
    return svg, W, H
