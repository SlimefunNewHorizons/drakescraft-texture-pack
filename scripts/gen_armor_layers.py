#!/usr/bin/env python3
"""Armaduras DrakesCraft KINTSUGI/DRAGON (26.x y 1.20): autoria en VECTOR (SVG) y export a 4x. Sin shader.

El SVG usa como unidades los PIXELES VANILLA (viewBox 64x32, 64x64, 128x128...), asi el layout/UV vanilla se
mantiene exacto y proporcional; la rasterizacion (rsvg-convert) sale a 4x: capas 256x128, baby/caballo 256x256, nautilus 512x512.
Estilo (dueño): base oscura con degradados y relieve, bordes de placa marcados, remaches discretos, pocas grietas
finas/estrellitas, acento minimo por material (oxido en hierro, cardenillo en cobre). Dragon: escamas + cresta/cuernos/espinas.

Salidas (por material, desde el MISMO svg):
  26.x : assets/minecraft/textures/entity/equipment/{humanoid,humanoid_leggings,humanoid_baby,horse_body,nautilus_body,wolf_body}/<mat>.png
  1.20 : assets/minecraft/textures/models/armor/<mat>_layer_{1,2}.png (+ leather_layer_N_overlay.png); copper no existe antes de 1.21.9
  propios: assets/drakescraft/textures/entity/equipment/... (kintsugi, dragon) + equipment/*.json
  fuentes: assets/drakescraft/textures/gear/svg/armor_<mat>_<capa>.svg ; iconos dragon 128x128 + items/models
Las capas de baby/caballo/nautilus/lobo se recortan con la mascara alpha del PNG vanilla del jar de cliente.
Uso: gen_armor_layers.py [--root .] [--jar client.jar]
"""
import argparse
import io
import json
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


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def mixc(a, b, t):
    a, b = (hx(a) if isinstance(a, str) else a), (hx(b) if isinstance(b, str) else b)
    return "#%02x%02x%02x" % tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# H base, h luz, d sombra, sp brillo, crack, mode, patches=[(color, fraccion)]
MATS = {
    "netherite": dict(H="#1d1925", h="#3a3048", d="#0a080e", sp="#8a4a9e", crack="#6e2c82", mode="plate"),
    "diamond": dict(H="#12333c", h="#2a6f7b", d="#06161b", sp="#4fb3bf", crack="#2e8a96", mode="plate"),
    "iron": dict(H="#3a4152", h="#6a7388", d="#14171f", sp="#9aa3b8", crack="#5a6478", mode="plate",
                 patches=[("#7a4828", .05), ("#5c361e", .035)]),
    "gold": dict(H="#3a2c10", h="#6e551c", d="#150f04", sp="#a88a3c", crack="#80642a", mode="plate"),
    "chainmail": dict(H="#232735", h="#5a6176", d="#0e1018", sp="#8d93a6", crack="#46506a", mode="mesh"),
    "copper": dict(H="#4a2819", h="#8a4a2c", d="#190c07", sp="#c9845a", crack="#96593a", mode="plate",
                   patches=[("#28786a", .05), ("#1e5a4e", .035)]),
    "turtle_scute": dict(H="#173a22", h="#3f8a4c", d="#07130b", sp="#8fd09a", crack="#46965a", mode="scale"),
    "leather": dict(H="#a0a0a0", h="#c8c8c8", d="#585858", sp="#ffffff", crack="#8c6e32", mode="plate"),
    "kintsugi": dict(H="#1a1424", h="#34264a", d="#08060d", sp="#9b6bd0", crack=GOLD, mode="plate"),
    "dragon": dict(H="#2a1450", h="#5b2bb5", d="#0d051a", sp="#b99be8", crack=GOLD, mode="scale", tint=True),
}
VANILLA_JSON = ["netherite", "diamond", "iron", "gold", "chainmail", "copper", "leather"]
HUMANOID_MATS = VANILLA_JSON + ["turtle_scute"]
CUSTOM = ["kintsugi", "dragon"]
OLD_NAME = {"netherite": "netherite", "diamond": "diamond", "iron": "iron", "gold": "gold", "chainmail": "chainmail",
            "leather": "leather", "turtle_scute": "turtle"}


def box(u, v, w, h, d):
    return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d), "right": (u, v + d, d, h),
            "front": (u + d, v + d, w, h), "left": (u + d + w, v + d, d, h), "back": (u + d + w + d, v + d, w, h)}


HEAD, BODY, ARM, LEG = box(0, 0, 8, 8, 8), box(16, 16, 8, 12, 4), box(40, 16, 4, 12, 4), box(0, 16, 4, 12, 4)
LAYER1 = {"head": HEAD, "body": BODY, "arm": ARM, "leg": LEG}
LAYER2 = {"body": BODY, "leg": LEG}


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Builder:
    def __init__(self, w, h, m, rng, overlay=False):
        self.w, self.h, self.m, self.rng, self.overlay = w, h, m, rng, overlay
        self.defs, self.body = [], []

    def grads(self):
        m = self.m
        H, hl, d = m["H"], m["h"], m["d"]
        for v in range(3):
            t = (-.1, 0, .12)[v]
            c0, c1, c2 = mixc(H, hl, .45 + t), mixc(H, hl, .08 + t / 2), mixc(H, d, .45 - t)
            self.defs.append(f'<linearGradient id="p{v}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c0}"/>'
                             f'<stop offset=".45" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>')
        if m.get("tint"):
            for nm, base, lt in (("m", "#5a1466", "#a040b8"), ("c", "#0b4658", "#2a96aa")):
                self.defs.append(f'<linearGradient id="p{nm}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{lt}"/>'
                                 f'<stop offset="1" stop-color="{base}"/></linearGradient>')
        self.defs.append(f'<radialGradient id="rv" cx=".35" cy=".35" r=".7"><stop offset="0" stop-color="{mixc(H, hl, .9)}"/>'
                         f'<stop offset="1" stop-color="{d}"/></radialGradient>')
        self.defs.append('<radialGradient id="gem" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#d8fbff"/>'
                         f'<stop offset=".5" stop-color="{CYN_B}"/><stop offset="1" stop-color="#0b4658"/></radialGradient>')
        self.defs.append(f'<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD_L}"/>'
                         f'<stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{GOLD_D}"/></linearGradient>')
        self.defs.append('<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation=".45"/></filter>')
        self.defs.append('<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.3" '
                         'numOctaves="2" seed="7" result="n"/><feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 -.18"/></filter>')

    def clip(self, runs):
        rects = "".join(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"/>' for x, y, w, h in runs)
        self.defs.append(f'<clipPath id="reg">{rects}</clipPath>')

    def add(self, s):
        self.body.append(s)

    def base(self):
        m, rng = self.m, self.rng
        if self.overlay:
            return
        self.add(f'<rect width="{self.w}" height="{self.h}" fill="{m["d"]}"/>')
        ox, oy = rng.randrange(4), rng.randrange(4)
        mode = m["mode"]
        if mode == "plate":
            T = 4
            for ty in range(-1, self.h // T + 1):
                for tx in range(-1, self.w // T + 1):
                    x, y = tx * T - ox + 4, ty * T - oy + 4
                    v = rng.randrange(3)
                    self.add(f'<rect x="{f(x + .2)}" y="{f(y + .2)}" width="{T - .4}" height="{T - .4}" rx=".55" fill="url(#p{v})" stroke="{m["d"]}" stroke-width=".14"/>')
                    self.add(f'<path d="M{f(x + .6)} {f(y + T - .7)} V{f(y + .7)} Q{f(x + .6)} {f(y + .5)} {f(x + .9)} {f(y + .5)} H{f(x + T - .7)}" fill="none" stroke="{m["h"]}" stroke-width=".1" opacity=".32"/>')
                    if rng.random() < .35:
                        self.add(f'<circle cx="{f(x + 1)}" cy="{f(y + 1)}" r=".26" fill="url(#rv)" stroke="{m["d"]}" stroke-width=".06"/>')
        elif mode == "mesh":
            self.add(f'<rect width="{self.w}" height="{self.h}" fill="{m["H"]}"/>')
            for ry in range(-1, int(self.h / 1.6) + 2):
                for rx_ in range(-1, self.w // 2 + 2):
                    cx, cy = rx_ * 2 + (ry % 2), ry * 1.6
                    self.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r=".78" fill="none" stroke="{m["d"]}" stroke-width=".5"/>'
                             f'<circle cx="{f(cx)}" cy="{f(cy)}" r=".78" fill="none" stroke="{mixc(m["H"], m["h"], .55)}" stroke-width=".22" stroke-dasharray="1.4 .9" opacity=".8"/>')
        else:  # scale
            for row in range(-1, int(self.h / 2.6) + 2):
                for sx in range(-1, self.w // 4 + 2):
                    x, y = sx * 4 + (row % 2) * 2, row * 2.6
                    fill = "url(#p%d)" % rng.randrange(3)
                    if m.get("tint"):
                        k = rng.random()
                        fill = "url(#pm)" if k < .05 else "url(#pc)" if k < .09 else fill
                    self.add(f'<path d="M{f(x)} {f(y)} H{f(x + 4)} V{f(y + 1.7)} Q{f(x + 4)} {f(y + 3.7)} {f(x + 2)} {f(y + 3.9)} Q{f(x)} {f(y + 3.7)} {f(x)} {f(y + 1.7)} Z" fill="{fill}" stroke="{m["d"]}" stroke-width=".16"/>')
                    self.add(f'<path d="M{f(x + .7)} {f(y + 1.5)} Q{f(x + 2)} {f(y + .6)} {f(x + 3.3)} {f(y + 1.5)}" fill="none" stroke="{m["h"]}" stroke-width=".11" opacity=".35"/>')
        for col, frac in m.get("patches", []):  # oxido / cardenillo: manchas suaves
            for _ in range(max(2, int(self.w * self.h * frac / 5))):
                x, y = rng.uniform(0, self.w), rng.uniform(0, self.h)
                self.add(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(rng.uniform(.5, 1.6))}" ry="{f(rng.uniform(.4, 1.2))}" fill="{col}" opacity=".5" filter="url(#blur)"/>')
        self.add(f'<rect width="{self.w}" height="{self.h}" filter="url(#grain)" opacity=".55"/>')

    def details(self, runs):
        m, rng = self.m, self.rng
        area = sum(w * h for _, _, w, h in runs)
        for _ in range(max(1, int(area / 220))):  # grietas finas
            r = rng.choice(runs)
            x, y = r[0] + rng.uniform(0, r[2]), r[1] + rng.uniform(0, r[3])
            pts = [(x, y)]
            for _s in range(rng.randrange(4, 8)):
                x += rng.uniform(-.7, .7)
                y += rng.uniform(.4, 1.1)
                pts.append((x, y))
            d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in pts)
            self.add(f'<path d="{d}" fill="none" stroke="{m["crack"]}" stroke-width=".26" opacity=".25" filter="url(#blur)"/>')
            self.add(f'<path d="{d}" fill="none" stroke="{m["crack"]}" stroke-width=".1" stroke-linejoin="round"/>')
        for _ in range(max(1, int(area / 420))):  # estrellitas
            r = rng.choice(runs)
            x, y = r[0] + rng.uniform(1, max(1.1, r[2] - 1)), r[1] + rng.uniform(1, max(1.1, r[3] - 1))
            s = rng.uniform(.5, .8)
            self.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(s)}" fill="{m["sp"]}" opacity=".18" filter="url(#blur)"/>')
            self.add(f'<path d="M{f(x)} {f(y - s)} L{f(x + s * .22)} {f(y - s * .22)} L{f(x + s)} {f(y)} L{f(x + s * .22)} {f(y + s * .22)} L{f(x)} {f(y + s)} '
                     f'L{f(x - s * .22)} {f(y + s * .22)} L{f(x - s)} {f(y)} L{f(x - s * .22)} {f(y - s * .22)} Z" fill="{mixc(m["sp"], "#ffffff", .5)}" opacity=".9"/>')
        for _ in range(int(area / 110)):  # brillos
            r = rng.choice(runs)
            self.add(f'<circle cx="{f(r[0] + rng.uniform(0, r[2]))}" cy="{f(r[1] + rng.uniform(0, r[3]))}" r=".11" fill="{m["sp"]}" opacity=".55"/>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w * SCALE}" height="{self.h * SCALE}">'
                f'<defs>{"".join(self.defs)}</defs><g clip-path="url(#reg)">{"".join(self.body)}</g></svg>')


def face_shade(b, rects, m):
    """Sombreado de volumen por cara: luz arriba, borde inferior oscuro."""
    for i, (x, y, w, h) in enumerate(rects):
        b.defs.append(f'<linearGradient id="fs{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".07"/>'
                      f'<stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".5"/></linearGradient>')
        b.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#fs{i})"/>')
        b.add(f'<rect x="{f(x + .05)}" y="{f(y + .05)}" width="{w - .1}" height="{h - .1}" fill="none" stroke="{m["d"]}" stroke-width=".22" opacity=".7"/>')


def dragon_extras(b, layer):
    """Cresta, cuernos, espinas y alas SUTILES en coordenadas de cara (unidades de pixel vanilla)."""
    a = b.add
    if layer == 1:
        x0, y0 = HEAD["top"][0], HEAD["top"][1]
        for j in range(0, 8, 2):
            a(f'<path d="M{x0 + 3.2} {y0 + j + 1.8} L{x0 + 4} {y0 + j - .2} L{x0 + 4.8} {y0 + j + 1.8} Z" fill="{"url(#gold)" if j % 4 == 0 else MAG}" stroke="{OUT}" stroke-width=".1"/>')
        fx, fy = HEAD["front"][0], HEAD["front"][1]
        for ex in (1.2, 5.2):  # ojos
            a(f'<ellipse cx="{f(fx + ex + .8)}" cy="{f(fy + 4.3)}" rx="1.1" ry=".55" fill="{CYN_B}" opacity=".35" filter="url(#blur)"/>')
            a(f'<path d="M{f(fx + ex)} {f(fy + 4.1)} Q{f(fx + ex + .8)} {f(fy + 3.7)} {f(fx + ex + 1.7)} {f(fy + 4.5)} Q{f(fx + ex + .8)} {f(fy + 4.6)} {f(fx + ex)} {f(fy + 4.1)} Z" fill="{CYN_B}"/>')
        a(f'<path d="M{fx} {fy + 3.2} L{fx + 3} {fy + 3.8} M{fx + 8} {fy + 3.2} L{fx + 5} {fy + 3.8}" stroke="url(#gold)" stroke-width=".28" fill="none"/>')
        for side, flip in (("right", False), ("left", True)):  # cuernos
            sx, sy = HEAD[side][0], HEAD[side][1]
            X = (lambda v, sx=sx: sx + 8 - v) if flip else (lambda v, sx=sx: sx + v)
            a(f'<path d="M{f(X(5.8))} {sy + 3.6} Q{f(X(3))} {sy + 3.2} {f(X(.3))} {sy + .1} Q{f(X(2.4))} {sy + 3.9} {f(X(4.6))} {sy + 4.6} Z" fill="url(#gold)" stroke="{OUT}" stroke-width=".12"/>')
        bx, by = HEAD["back"][0], HEAD["back"][1]
        for j in range(0, 8, 2):
            a(f'<path d="M{bx + 3.3} {by + j + 1.6} L{bx + 4} {by + j} L{bx + 4.7} {by + j + 1.6} Z" fill="{MAG}"/>')
        cx, cy = BODY["front"][0], BODY["front"][1]  # gema + costillas
        for j in (3, 6.2, 9.2):
            a(f'<path d="M{cx + 1} {cy + j} Q{cx + 2} {f(cy + j + .6)} {cx + 3} {cy + j} M{cx + 5} {cy + j} Q{cx + 6} {f(cy + j + .6)} {cx + 7} {cy + j}" fill="none" stroke="{GOLD_D}" stroke-width=".22"/>')
        a(f'<path d="M{cx + 4} {f(cy + 3.4)} L{f(cx + 4.9)} {f(cy + 4.8)} L{cx + 4} {f(cy + 6.2)} L{f(cx + 3.1)} {f(cy + 4.8)} Z" fill="url(#gem)" stroke="{GOLD_D}" stroke-width=".16"/>')
        kx, ky = BODY["back"][0], BODY["back"][1]  # espina y alas
        for j in range(0, 12, 2):
            a(f'<path d="M{f(kx + 3.5)} {f(ky + j + 1.7)} L{kx + 4} {ky + j} L{f(kx + 4.5)} {f(ky + j + 1.7)} Z" fill="{GOLD_D}"/>')
        for flip in (False, True):
            X = (lambda v: kx + 8 - v) if flip else (lambda v: kx + v)
            a(f'<path d="M{f(X(3.2))} {f(ky + 6.2)} Q{f(X(1.2))} {f(ky + 4.8)} {f(X(.2))} {f(ky + 1.4)} L{f(X(.2))} {ky + 6} Q{f(X(1.2))} {f(ky + 6.6)} {f(X(3.2))} {f(ky + 8.2)} Z" fill="{MAG}" opacity=".28"/>')
            for e, end in ((6.2, 2), (8.2, 6)):
                a(f'<path d="M{f(X(3.2))} {f(ky + e)} Q{f(X(1.2))} {f(ky + e - 1.4)} {f(X(.2))} {ky + end}" fill="none" stroke="url(#gold)" stroke-width=".28"/>')
        for fn in ("right", "left", "front", "back"):  # hombreras
            ax, ay = ARM[fn][0], ARM[fn][1]
            a(f'<path d="M{f(ax + .8)} {f(ay + 1.6)} L{ax + 2} {f(ay - .2)} L{f(ax + 3.2)} {f(ay + 1.6)} Z" fill="url(#gold)" stroke="{OUT}" stroke-width=".1"/>')
        for fn in ("front", "right", "left", "back"):  # garras
            lx, ly = LEG[fn][0], LEG[fn][1]
            for k in (.4, 1.6, 2.8):
                a(f'<path d="M{f(lx + k)} {ly + 11} L{f(lx + k + .4)} {ly + 12} L{f(lx + k + .8)} {ly + 11} Z" fill="url(#gold)"/>')
    else:
        for fn, wd in (("front", 8), ("back", 8), ("left", 4), ("right", 4)):
            x, y = BODY[fn][0], BODY[fn][1]
            for i in range(0, wd, 2):
                a(f'<rect x="{f(x + i + .3)}" y="{f(y + .2)}" width="1.2" height=".6" rx=".2" fill="{GOLD_D}"/>')
        lx, ly = LEG["front"][0], LEG["front"][1]
        a(f'<path d="M{lx + 2} {f(ly + 4.6)} L{f(lx + 2.9)} {f(ly + 5.6)} L{lx + 2} {f(ly + 6.6)} L{f(lx + 1.1)} {f(ly + 5.6)} Z" fill="url(#gem)" stroke="{GOLD_D}" stroke-width=".14"/>')


def mask_runs(img):
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


def build_svg(mat, w, h, runs, key, overlay=False, face_rects=None, layer=None):
    m = MATS[mat]
    b = Builder(w, h, m, random.Random(key), overlay)
    b.grads()
    b.clip(runs)
    b.base()
    if face_rects and not overlay:
        face_shade(b, face_rects, m)
    b.details(runs)
    if mat == "dragon" and layer and not overlay:
        dragon_extras(b, layer)
    return b.svg()


def rasterize(svg_text, svg_path, png_path, size):
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_text, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(size[0]), "-h", str(size[1]), "-o", str(png_path), str(svg_path)], check=True)
    return Image.open(png_path).convert("RGBA")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def icon_svg(piece):
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
            parts = {"head": HEAD} if mat == "turtle_scute" else (LAYER1 if layer == 1 else LAYER2)
            rects = [r for p in parts.values() for r in p.values()]
            key = f"{mat}-{layer}"
            sv = build_svg(mat, 64, 32, rects, key, face_rects=rects, layer=layer)
            im = rasterize(sv, svgd / f"armor_{mat}_{sub}.svg", base / sub / f"{mat}.png", (64 * SCALE, 32 * SCALE))
            sheet[(mat, sub)] = im
            if mat == "leather":
                osv = build_svg(mat, 64, 32, rects, key + "o", overlay=True)
                rasterize(osv, svgd / f"armor_leather_{sub}_overlay.svg", base / sub / "leather_overlay.png", (64 * SCALE, 32 * SCALE))
            if mat in OLD_NAME:  # formato 1.20.x desde el mismo SVG
                old = mc / "textures/models/armor"
                old.mkdir(parents=True, exist_ok=True)
                im.save(old / f"{OLD_NAME[mat]}_layer_{layer}.png")
                if mat == "leather":
                    Image.open(base / sub / "leather_overlay.png").save(old / f"leather_layer_{layer}_overlay.png")
        src = "iron" if mat in CUSTOM else mat
        for sub, pool in (("humanoid_baby", HUMANOID_MATS), ("horse_body", ["netherite", "diamond", "iron", "gold", "copper", "leather"]),
                          ("nautilus_body", ["netherite", "diamond", "iron", "gold", "copper"])):
            if src not in pool or not have(sub, src):
                continue
            vm = vanilla_png(sub, src)
            w, h = vm.size
            sv = build_svg(mat, w, h, mask_runs(vm), f"{mat}-{sub}")
            sheet[(mat, sub)] = rasterize(sv, svgd / f"armor_{mat}_{sub}.svg", base / sub / f"{mat}.png", (w * SCALE, h * SCALE))
            if mat == "leather" and sub in ("humanoid_baby", "horse_body"):
                osv = build_svg(mat, w, h, mask_runs(vanilla_png(sub, "leather")), f"{mat}-{sub}o", overlay=True)
                rasterize(osv, svgd / f"armor_leather_{sub}_overlay.svg", base / sub / "leather_overlay.png", (w * SCALE, h * SCALE))
        if mat != "turtle_scute":
            runs = mask_runs(vanilla_png("wolf_body", "armadillo_scute"))
            sv = build_svg(mat, 64, 32, runs, f"{mat}-wolf")
            sheet[(mat, "wolf_body")] = rasterize(sv, svgd / f"armor_{mat}_wolf_body.svg", base / "wolf_body" / f"{mat}.png", (64 * SCALE, 32 * SCALE))
            if mat == "leather":
                osv = build_svg(mat, 64, 32, runs, f"{mat}-wolfo", overlay=True)
                rasterize(osv, svgd / "armor_leather_wolf_body_overlay.svg", base / "wolf_body" / "leather_overlay.png", (64 * SCALE, 32 * SCALE))

    for mat in VANILLA_JSON:  # equipment JSON a partir del REAL del jar
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
