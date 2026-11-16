#!/usr/bin/env python3
"""Armaduras Artísticas de Alta Definición para DrakesCraft (26.x y 1.20).
Diseño heráldico y anatómico vectorial (SVG) con export a 4x (256x128).
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
OUT = "#0a0810"
GOLD, GOLD_D, GOLD_L = "#b08a30", "#684e1a", "#d6b860"
MAG, CYN, CYN_B = "#9634aa", "#2496aa", "#50dcf0"

# --- PALETAS ARTÍSTICAS RICAS Y CONTRASTADAS ---
PALETTES = {
    "netherite": {
        "base_dark": "#120e18",
        "base_mid": "#251d2f",
        "base_light": "#3f334e",
        "specular": "#9f90b8",
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

def mask_runs(img: Image.Image) -> list[tuple[int, int, int, int]]:
    w, h = img.size
    runs = []
    for y in range(h):
        x = 0
        while x < w:
            if img.getpixel((x, y))[3] > 0:
                e = x
                while e + 1 < w and img.getpixel((e + 1, y))[3] > 0:
                    e += 1
                runs.append((x, y, e - x + 1, 1))
                x = e + 1
            else:
                x += 1
    return runs

def upscale_nearest(img: Image.Image, scale: int) -> Image.Image:
    w, h = img.size
    out = Image.new("RGBA", (w * scale, h * scale))
    px_in = img.convert("RGBA").load()
    px_out = out.load()
    for y in range(h):
        for x in range(w):
            p = px_in[x, y]
            if p[3] == 0:
                continue
            for dy in range(scale):
                for dx in range(scale):
                    px_out[x * scale + dx, y * scale + dy] = p
    return out

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
    """Casco anatómico (0..32, 0..16)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd = pal["specular"], pal["base_dark"]
    style = pal["style"]

    # 1. Base sólida
    a(f'<rect x="0" y="0" width="32" height="16" fill="url(#g_plate)"/>')

    # Estilo especial: Chainmail
    if style == "chainmail":
        for ry in range(0, 16, 2):
            for rx_ in range(0, 32, 2):
                cx, cy = rx_ + (1 if (ry // 2) % 2 else 0), ry + 1
                a(f'<circle cx="{cx}" cy="{cy}" r=".9" fill="none" stroke="{bd}" stroke-width=".4"/>'
                  f'<circle cx="{cx}" cy="{cy}" r=".9" fill="none" stroke="{sp}" stroke-width=".2" stroke-dasharray="1.2 .8"/>')

    # Estilo especial: Tortuga (hexágonos de caparazón)
    elif style == "turtle":
        for ty in (1, 5, 9, 13):
            for tx in range(0, 32, 4):
                cx, cy = tx + (2 if (ty // 4) % 2 else 0), ty
                a(f'<polygon points="{cx-1.5},{cy} {cx-.8},{cy-1.3} {cx+.8},{cy-1.3} {cx+1.5},{cy} {cx+.8},{cy+1.3} {cx-.8},{cy+1.3}" '
                  f'fill="url(#g_diag)" stroke="{tr_d}" stroke-width=".15"/>')

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
    if mat in ("diamond", "dragon", "gold", "netherite", "kintsugi"):
        a(f'<path d="M 12 8.3 L 12.8 9.2 L 12 10.1 L 11.2 9.2 Z" fill="url(#g_gem)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<circle cx="12" cy="9.2" r=".2" fill="#fff" filter="url(#soft)"/>')

    # Visera y ceja
    a(f'<path d="M 8 10.2 L 12 10.8 L 16 10.2 L 16 11.3 L 12 12 L 8 11.3 Z" fill="url(#g_diag)" stroke="{bd}" stroke-width=".15"/>')
    a(f'<path d="M 8.2 10.3 L 12 10.9 L 15.8 10.3" fill="none" stroke="{sp}" stroke-width=".2"/>')

    # Puente nasal
    a(f'<rect x="11.3" y="10.8" width="1.4" height="2.2" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".1"/>')
    a(f'<line x1="12" y1="10.8" x2="12" y2="13" stroke="{tr_l}" stroke-width=".2"/>')

    # Guardamejillas laterales en el frontal
    a(f'<path d="M 8 12.5 H 9.5 V 15.8 H 8 Z" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<path d="M 14.5 12.5 H 16 V 15.8 H 14.5 Z" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<circle cx="8.7" cy="14.5" r=".2" fill="{tr_l}"/>')
    a(f'<circle cx="15.3" cy="14.5" r=".2" fill="{tr_l}"/>')

    # 4. Laterales (sienes y orejeras: 0..8 y 16..24)
    for sx in (0, 16):
        cx = sx + 4
        a(f'<circle cx="{cx}" cy="10.5" r="1.8" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".15"/>')
        a(f'<circle cx="{cx}" cy="10.5" r="1.1" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<circle cx="{cx}" cy="10.5" r=".4" fill="url(#g_gem)" stroke="{tr_d}" stroke-width=".06"/>')
        a(f'<path d="M {sx} 12 Q {cx} 13.5 {sx + 8} 12" fill="none" stroke="{tr}" stroke-width=".25"/>')
        for dy in (-.7, 0, .7):
            a(f'<line x1="{cx - .6}" y1="{10.5 + dy}" x2="{cx + .6}" y2="{10.5 + dy}" stroke="{bd}" stroke-width=".18"/>')

    # 5. Cogotera trasera (24..32)
    for ly in (8, 10.2, 12.4, 14.2):
        a(f'<rect x="24" y="{ly}" width="8" height="2" fill="url(#g_plate)" stroke="{tr_d}" stroke-width=".12"/>')
        a(f'<line x1="24" y1="{ly + .2}" x2="32" y2="{ly + .2}" stroke="{sp}" stroke-width=".2"/>')
        a(f'<circle cx="25" cy="{ly + 1}" r=".18" fill="{tr_l}"/>')
        a(f'<circle cx="31" cy="{ly + 1}" r=".18" fill="{tr_l}"/>')

def draw_cuirass(b: SvgBuilder, pal: dict, mat: str):
    """Coraza principal (Body: x=16..40, y=16..32)."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd, bm = pal["specular"], pal["base_dark"], pal["base_mid"]
    ac, ac_g = pal["accent"], pal["accent_glow"]
    style = pal["style"]

    # Base sólida del torso
    a(f'<rect x="16" y="16" width="24" height="16" fill="url(#g_plate)"/>')

    # 1. Hombros / Cuello superior (20..28, 16..20)
    a(f'<rect x="20" y="16" width="8" height="4" fill="url(#g_diag)"/>')
    a(f'<rect x="22" y="16.5" width="4" height="3" rx=".8" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<ellipse cx="24" cy="18" rx="1.4" ry=".8" fill="{bd}"/>')

    # 2. Frente del Peto (20..28, 20..32)
    # Gorguera
    a(f'<path d="M 20 20 L 24 21.5 L 28 20 L 28 21.2 L 24 22.8 L 20 21.2 Z" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<path d="M 20.5 20.3 L 24 21.7 L 27.5 20.3" fill="none" stroke="{tr_l}" stroke-width=".25"/>')

    # Estilo específico de coraza:
    if style == "chainmail":
        for ry in range(21, 31, 2):
            for rx_ in range(20, 28, 2):
                cx, cy = rx_ + (1 if (ry // 2) % 2 else 0), ry + 1
                a(f'<circle cx="{cx}" cy="{cy}" r=".9" fill="none" stroke="{bd}" stroke-width=".35"/>'
                  f'<circle cx="{cx}" cy="{cy}" r=".9" fill="none" stroke="{sp}" stroke-width=".18" stroke-dasharray="1.2 .8"/>')
    elif style == "iron":
        # Flauta gótica radiante
        for fx, ang in ((21, -2), (22.2, -1), (23.2, 0), (24.8, 0), (25.8, 1), (27, 2)):
            a(f'<line x1="{fx}" y1="21.5" x2="{fx + ang * .4}" y2="28" stroke="{sp}" stroke-width=".3"/>'
              f'<line x1="{fx + .1}" y1="21.5" x2="{fx + ang * .4 + .1}" y2="28" stroke="{bd}" stroke-width=".15"/>')
    elif style == "copper":
        # Manómetros / válvulas dobles de presión con agujas rojas
        for gx in (22.2, 25.8):
            a(f'<circle cx="{gx}" cy="24" r="1.4" fill="#ffffff" stroke="{tr_d}" stroke-width=".2"/>')
            a(f'<circle cx="{gx}" cy="24" r="1.1" fill="none" stroke="{bd}" stroke-width=".1"/>')
            a(f'<line x1="{gx}" y1="24" x2="{gx + .6}" y2="23.4" stroke="#d91438" stroke-width=".25" stroke-linecap="round"/>')
            a(f'<circle cx="{gx}" cy="24" r=".2" fill="{bd}"/>')
    else:
        # Pectorales esculpidos
        a(f'<path d="M 20.3 21.8 L 23.8 22.8 L 23.8 26.2 L 20.5 25.5 Z" fill="url(#g_diag)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<path d="M 27.7 21.8 L 24.2 22.8 L 24.2 26.2 L 27.5 25.5 Z" fill="url(#g_diag)" stroke="{tr_d}" stroke-width=".1"/>')
        a(f'<line x1="24" y1="21.5" x2="24" y2="28.5" stroke="{tr_l}" stroke-width=".3"/>')

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

    # Placas abdominales articuladas (faulds)
    for ay in (26.8, 28.2, 29.5):
        a(f'<path d="M 20.8 {ay} Q 24 {ay + .4} 27.2 {ay} L 27.4 {ay + 1.1} Q 24 {ay + 1.5} 20.6 {ay + 1.1} Z" '
          f'fill="url(#g_plate)" stroke="{bd}" stroke-width=".12"/>')
        a(f'<path d="M 21 {ay + .15} Q 24 {ay + .55} 27 {ay + .15}" fill="none" stroke="{sp}" stroke-width=".2"/>')

    # Cinturón de combate
    a(f'<rect x="20" y="30.5" width="8" height="1.5" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<line x1="20" y1="30.8" x2="28" y2="30.8" stroke="{tr_l}" stroke-width=".2"/>')
    a(f'<rect x="23.1" y="30.2" width="1.8" height="1.8" rx=".3" fill="url(#g_gem)" stroke="{tr_l}" stroke-width=".15"/>')
    a(f'<rect x="23.6" y="30.7" width=".8" height=".8" fill="{bd}"/>')

    # Flancos laterales (16..20 y 28..32)
    for fx in (16, 28):
        for sy in (23, 27):
            a(f'<rect x="{fx}" y="{sy}" width="4" height="1.2" fill="{bd}" stroke="{tr_d}" stroke-width=".1"/>')
            a(f'<rect x="{fx + 1.3}" y="{sy - .1}" width="1.4" height="1.4" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".08"/>')

    # Espalda de la coraza (32..40)
    a(f'<rect x="35.3" y="20.5" width="1.4" height="9.5" fill="url(#g_trim)" stroke="{tr_d}" stroke-width=".12"/>')
    a(f'<line x1="36" y1="20.5" x2="36" y2="30" stroke="{tr_l}" stroke-width=".25"/>')
    for sy in (21.5, 25):
        a(f'<path d="M 32.5 {sy} L 35.3 {sy + .8} L 35.3 {sy + 2.8} L 32.5 {sy + 2} Z" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')
        a(f'<path d="M 39.5 {sy} L 36.7 {sy + .8} L 36.7 {sy + 2.8} L 39.5 {sy + 2} Z" fill="url(#g_diag)" stroke="{bd}" stroke-width=".1"/>')

def draw_pauldrons(b: SvgBuilder, pal: dict, mat: str):
    """Hombreras y guanteletes en el brazo (Arms: x=40..56, y=16..32)."""
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
        a(f'<line x1="{bx}" y1="30.7" x2="{bx + 4}" y2="30.7" stroke="{tr_l}" stroke-width=".2"/>')

def draw_boots(b: SvgBuilder, pal: dict, mat: str):
    """Botas de combate (Legs en Capa 1: x=0..16, y=26..32)."""
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
    """Grebas, musleras y cinturón (Capa 2: Body y Legs)."""
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
    """Detalles únicos por material: Cuernos, alas, grietas Kintsugi, destellos de diamante."""
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

def draw_mob_armor(b: SvgBuilder, pal: dict, mat: str, sub: str, w: int, h: int):
    """Genera armaduras de caballo, lobo, nautilus y crías con estética heráldica."""
    a = b.add
    tr, tr_d, tr_l = pal["trim"], pal["trim_dark"], pal["trim_light"]
    sp, bd = pal["specular"], pal["base_dark"]

    # Fondo general
    a(f'<rect width="{w}" height="{h}" fill="url(#g_plate)"/>')

    # Bardeado y ribetes ornamentales
    T = 8
    for y_ in range(0, h, T):
        a(f'<line x1="0" y1="{y_}" x2="{w}" y2="{y_}" stroke="{bd}" stroke-width=".3"/>')
        a(f'<line x1="0" y1="{y_ + .2}" x2="{w}" y2="{y_ + .2}" stroke="{sp}" stroke-width=".2"/>')
        for x_ in range(0, w, T):
            a(f'<circle cx="{x_ + 1}" cy="{y_ + 1}" r=".35" fill="{tr_l}" stroke="{tr_d}" stroke-width=".08"/>')

    if sub == "horse_body":
        # Tesela heráldica central para caballo
        a(f'<rect x="{w/2 - 8}" y="{h/2 - 6}" width="16" height="12" rx="2" fill="url(#g_diag)" stroke="{tr}" stroke-width=".4"/>')
        a(f'<circle cx="{w/2}" cy="{h/2}" r="3" fill="url(#g_gem)" stroke="{tr_l}" stroke-width=".3"/>')

def build_svg(mat: str, w: int, h: int, runs: list[tuple[int, int, int, int]],
              seed_key: str, layer: int = 1, sub: str = "humanoid") -> str:
    """Función de despacho para la generación de cualquier capa de armadura."""
    pal = PALETTES.get(mat, PALETTES["iron"])
    b = SvgBuilder(w, h, pal, seed_key)
    setup_gradients(b, pal)
    b.set_clip_mask(runs)

    if sub in ("humanoid", "humanoid_baby"):
        if layer == 1:
            draw_helmet(b, pal, mat)
            draw_cuirass(b, pal, mat)
            draw_pauldrons(b, pal, mat)
            draw_boots(b, pal, mat)
        else:
            draw_leggings(b, pal, mat)
        draw_special_overlays(b, pal, mat, layer)
    elif sub == "humanoid_leggings":
        draw_leggings(b, pal, mat)
        draw_special_overlays(b, pal, mat, 2)
    else:
        draw_mob_armor(b, pal, mat, sub, w, h)

    return b.build()

def rasterize(svg_text: str, svg_path: Path, png_path: Path, size: tuple[int, int]) -> Image.Image:
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_text, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(size[0]), "-h", str(size[1]), "-o", str(png_path), str(svg_path)], check=True)
    return Image.open(png_path).convert("RGBA")

def write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

def icon_svg(piece: str) -> str:
    shapes = {
        "helmet": ('<path id="s" d="M64 22 L40 26 Q22 34 20 58 L20 88 Q20 96 28 98 L42 98 L42 84 L50 76 L64 76 Z"/>',
                   '<path id="h" d="M30 40 Q14 34 6 6 Q24 16 42 30 Z"/>'),
        "chestplate": ('<path id="s" d="M64 26 L42 26 Q30 30 20 26 L8 34 Q2 50 10 62 L22 58 L24 106 Q44 114 64 112 Z"/>',
                       '<path id="h" d="M10 38 L0 20 L22 30 Z"/>'),
        "leggings": ('<path id="s" d="M64 30 L22 30 L20 58 L26 112 L56 112 L58 62 L64 62 Z"/>',
                     '<path id="h" d="M0 0 Z"/>'),
        "boots": ('<path id="s" d="M64 50 L24 50 L24 86 Q10 90 8 104 L8 114 L64 114 Z"/>',
                  '<path id="h" d="M10 108 L16 120 L22 108 L28 120 L34 108 Z"/>'),
    }[piece]
    extra = {
        "helmet": f'<path d="M64 8 L60 34 L68 34 Z" fill="{MAG}" stroke="{OUT}" stroke-width="2"/><ellipse cx="46" cy="64" rx="14" ry="6" fill="{CYN_B}" opacity=".3" filter="url(#bl)"/>'
                  f'<path d="M34 62 Q46 56 58 66 Q46 70 34 62 Z" fill="{CYN_B}"/><path d="M70 66 Q82 56 94 62 Q82 70 70 66 Z" fill="{CYN_B}"/>',
        "chestplate": f'<path d="M64 52 L72 64 L64 78 L56 64 Z" fill="url(#gem)" stroke="{GOLD_D}" stroke-width="2"/><path d="M64 30 V50 M64 80 V108" stroke="{GOLD_D}" stroke-width="2.5"/>',
        "leggings": f'<path d="M22 30 H106 V38 H22 Z" fill="url(#gold)" opacity=".85"/><path d="M40 70 L46 78 L40 86 L34 78 Z" fill="url(#gem)" stroke="{GOLD_D}" stroke-width="1.5"/>',
        "boots": '',
    }[piece]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 128 128" width="128" height="128">
<defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5b2bb5"/><stop offset=".45" stop-color="#2a1450"/><stop offset="1" stop-color="#0d051a"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient>
<radialGradient id="gem" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#d8fbff"/><stop offset=".5" stop-color="{CYN_B}"/><stop offset="1" stop-color="#0b4658"/></radialGradient>
<pattern id="sc" width="12" height="9" patternUnits="userSpaceOnUse"><path d="M0 9 Q6 -1 12 9" fill="none" stroke="#b99be8" stroke-width="1" opacity=".22"/><path d="M-6 4.5 Q0 -4 6 4.5 M6 4.5 Q12 -4 18 4.5" fill="none" stroke="#000" stroke-width="1" opacity=".25"/></pattern>
<filter id="bl"><feGaussianBlur stdDeviation="3"/></filter>
{shapes[0]}{shapes[1]}
</defs>
<use xlink:href="#h" fill="url(#gold)" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>
<use xlink:href="#s" fill="url(#g)" stroke="{OUT}" stroke-width="3.5" stroke-linejoin="round"/>
<use xlink:href="#s" fill="url(#sc)"/>
<g transform="translate(128 0) scale(-1 1)"><use xlink:href="#h" fill="url(#gold)" stroke="{OUT}" stroke-width="3" stroke-linejoin="round"/>
<use xlink:href="#s" fill="url(#g)" stroke="{OUT}" stroke-width="3.5" stroke-linejoin="round"/><use xlink:href="#s" fill="url(#sc)"/></g>
{extra}
</svg>'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--jar", default=str(DEFAULT_JAR))
    a = ap.parse_args()
    root = Path(a.root)
    mc, dk = root / "assets/minecraft", root / "assets/drakescraft"
    svgd = dk / "textures/gear/svg"
    z = zipfile.ZipFile(a.jar)
    names = set(z.namelist())

    def vanilla_png(layer, name):
        return Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/entity/equipment/{layer}/{name}.png"))).convert("RGBA")

    def have(layer, name):
        return f"assets/minecraft/textures/entity/equipment/{layer}/{name}.png" in names

    sheet = {}
    for mat in HUMANOID_MATS + CUSTOM:
        base = (dk if mat in CUSTOM else mc) / "textures/entity/equipment"
        for layer, sub in ((1, "humanoid"), (2, "humanoid_leggings")):
            if mat == "turtle_scute" and layer == 2:
                continue
            src = "netherite" if mat in CUSTOM else mat
            vm = vanilla_png(sub, src)
            runs = mask_runs(vm)
            if mat == "dragon" and layer == 1:
                # Ojos cian en el visor
                runs = runs + [(9, 11, 2, 1), (9, 12, 2, 1), (13, 11, 2, 1), (13, 12, 2, 1)]
            key = f"{mat}-{layer}"
            sv = build_svg(mat, 64, 32, runs, key, layer=layer, sub=sub)
            im = rasterize(sv, svgd / f"armor_{mat}_{sub}.svg", base / sub / f"{mat}.png", (64 * SCALE, 32 * SCALE))
            sheet[(mat, sub)] = im
            if mat == "leather":
                vom = vanilla_png(sub, "leather_overlay")
                overlay_im = upscale_nearest(vom, SCALE)
                overlay_png = base / sub / "leather_overlay.png"
                overlay_png.parent.mkdir(parents=True, exist_ok=True)
                overlay_im.save(overlay_png)
            if mat in OLD_NAME:
                old = mc / "textures/models/armor"
                old.mkdir(parents=True, exist_ok=True)
                im.save(old / f"{OLD_NAME[mat]}_layer_{layer}.png")
                if mat == "leather":
                    overlay_im.save(old / f"leather_layer_{layer}_overlay.png")

        src = "iron" if mat in CUSTOM else mat
        for sub, pool in (("humanoid_baby", HUMANOID_MATS),
                          ("horse_body", ["netherite", "diamond", "iron", "gold", "copper", "leather"]),
                          ("nautilus_body", ["netherite", "diamond", "iron", "gold", "copper"])):
            if src not in pool or not have(sub, src):
                continue
            vm = vanilla_png(sub, src)
            w, h = vm.size
            sv = build_svg(mat, w, h, mask_runs(vm), f"{mat}-{sub}", sub=sub)
            sheet[(mat, sub)] = rasterize(sv, svgd / f"armor_{mat}_{sub}.svg", base / sub / f"{mat}.png", (w * SCALE, h * SCALE))
            if mat == "leather" and sub in ("humanoid_baby", "horse_body"):
                vom = vanilla_png(sub, "leather_overlay")
                overlay_im = upscale_nearest(vom, SCALE)
                overlay_im.save(base / sub / "leather_overlay.png")

        if mat != "turtle_scute":
            runs = mask_runs(vanilla_png("wolf_body", "armadillo_scute"))
            sv = build_svg(mat, 64, 32, runs, f"{mat}-wolf", sub="wolf_body")
            sheet[(mat, "wolf_body")] = rasterize(sv, svgd / f"armor_{mat}_wolf_body.svg", base / "wolf_body" / f"{mat}.png", (64 * SCALE, 32 * SCALE))

    for mat in VANILLA_JSON:
        j = json.loads(z.read(f"assets/minecraft/equipment/{mat}.json"))
        j["layers"]["wolf_body"] = json.loads(json.dumps(j["layers"]["humanoid"])) if mat == "leather" else [{"texture": f"minecraft:{mat}"}]
        write_json(mc / "equipment" / f"{mat}.json", j)
    for mat in CUSTOM:
        t = lambda mat=mat: [{"texture": f"drakescraft:{mat}"}]
        write_json(dk / "equipment" / f"{mat}.json", {"layers": {"humanoid": t(), "humanoid_baby": t(), "humanoid_leggings": t(),
                                                                  "horse_body": t(), "nautilus_body": t(), "wolf_body": t()}})

    icons = {}
    for piece in ("helmet", "chestplate", "leggings", "boots"):
        icons[piece] = rasterize(icon_svg(piece), svgd / f"dragon_{piece}.svg", dk / f"textures/item/dragon_{piece}.png", (128, 128))
        write_json(dk / f"models/item/dragon_{piece}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"drakescraft:item/dragon_{piece}"}})
        write_json(dk / f"items/dragon_{piece}.json", {"model": {"type": "minecraft:model", "model": f"drakescraft:item/dragon_{piece}"}})

    prev = root / "docs/previews"
    prev.mkdir(parents=True, exist_ok=True)
    order = ["netherite", "diamond", "iron", "gold", "chainmail", "copper", "leather", "turtle_scute", "kintsugi", "dragon"]
    cw, rh = 256, 128
    sh = Image.new("RGBA", (cw * 3 + 40, 140 + len(order) * (rh + 6) + 3 * 262 + 20), (44, 44, 54, 255))
    x = 10
    for im in icons.values():
        sh.alpha_composite(im, (x, 6))
        x += 134
    y = 140
    for mat in order:
        for k, sub in enumerate(("humanoid", "humanoid_leggings", "wolf_body")):
            if (mat, sub) in sheet:
                sh.alpha_composite(sheet[(mat, sub)], (10 + k * (cw + 10), y))
        y += rh + 6
    for mat in ("dragon", "kintsugi", "netherite"):
        x = 10
        for sub in ("horse_body", "humanoid_baby", "nautilus_body"):
            im = sheet.get((mat, sub))
            if im:
                sh.alpha_composite(im.resize((256, 256), Image.LANCZOS), (x, y))
                x += 266
        y += 262
    sh.crop((0, 0, sh.size[0], y)).save(prev / "armaduras_kintsugi_dragon.png")
    print("ok", sorted({k[0] for k in sheet}))

if __name__ == "__main__":
    main()
