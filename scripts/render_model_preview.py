#!/usr/bin/env python3
"""Vista ortografica (frontal XY o lateral ZY) de modelos de bloque con cuboides + rotacion Z. Uso: render_model_preview.py out.png modelo.json... """
import sys, json, math
from PIL import Image, ImageDraw
from pathlib import Path
CELLS_COL = {}
def cellcolor(atlas, uv):
    u = (uv[0] + uv[2]) / 2 / 16; v = (uv[1] + uv[3]) / 2 / 16
    return atlas.getpixel((int(u*atlas.width), int(v*atlas.height)))[:3]
def draw(model, atlas, view, S=14):
    W = 16*S + 40
    img = Image.new("RGBA", (W, W), (50, 46, 62, 255)); d = ImageDraw.Draw(img)
    polys = []
    for e in model["elements"]:
        x1, y1, z1 = e["from"]; x2, y2, z2 = e["to"]
        col = cellcolor(atlas, e["faces"]["north"]["uv"])
        pts = [(x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1), (x1, y1, z2), (x2, y1, z2), (x2, y2, z2), (x1, y2, z2)]
        r = e.get("rotation")
        if r:
            a = math.radians(r["angle"]); ox, oy, _ = r["origin"]
            pts = [(ox + (x-ox)*math.cos(a) - (y-oy)*math.sin(a), oy + (x-ox)*math.sin(a) + (y-oy)*math.cos(a), z) for x, y, z in pts]
        if view == "front":
            xy = [(x, y) for x, y, z in pts]; depth = -min(z1, z2)
        else:
            xy = [(z, y) for x, y, z in pts]; depth = -min(x for x, y, z in pts)
        hull = convex(xy)
        polys.append((depth, hull, col))
    for depth, hull, col in sorted(polys, key=lambda t: t[0]):
        d.polygon([(20 + x*S, W - 20 - y*S) for x, y in hull], fill=col + (255,), outline=(13, 10, 20, 255))
    d.rectangle([20, 20, W-20, W-20], outline=(90, 84, 110, 255))
    return img
def convex(p):
    p = sorted(set(p))
    def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo = []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0: lo.pop()
        lo.append(q)
    up = []
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0: up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]
if __name__ == "__main__":
    out = sys.argv[1]; files = sys.argv[2:]
    atlas = Image.open("assets/drakescraft/textures/item/gear3d/ranged_atlas.png").convert("RGBA")
    ims = []
    for f in files:
        m = json.load(open(f)); ims.append(draw(m, atlas, "front")); ims.append(draw(m, atlas, "side"))
    n = len(ims); cols = min(n, 6); rows = (n + cols - 1)//cols
    W = Image.new("RGB", (ims[0].width*cols, ims[0].height*rows))
    for i, im in enumerate(ims): W.paste(im, ((i % cols)*im.width, (i//cols)*im.height))
    W.save(out)
