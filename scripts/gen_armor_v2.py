#!/usr/bin/env python3
"""Armaduras v2 (dragon con escamas, kintsugi laqueada, tecnologica x4 colores) a 4x (256x128), cara abierta,
alas de dragon via capa `wings` (sale del molde). Uso: gen_armor_v2.py [--root .]"""
import json, math, random, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

K = 4
def hx(s): return np.array([int(s[i:i+2], 16) for i in (1, 3, 5)], float)
def ramp(c0, c1, t): return hx(c0)*(1-t)+hx(c1)*t

# ---------- superficies base (devuelven array HxWx3) ----------
def scales(W, H, dark, light, cw=11, ch=8, seed=1):
    img = np.zeros((H, W, 3)); rng = random.Random(seed)
    r = cw*0.62
    for y in range(H):
        row = y//ch
        for x in range(W):
            best = None
            for rr in (row, row-1):          # la fila inferior tapa a la superior
                xo = x + (cw/2 if rr % 2 else 0)
                col = int(xo//cw)
                cx = col*cw + cw/2 - (cw/2 if rr % 2 else 0)
                cy = rr*ch + ch*0.35
                dx, dy = (x-cx)/r, (y-cy)/(r*0.95)
                d = math.hypot(dx, dy)
                if d <= 1.0 and (best is None or rr == row):
                    best = (dx, dy, d)
                    if rr == row: break
            if best is None: img[y, x] = hx(dark)*0.45; continue
            dx, dy, d = best
            t = 0.55 + 0.45*(-(dx*0.45+dy*0.75))      # luz arriba-izquierda
            t = min(1, max(0, t))*(1-0.55*max(0, d-0.72)/0.28)
            img[y, x] = ramp(dark, light, min(1, max(0, t)))
            if d > 0.93: img[y, x] = hx(dark)*0.35
    return img

def plates(W, H, dark, light, pw=24, ph=24, seed=2, bevel=3):
    img = np.zeros((H, W, 3))
    for y in range(H):
        for x in range(W):
            px, py = x % pw, y % ph
            e = min(px, py, pw-1-px, ph-1-py)
            t = 0.35 + 0.1*math.sin((x+y*0.3)/9)
            if e < bevel:
                top, left = py < bevel and py <= px, px < bevel and px < py
                t = 0.78 if (top or left) and e < bevel else 0.08
                if e == 0: t = 0.0
            img[y, x] = ramp(dark, light, t)
    return img

# ---------- helpers de composicion ----------
class Sheet:
    def __init__(self, base):
        self.base = base; self.H, self.W = base.shape[:2]
        self.mask = Image.new("L", (self.W, self.H), 0)
        self.top = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.top)
        self.cut = Image.new("L", (self.W, self.H), 0); self.cd = ImageDraw.Draw(self.cut)
    def region(self, x, y, w, h): ImageDraw.Draw(self.mask).rectangle([x*K, y*K, (x+w)*K-1, (y+h)*K-1], fill=255)
    def hole(self, x, y, w, h): self.cd.rectangle([x*K, y*K, (x+w)*K-1, (y+h)*K-1], fill=255)
    def rect(self, x, y, w, h, c, a=255): self.d.rectangle([x*K, y*K, (x+w)*K-1, (y+h)*K-1], fill=hxa(c, a))
    def poly(self, pts, c, a=255): self.d.polygon([(px*K, py*K) for px, py in pts], fill=hxa(c, a))
    def line(self, pts, c, wd=1.0, a=255): self.d.line([(px*K, py*K) for px, py in pts], fill=hxa(c, a), width=max(1, int(wd*K)))
    def ell(self, x, y, w, h, c, a=255): self.d.ellipse([x*K, y*K, (x+w)*K-1, (y+h)*K-1], fill=hxa(c, a))
    def out(self):
        im = Image.fromarray(np.clip(self.base, 0, 255).astype("uint8")).convert("RGBA")
        im.alpha_composite(self.top)
        a = np.array(self.mask).astype(int)
        # contorno oscuro de 1px (4x) en el borde de cada region para separar piezas
        a2 = np.minimum(a, 255-np.array(self.cut))
        r = np.array(im); r[..., 3] = a2
        return Image.fromarray(r.astype("uint8"))

def hxa(c, a=255): return tuple(int(v) for v in hx(c)) + (a,)

def add_noise(base, seed=5, amt=6):
    rng = np.random.default_rng(seed); return base + rng.normal(0, amt, base.shape[:2])[..., None]

def gold(s, x, y, w, h): s.rect(x, y, w, h, "#d6a93a"); s.rect(x, y, w, 0.25, "#f6dc7e"); s.rect(x, y+h-0.25, w, 0.25, "#6e4f12")

# regiones capa 1 / capa 2
def layer1_regions(s):
    s.region(0, 0, 32, 16); s.region(16, 16, 24, 16); s.region(40, 16, 16, 16)
    s.region(0, 16, 16, 4); s.region(0, 27, 16, 5)
def layer2_regions(s):
    s.region(16, 16, 24, 4); s.region(16, 27, 24, 5); s.region(0, 16, 16, 16)

def face_open(s, brow=2):  # cara abierta: solo ceja y mejillas
    s.hole(9, 8+brow, 6, 8-brow)   # deja pasar la cara del jugador (el hueco central de la cara frontal)

# ---------- DRAGON ----------
def dragon():
    P = dict(d="#1a0b38", l="#7a45cc")
    s1 = Sheet(add_noise(scales(256, 128, P["d"], P["l"], 10, 7, 1)))
    layer1_regions(s1)
    # cabeza: frente (8,8)-(16,16): ceja dorada + ojos cian brillantes; hueco de cara
    face_open(s1, 2)
    s1.rect(8, 8, 8, 1.5, "#2a1458"); gold(s1, 8, 9, 8, 1)
    s1.poly([(9, 9.2), (11.4, 9.2), (10.6, 10.0)], "#58e6ff"); s1.poly([(14.6, 9.2), (12.6, 9.2), (13.4, 10.0)], "#58e6ff")
    s1.rect(8, 10, 1, 4, "#2a1458"); s1.rect(15, 10, 1, 4, "#2a1458"); gold(s1, 8, 13.5, 1, 1); gold(s1, 15, 13.5, 1, 1)
    # cresta dorsal en la tapa y nuca
    s1.rect(11.5, 0, 1, 8, "#b02be0"); s1.rect(11.7, 0, 0.6, 8, "#e49cff")
    for i in range(4): s1.poly([(11.5, 1+i*2), (12.5, 1+i*2), (12, 0.2+i*2)], "#ff7bf5")
    s1.rect(27.5, 8, 1, 8, "#b02be0")
    # cuernos: laterales de la cabeza (derecho x0-8 / izquierdo x16-24), curvos hacia atras
    for ox, sgn in ((0, 1), (16, -1)):
        pts = [(ox+2, 14), (ox+4, 11), (ox+6, 9.5), (ox+8, 9), (ox+6.5, 10.6), (ox+5, 12), (ox+3.5, 14)] if sgn > 0 else [(ox+6, 14), (ox+4, 11), (ox+2, 9.5), (ox, 9), (ox+1.5, 10.6), (ox+3, 12), (ox+4.5, 14)]
        s1.poly(pts, "#e6c564"); s1.line(pts[:4], "#fff1b0", 0.3)
    # torso frente (20,20)-(28,32): placa pectoral dorada, gema, vientre en bandas
    for i in range(6): s1.rect(21, 26+i*1.0, 6, 0.3, "#0d051f", 160)
    gold(s1, 20, 20, 8, 1.2)
    s1.poly([(22, 21.5), (26, 21.5), (26.8, 24), (24, 27.5), (21.2, 24)], "#d6a93a")
    s1.poly([(22.4, 22), (25.6, 22), (26.2, 24), (24, 26.8), (21.8, 24)], "#3a1b78")
    s1.poly([(24, 22.4), (25.2, 24), (24, 26), (22.8, 24)], "#6af0ff"); s1.poly([(24, 22.4), (24.6, 24), (24, 25), (23.4, 24)], "#e9ffff")
    # espalda (32,20)-(40,32): espinazo magenta y raiz de alas
    s1.rect(35.5, 20, 1, 12, "#2a1458")
    for i in range(6): s1.poly([(35, 21+i*1.9), (37, 21+i*1.9), (36, 19.6+i*1.9)], "#e24bff")
    s1.line([(33, 22), (35, 25), (33, 29)], "#e6c564", 0.3); s1.line([(39, 22), (37, 25), (39, 29)], "#e6c564", 0.3)
    # hombreras (arriba de brazos) con pinchos dorados
    for ax in (44, 48, 52):
        s1.rect(ax-4+0, 20, 4, 3, "#2a1458"); gold(s1, ax-4, 22.4, 4, 0.8)
    for ax in (44, 52): s1.poly([(ax-3, 20), (ax-1, 20), (ax-2, 17.5)], "#e6c564")
    gold(s1, 40, 28.5, 16, 1)   # brazalete
    # botas: garras doradas abajo
    gold(s1, 0, 27, 16, 1)
    for x in range(0, 16, 2): s1.poly([(x, 31.2), (x+1, 31.2), (x+0.5, 32)], "#ffe9a0")
    s1.rect(0, 20, 16, 7, "#000000", 0); s1.hole(0, 20, 16, 7)  # solo botas visibles
    s1.hole(0, 16, 16, 4)

    s2 = Sheet(add_noise(scales(256, 128, P["d"], P["l"], 10, 7, 2)))
    layer2_regions(s2)
    gold(s2, 16, 27, 24, 1.4)   # cinturon
    s2.poly([(22.5, 27), (25.5, 27), (26, 29), (24, 31.2), (22, 29)], "#d6a93a")
    s2.poly([(23.2, 27.6), (24.8, 27.6), (25, 29), (24, 30.4), (23, 29)], "#6af0ff")
    for lx in (0, 4, 8, 12):
        s2.poly([(lx+0.5, 22), (lx+3.5, 22), (lx+3, 25), (lx+2, 26.2), (lx+1, 25)], "#d6a93a")   # rodilleras
        s2.poly([(lx+1.3, 22.6), (lx+2.7, 22.6), (lx+2.5, 24.5), (lx+2, 25.3), (lx+1.5, 24.5)], "#3a1b78")
    s2.rect(0, 30.5, 16, 1.5, "#2a1458"); gold(s2, 0, 30.2, 16, 0.6)

    # alas: elytra-UV 64x32 (ala en (22,0) 10x20x2): silueta con dedos, membrana magenta, huesos dorados
    w = Sheet(np.zeros((128, 256, 3))); w.base[:] = hx("#2a1458")
    w.region(22, 0, 24, 22)
    s = w
    s.base[:] = add_noise(scales(256, 128, "#240f4a", "#8a3fd0", 12, 8, 3))
    for fx in (24, 34):    # frente y dorso: ala de dragon (tope = hombro; abajo = punta)
        s.hole(fx, 2, 10, 20)   # se reconstruye abajo con poligono
    w.cut = Image.new("L", (256, 128), 0); w.cd = ImageDraw.Draw(w.cut)
    for fx in (24, 34):
        mirror = fx == 34
        def X(x): return fx+(10-x if mirror else x)
        # recortes entre dedos (alpha 0)
        for pts in ([(3, 12), (4, 22), (2, 22)], [(6.2, 13), (7, 22), (5, 22)], [(9, 14), (10, 22), (8, 22)]):
            w.cd.polygon([(X(px)*K, (2+py-2)*K) for px, py in pts], fill=255)
        # membrana magenta
        w.poly([(X(0.2), 5), (X(3), 12.5), (X(4.5), 21.5), (X(1.5), 21.5)], "#b02be0", 255)
        # huesos/dedos
        w.line([(X(0.5), 3), (X(3), 12), (X(3.6), 21)], "#e6c564", 0.55); w.line([(X(1.5), 3.5), (X(6), 14), (X(6.4), 21.4)], "#e6c564", 0.5)
        w.line([(X(2.5), 3.5), (X(9), 15), (X(9.2), 21)], "#e6c564", 0.45)
        w.rect(X(0) if not mirror else X(1.2), 2, 1.2, 4, "#f4d97c")
    return s1.out(), s2.out(), w.out()

# ---------- TECNOLOGICA ----------
ACC = {"cyan": ("#35e4ff", "#bdf7ff"), "magenta": ("#ff3fd8", "#ffc4f3"), "gold": ("#ffc933", "#fff0b0"), "green": ("#4dff88", "#c9ffe0")}
def circuits(s, regions, acc, seed):
    rng = random.Random(seed); a, b = ACC[acc]
    for (x, y, w, h) in regions:
        for _ in range(max(2, int(w*h/40))):
            px, py = x+rng.randint(1, max(1, int(w)-2)), y+rng.randint(1, max(1, int(h)-2)); pts = [(px, py)]
            for _ in range(rng.randint(2, 4)):
                if rng.random() < .5: px = min(x+w-0.5, max(x+0.5, px+rng.choice((-3, -2, 2, 3))))
                else: py = min(y+h-0.5, max(y+0.5, py+rng.choice((-3, -2, 2, 3))))
                pts.append((px, py))
            s.line(pts, a, 0.22); s.ell(pts[-1][0]-0.4, pts[-1][1]-0.4, 0.8, 0.8, b)

def tech(acc):
    a, b = ACC[acc]
    P = dict(d="#0b0f1a", l="#4a566e")
    s1 = Sheet(add_noise(plates(256, 128, P["d"], P["l"], 24, 20, 1), 7, 4))
    layer1_regions(s1)
    face_open(s1, 3)
    s1.rect(8, 8, 8, 2, "#10162a"); s1.rect(8, 10, 8, 0.4, a)
    s1.rect(8, 10.4, 8, 1.4, a, 70)      # visor translucido
    s1.rect(8, 11.8, 1, 3.2, "#10162a"); s1.rect(15, 11.8, 1, 3.2, "#10162a"); s1.rect(11.2, 11.5, 1.6, 2.5, "#10162a")
    s1.rect(8, 8.5, 8, 0.25, b)
    s1.rect(1, 11, 6, 1, "#10162a"); s1.rect(2, 11.3, 4, 0.4, a)  # lateral: antena/auricular
    s1.rect(24, 10, 8, 2, "#10162a"); s1.rect(24.5, 10.5, 7, 0.5, a)
    s1.rect(11.5, 0, 1, 8, a); s1.rect(8, 3.5, 8, 0.4, a, 150)
    circuits(s1, [(0, 0, 32, 8), (17, 17, 22, 3)], acc, 11)
    # torso
    s1.rect(20, 20, 8, 1, "#10162a"); s1.poly([(22, 22), (26, 22), (26.8, 25), (24, 28), (21.2, 25)], "#10162a")
    s1.poly([(22.4, 22.4), (25.6, 22.4), (26.2, 25), (24, 27.4), (21.8, 25)], "#050810"); s1.ell(23, 23.6, 2, 2, a); s1.ell(23.5, 24.1, 1, 1, b)
    s1.rect(32, 21, 8, 1, "#10162a"); s1.rect(35, 22, 2, 8, "#10162a"); s1.rect(35.4, 22.5, 1.2, 7, a, 200)
    circuits(s1, [(20, 28, 8, 3), (32, 24, 8, 7), (40, 21, 16, 10)], acc, 12)
    s1.rect(40, 20, 16, 2.4, "#10162a"); s1.rect(40, 22, 16, 0.3, a)
    s1.rect(0, 27, 16, 1, "#10162a"); s1.rect(0, 27.8, 16, 0.3, a)
    s1.hole(0, 20, 16, 7); s1.hole(0, 16, 16, 4)
    s2 = Sheet(add_noise(plates(256, 128, P["d"], P["l"], 24, 20, 3), 8, 4))
    layer2_regions(s2)
    s2.rect(16, 27, 24, 1.2, "#10162a"); s2.rect(16, 28.2, 24, 0.3, a); s2.rect(22.5, 28.2, 3, 3, "#050810"); s2.rect(23.5, 29, 1, 1.4, a)
    for lx in (0, 4, 8, 12):
        s2.rect(lx+0.5, 22, 3, 3, "#10162a"); s2.rect(lx+1.5, 22.6, 1, 1.8, a, 220)
    s2.rect(0, 30, 16, 0.4, a)
    circuits(s2, [(0, 17, 16, 4), (16, 29, 24, 3), (0, 25, 16, 4)], acc, 13)
    return s1.out(), s2.out()

# ---------- KINTSUGI (laca morado-negra con vetas de oro grandes) ----------
def kintsugi():
    s1 = Sheet(add_noise(plates(256, 128, "#14101e", "#5b4a7e", 20, 20, 1, 4), 4, 3))
    layer1_regions(s1); face_open(s1, 3)
    s1.rect(8, 8, 8, 2, "#1c1530"); gold(s1, 8, 9.6, 8, 0.6); s1.rect(8, 10, 1, 4, "#1c1530"); s1.rect(15, 10, 1, 4, "#1c1530")
    # moneda/cresta de oro en frente
    s1.poly([(11, 8), (13, 8), (12, 6.3)], "#e6c564")
    rng = random.Random(9)
    for (x, y, w, h) in [(0, 0, 32, 16), (20, 20, 8, 12), (32, 20, 8, 12), (40, 20, 16, 12), (0, 27, 16, 5)]:
        for _ in range(int(w*h/22)+1):
            px, py = x+rng.uniform(0, w), y+rng.uniform(0, h); pts = [(px, py)]
            for _ in range(rng.randint(3, 6)):
                px = min(x+w, max(x, px+rng.uniform(-1.6, 1.6))); py = min(y+h, max(y, py+rng.uniform(-1.6, 1.6))); pts.append((px, py))
            s1.line(pts, "#7a5712", 0.45); s1.line(pts, "#f2c94c", 0.26)
    s1.poly([(22, 22), (26, 22), (24, 27)], "#e6c564"); s1.poly([(23, 22.6), (25, 22.6), (24, 25.5)], "#1c1530")
    s1.hole(0, 20, 16, 7); s1.hole(0, 16, 16, 4)
    s2 = Sheet(add_noise(plates(256, 128, "#14101e", "#5b4a7e", 20, 20, 2, 4), 5, 3))
    layer2_regions(s2); gold(s2, 16, 27, 24, 1.2)
    for _ in range(26):
        x, y = rng.uniform(0, 16), rng.uniform(17, 32); pts = [(x, y)]
        for _ in range(4): x += rng.uniform(-1.4, 1.4); y += rng.uniform(0.5, 2); pts.append((min(16, max(0, x)), min(32, y)))
        s2.line(pts, "#7a5712", 0.45); s2.line(pts, "#f2c94c", 0.26)
    return s1.out(), s2.out()

def save(root, ns, name, l1, l2, wings=None):
    base = Path(root)/f"assets/{ns}/textures/entity/equipment"
    for d, im in (("humanoid", l1), ("humanoid_baby", l1), ("humanoid_leggings", l2)):
        (base/d).mkdir(parents=True, exist_ok=True); im.save(base/d/f"{name}.png")
    layers = {"humanoid": [{"texture": f"{ns}:{name}"}], "humanoid_baby": [{"texture": f"{ns}:{name}"}], "humanoid_leggings": [{"texture": f"{ns}:{name}"}]}
    if wings is not None:
        (base/"wings").mkdir(parents=True, exist_ok=True); wings.save(base/"wings"/f"{name}.png"); layers["wings"] = [{"texture": f"{ns}:{name}", "use_player_texture": False}]
    # conserva capas de caballo/lobo/nautilo ya existentes
    ej = Path(root)/f"assets/{ns}/equipment/{name}.json"
    if ej.exists():
        old = json.loads(ej.read_text())["layers"]
        for k in ("horse_body", "nautilus_body", "wolf_body"):
            if k in old: layers[k] = old[k]
    ej.parent.mkdir(parents=True, exist_ok=True); ej.write_text(json.dumps({"layers": layers}, indent=2))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="."); a = ap.parse_args()
    l1, l2, w = dragon(); save(a.root, "drakescraft", "dragon", l1, l2, w)
    l1, l2 = kintsugi(); save(a.root, "drakescraft", "kintsugi", l1, l2)
    for c in ACC:
        l1, l2 = tech(c); save(a.root, "drakescraft", f"tech_{c}", l1, l2)
    print("ok")
