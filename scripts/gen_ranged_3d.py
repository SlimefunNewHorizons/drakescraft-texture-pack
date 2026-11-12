#!/usr/bin/env python3
"""Modelos 3D de arco, ballesta, tridente y escudo (cuboides, paleta dorada/morada/acero) + atlas vectorial 128 px.
Arco/ballesta: dibujados "de pie" y girados -45 en Z (como las herramientas). Tridente/escudo: se modelan en las
coordenadas de entidad vanilla y se convierten (x,-y,-z)+8 para reutilizar los `display` del jar.
Salida: assets/drakescraft/models/item/gear3d/{bow,bow_pull_0..2,crossbow,crossbow_pull_0..2,crossbow_arrow,
crossbow_firework,trident_in_hand,trident_throwing,shield,shield_blocking}.json + textures/item/gear3d/ranged_atlas.png.
Uso: gen_ranged_3d.py [--jar client.jar]"""
import argparse, json, subprocess, zipfile
from pathlib import Path

JAR = Path.home() / ".local/share/horizon-launcher/versions/nightly-2026-11-05-66f3981/.local/minecraft/26.3/jars/client.jar"
CELLS = {  # (columna, fila) del atlas 4x4; color base, color luz (degradado)
    "wood": (0, 0, "#6b4a2b", "#9a6c3c"), "wood_d": (1, 0, "#3d2814", "#5a3a1e"), "gold": (2, 0, "#d6a93a", "#fff1a8"), "gold_d": (3, 0, "#8a6418", "#c9962c"),
    "string": (0, 1, "#d8d4e8", "#ffffff"), "metal": (1, 1, "#5d6278", "#8a90ab"), "purple": (2, 1, "#7c3aed", "#c9a8ff"), "cyan": (3, 1, "#22c3dc", "#b8f5ff"),
    "white": (0, 2, "#e8e4f0", "#ffffff"), "feather": (1, 2, "#b8b2d0", "#f3efff"), "red": (2, 2, "#d93a3a", "#ff8a8a"), "dark": (3, 2, "#16121e", "#2d2638"),
    "steel": (0, 3, "#aeb7c8", "#eef2fb"), "steel_d": (1, 3, "#6b7488", "#9aa3b8"), "bronze": (2, 3, "#b4682e", "#e6a56a"), "leather": (3, 3, "#4a3220", "#6a4a30"),
}
K = 1.0
TEX = "drakescraft:item/gear3d/ranged_atlas"


def atlas(root):
    cells = ""
    for n, (c, r, c0, c1) in CELLS.items():
        gid = f"g{n}"
        cells += (f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c0}"/></linearGradient>'
                  f'<rect x="{c*4}" y="{r*4}" width="4" height="4" fill="url(#{gid})"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="128" height="128">{cells}</svg>'
    sd = root/"assets/drakescraft/textures/gear/svg_hd"; sd.mkdir(parents=True, exist_ok=True)
    (sd/"ranged_atlas.svg").write_text(svg)
    out = root/"assets/drakescraft/textures/item/gear3d"; out.mkdir(parents=True, exist_ok=True)
    subprocess.run(["rsvg-convert", "-w", "128", "-h", "128", str(sd/"ranged_atlas.svg"), "-o", str(out/"ranged_atlas.png")], check=True)


def box(x1, y1, z1, x2, y2, z2, cell, rot=None):
    c, r = CELLS[cell][:2]
    uv = [c*4 + .5, r*4 + .5, c*4 + 3.5, r*4 + 3.5]
    if K != 1.0:
        x1, y1, z1, x2, y2, z2 = [8 + (v - 8) * K for v in (x1, y1, z1, x2, y2, z2)]
    e = {"from": [round(x1, 3), round(y1, 3), round(z1, 3)], "to": [round(x2, 3), round(y2, 3), round(z2, 3)],
         "faces": {f: {"uv": uv, "texture": "#a"} for f in ("north", "south", "east", "west", "up", "down")}}
    if rot:
        e["rotation"] = {"origin": [8, 8, 8], "axis": "z", "angle": rot}
    return e


def ent(x, y, z, w, h, d, cell):
    """caja en coordenadas de entidad -> espacio de bloque (x,-y,-z)+8"""
    return box(8 + x, 8 - (y + h), 8 - (z + d), 8 + x + w, 8 - y, 8 - z, cell)


def model(elements, display=None, extra=None):
    m = {"textures": {"a": TEX, "particle": TEX}, "elements": elements}
    if display:
        m["display"] = display
    if extra:
        m.update(extra)
    return m


def stairs(p0, p1, th, cell, rot, n=6):
    """segmento p0->p1 aproximado por n cajas de pie (cuerda del arco/ballesta)"""
    out = []
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        xa, ya = p0[0] + (p1[0]-p0[0])*t0, p0[1] + (p1[1]-p0[1])*t0
        xb, yb = p0[0] + (p1[0]-p0[0])*t1, p0[1] + (p1[1]-p0[1])*t1
        out.append(box(min(xa, xb) - th/2, min(ya, yb) - th/2, 7.85, max(xa, xb) + th/2, max(ya, yb) + th/2, 8.15, cell, rot))
    return out


R = -45   # arco: arco hacia arriba-izquierda, cuerda en diagonal
RC = 45   # ballesta: dispara hacia arriba-izquierda (como el sprite vanilla)
def bow(pull):
    e = []
    up = [(3, 10, 5, 12), (3.6, 12, 5.6, 13.8), (4.6, 13.8, 6.6, 15), (6.3, 14.6, 9.2, 15.8)]
    for (a, b, c, d) in up:
        e.append(box(a, b, 7, c, d, 9, "wood", R))
        e.append(box(a, 16-d, 7, c, 16-b, 9, "wood", R))
    e.append(box(2.7, 6, 6.6, 5.3, 10, 9.4, "wood_d", R))        # empuñadura
    e.append(box(2.4, 7.1, 6.4, 5.6, 8.9, 9.6, "gold", R))       # abrazadera
    e.append(box(2.3, 6.1, 6.5, 5.7, 6.6, 9.5, "gold_d", R)); e.append(box(2.3, 9.4, 6.5, 5.7, 9.9, 9.5, "gold_d", R))
    for tip in (15.2, 0.8):                                       # puntas doradas + gema
        e.append(box(8.8, tip-0.8, 6.8, 10.8, tip+0.8, 9.2, "gold", R))
    e.append(box(3.1, 7.6, 9.4, 4.9, 8.4, 9.8, "purple", R))
    nock = (10.4 + (0.0, 2.6, 4.4)[pull], 8)
    for sgn_end in ((10.4, 15.2), (10.4, 0.8)):
        e += stairs(sgn_end, nock, 0.5, "string", R, 6 if pull else 1)
    if pull:
        ax = nock[0]
        e.append(box(1.4, 7.8, 7.8, ax, 8.2, 8.2, "wood_d", R))              # astil
        e.append(box(0.3, 7.5, 7.6, 1.6, 8.5, 8.4, "steel", R))              # punta
        e.append(box(ax-0.2, 7.5, 7.5, ax+1.0, 8.5, 8.5, "feather", R))      # plumas
    return model(e, DISP["bow"])


def crossbow(pull, load):
    global K
    K = 0.8
    e = []
    e.append(box(6.6, 0.8, 7, 9.4, 11.2, 9, "wood", RC))
    e.append(box(6.2, 0.2, 6.8, 9.8, 1.6, 9.2, "gold", RC))                    # culata
    e.append(box(6.4, 3.0, 6.8, 9.6, 6.0, 9.2, "wood_d", RC))                  # empuñadura
    e.append(box(7.4, 4.0, 9, 8.6, 5.2, 9.8, "bronze", RC))                    # gatillo
    e.append(box(7.4, 8.0, 9, 8.6, 9.4, 9.4, "purple", RC))                    # gema
    e.append(box(7.6, 6.0, 9, 8.4, 14.0, 9.6, "steel_d", RC))                  # carril
    e.append(box(1.6, 11.4, 6.8, 14.4, 13.2, 9.2, "metal", RC))                # arco (prod)
    for sx in (0.8, 13.8):
        e.append(box(sx, 12.6, 6.9, sx+1.4, 14.8, 9.1, "gold", RC))            # puntas
    for bx in (4.4, 10.6):
        e.append(box(bx, 11.2, 6.6, bx+1.0, 13.4, 9.4, "gold_d", RC))
    ny = (14.5, 12.4, 10.4, 8.6)[pull]
    nock = (8, ny)
    for tip in ((1.5, 14.6), (14.5, 14.6)):
        e += stairs(tip, nock, 0.5, "string", RC, 5)
    if load == "arrow":
        e.append(box(7.8, 8.8, 8.2, 8.2, 15.4, 8.8, "wood_d", RC)); e.append(box(7.5, 15.2, 8.0, 8.5, 16.6, 9.0, "steel", RC))
        e.append(box(7.5, 8.4, 8.1, 8.5, 9.6, 8.9, "feather", RC))
    elif load == "rocket":
        e.append(box(7.2, 8.6, 8.0, 8.8, 14.0, 9.6, "red", RC)); e.append(box(7.2, 14.0, 8.0, 8.8, 15.4, 9.6, "gold", RC))
        e.append(box(7.8, 7.4, 8.4, 8.2, 8.6, 8.8, "wood_d", RC))
    K = 1.0
    return model(e, DISP["crossbow"])


def trident(extra_display):
    e = [ent(-0.5, 2, -0.5, 1, 25, 1, "wood_d"),
         ent(-0.95, 2.0, -0.95, 1.9, 1.4, 1.9, "gold"), ent(-0.95, 12.0, -0.95, 1.9, 1.2, 1.9, "gold"), ent(-0.95, 22.0, -0.95, 1.9, 1.2, 1.9, "gold"),
         ent(-1.0, 26.2, -1.0, 2.0, 1.8, 2.0, "purple"),
         ent(-1.5, 0, -0.5, 3, 2, 1, "steel"), ent(-1.9, 0.3, -0.9, 3.8, 0.8, 1.8, "gold"),
         ent(-2.5, -3, -0.5, 1, 4, 1, "steel"), ent(-0.5, -4.6, -0.5, 1, 4.6, 1, "steel"), ent(1.5, -3, -0.5, 1, 4, 1, "steel"),
         ent(-3.1, -1.4, -0.5, 0.6, 1.6, 1, "steel_d"), ent(2.5, -1.4, -0.5, 0.6, 1.6, 1, "steel_d"),
         ent(-0.25, -3.6, -0.7, 0.5, 3.6, 1.4, "cyan")]
    return model(e, extra_display, {"gui_light": "front"})


def shield(blocking):
    e = [ent(-6, -11, -2, 12, 22, 1, "metal"),
         ent(-6.4, -11.4, -2.4, 12.8, 1.0, 1.8, "gold"), ent(-6.4, 10.4, -2.4, 12.8, 1.0, 1.8, "gold"),
         ent(-6.4, -11.4, -2.4, 1.0, 22.8, 1.8, "gold"), ent(5.4, -11.4, -2.4, 1.0, 22.8, 1.8, "gold"),
         ent(-1.0, -9.0, -2.5, 2.0, 18.0, 1.9, "gold_d"), ent(-5.0, -1.0, -2.5, 10.0, 2.0, 1.9, "gold_d"),
         ent(-2.2, -2.2, -2.8, 4.4, 4.4, 2.0, "purple"), ent(-1.0, -1.0, -3.0, 2.0, 2.0, 2.2, "cyan"),
         ent(-1, -3, -1, 2, 6, 6, "leather")]
    return model(e, DISP["shield_blocking" if blocking else "shield"], {"gui_light": "front"})


DISP = {}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--jar", type=Path, default=JAR); a = ap.parse_args()
    root = Path(".")
    with zipfile.ZipFile(a.jar) as z:
        for n in ("bow", "crossbow", "trident_in_hand", "trident_throwing", "shield", "shield_blocking"):
            DISP[n] = json.loads(z.read(f"assets/minecraft/models/item/{n}.json"))["display"]
    atlas(root)
    out = root/"assets/drakescraft/models/item/gear3d"; out.mkdir(parents=True, exist_ok=True)
    M = {"bow": bow(0), "bow_pull_0": bow(0), "bow_pull_1": bow(1), "bow_pull_2": bow(2),
         "crossbow": crossbow(0, None), "crossbow_pull_0": crossbow(0, None), "crossbow_pull_1": crossbow(1, None), "crossbow_pull_2": crossbow(3, None),
         "crossbow_arrow": crossbow(3, "arrow"), "crossbow_firework": crossbow(3, "rocket"),
         "trident_in_hand": trident(DISP["trident_in_hand"]), "trident_throwing": trident(DISP["trident_throwing"]),
         "shield": shield(False), "shield_blocking": shield(True)}
    for n, m in M.items():
        (out/f"{n}.json").write_text(json.dumps(m, indent=1))
    print(len(M), "modelos")


if __name__ == "__main__":
    main()
