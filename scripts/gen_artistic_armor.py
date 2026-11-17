#!/usr/bin/env python3
"""Generador de Armaduras Artísticas de Alta Definición para DrakesCraft.
Diseño heráldico y anatómico vectorial (SVG) con resolución 4x (256x128).
Reemplaza el patrón genérico de bloques por placas esculpidas, gorgueras, petos,
hombreras, grebas, visores y ornamentos únicos por material.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import random
import subprocess
import zipfile
from pathlib import Path
from PIL import Image

DEFAULT_JAR = Path.home() / ".local/share/horizon-launcher/versions/nightly-2026-11-05-66f3981/.local/minecraft/26.3/jars/client.jar"
SCALE = 4

# --- PALETAS ARTÍSTICAS RICAS Y CONTRASTADAS ---
PALETTES = {
    "netherite": {
        "base_dark": "#120e18",
        "base_mid": "#241d2e",
        "base_light": "#3d324c",
        "specular": "#a092b8",
        "trim": "#d4af37",      # Oro ancestral
        "trim_dark": "#7a5f13",
        "trim_light": "#fff099",
        "accent": "#9933ff",    # Resplandor nether violeta
        "accent_glow": "#c280ff",
        "rivet": "#e0c068",
        "joint": "#0a070e",
        "style": "netherite"
    },
    "diamond": {
        "base_dark": "#022633",
        "base_mid": "#0a5669",
        "base_light": "#158c9e",
        "specular": "#64f5ff",
        "trim": "#c8f6ff",      # Platino cristalino
        "trim_dark": "#0e4a57",
        "trim_light": "#ffffff",
        "accent": "#00f0ff",    # Gema cian pura
        "accent_glow": "#a6fdff",
        "rivet": "#b8f4ff",
        "joint": "#01131a",
        "style": "diamond"
    },
    "iron": {
        "base_dark": "#252b36",
        "base_mid": "#4f596b",
        "base_light": "#838f9f",
        "specular": "#dce4ec",
        "trim": "#c49a45",      # Bronce / latón
        "trim_dark": "#5e4514",
        "trim_light": "#fce088",
        "accent": "#eef4fa",    # Acero pulido
        "accent_glow": "#ffffff",
        "rivet": "#d8b056",
        "joint": "#15181f",
        "style": "iron"
    },
    "gold": {
        "base_dark": "#4a3300",
        "base_mid": "#9e7408",
        "base_light": "#dca71b",
        "specular": "#fff085",
        "trim": "#ffe066",      # Oro brillante
        "trim_dark": "#664700",
        "trim_light": "#ffffff",
        "accent": "#d91438",    # Rubí imperial
        "accent_glow": "#ff6685",
        "rivet": "#ffeaa0",
        "joint": "#261a00",
        "style": "gold"
    },
    "copper": {
        "base_dark": "#361608",
        "base_mid": "#783616",
        "base_light": "#b85c2c",
        "specular": "#f7a072",
        "trim": "#228068",      # Cardenillo / pátina turquesa
        "trim_dark": "#104235",
        "trim_light": "#52deb8",
        "accent": "#e87038",    # Cobre pulido
        "accent_glow": "#ffd1b3",
        "rivet": "#e5a044",
        "joint": "#1c0a03",
        "style": "copper"
    },
    "chainmail": {
        "base_dark": "#181c24",
        "base_mid": "#384152",
        "base_light": "#6b778c",
        "specular": "#b8c4d8",
        "trim": "#422818",      # Cuero de gambesón
        "trim_dark": "#24140b",
        "trim_light": "#805234",
        "accent": "#90a0b8",    # Anillas pulidas
        "accent_glow": "#ffffff",
        "rivet": "#c0cdd8",
        "joint": "#0d0f14",
        "style": "chainmail"
    },
    "turtle_scute": {
        "base_dark": "#0a2614",
        "base_mid": "#195c32",
        "base_light": "#329955",
        "specular": "#82f0a8",
        "trim": "#38b2ac",      # Prismarina abisal
        "trim_dark": "#134e4a",
        "trim_light": "#99f6e4",
        "accent": "#48e07b",    # Escamas esmeralda
        "accent_glow": "#bbf7d0",
        "rivet": "#6ee7b7",
        "joint": "#05140a",
        "style": "turtle"
    },
    "leather": {
        "base_dark": "#3d2212",
        "base_mid": "#734324",
        "base_light": "#a8693d",
        "specular": "#dba479",
        "trim": "#f0dbbe",      # Costura doble artesanal
        "trim_dark": "#261408",
        "trim_light": "#ffffff",
        "accent": "#c48350",    # Cuero teñido
        "accent_glow": "#ffd7b3",
        "rivet": "#c89a3c",     # Remaches latón
        "joint": "#1f1008",
        "style": "leather"
    },
    "dragon": {
        "base_dark": "#10061e",
        "base_mid": "#2a104c",
        "base_light": "#52238f",
        "specular": "#b875ff",
        "trim": "#ffd033",      # Oro imperial de dragón
        "trim_dark": "#7a5e08",
        "trim_light": "#fff7b3",
        "accent": "#00f0ff",    # Ojos y aliento cian del vacío
        "accent_glow": "#70ffff",
        "rivet": "#ffda55",
        "joint": "#080210",
        "style": "dragon"
    },
    "kintsugi": {
        "base_dark": "#0b0912",
        "base_mid": "#1b1726",
        "base_light": "#322c42",
        "specular": "#8e84a6",
        "trim": "#ffd700",      # Oro líquido fundido (Kintsugi)
        "trim_dark": "#8a6d00",
        "trim_light": "#fff499",
        "accent": "#ffd700",
        "accent_glow": "#fffad6",
        "rivet": "#ffd700",
        "joint": "#050408",
        "style": "kintsugi"
    }
}

VANILLA_JSON = ["netherite", "diamond", "iron", "gold", "chainmail", "copper", "leather"]
HUMANOID_MATS = VANILLA_JSON + ["turtle_scute"]
CUSTOM = ["kintsugi", "dragon"]
OLD_NAME = {
    "netherite": "netherite", "diamond": "diamond", "iron": "iron", "gold": "gold",
    "chainmail": "chainmail", "leather": "leather", "turtle_scute": "turtle"
}

def f(val: float) -> str:
    return f"{val:.2f}".rstrip("0").rstrip(".")

class SvgBuilder:
    def __init__(self, w: int, h: int, pal: dict, seed_key: str):
        self.w, self.h, self.pal = w, h, pal
        self.rng = random.Random(seed_key)
        self.defs: list[str] = []
        self.body: list[str] = []

    def add_def(self, s: str):
        self.defs.append(s)

    def add(self, s: str):
        self.body.append(s)

    def set_clip_mask(self, runs: list[tuple[int, int, int, int]]):
        rects = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>' for x, y, w, h in runs)
        self.add_def(f'<clipPath id="reg">{rects}</clipPath>')

    def build(self) -> str:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w * SCALE}" height="{self.h * SCALE}">'
            f'<defs>{"".join(self.defs)}</defs>'
            f'<g clip-path="url(#reg)">{"".join(self.body)}</g>'
            f'</svg>'
        )

def setup_gradients(b: SvgBuilder, pal: dict):
    # Gradientes metálicos, biseles y brillos
    bd, bm, bl, sp = pal["base_dark"], pal["base_mid"], pal["base_light"], pal["specular"]
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    ac, ac_g = pal["accent"], pal["accent_glow"]

    b.add_def(f'<linearGradient id="g_plate" x1="0" y1="0" x2="0" y2="1">'
              f'<stop offset="0" stop-color="{bl}"/><stop offset=".4" stop-color="{bm}"/>'
              f'<stop offset="1" stop-color="{bd}"/></linearGradient>')
    b.add_def(f'<linearGradient id="g_diag" x1="0" y1="0" x2="1" y2="1">'
              f'<stop offset="0" stop-color="{sp}" stop-opacity=".7"/>'
              f'<stop offset=".3" stop-color="{bl}"/><stop offset=".8" stop-color="{bm}"/>'
              f'<stop offset="1" stop-color="{bd}"/></linearGradient>')
    b.add_def(f'<linearGradient id="g_trim" x1="0" y1="0" x2="0" y2="1">'
              f'<stop offset="0" stop-color="{tr_l}"/><stop offset=".5" stop-color="{tr}"/>'
              f'<stop offset="1" stop-color="{tr_d}"/></linearGradient>')
    b.add_def(f'<linearGradient id="g_trim_h" x1="0" y1="0" x2="1" y2="0">'
              f'<stop offset="0" stop-color="{tr_l}"/><stop offset=".5" stop-color="{tr}"/>'
              f'<stop offset="1" stop-color="{tr_d}"/></linearGradient>')
    b.add_def(f'<radialGradient id="g_gem" cx=".4" cy=".35" r=".7">'
              f'<stop offset="0" stop-color="{ac_g}"/><stop offset=".6" stop-color="{ac}"/>'
              f'<stop offset="1" stop-color="{bd}"/></radialGradient>')
    b.add_def(f'<linearGradient id="g_flute" x1="0" y1="0" x2="1" y2="0">'
              f'<stop offset="0" stop-color="{bd}" stop-opacity=".8"/>'
              f'<stop offset=".4" stop-color="{sp}" stop-opacity=".6"/>'
              f'<stop offset="1" stop-color="{bd}" stop-opacity=".8"/></linearGradient>')
    b.add_def('<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
              '<feGaussianBlur stdDeviation=".4"/></filter>')
    b.add_def('<filter id="soft" x="-20%" y="-20%" width="140%" height="140%">'
              '<feGaussianBlur stdDeviation=".15"/></filter>')

def draw_helmet(b: SvgBuilder, pal: dict, mat: str):
    """Dibuja el casco anatómico (0..32, 0..16)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd = pal["specular"], pal["base_dark"]

    # 1. Base sólida de fondo con degradado de volumen
    a(f'<rect x="0" y="0" width="32" height="16" fill="url(#g_plate)"/>')

    # 2. Cresta superior (top: x=8..16, y=0..8)
    a(f'<rect x="11.2" y="0" width="1.6" height="8" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
    a(f'<line x1="12" y1="0" x2="12" y2="8" stroke="{sp}" stroke-width=".3" stroke-linecap="round"/>')
    for y_ in (2, 4, 6):
        a(f'<path d="M 8.5 {y_} Q 12 {y_ - .6} 15.5 {y_}" fill="none" stroke="{tr_d}" stroke-width=".2"/>')
        a(f'<circle cx="9.2" cy="{y_}" r=".2" fill="{tr_l}"/>')
        a(f'<circle cx="14.8" cy="{y_}" r=".2" fill="{tr_l}"/>')

    # 3. Frente del casco (front: x=8..16, y=8..16)
    a(f'<rect x="8" y="8" width="8" height="2.2" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".14"/>')
    a(f'<line x1="8" y1="8.3" x2="16" y2="8.3" stroke="{tr_l}" stroke-width=".2"/>')
    for x_ in (8.8, 10.4, 13.6, 15.2):
        a(f'<circle cx="{x_}" cy="9.1" r=".22" fill="{tr_l}" stroke="{tr_d}" stroke-width=".05"/>')

    # Gema o emblema frontal central (x=12, y=9.1)
    if mat in ("diamond", "dragon", "gold", "netherite"):
        a(f'<path d="M 12 8.3 L 12.8 9.2 L 12 10.1 L 11.2 9.2 Z" fill="url(#g_gem)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<circle cx="12" cy="9.2" r=".2" fill="#fff" filter="url(#soft)"/>')

    # Protección de ceja y visera (y=10..12)
    a(f'<path d="M 8 10.2 L 12 10.8 L 16 10.2 L 16 11.3 L 12 12 L 8 11.3 Z" fill="url(#g_diag)" stroke="{bd}" stroke-width=".15"/>')
    a(f'<path d="M 8.2 10.3 L 12 10.9 L 15.8 10.3" fill="none" stroke="{sp}" stroke-width=".2"/>')

    # Puente nasal (y=11..13, x=11.3..12.7)
    a(f'<rect x="11.3" y="10.8" width="1.4" height="2.2" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
    a(f'<line x1="12" y1="10.8" x2="12" y2="13" stroke="{tr_l}" stroke-width=".2"/>')

    # Guardamejillas laterales en el frontal (y=13..16, x=8..9.5 y x=14.5..16)
    a(f'<path d="M 8 12.5 H 9.5 V 15.8 H 8 Z" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<path d="M 14.5 12.5 H 16 V 15.8 H 14.5 Z" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<circle cx="8.7" cy="14.5" r=".2" fill="{tr_l}"/>')
    a(f'<circle cx="15.3" cy="14.5" r=".2" fill="{tr_l}"/>')

    # 4. Laterales del casco (right: x=0..8, left: x=16..24, y=8..16)
    for sx, is_left in ((0, False), (16, True)):
        cx = sx + 4
        a(f'<circle cx="{cx}" cy="10.5" r="1.8" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".15"/>')
        a(f'<circle cx="{cx}" cy="10.5" r="1.1" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<circle cx="{cx}" cy="10.5" r=".4" fill="url(#g_gem)" stroke="{tr_d}" stroke-width=".06"/>')
        a(f'<path d="M {sx} 12 Q {cx} 13.5 {sx + 8} 12" fill="none" stroke="{tr}" stroke-width=".25"/>')
        for dy in (-.7, 0, .7):
            a(f'<line x1="{cx - .6}" y1="{10.5 + dy}" x2="{cx + .6}" y2="{10.5 + dy}" stroke="{bd}" stroke-width=".18"/>')

    # 5. Cogotera trasera (back: x=24..32, y=8..16)
    for ly in (8, 10.2, 12.4, 14.2):
        a(f'<rect x="24" y="{ly}" width="8" height="2" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".12"/>')
        a(f'<line x1="24" y1="{ly + .2}" x2="32" y2="{ly + .2}" stroke="{sp}" stroke-width=".2"/>')
        a(f'<circle cx="25" cy="{ly + 1}" r=".18" fill="{tr_l}"/>')
        a(f'<circle cx="31" cy="{ly + 1}" r=".18" fill="{tr_l}"/>')

def draw_cuirass(b: SvgBuilder, pal: dict, mat: str):
    """Dibuja el peto / coraza principal (Body: x=16..40, y=16..32)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd, bm = pal["specular"], pal["base_dark"], pal["base_mid"]
    ac, ac_g = pal["accent"], pal["accent_glow"]

    a(f'<rect x="16" y="16" width="24" height="16" fill="url(#g_plate)"/>')

    # 1. Hombros / Cuello superior (top: x=20..28, y=16..20)
    a(f'<rect x="20" y="16" width="8" height="4" fill="url(#g_diag)"/>')
    a(f'<rect x="22" y="16.5" width="4" height="3" rx=".8" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<ellipse cx="24" cy="18" rx="1.4" ry=".8" fill="{bd}"/>')

    # 2. Frente del Peto (front: x=20..28, y=20..32)
    # Gorguera / cuello protector
    a(f'<path d="M 20 20 L 24 21.5 L 28 20 L 28 21.2 L 24 22.8 L 20 21.2 Z" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<path d="M 20.5 20.3 L 24 21.7 L 27.5 20.3" fill="none" stroke="{tr_l}" stroke-width=".25"/>')

    # Placas pectorales esculpidas
    a(f'<path d="M 20.3 21.8 L 23.8 22.8 L 23.8 26.2 L 20.5 25.5 Z" fill="url(#g_diag)" stroke="{tr_d}" stroke-width=".1"/>')
    a(f'<path d="M 27.7 21.8 L 24.2 22.8 L 24.2 26.2 L 27.5 25.5 Z" fill="url(#g_diag)" stroke="{tr_d}" stroke-width=".1"/>')
    a(f'<line x1="24" y1="21.5" x2="24" y2="28.5" stroke="{tr_l}" stroke-width=".3"/>')
    a(f'<line x1="24" y1="21.5" x2="24" y2="28.5" stroke="{tr_d}" stroke-width=".1" stroke-dasharray=".8 .4"/>')

    # Emblemas centrales
    if mat == "diamond":
        a(f'<path d="M 24 22.5 L 25.6 24.2 L 24 25.9 L 22.4 24.2 Z" fill="url(#g_gem)" stroke="#fff" stroke-width=".18"/>')
        a(f'<circle cx="24" cy="24.2" r=".5" fill="#fff" filter="url(#soft)"/>')
        a(f'<path d="M 24 21.8 V 26.6 M 21.6 24.2 H 26.4" stroke="#fff" stroke-width=".2" opacity=".8"/>')
    elif mat == "dragon":
        a(f'<path d="M 24 22.8 L 25.4 24.5 L 24 26.2 L 22.6 24.5 Z" fill="url(#g_gem)" stroke="{tr_d}" stroke-width=".15"/>')
        a(f'<circle cx="24" cy="24.5" r=".4" fill="{ac_g}" filter="url(#glow)"/>')
        for ry, span in ((23.2, 2.8), (24.8, 3.2), (26.4, 2.6)):
            a(f'<path d="M {24 - span} {ry} Q 24 {ry - .5} {24 + span} {ry}" fill="none" stroke="{tr}" stroke-width=".25"/>')
    elif mat == "gold":
        a(f'<circle cx="24" cy="24.2" r="1.3" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
        a(f'<circle cx="24" cy="24.2" r=".6" fill="{ac}" stroke="{tr_d}" stroke-width=".1"/>')
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1, y1 = 24 + math.cos(rad) * 1.4, 24.2 + math.sin(rad) * 1.4
            x2, y2 = 24 + math.cos(rad) * 2.1, 24.2 + math.sin(rad) * 2.1
            a(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{tr_l}" stroke-width=".2"/>')
    elif mat in ("netherite", "kintsugi"):
        a(f'<path d="M 24 22.6 L 25.8 24.2 L 24 25.8 L 22.2 24.2 Z" fill="{bd}" stroke="{tr}" stroke-width=".2"/>')
        a(f'<path d="M 24 23.2 L 25.2 24.2 L 24 25.2 L 22.8 24.2 Z" fill="url(#g_trim)"/>')

    # Placas abdominales articuladas
    for ay in (26.8, 28.2, 29.5):
        a(f'<path d="M 20.8 {ay} Q 24 {ay + .4} 27.2 {ay} L 27.4 {ay + 1.1} Q 24 {ay + 1.5} 20.6 {ay + 1.1} Z" '
          f'fill="url(#g_plate)" stroke="{bd}" stroke-width=".12"/>')
        a(f'<path d="M 21 {ay + .15} Q 24 {ay + .55} 27 {ay + .15}" fill="none" stroke="{sp}" stroke-width=".2"/>')

    # Cinturón de combate
    a(f'<rect x="20" y="30.5" width="8" height="1.5" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<line x1="20" y1="30.8" x2="28" y2="30.8" stroke="{tr_l}" stroke-width=".2"/>')
    a(f'<rect x="23.1" y="30.2" width="1.8" height="1.8" rx=".3" fill="url(#g_gem)" stroke="{tr_l}" stroke-width=".15"/>')
    a(f'<rect x="23.6" y="30.7" width=".8" height=".8" fill="{bd}"/>')

    # Flancos laterales
    for fx in (16, 28):
        for sy in (23, 27):
            a(f'<rect x="{fx}" y="{sy}" width="4" height="1.2" fill="{bd}" stroke="{tr_d}" stroke-width=".1"/>')
            a(f'<rect x="{fx + 1.3}" y="{sy - .1}" width="1.4" height="1.4" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".08"/>')

    # Espalda de la coraza
    a(f'<rect x="35.3" y="20.5" width="1.4" height="9.5" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<line x1="36" y1="20.5" x2="36" y2="30" stroke="{tr_l}" stroke-width=".25"/>')
    for sy, dy in ((21.5, 33), (25, 33)):
        a(f'<path d="M 32.5 {sy} L 35.3 {sy + .8} L 35.3 {sy + 2.8} L 32.5 {sy + 2} Z" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')
        a(f'<path d="M 39.5 {sy} L 36.7 {sy + .8} L 36.7 {sy + 2.8} L 39.5 {sy + 2} Z" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')

def draw_pauldrons(b: SvgBuilder, pal: dict, mat: str):
    """Dibuja hombreras y guanteletes en el brazo (Arms: x=40..56, y=16..32)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd = pal["specular"], pal["base_dark"]

    a(f'<rect x="40" y="16" width="16" height="16" fill="url(#g_plate)"/>')

    # Hombrera superior
    a(f'<rect x="44" y="16" width="4" height="4" fill="url(#g_diag)"/>')
    a(f'<circle cx="46" cy="18" r="1.4" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".15"/>')
    a(f'<circle cx="46" cy="18" r=".5" fill="url(#g_gem)"/>')

    # Placas escalonadas de la hombrera
    for bx in (40, 44, 48, 52):
        for py, h_ in ((20, 1.4), (21.4, 1.4), (22.8, 1.3)):
            a(f'<rect x="{bx}" y="{py}" width="4" height="{h_}" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".1"/>')
            a(f'<line x1="{bx}" y1="{py + .2}" x2="{bx + 4}" y2="{py + .2}" stroke="{sp}" stroke-width=".18"/>')
            a(f'<circle cx="{bx + 2}" cy="{py + h_ / 2}" r=".18" fill="{tr_l}"/>')

    # Codal protector
    a(f'<rect x="44" y="24.2" width="4" height="1.8" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
    a(f'<path d="M 46 24.3 L 47.2 25.1 L 46 25.9 L 44.8 25.1 Z" fill="url(#g_gem)" stroke="{tr_d}" stroke-width=".08"/>')

    # Brazal / Guantelete
    for bx in (40, 44, 48, 52):
        a(f'<rect x="{bx}" y="26.5" width="4" height="4.5" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')
        a(f'<line x1="{bx + 2}" y1="26.5" x2="{bx + 2}" y2="31" stroke="{sp}" stroke-width=".2"/>')
        a(f'<rect x="{bx}" y="30.5" width="4" height="1.5" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<line x1="{bx}" y1="30.7" x2="{bx + 4}" y2="{30.7}" stroke="{tr_l}" stroke-width=".2"/>')

def draw_boots(b: SvgBuilder, pal: dict, mat: str):
    """Dibuja las botas de combate (Legs en Capa 1: x=0..16, y=26..32)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd = pal["specular"], pal["base_dark"]

    a(f'<rect x="0" y="26" width="16" height="6" fill="url(#g_plate)"/>')

    for lx in (0, 4, 8, 12):
        a(f'<rect x="{lx}" y="26.2" width="4" height="1.3" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<line x1="{lx}" y1="26.4" x2="{lx + 4}" y2="26.4" stroke="{tr_l}" stroke-width=".18"/>')
        a(f'<rect x="{lx + .3}" y="27.5" width="3.4" height="3" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')
        a(f'<line x1="{lx + 2}" y1="27.5" x2="{lx + 2}" y2="30.5" stroke="{sp}" stroke-width=".25"/>')
        a(f'<rect x="{lx}" y="30.8" width="4" height="1.2" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<circle cx="{lx + 1}" cy="31.4" r=".18" fill="{tr_l}"/>')
        a(f'<circle cx="{lx + 3}" cy="31.4" r=".18" fill="{tr_l}"/>')

def draw_leggings(b: SvgBuilder, pal: dict, mat: str):
    """Dibuja las grebas, musleras y cinturón (Capa 2: Body y Legs)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd = pal["specular"], pal["base_dark"]

    a(f'<rect x="0" y="16" width="40" height="16" fill="url(#g_plate)"/>')

    # Cinturón principal
    a(f'<rect x="16" y="20" width="24" height="2.2" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<line x1="16" y1="20.3" x2="40" y2="20.3" stroke="{tr_l}" stroke-width=".25"/>')
    a(f'<rect x="23" y="20" width="2" height="2.2" rx=".3" fill="url(#g_gem)" stroke="{tr_l}" stroke-width=".14"/>')

    # Escarcelas
    for tx in (20.5, 25.5):
        a(f'<path d="M {tx} 22.2 H {tx + 2} L {tx + 2.3} 25.5 L {tx + 1} 26.2 L {tx - .3} 25.5 Z" '
          f'fill="url(#g_diag)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<circle cx="{tx + 1}" cy="23.2" r=".2" fill="{tr_l}"/>')

    # Musleras
    for lx in (0, 4, 8, 12):
        a(f'<rect x="{lx + .2}" y="20.2" width="3.6" height="3.8" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')
        a(f'<line x1="{lx + 2}" y1="20.2" x2="{lx + 2}" y2="24" stroke="{sp}" stroke-width=".2"/>')
        if lx == 12:
            a(f'<line x1="12" y1="21.5" x2="16" y2="21.5" stroke="{bd}" stroke-width=".5"/>')
            a(f'<line x1="12" y1="23" x2="16" y2="23" stroke="{bd}" stroke-width=".5"/>')

    # Rodillera acorazada
    for kx in (4, 8):
        a(f'<path d="M {kx + 2} 24 L {kx + 3.6} 25.3 L {kx + 2} 26.6 L {kx + .4} 25.3 Z" '
          f'fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
        a(f'<path d="M {kx + 2} 24.5 L {kx + 3} 25.3 L {kx + 2} 26.1 L {kx + 1} 25.3 Z" '
          f'fill="url(#g_gem)" stroke="{tr_l}" stroke-width=".08"/>')
        a(f'<circle cx="{kx + 2}" cy="25.3" r=".25" fill="#fff" filter="url(#soft)"/>')

    # Grebas de espinilla
    for lx in (0, 4, 8, 12):
        a(f'<rect x="{lx + .2}" y="27" width="3.6" height="4.8" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')
        a(f'<line x1="{lx + 2}" y1="27" x2="{lx + 2}" y2="31.8" stroke="{sp}" stroke-width=".3"/>')
        a(f'<line x1="{lx}" y1="31.6" x2="{lx + 4}" y2="31.6" stroke="{tr}" stroke-width=".25"/>')

def draw_special_overlays(b: SvgBuilder, pal: dict, mat: str, layer: int):
    """Detalles únicos por material: Cuernos, escamas, alas, grietas Kintsugi."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    ac, ac_g = pal["accent"], pal["accent_glow"]

    if mat == "dragon":
        if layer == 1:
            # Cuernos de dragón laterales imponentes
            a(f'<path d="M 6.5 11.5 Q 4 10 1 7 Q 3.5 9 6.5 9.8 Z" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".14"/>')
            a(f'<path d="M 1.5 7.3 Q 3.8 9.2 6.5 10" fill="none" stroke="{tr_l}" stroke-width=".2"/>')
            a(f'<path d="M 17.5 11.5 Q 20 10 23 7 Q 20.5 9 17.5 9.8 Z" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".14"/>')
            a(f'<path d="M 22.5 7.3 Q 20.2 9.2 17.5 10" fill="none" stroke="{tr_l}" stroke-width=".2"/>')

            # Ojos de dragón cian luminosos dentro del visor
            for ex in (9.2, 13.2):
                a(f'<ellipse cx="{ex + .8}" cy="11.8" rx="1.2" ry=".6" fill="{ac}" filter="url(#glow)"/>')
                a(f'<ellipse cx="{ex + .8}" cy="11.8" rx=".8" ry=".35" fill="#ffffff"/>')
                a(f'<line x1="{ex + .8}" y1="11.2" x2="{ex + .8}" y2="12.4" stroke="{pal["base_dark"]}" stroke-width=".2"/>')

            # Alas de dragón desplegadas en la espalda
            a(f'<path d="M 35 22 Q 32.5 19 32 17 L 32 23 Q 33.5 24 35 25 Z" fill="{pal["base_dark"]}" stroke="{tr}" stroke-width=".15"/>')
            a(f'<path d="M 35 22 Q 33 20 32.2 17.2" fill="none" stroke="{tr_l}" stroke-width=".25"/>')
            a(f'<path d="M 37 22 Q 39.5 19 40 17 L 40 23 Q 38.5 24 37 25 Z" fill="{pal["base_dark"]}" stroke="{tr}" stroke-width=".15"/>')
            a(f'<path d="M 37 22 Q 39 20 39.8 17.2" fill="none" stroke="{tr_l}" stroke-width=".25"/>')

            # Garras de dragón en las botas
            for bx in (0, 4, 8, 12):
                for kx in (bx + .8, bx + 2, bx + 3.2):
                    a(f'<path d="M {kx - .3} 31.2 L {kx} 32 L {kx + .3} 31.2 Z" fill="{tr_l}" stroke="{tr_d}" stroke-width=".08"/>')

    elif mat == "kintsugi":
        crack_paths = [
            "M 10 9 Q 11.5 10.5 12 10 Q 13 9.5 14.5 10.5",
            "M 12 10 L 12 13 Q 13.5 14 15 14.5",
            "M 3 10 Q 4.5 11 4 13 Q 5 14 6 15",
            "M 19 10 Q 18 11.5 18.5 13 Q 17.5 14 17 15",
            "M 21 21 Q 23 23 24 22.5 Q 26 24 27.5 23",
            "M 24 22.5 L 24 26 Q 22.5 27.5 21 28",
            "M 24 26 Q 25.5 28 27 28.5",
            "M 24 28.5 L 24 31",
            "M 34 22 Q 36 24 37 23.5 Q 38 25 39 26",
            "M 42 22 Q 44 24 45 23 Q 46 25 47 27",
            "M 45 23 L 45 30",
            "M 2 22 Q 4 24 5 26 Q 6 25 7 28",
            "M 5 26 L 5 31",
            "M 10 22 Q 12 24 13 26 Q 14 28 15 30"
        ]
        for cp in crack_paths:
            a(f'<path d="{cp}" fill="none" stroke="{tr}" stroke-width=".45" opacity=".4" filter="url(#glow)"/>')
            a(f'<path d="{cp}" fill="none" stroke="{tr_l}" stroke-width=".2" stroke-linecap="round" stroke-linejoin="round"/>')
            pts = cp.split()
            for idx in (1, 4, len(pts) - 1):
                try:
                    px, py = float(pts[idx - 1]), float(pts[idx])
                    a(f'<circle cx="{px}" cy="{py}" r=".25" fill="{tr_l}" stroke="{tr_d}" stroke-width=".06"/>')
                except Exception:
                    pass

    elif mat == "diamond":
        glints = [(12, 9), (24, 24.2), (46, 18), (6, 25.3), (10, 25.3)] if layer == 1 else [(6, 25.3), (10, 25.3), (24, 21)]
        for gx, gy in glints:
            a(f'<circle cx="{gx}" cy="{gy}" r="1" fill="#fff" opacity=".35" filter="url(#glow)"/>')
            a(f'<path d="M {gx} {gy - 1.2} L {gx + .25} {gy - .25} L {gx + 1.2} {gy} L {gx + .25} {gy + .25} '
              f'L {gx} {gy + 1.2} L {gx - .25} {gy + .25} L {gx - 1.2} {gy} L {gx - .25} {gy - .25} Z" fill="#ffffff"/>')

def build_artistic_svg(mat: str, w: int, h: int, runs: list[tuple[int, int, int, int]],
                       seed_key: str, layer: int = 1) -> str:
    """Construye el SVG completo con diseño heráldico y anatómico."""
    pal = PALETTES.get(mat, PALETTES["iron"])
    b = SvgBuilder(w, h, pal, seed_key)
    setup_gradients(b, pal)
    b.set_clip_mask(runs)

    if layer == 1:
        draw_helmet(b, pal, mat)
        draw_cuirass(b, pal, mat)
        draw_pauldrons(b, pal, mat)
        draw_boots(b, pal, mat)
    else:
        draw_leggings(b, pal, mat)

    draw_special_overlays(b, pal, mat, layer)
    return b.build()
