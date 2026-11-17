#!/usr/bin/env python3
"""Generador de modelos 3D y relieve para el arsenal griego de DrakesCraft.

Permite dos modos:
1. Modo 'scale' (lo mas rapido): Genera template handheld_thick con grosor Z ampliado (2.4x)
   para que la textura 2D existente tenga volumen solido en mano sin tocar geometria.
2. Modo 'relief' (relieve real escalonado): Analiza los PNGs 32x32 existentes y genera
   modelos JSON con cuboides 3D reales (filo afilado, cuerpo medio, lomo/guarda/pomo grueso)
   mapeados 1:1 a las texturas existentes.

Uso:
  python3 gen_greek_relief_3d.py --mode scale   (por defecto)
  python3 gen_greek_relief_3d.py --mode relief
"""
import argparse
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "assets/drakescraft/models/item/greek"
TEXTURES_DIR = ROOT / "assets/drakescraft/textures/item/greek"
TEMPLATE_DIR = ROOT / "assets/drakescraft/models/item"

MATERIALS = ["wood", "stone", "iron", "gold", "diamond", "netherite"]
WEAPONS = ["labrys", "xiphos"]

DISPLAY_THICK = {
    "thirdperson_righthand": {
        "rotation": [0, -90, 55],
        "translation": [0, 4.0, 0.5],
        "scale": [0.85, 0.85, 2.5]
    },
    "thirdperson_lefthand": {
        "rotation": [0, 90, -55],
        "translation": [0, 4.0, 0.5],
        "scale": [0.85, 0.85, 2.5]
    },
    "firstperson_righthand": {
        "rotation": [0, -90, 25],
        "translation": [1.13, 3.2, 1.13],
        "scale": [0.68, 0.68, 2.4]
    },
    "firstperson_lefthand": {
        "rotation": [0, 90, -25],
        "translation": [1.13, 3.2, 1.13],
        "scale": [0.68, 0.68, 2.4]
    },
    "ground": {
        "rotation": [0, 0, 0],
        "translation": [0, 2, 0],
        "scale": [0.5, 0.5, 1.5]
    },
    "gui": {
        "rotation": [0, 0, 0],
        "translation": [0, 0, 0],
        "scale": [1, 1, 1]
    },
    "fixed": {
        "rotation": [0, 180, 0],
        "translation": [0, 0, 0],
        "scale": [1, 1, 1]
    }
}

DISPLAY_RELIEF_3D = {
    "thirdperson_righthand": {
        "rotation": [0, -90, 55],
        "translation": [0, 4.0, 0.5],
        "scale": [0.85, 0.85, 0.85]
    },
    "thirdperson_lefthand": {
        "rotation": [0, 90, -55],
        "translation": [0, 4.0, 0.5],
        "scale": [0.85, 0.85, 0.85]
    },
    "firstperson_righthand": {
        "rotation": [0, -90, 25],
        "translation": [1.13, 3.2, 1.13],
        "scale": [0.68, 0.68, 0.68]
    },
    "firstperson_lefthand": {
        "rotation": [0, 90, -25],
        "translation": [1.13, 3.2, 1.13],
        "scale": [0.68, 0.68, 0.68]
    },
    "ground": {
        "rotation": [0, 0, 0],
        "translation": [0, 2, 0],
        "scale": [0.5, 0.5, 0.5]
    },
    "gui": {
        "rotation": [0, 0, 0],
        "translation": [0, 0, 0],
        "scale": [1, 1, 1]
    },
    "fixed": {
        "rotation": [0, 180, 0],
        "translation": [0, 0, 0],
        "scale": [1, 1, 1]
    }
}


def setup_thick_parent():
    """Crea handheld_thick.json y actualiza los 12 modelos para heredar de el."""
    parent_path = TEMPLATE_DIR / "handheld_thick.json"
    parent_data = {
        "parent": "minecraft:item/handheld",
        "credit": "DrakesCraft Handheld Thick 3D Template by JackStar",
        "display": DISPLAY_THICK
    }
    parent_path.write_text(json.dumps(parent_data, indent=2) + "\n", encoding="utf-8")
    print(f"Creado template base: {parent_path.relative_to(ROOT)}")

    updated = 0
    for weapon in WEAPONS:
        for mat in MATERIALS:
            model_path = MODELS_DIR / f"{weapon}_{mat}.json"
            if model_path.exists():
                data = json.loads(model_path.read_text(encoding="utf-8"))
                data["parent"] = "drakescraft:item/handheld_thick"
                model_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
                updated += 1
    print(f"Actualizados {updated} modelos griegos con grosor Z solido en mano.")


def compute_distances(im):
    w, h = im.size
    dist = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if im.getpixel((x, y))[3] > 128:
                dist[y][x] = 1
    for step in range(1, 4):
        for y in range(h):
            for x in range(w):
                if dist[y][x] == step:
                    all_neigh = True
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            ny, nx = y + dy, x + dx
                            if not (0 <= ny < h and 0 <= nx < w and dist[ny][nx] >= step):
                                all_neigh = False
                    if all_neigh:
                        dist[y][x] = step + 1
    return dist


def generate_relief_elements(png_path):
    im = Image.open(png_path)
    w, h = im.size
    scale_coord = 16.0 / w
    dist = compute_distances(im)

    z_map = {
        1: (7.5, 8.5),
        2: (7.1, 8.9),
        3: (6.6, 9.4)
    }

    grid = [[min(dist[y][x], 3) for x in range(w)] for y in range(h)]
    visited = [[False] * w for _ in range(h)]
    elements = []

    for y in range(h):
        for x in range(w):
            d = grid[y][x]
            if d > 0 and not visited[y][x]:
                x2 = x
                while x2 < w and grid[y][x2] == d and not visited[y][x2]:
                    x2 += 1
                rw = x2 - x
                y2 = y
                while y2 < h:
                    can_expand = True
                    for tx in range(x, x2):
                        if grid[y2][tx] != d or visited[y2][tx]:
                            can_expand = False
                            break
                    if not can_expand:
                        break
                    y2 += 1
                rh = y2 - y

                for ty in range(y, y2):
                    for tx in range(x, x2):
                        visited[ty][tx] = True

                z_from, z_to = z_map[d]
                mc_x_from = round(x * scale_coord, 3)
                mc_x_to = round((x + rw) * scale_coord, 3)
                mc_y_from = round((h - (y + rh)) * scale_coord, 3)
                mc_y_to = round((h - y) * scale_coord, 3)

                uv_x1 = round(x * (16.0 / w), 2)
                uv_x2 = round((x + rw) * (16.0 / w), 2)
                uv_y1 = round(y * (16.0 / h), 2)
                uv_y2 = round((y + rh) * (16.0 / h), 2)

                el = {
                    "from": [mc_x_from, mc_y_from, z_from],
                    "to": [mc_x_to, mc_y_to, z_to],
                    "faces": {
                        "north": {"uv": [uv_x2, uv_y1, uv_x1, uv_y2], "texture": "#layer0"},
                        "south": {"uv": [uv_x1, uv_y1, uv_x2, uv_y2], "texture": "#layer0"},
                        "east": {"uv": [uv_x2, uv_y1, uv_x2, uv_y2], "texture": "#layer0"},
                        "west": {"uv": [uv_x1, uv_y1, uv_x1, uv_y2], "texture": "#layer0"},
                        "up": {"uv": [uv_x1, uv_y1, uv_x2, uv_y1], "texture": "#layer0"},
                        "down": {"uv": [uv_x1, uv_y2, uv_x2, uv_y2], "texture": "#layer0"}
                    }
                }
                elements.append(el)
    return elements


def setup_relief_models():
    """Genera modelos 3D con relieve escalonado para cada arma y material."""
    total = 0
    for weapon in WEAPONS:
        for mat in MATERIALS:
            png_path = TEXTURES_DIR / f"{weapon}_{mat}.png"
            if not png_path.exists():
                continue
            elements = generate_relief_elements(png_path)
            model_data = {
                "credit": f"DrakesCraft Greek Arsenal 3D Relief - {weapon}_{mat} by JackStar",
                "textures": {
                    "layer0": f"drakescraft:item/greek/{weapon}_{mat}",
                    "particle": f"drakescraft:item/greek/{weapon}_{mat}"
                },
                "display": DISPLAY_RELIEF_3D,
                "elements": elements
            }
            out_file = MODELS_DIR / f"{weapon}_{mat}.json"
            out_file.write_text(json.dumps(model_data, indent=2) + "\n", encoding="utf-8")
            total += 1
    print(f"Generados {total} modelos 3D con relieve escalonado en {MODELS_DIR.relative_to(ROOT)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["scale", "relief"], default="scale",
                        help="'scale': Grosor solido instantaneo via JSON. 'relief': Esculpido 3D multinivel.")
    args = parser.parse_args()

    if args.mode == "scale":
        setup_thick_parent()
    else:
        setup_relief_models()


if __name__ == "__main__":
    main()
