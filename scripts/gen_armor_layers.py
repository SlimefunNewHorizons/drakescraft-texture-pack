#!/usr/bin/env python3
"""Armaduras DrakesCraft estilo KINTSUGI + armadura de DRAGON (26.x). Sin shader, solo pixeles pintados.

Materiales vanilla 26.x cubiertos: leather (teñible + overlay), chainmail, iron, gold, diamond, netherite, copper,
turtle_scute (casco). Propios: drakescraft:kintsugi y drakescraft:dragon.
Capas por material (las que existan en el vanilla del jar de cliente):
  humanoid (64x32), humanoid_leggings (64x32)      -> pintado por caras (UV vanilla)
  humanoid_baby (64x64), horse_body (64x64), nautilus_body (128x128), wolf_body (64x32)
                                                    -> mismo estilo pintado sobre la MASCARA (alpha) del PNG vanilla del jar
Equipment JSON: se parte del JSON REAL del jar (conserva humanoid_baby, trim_overrides, dyeable...) y se anade wolf_body.
Para dragon: iconos 2D de item (casco/peto/pantalon/botas) + assets/drakescraft/items|models/item.
Salida extra: fuentes SVG (assets/drakescraft/textures/gear/svg) y hoja de vista previa docs/previews/.
Uso: gen_armor_layers.py [--root .] [--jar <client.jar>]
"""
import argparse
import json
import random
import zipfile
from pathlib import Path
from PIL import Image

DEFAULT_JAR = Path.home() / ".local/share/horizon-launcher/versions/nightly-2026-11-05-66f3981/.local/minecraft/26.3/jars/client.jar"
OUTLINE = (10, 8, 16)
GOLD, GOLD_D, GOLD_L, WHITE = (176, 138, 48), (104, 78, 26), (214, 184, 96), (235, 232, 245)  # oro apagado
MAGENTA, CYAN = (150, 52, 170), (36, 150, 170)  # acentos tenues
BRIGHT_CYAN = (80, 220, 240)


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# Estilo contenido: base OSCURA con micro-variacion; acento total por capa ~<=7%.
# crack: color de grietas finas; patch: (color, fraccion) manchas (oxido/cardenillo); mode: plate | mesh | scale
MATS = {
    "netherite": dict(H="#1d1925", h="#3a3048", d="#0c0a11", sp="#7a3a8e", crack=(110, 44, 130), mode="plate"),
    "diamond":   dict(H="#12333c", h="#2a6f7b", d="#081a20", sp="#4fb3bf", crack=(46, 138, 150), mode="plate"),
    "iron":      dict(H="#3a4152", h="#6a7388", d="#1b1f2a", sp="#9aa3b8", crack=(90, 100, 120), mode="plate",
                      patch=((122, 72, 40), .045), patch2=((92, 54, 30), .03)),
    "gold":      dict(H="#3a2c10", h="#6e551c", d="#1b1305", sp="#a88a3c", crack=(128, 100, 38), mode="plate"),
    "chainmail": dict(H="#2e3342", h="#5a6176", d="#151822", sp="#8d93a6", crack=(70, 78, 98), mode="mesh"),
    "copper":    dict(H="#4a2819", h="#8a4a2c", d="#1f0f09", sp="#c9845a", crack=(150, 90, 56), mode="plate",
                      patch=((40, 120, 104), .05), patch2=((30, 88, 78), .03)),
    "turtle_scute": dict(H="#173a22", h="#3f8a4c", d="#09170e", sp="#8fd09a", crack=(70, 150, 90), mode="scale"),
    "leather":   dict(H="#a0a0a0", h="#c4c4c4", d="#5e5e5e", sp="#ffffff", crack=(140, 110, 50), mode="plate", gray=True),
    "kintsugi":  dict(H="#1a1424", h="#34264a", d="#0a0810", sp="#9b6bd0", crack=GOLD, mode="plate"),
    "dragon":    dict(H="#2a1450", h="#5b2bb5", d="#10061f", sp="#b99be8", crack=GOLD, mode="scale", tint=True),
}
VANILLA_JSON = ["netherite", "diamond", "iron", "gold", "chainmail", "copper", "leather"]  # con equipment json en el jar
HUMANOID_MATS = VANILLA_JSON + ["turtle_scute"]
CUSTOM = ["kintsugi", "dragon"]
ACCENT_M, ACCENT_C = hx("#6a1470"), hx("#0b5a70")


def box(u, v, w, h, d):
    return {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d), "right": (u, v + d, d, h),
            "front": (u + d, v + d, w, h), "left": (u + d + w, v + d, d, h), "back": (u + d + w + d, v + d, w, h)}


HEAD, BODY, ARM, LEG = box(0, 0, 8, 8, 8), box(16, 16, 8, 12, 4), box(40, 16, 4, 12, 4), box(0, 16, 4, 12, 4)
LAYER1 = {"head": HEAD, "body": BODY, "arm": ARM, "leg": LEG}
LAYER2 = {"body": BODY, "leg": LEG}


BRIGHT = {}


def rect_set(r):
    x0, y0, w, h = r
    return {(x0 + i, y0 + j) for j in range(h) for i in range(w)}


def base_color(x, y, m, ox, oy, seed):
    H, hl, d = hx(m["H"]), hx(m["h"]), hx(m["d"])
    mode = m["mode"]
    j = ((x * 2654435761 ^ y * 40503 ^ seed) >> 3) % 5  # micro-variacion de tono
    var = (-5, -2, 0, 2, 5)[j]
    jit = lambda c: tuple(max(0, min(255, v + var)) for v in c)
    if mode == "mesh":  # eslabones: anillos 4x4 de borde claro tenue y centro oscuro
        i, k = (x + (y // 4 % 2) * 2) % 4, y % 4
        if i in (0, 3) and k in (1, 2) or k in (0, 3) and i in (1, 2):
            return jit(mix(H, hl, .6))
        return jit(d if (i, k) in ((1, 1), (2, 2)) else H)
    if mode == "scale":
        row = (y + ox) // 3
        c, r = (x + oy + (row % 2) * 2) % 4, (y + ox) % 3
        cx = (x + oy + (row % 2) * 2) // 4
        if m.get("tint"):
            kk = (cx * 73856093 ^ row * 19349663 ^ seed) % 100
            if kk < 5:
                H, hl = ACCENT_M, mix(ACCENT_M, (240, 140, 250), .45)
            elif kk < 9:
                H, hl = ACCENT_C, mix(ACCENT_C, (150, 240, 255), .45)
        if r == 0 or c == 0:
            return d
        if r == 1 and c == 1 and (cx + row) % 2 == 0:
            return mix(H, hl, .55)
        return jit(H if r == 1 else tuple(max(0, v - 8) for v in H))
    px_, py_ = (x + ox) % 4, (y + oy) % 4
    cell = ((x + ox) // 4 * 31 + (y + oy) // 4 * 17 + seed) % 3
    if px_ == 0 and py_ == 0:
        return OUTLINE if not m.get("gray") else d
    if px_ == 0 or py_ == 0:
        return d
    if px_ == 1 and py_ == 1 and cell == 0:
        return mix(H, hl, .6)       # remache discreto
    if (px_ == 1 or py_ == 1) and (x + y) % 3 == 0:
        return mix(H, hl, .25)      # canto iluminado apenas
    return jit(H)


def blob(px, region, rng, color, frac, pts):
    for _ in range(max(1, int(len(region) * frac / 4))):
        x, y = rng.choice(pts)
        for _s in range(4):
            if (x, y) in region:
                px[(x, y)] = color
            x += rng.choice((-1, 0, 1))
            y += rng.choice((-1, 0, 1))


def paint(px, region, m, rng, seed=0, cracks=True):
    """Base oscura + pocas grietas finas + estrellitas sueltas + brillos tenues (+ oxido/cardenillo)."""
    if not region:
        return
    ox, oy = rng.randrange(4), rng.randrange(4)
    for (x, y) in region:
        px[(x, y)] = base_color(x, y, m, ox, oy, seed)
    n = len(region)
    pts = sorted(region)
    for key in ("patch", "patch2"):
        if key in m:
            blob(px, region, rng, m[key][0], m[key][1], pts)
    crack = m["crack"]
    if cracks:
        for _ in range(max(1, n // 220)):  # grietas finas de 1 px, cortas
            x, y = rng.choice(pts)
            for _s in range(rng.randrange(4, 9)):
                if (x, y) not in region:
                    break
                px[(x, y)] = crack if rng.random() > .2 else mix(crack, (0, 0, 0), .5)
                y += 1
                x += rng.choice((-1, 0, 0, 1))
    for _ in range(max(1, n // 400)):  # estrellita suelta tenue
        cx, cy = rng.choice(pts)
        if all((cx + dx, cy + dy) in region for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            px[(cx, cy)] = mix(hx(m["sp"]), WHITE, .6)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                px[(cx + dx, cy + dy)] = mix(px[(cx + dx, cy + dy)], hx(m["sp"]), .35)
    sp = hx(m["sp"])
    for _ in range(n // 90):
        px[rng.choice(pts)] = mix(sp, (0, 0, 0), .35)


def paint_overlay(px, region, m, rng):
    """Overlay sin teñir (cuero): solo grietas, estrellitas y brillos; el resto transparente."""
    tmp = {}
    paint(tmp, region, m, rng)
    base = {k: v for k, v in tmp.items() if max(v) > 120}
    px.update(base)


class Face:
    def __init__(self, px, rect):
        self.px, self.r = px, rect

    def put(self, i, j, c):
        x0, y0, w, h = self.r
        if 0 <= i < w and 0 <= j < h:
            self.px[(x0 + i, y0 + j)] = c


def dragon_extras(px, layer):
    """Cresta, cuernos, espinas y alas SUTILES: base oscura, pocos pixeles de acento."""
    F = lambda part, f: Face(px, part[f])
    if layer == 1:
        t = F(HEAD, "top")  # cresta central: puntos dorados espaciados
        for j in range(0, 8, 2):
            t.put(3, j, GOLD); t.put(4, j, MAGENTA)
        fr = F(HEAD, "front")
        fr.put(2, 4, BRIGHT_CYAN); fr.put(5, 4, BRIGHT_CYAN)   # ojos
        fr.put(1, 4, CYAN); fr.put(6, 4, CYAN)
        for i in (0, 7):
            fr.put(i, 0, GOLD); fr.put(i, 1, GOLD_D)          # base de cuernos
        for side, flip in (("right", False), ("left", True)):  # cuernos barridos hacia atras
            s = F(HEAD, side)
            for (i, j) in ((5, 3), (4, 2), (3, 2), (2, 1), (1, 1), (0, 0)):
                s.put(7 - i if flip else i, j, GOLD if (i + j) % 2 else GOLD_D)
        b = F(HEAD, "back")
        for j in range(0, 8, 2):
            b.put(3, j, GOLD_D); b.put(4, j, MAGENTA)
        f = F(BODY, "front")  # pecho: gema unica y costillas tenues
        f.put(3, 4, BRIGHT_CYAN); f.put(4, 4, CYAN); f.put(3, 5, CYAN); f.put(4, 5, CYAN)
        for j in (3, 6, 9):
            for i in (1, 2, 5, 6):
                f.put(i, j, GOLD_D)
        bk = F(BODY, "back")  # espina dorsal y dos huesos de ala por lado
        for j in range(0, 12, 2):
            bk.put(3, j, GOLD_D); bk.put(4, j, GOLD_D)
        for flip in (False, True):
            X = (lambda i: 7 - i) if flip else (lambda i: i)
            for off in (3, 5):
                for k in range(4):
                    bk.put(X(3 - k), off + k, GOLD if k == 3 else GOLD_D)
            bk.put(X(1), 4, MAGENTA); bk.put(X(0), 5, CYAN)
        for f_ in ("right", "left", "front", "back"):   # hombreras con espina
            a = F(ARM, f_)
            for i in range(4):
                a.put(i, 0, GOLD_D)
            a.put(1, 1, MAGENTA)
        for f_ in ("front", "right", "left", "back"):   # garras
            l = F(LEG, f_)
            for i in range(4):
                l.put(i, 8, GOLD_D)
            l.put(1, 11, GOLD)
    else:
        for f_ in ("front", "back", "left", "right"):
            bf = F(BODY, f_)
            for i in range(0, 8 if f_ in ("front", "back") else 4, 2):
                bf.put(i, 0, GOLD_D)
        lf = F(LEG, "front")
        lf.put(1, 5, CYAN); lf.put(2, 5, CYAN)


def humanoid_layer(mat, layer, overlay=False):
    m = MATS[mat]
    rng = random.Random(f"{mat}-{layer}-{overlay}")
    px = {}
    parts = LAYER1 if layer == 1 else LAYER2
    if mat == "turtle_scute":
        parts = {"head": HEAD}
    for pname, faces in parts.items():
        for fname, rect in faces.items():
            region = rect_set(rect)
            if overlay:
                paint_overlay(px, region, m, rng)
                continue
            paint(px, region, m, rng, seed=len(px))
            x0, y0, w, h = rect
            for i in range(w):  # borde inferior mas oscuro
                px[(x0 + i, y0 + h - 1)] = hx(m["d"])
            if layer == 2 and pname == "body" and fname in ("front", "back", "left", "right"):
                for i in range(w):
                    px[(x0 + i, y0)] = hx(m["d"])
                    if i % 4 == 1:
                        px[(x0 + i, y0 + 1)] = GOLD_D
    if mat == "dragon" and not overlay:
        dragon_extras(px, layer)
    return px


def mask_layer(mask_img, mat, overlay=False):
    m = MATS[mat]
    rng = random.Random(f"{mat}-mask-{mask_img.size}-{overlay}")
    region = {(x, y) for y in range(mask_img.size[1]) for x in range(mask_img.size[0]) if mask_img.getpixel((x, y))[3] > 0}
    px = {}
    (paint_overlay if overlay else paint)(px, region, m, rng)
    return px, mask_img.size


def save_png(px, size, path):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    for (x, y), c in px.items():
        if 0 <= x < size[0] and 0 <= y < size[1]:
            im.putpixel((x, y), tuple(c) + (255,))
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    tot = sum(1 for c in px.values())
    br = sum(1 for c in px.values() if max(c) > 150)
    BRIGHT[str(path.relative_to(path.parents[5]) if len(path.parents) > 5 else path)] = br / max(1, tot)
    return im


def save_svg(px, size, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h = size
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * 8}" height="{h * 8}" shape-rendering="crispEdges">']
    for y in range(h):
        x = 0
        while x < w:
            c = px.get((x, y))
            if c is None:
                x += 1
                continue
            e = x
            while e + 1 < w and px.get((e + 1, y)) == c:
                e += 1
            out.append(f'<rect x="{x}" y="{y}" width="{e - x + 1}" height="1" fill="#{c[0]:02x}{c[1]:02x}{c[2]:02x}"/>')
            x = e + 1
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ---------------- iconos 2D del set dragon (mitad izquierda 8 col x 16 filas, se espeja) ----------------
ICONS = {
    "helmet": ["G......P", "GG....PP", "oGoooooP", ".oHhHHHP", "oHhHHHHH", "oGGGGGGG", "oHEEHHHH", "oHHHHHHH",
               "oHd.HHHH", "oHd..HHH", "oHd.....", "ood.....", "........", "........", "........", "........"],
    "chestplate": ["........", "P.......", "PGo..ooo", "oGHooHHH", "oHhHHHHH", "oHHHGGGG", "oHHHGEEG", ".oHHGEEG",
                   ".oHHGGGG", ".oHdHHHH", ".oHdHHHH", ".oHdHHHH", ".oHdHHHH", ".ooHdHHH", "..ooooDD", "........"],
    "leggings": ["........", "........", ".ooooooo", ".oGGGGGG", ".oHHHhHH", ".oHHHHHH", ".oHHHHHo", ".oHHHHHo",
                 ".oHHdoo.", ".oHEdo..", ".oHHdo..", ".oHHdo..", ".oHHdo..", ".oHhdo..", ".ooood..", "........"],
    "boots": ["........", "........", "........", "........", "........", "..oooo..", "..oHho..", "..oHHo..",
              "..oGGo..", "..oHHo..", ".ooHHo..", "oHHHHo..", "oGHHHo..", "oGDDDo..", "ooooooo.", "........"],
}


def icon_px(rows):
    m = MATS["dragon"]
    H, hl, d = hx(m["H"]), hx(m["h"]), hx(m["d"])
    px = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            c = {"o": OUTLINE, "H": H, "h": hl, "D": d, "d": d, "G": GOLD_D, "P": MAGENTA, "E": BRIGHT_CYAN}[ch]
            if ch == "H" and (x + y) % 3 == 0:
                c = tuple(max(0, v - 15) for v in H)  # escamas
            for xx in (x, 15 - x):
                if (xx, y) not in px or xx == x:
                    px[(xx, y)] = c
    return px


# ---------------- principal ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--jar", default=str(DEFAULT_JAR))
    a = ap.parse_args()
    root = Path(a.root)
    mc, dk = root / "assets/minecraft", root / "assets/drakescraft"
    svg = dk / "textures/gear/svg"
    z = zipfile.ZipFile(a.jar)
    import io

    def vanilla_png(layer, name):
        return Image.open(io.BytesIO(z.read(f"assets/minecraft/textures/entity/equipment/{layer}/{name}.png"))).convert("RGBA")

    def have(layer, name):
        return f"assets/minecraft/textures/entity/equipment/{layer}/{name}.png" in z.namelist()

    sheet = {}
    for mat in HUMANOID_MATS + CUSTOM:
        base = (dk if mat in CUSTOM else mc) / "textures/entity/equipment"
        # humanoid + leggings por caras
        for layer, sub in ((1, "humanoid"), (2, "humanoid_leggings")):
            if mat == "turtle_scute" and layer == 2:
                continue
            px = humanoid_layer(mat, layer)
            im = save_png(px, (64, 32), base / sub / f"{mat}.png")
            save_svg(px, (64, 32), svg / f"armor_{mat}_{sub}.svg")
            sheet[(mat, sub)] = im
            if mat == "leather":
                opx = humanoid_layer(mat, layer, overlay=True)
                save_png(opx, (64, 32), base / sub / "leather_overlay.png")
        # capas por mascara (UV vanilla desconocido por caras): baby / caballo / nautilus / lobo
        src = "iron" if mat in CUSTOM else mat
        for sub, pool in (("humanoid_baby", HUMANOID_MATS), ("horse_body", ["netherite", "diamond", "iron", "gold", "copper", "leather"]),
                          ("nautilus_body", ["netherite", "diamond", "iron", "gold", "copper"])):
            if src not in pool or not have(sub, src):
                continue
            px, size = mask_layer(vanilla_png(sub, src), mat)
            sheet[(mat, sub)] = save_png(px, size, base / sub / f"{mat}.png")
            if mat == "leather" and sub in ("humanoid_baby", "horse_body"):
                opx, size = mask_layer(vanilla_png(sub, "leather"), mat, overlay=True)
                save_png(opx, size, base / sub / "leather_overlay.png")
        if mat != "turtle_scute":  # armadura de lobo: mascara del armadillo (64x32)
            px, size = mask_layer(vanilla_png("wolf_body", "armadillo_scute"), mat)
            sheet[(mat, "wolf_body")] = save_png(px, size, base / "wolf_body" / f"{mat}.png")
            if mat == "leather":
                opx, size = mask_layer(vanilla_png("wolf_body", "armadillo_scute"), mat, overlay=True)
                save_png(opx, size, base / "wolf_body" / "leather_overlay.png")

    # equipment JSON: parte del JSON real del jar
    for mat in VANILLA_JSON:
        j = json.loads(z.read(f"assets/minecraft/equipment/{mat}.json"))
        if mat == "leather":
            j["layers"]["wolf_body"] = json.loads(json.dumps(j["layers"]["humanoid"]))
        else:
            j["layers"]["wolf_body"] = [{"texture": f"minecraft:{mat}"}]
        write_json(mc / "equipment" / f"{mat}.json", j)
    for mat in CUSTOM:
        t = lambda: [{"texture": f"drakescraft:{mat}"}]
        layers = {"humanoid": t(), "humanoid_baby": t(), "humanoid_leggings": t(), "horse_body": t(),
                  "nautilus_body": t(), "wolf_body": t()}
        write_json(dk / "equipment" / f"{mat}.json", {"layers": layers})

    # iconos del set dragon
    icons = {}
    for piece, rows in ICONS.items():
        px = icon_px(rows)
        full = {}
        for (x, y), c in px.items():
            full[(x, y)] = c
        for (x, y) in list(full):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = (x + dx, y + dy)
                    if 0 <= p[0] < 16 and 0 <= p[1] < 16 and p not in full:
                        full[p] = OUTLINE
        icons[piece] = save_png(full, (16, 16), dk / f"textures/item/dragon_{piece}.png")
        save_svg(full, (16, 16), svg / f"dragon_{piece}.svg")
        write_json(dk / f"models/item/dragon_{piece}.json", {"parent": "minecraft:item/generated", "textures": {"layer0": f"drakescraft:item/dragon_{piece}"}})
        write_json(dk / f"items/dragon_{piece}.json", {"model": {"type": "minecraft:model", "model": f"drakescraft:item/dragon_{piece}"}})

    # hoja de vista previa
    prev = root / "docs/previews"
    prev.mkdir(parents=True, exist_ok=True)
    S = 4
    order = ["netherite", "diamond", "iron", "gold", "chainmail", "copper", "leather", "turtle_scute", "kintsugi", "dragon"]
    W = 64 * 2 * S + 20 + 4 * 16 * 6 + 20
    sh = Image.new("RGBA", (max(W, 1400), 40 + len(order) * (32 * S + 8) + 2 * (64 * S + 12) + 32 * S + 20), (40, 40, 48, 255))
    y = 6
    x = 10
    for piece, im in icons.items():
        sh.alpha_composite(im.resize((96, 96), Image.NEAREST), (x, y))
        x += 104
    y = 110
    for mat in order:
        x = 6
        for sub in ("humanoid", "humanoid_leggings", "wolf_body"):
            im = sheet.get((mat, sub))
            if im:
                sh.alpha_composite(im.resize((64 * S, 32 * S), Image.NEAREST), (x, y))
            x += 64 * S + 6
        y += 32 * S + 8
    for mat in ("dragon", "kintsugi", "netherite"):
        x = 6
        for sub, sz in (("horse_body", 64 * S // 2 * 2 // 2), ("humanoid_baby", 64 * S // 2 * 2 // 2), ("nautilus_body", 128 * 2)):
            im = sheet.get((mat, sub))
            if im:
                s = im.size[0]
                k = 256 // s if s <= 128 else 1
                sh.alpha_composite(im.resize((s * k, s * k), Image.NEAREST) if k > 0 else im, (x, y))
                x += s * k + 6
        y += 262
    sh = sh.crop((0, 0, sh.size[0], min(sh.size[1], y)))
    sh.save(prev / "armaduras_kintsugi_dragon.png")
    worst = sorted(BRIGHT.items(), key=lambda t: -t[1] if "overlay" not in t[0] else 0)[:4]
    print("ok", sorted({k[0] for k in sheet}), "brillo max:", [(k.split("/")[-1], round(v, 3)) for k, v in worst])


if __name__ == "__main__":
    main()
