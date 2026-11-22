#!/usr/bin/env python3
"""Genera texturas 32x32 HD estilo NBQ industrial para la Armadura Hazmat de Slimefun."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw

OUT_DIR = Path(__file__).resolve().parent.parent / "assets/slimefun/textures/item/12_armor"

# Paleta NBQ industrial de alta visibilidad
OUTLINE = (24, 24, 28, 255)
SUIT_HI = (255, 214, 58, 255)
SUIT_MID = (242, 176, 20, 255)
SUIT_SHADE = (196, 124, 12, 255)
SUIT_DARK = (138, 78, 8, 255)
CHARCOAL = (44, 48, 56, 255)
CHARCOAL_HI = (78, 84, 96, 255)
RUBBER = (30, 32, 38, 255)
METAL = (168, 178, 190, 255)
VISOR_DARK = (18, 92, 128, 255)
VISOR_MID = (52, 188, 224, 255)
VISOR_HI = (176, 245, 255, 255)
RAD_GREEN = (98, 240, 118, 255)


def _new() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def make_helmet() -> Image.Image:
    img, d = _new()
    # Capucha / domo NBQ
    d.rounded_rectangle([5, 4, 26, 26], radius=6, fill=SUIT_MID, outline=OUTLINE, width=2)
    d.rectangle([8, 6, 23, 8], fill=SUIT_HI)
    d.rectangle([7, 9, 9, 23], fill=SUIT_HI)
    d.rectangle([22, 9, 24, 23], fill=SUIT_SHADE)
    # Visor panoramico reflectante
    d.rounded_rectangle([8, 10, 23, 18], radius=3, fill=VISOR_DARK, outline=CHARCOAL, width=2)
    d.rectangle([10, 12, 21, 16], fill=VISOR_MID)
    d.line([(10, 12), (16, 12)], fill=VISOR_HI, width=1)
    d.point((11, 13), fill=VISOR_HI)
    d.point((12, 13), fill=VISOR_HI)
    # Respirador / mascara dual NBQ
    d.rounded_rectangle([12, 19, 19, 26], radius=2, fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rectangle([14, 21, 17, 24], fill=CHARCOAL_HI)
    # Filtros laterales
    d.rounded_rectangle([6, 20, 11, 25], radius=2, fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rounded_rectangle([20, 20, 25, 25], radius=2, fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rectangle([7, 22, 10, 23], fill=SUIT_HI)
    d.rectangle([21, 22, 24, 23], fill=SUIT_HI)
    # Sello metalico de cuello
    d.rectangle([8, 26, 23, 28], fill=METAL, outline=OUTLINE, width=1)
    return img


def make_chestplate() -> Image.Image:
    img, d = _new()
    # Mangas
    d.rounded_rectangle([2, 6, 9, 22], radius=2, fill=SUIT_MID, outline=OUTLINE, width=2)
    d.rounded_rectangle([22, 6, 29, 22], radius=2, fill=SUIT_SHADE, outline=OUTLINE, width=2)
    d.rectangle([4, 8, 6, 18], fill=SUIT_HI)
    # Puños hermeticos
    d.rectangle([3, 19, 8, 22], fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rectangle([23, 19, 28, 22], fill=CHARCOAL, outline=OUTLINE, width=1)
    # Torso principal
    d.rounded_rectangle([7, 5, 24, 27], radius=3, fill=SUIT_MID, outline=OUTLINE, width=2)
    d.rectangle([9, 7, 13, 24], fill=SUIT_HI)
    d.rectangle([20, 7, 22, 24], fill=SUIT_SHADE)
    # Cuello / escote
    d.rectangle([12, 5, 19, 8], fill=CHARCOAL, outline=OUTLINE, width=1)
    # Arnes y cremallera sellada
    d.rectangle([15, 9, 16, 26], fill=CHARCOAL)
    # Panel dosimetro / insignia radioactiva en el pecho
    d.rounded_rectangle([10, 11, 21, 17], radius=2, fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rectangle([12, 13, 14, 15], fill=RAD_GREEN)
    d.rectangle([16, 13, 19, 15], fill=SUIT_HI)
    # Cinturon de contencion con franjas negras/amarillas
    d.rectangle([8, 22, 23, 25], fill=CHARCOAL, outline=OUTLINE, width=1)
    for x in (10, 14, 18):
        d.rectangle([x, 23, x + 1, 24], fill=SUIT_HI)
    d.rectangle([14, 22, 17, 25], fill=METAL, outline=OUTLINE, width=1)
    return img


def make_leggings() -> Image.Image:
    img, d = _new()
    # Pretina / cintura
    d.rounded_rectangle([6, 4, 25, 10], radius=2, fill=CHARCOAL, outline=OUTLINE, width=2)
    d.rectangle([13, 5, 18, 9], fill=METAL, outline=OUTLINE, width=1)
    # Pierna izquierda y derecha
    d.rounded_rectangle([6, 9, 15, 28], radius=2, fill=SUIT_MID, outline=OUTLINE, width=2)
    d.rounded_rectangle([16, 9, 25, 28], radius=2, fill=SUIT_SHADE, outline=OUTLINE, width=2)
    d.rectangle([8, 11, 10, 26], fill=SUIT_HI)
    d.rectangle([18, 11, 20, 26], fill=SUIT_MID)
    # Rodilleras reforzadas NBQ
    d.rounded_rectangle([7, 16, 14, 21], radius=1, fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rounded_rectangle([17, 16, 24, 21], radius=1, fill=CHARCOAL, outline=OUTLINE, width=1)
    d.rectangle([9, 18, 12, 19], fill=CHARCOAL_HI)
    d.rectangle([19, 18, 22, 19], fill=CHARCOAL_HI)
    # Sellos de tobillo
    d.rectangle([7, 25, 14, 27], fill=SUIT_DARK)
    d.rectangle([17, 25, 24, 27], fill=SUIT_DARK)
    return img


def make_boots() -> Image.Image:
    img, d = _new()
    # Bota izquierda
    d.rounded_rectangle([5, 11, 14, 26], radius=2, fill=RUBBER, outline=OUTLINE, width=2)
    d.rounded_rectangle([3, 21, 14, 27], radius=2, fill=RUBBER, outline=OUTLINE, width=2)
    d.rectangle([7, 13, 9, 23], fill=CHARCOAL_HI)
    d.rectangle([6, 13, 13, 15], fill=SUIT_MID)  # banda reflectante NBQ
    d.rectangle([4, 25, 13, 27], fill=SUIT_HI)   # suela industrial amarilla
    # Bota derecha
    d.rounded_rectangle([17, 11, 26, 26], radius=2, fill=RUBBER, outline=OUTLINE, width=2)
    d.rounded_rectangle([17, 21, 28, 27], radius=2, fill=RUBBER, outline=OUTLINE, width=2)
    d.rectangle([19, 13, 21, 23], fill=CHARCOAL_HI)
    d.rectangle([18, 13, 25, 15], fill=SUIT_MID)
    d.rectangle([18, 25, 27, 27], fill=SUIT_HI)
    return img


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = {
        "hazmat_helmet.png": make_helmet(),
        "hazmat_chestplate.png": make_chestplate(),
        "hazmat_leggings.png": make_leggings(),
        "hazmat_boots.png": make_boots(),
    }
    for fname, im in outputs.items():
        path = OUT_DIR / fname
        im.save(path, "PNG")
        print(f"OK {path.name} ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    main()
