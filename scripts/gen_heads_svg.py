#!/usr/bin/env python3
"""Cabezas Slimefun (player_head) DrakesCraft: pixel-art 16x16 griego/dorado/morado/galactico/tech.

Por cada item de la tabla ITEMS genera:
  - SVG 16x16 (un rect por pixel)       assets/drakescraft/textures/heads/svg/<id>.svg
  - PNG (rsvg-convert)                  assets/drakescraft/textures/heads/<id>.png
  - modelo item/generated               assets/minecraft/models/slimefun/drakes_heads/<id>.json
  - case por custom_name en             assets/minecraft/items/player_head.json (y overlay_*/ si existen)
Idempotente: borra los cases propios (modelo slimefun/drakes_heads/) y los vuelve a insertar.
Uso (desde la raiz del pack): python3 scripts/gen_heads_svg.py [--no-png]
Para agregar una cabeza: una linea en ITEMS  ID|&nombre en legacy|contenedor|glifo|tema(opcional)
El nombre debe ser IDENTICO al display name de Slimefun (el pack empareja por custom_name + color).
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

OUT = "#0d0a14"
THEMES = {  # base, luz, sombra
    "gold":   ("#e0ad3a", "#fff1a8", "#8f6a1c"),
    "purple": ("#7c3aed", "#c4a1ff", "#431f8a"),
    "dark":   ("#3a3350", "#8b7fb0", "#16121e"),
    "cyan":   ("#22b8cf", "#a5f3fc", "#0e6c80"),
    "green":  ("#34d399", "#bbf7d0", "#0f7a53"),
    "red":    ("#e11d48", "#fda4af", "#7f1030"),
    "blue":   ("#3b82f6", "#bfdbfe", "#1e3a8a"),
    "white":  ("#d5dbea", "#ffffff", "#7b8399"),
    "pink":   ("#d946ef", "#f5c2ff", "#86198f"),
    "orange": ("#f97316", "#fed7aa", "#9a3412"),
    "gray":   ("#8d93a6", "#c9cee0", "#4b5064"),
}
CODE_THEME = dict(zip("0123456789abcdef", "dark blue green cyan red purple gold gray dark blue green cyan red pink gold white".split()))
CODE_COLOR = dict(zip("0123456789abcdef", (
    "black dark_blue dark_green dark_aqua dark_red dark_purple gold gray dark_gray blue green aqua red light_purple yellow white").split()))
STONE = "#2d2638"
SCREEN = "#16121e"
STEEL = ("#aeb7c8", "#eef2fb", "#6b7488")

GLYPHS = {
    "bolt": ["...XXX.", "..XXX..", ".XXX...", "XXXXXX.", "..XXX..", ".XX....", "X......"],
    "heart": [".XX.XX.", "XXXXXXX", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."],
    "snow": ["...X...", "X..X..X", ".X.X.X.", "XXXXXXX", ".X.X.X.", "X..X..X", "...X..."],
    "star4": ["...X...", "...X...", "..XXX..", "XXXXXXX", "..XXX..", "...X...", "...X..."],
    "flame": ["...X...", "..XX...", "..XXX..", ".XXXXX.", ".XXXXXX", ".XXXXX.", "..XXX.."],
    "ghost": ["..XXX..", ".XXXXX.", "XX.X.XX", "XXXXXXX", "XXXXXXX", "XXXXXXX", "X.X.X.X"],
    "drop": ["...X...", "..XXX..", "..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", ".XXXXX."],
    "up": ["...X...", "..XXX..", ".XXXXX.", "XXXXXXX", "..XXX..", "..XXX..", "..XXX.."],
    "gear": [".X.X.X.", ".XXXXX.", "XXX.XXX", ".X...X.", "XXX.XXX", ".XXXXX.", ".X.X.X."],
    "eye": [".......", "..XXX..", ".X...X.", "XX.X.XX", ".X...X.", "..XXX..", "......."],
    "skull": [".XXXXX.", "XXXXXXX", "X..X..X", "XXXXXXX", ".XXXXX.", ".X.X.X.", ".X.X.X."],
    "ring": ["...X...", "..XXX..", ".X...X.", ".X...X.", ".X...X.", "..XXX..", "......."],
    "swords": ["X.....X", ".X...X.", "..X.X..", "...X...", "..XXX..", ".X...X.", "XX...XX"],
    "cloud": [".......", "..XX...", ".XXXX.X", "XXXXXXX", "XXXXXXX", ".XXXXX.", "......."],
    "spiral": ["XXXXXXX", "X.....X", "X.XXX.X", "X.X.X.X", "X.X...X", "X.XXXXX", "X......"],
    "dish": ["X.....X", "XX...XX", ".XXXXX.", "..XXX..", "...X.X.", "...X..X", "..XXX.."],
    "horn": [".....XX", "...XXXX", "..XXXX.", ".XXXX..", "XXXX...", "XXX....", ".XX...."],
    "potion": ["..XXX..", "...X...", "..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", ".XXXXX."],
    "helmet": ["..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", "XXX.XXX", "XX...XX", "XX...XX"],
    "mushroom": ["..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", "...X...", "...X...", "..XXX.."],
    "jar": ["..XXX..", ".XXXXX.", "..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", ".XXXXX."],
    "sack": ["..X.X..", "...X...", "..XXX..", ".XXXXX.", "XXXXXXX", "XXXXXXX", ".XXXXX."],
    "coin": ["..XXX..", ".X...X.", "X..X..X", "X.XXX.X", "X..X..X", ".X...X.", "..XXX.."],
    "plus": ["..XXX..", "..XXX..", "XXXXXXX", "XXXXXXX", "XXXXXXX", "..XXX..", "..XXX.."],
    "shield": ["XXXXXXX", "XXXXXXX", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."],
    "atom": ["...X...", ".X.X.X.", "..XXX..", "XXXXXXX", "..XXX..", ".X.X.X.", "...X..."],
    "thermo": ["...X...", "...X...", "...X...", "...X...", "..XXX..", ".XXXXX.", "..XXX.."],
    "sun": ["X..X..X", ".X.X.X.", "..XXX..", "XXXXXXX", "..XXX..", ".X.X.X.", "X..X..X"],
    "chip": ["X.X.X.X", ".XXXXX.", "XXXXXXX", ".XXXXX.", "XXXXXXX", ".XXXXX.", "X.X.X.X"],
    "grid": ["X.X.X.X", ".......", "X.X.X.X", ".......", "X.X.X.X", ".......", "X.X.X.X"],
    "funnel": ["XXXXXXX", ".XXXXX.", "..XXX..", "...X...", "...X...", "...X...", "......."],
    "squeeze": ["...X...", "X..X..X", "XX.X.XX", "XXXXXXX", "XX.X.XX", "X..X..X", "...X..."],
    "pick": [".XXXXX.", "X..X..X", "...X...", "...X...", "...X...", "...X...", "...X..."],
}


def rot(gl):  # 90 grados horario
    return ["".join(gl[len(gl) - 1 - r][c] for r in range(len(gl))) for c in range(len(gl[0]))]


GLYPHS["right"] = rot(GLYPHS["up"])
GLYPHS["down"] = rot(GLYPHS["right"])
GLYPHS["left"] = rot(GLYPHS["down"])

# ---------------------------------------------------------------- primitivas


def rect(g, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[(x, y)] = c


def bevel(g, x0, y0, x1, y1, th):
    b, l, d = THEMES[th]
    rect(g, x0, y0, x1, y1, b)
    rect(g, x0, y0, x1, y0, l)
    rect(g, x0, y0, x0, y1, l)
    rect(g, x0, y1, x1, y1, d)
    rect(g, x1, y0, x1, y1, d)
    g[(x0, y1)] = b
    g[(x1, y0)] = b


def glyph(g, name, x0, y0, c):
    for r, row in enumerate(GLYPHS[name]):
        for k, ch in enumerate(row):
            if ch == "X":
                g[(x0 + k, y0 + r)] = c


def slab(g, th, gl):
    b, l, d = THEMES[th]
    spans = {2: (4, 11), 3: (3, 12), 12: (3, 12), 13: (4, 11)}
    cells = set()
    for y in range(2, 14):
        a, z = spans.get(y, (2, 13))
        for x in range(a, z + 1):
            cells.add((x, y))
    for (x, y) in cells:
        edge = any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        g[(x, y)] = (l if (x + y) < 15 else b) if edge else STONE
    for (x, y) in ((4, 3), (11, 3), (4, 12), (11, 12)):
        g[(x, y)] = d
    if gl:
        glyph(g, gl, 4, 4, l)


def cube(g, th, gl):
    b, l, d = THEMES[th]
    bevel(g, 2, 2, 13, 13, th)
    for p in ((3, 3), (12, 3), (3, 12), (12, 12)):
        g[p] = STEEL[1]
    if gl:
        rect(g, 4, 4, 11, 11, SCREEN)
        glyph(g, gl, 4, 4, l)
    else:
        rect(g, 5, 5, 10, 10, d)
        rect(g, 6, 6, 9, 9, b)
        g[(6, 6)] = l


def orb(g, th, gl):
    b, l, d = THEMES[th]
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            if dx * dx + dy * dy <= 6.3 ** 2:
                t = (dx + dy) / 8.9
                g[(x, y)] = l if t < -0.55 else (d if t > 0.45 else b)
    g[(5, 4)] = g[(4, 5)] = "#ffffff"
    if gl:
        glyph(g, gl, 4, 4, SCREEN if th != "dark" else l)


def gem(g, th, gl):
    b, l, d = THEMES[th]
    rows = {2: (5, 10), 3: (3, 12), 4: (2, 13), 5: (3, 12), 6: (4, 11), 7: (5, 10), 8: (5, 10), 9: (6, 9), 10: (6, 9), 11: (7, 8), 12: (7, 8)}
    for y, (a, z) in rows.items():
        for x in range(a, z + 1):
            c = l if y <= 3 else (b if x < 8 else d)
            if y <= 4 and x in (7, 8):
                c = "#ffffff"
            g[(x, y)] = c
    rect(g, 3, 4, 12, 4, b)
    g[(2, 4)] = l
    g[(13, 4)] = d


def can(g, th, gl):
    b, l, d = THEMES[th]
    rect(g, 4, 2, 11, 13, b)
    rect(g, 11, 4, 11, 11, d)
    for y in (2, 3, 12, 13):
        rect(g, 4, y, 11, y, STEEL[0] if y in (2, 12) else STEEL[2])
    g[(4, 2)] = g[(5, 2)] = STEEL[1]
    rect(g, 6, 1, 9, 1, STEEL[2])
    if gl:
        glyph(g, gl, 4, 4, l)


def panel(g, th, tier):
    b, l, d = THEMES[th]
    bevel(g, 1, 2, 14, 12, th)
    for y0 in (3, 7):
        for x0 in (2, 6, 10):
            rect(g, x0, y0, x0 + 3, y0 + 2, "#1d3a8a")
            g[(x0, y0)] = "#60a5fa"
            g[(x0 + 1, y0 + 1)] = "#2563eb"
    for i in range(8):
        g[(3 + i, 11)] = l if i < tier else d
    rect(g, 7, 13, 8, 14, STEEL[2])
    rect(g, 5, 14, 10, 14, STEEL[0])


def cell(g, th, n):
    b, l, d = THEMES[th]
    rect(g, 3, 4, 12, 14, d)
    rect(g, 3, 4, 3, 14, b)
    rect(g, 6, 2, 9, 3, STEEL[0])
    rect(g, 7, 2, 8, 2, STEEL[1])
    for i in range(12):
        cx, cy = 4 + (i % 3) * 3, 5 + (i // 3) * 3
        # n celdas encendidas de abajo arriba
        lit = (11 - i) < n
        rect(g, cx, cy, cx + 1, cy + 1, b if lit else "#1b1526")
        if lit:
            g[(cx, cy)] = l


CONT = {"slab": slab, "cube": cube, "orb": orb, "gem": gem, "can": can}

# ---------------------------------------------------------------- datos
# ID|nombre legacy|contenedor|glifo|tema
ITEMS = """
ADVANCED_GEO_MINER|&cAdvanced &fGeoMiner|cube|pick|
ADVANCED_NETHER_STAR_REACTOR|&cAdvanced Nether Star Reactor|cube|star4|purple
ADVANCED_SOLAR_GEN|&aAdvanced Solar Generator|panel|6|green
AIR_QUALITY_METER|&bMedidor de Calidad del Aire|cube|cloud|
ATMOSPHERIC_HARVESTER|&fAtmospheric Harvester|cube|cloud|
BOOSTED_CARBONADO|&dBoosted Carbonado|gem||
CHEST_TERMINAL|&3CT Access Terminal|cube|grid|
CINNABARITE|&cCinabrio|gem||
COMMAND_HUB|&eCommand Hub|cube|chip|
COMMAND_HUB_ENGINE|&cCommand Hub Engine|cube|gear|
CORONALIS_ANTENNA_DISH|&dPlato de Antena Parabólica|slab|dish|
CORONALIS_CONTROL_CONSOLE|&6Consola de Control del Observatorio|cube|chip|
CORONALIS_DATA_CELL|&bCelda de Datos Celestes|can|grid|
CORONALIS_PID_CONTROLLER|&dControlador PID del Vacío|cube|spiral|
CORONALIS_RADIO_TELESCOPE|&6Escucha del Vacío — Antena|slab|dish|
CORONALIS_RECEIVER|&dReceptor de Radiofrecuencia (1mm)|cube|star4|
CORONALIS_RECORD_DISCOVERED|&e&lEco de Fase Coronalis|orb|star4|
CT_EXPORT_BUS|&3CT Export Bus|slab|right|
CT_IMPORT_BUS|&3CT Import Bus|slab|left|
CT_PANEL|&3CT Illuminated Panel|cube|sun|
DAXI_ABSORPTION|&aDaxi (A)|orb|heart|gold
DAXI_FORTITUDE|&aDaxi (F)|orb|shield|gray
DAXI_REGENERATION|&aDaxi (R)|orb|plus|pink
DAXI_SATURATION|&aDaxi (H)|orb|drop|
DAXI_STRENGTH|&aDaxi (S)|orb|swords|red
ENDER_CHEST_EXTRACTION_NODE|&6Ender Chest Extraction Node|cube|up|purple
ENDER_CHEST_INSERTION_NODE|&bEnder Chest Insertion Node|cube|down|purple
FN_ASSEMBLY_STATION|&dFN Assembly Station|cube|gear|dark
FN_MAGIC_ALTAR|&dFN Magic Altar|slab|star4|
FN_METAL_SCRAPS|&dMetal Scrap|gem||gray
FN_SCRAP_RECYCLER|&dFN Scrap Recycler|cube|spiral|gray
FN_MACHINERY_BASIC_MACHINE_BLOCK|&dBasic Machine Block|cube||gray
FN_MACHINERY_HIGHTECH_MACHINE_BLOCK|&dHigh Tech Machine Block|cube|chip|
FN_MACHINERY_COMPONENT_PART|&dComponent Part|cube|chip|cyan
FN_MACHINERY_COMPRESSOR_PART|&dCompressor Part|cube|squeeze|
FN_MACHINERY_CONDENSER_PART|&dCondenser Part|cube|drop|blue
FN_MACHINERY_DOWNGRADER_PART|&dDowngrader Part|cube|down|
FN_MACHINERY_FUNNEL_PART|&dFunnel Part|cube|funnel|
FN_MACHINERY_GEAR_PART|&dGear Part|cube|gear|gold
FN_MACHINERY_MACHINE_PART|&dMachine Part|cube|gear|cyan
FN_MACHINERY_MOTOR_SWITCH|&dMotor Switch|cube|bolt|orange
FN_MACHINERY_POWER_COMPONENT|&dPower Component|cube|bolt|
FN_MACHINERY_RECYCLER_PART|&dRecycler Part|cube|spiral|green
FN_MACHINERY_THREAD_PART|&dThread Part|cube|spiral|
FN_MAGICAL_ITEMS_AGILITY_RUNE|&eAgility Rune|slab|up|
FN_MAGICAL_ITEMS_CLOUD_RUNE|&3Cloud Rune|slab|cloud|
FN_MAGICAL_ITEMS_HEART_RUNE|&dHeart Rune|slab|heart|
FN_MAGICAL_ITEMS_ICE_RUNE|&bIce Rune|slab|snow|
FN_MAGICAL_ITEMS_INTELLECT_RUNE|&9Intellect Rune|slab|eye|
FN_MAGICAL_ITEMS_LINGER_RUNE|&2Linger Rune|slab|spiral|
FN_MAGICAL_ITEMS_PESTILENCE_RUNE|&aPestilence Rune|slab|skull|
FN_MAGICAL_ITEMS_POWER_RUNE|&9Power Rune|slab|bolt|
FN_MAGICAL_ITEMS_SPARKLING_RUNE|&eSparkling Rune|slab|sun|
FN_MAGICAL_ITEMS_SPIRAL_FIRE_RUNE|&cSpiral Fire Rune|slab|flame|
FN_MAGICAL_ITEMS_SPIRIT_RUNE|&fSpirit Rune|slab|ghost|
FN_MAGICAL_ITEMS_UNBIND_RUNE|&6Unbind Rune|slab|ring|
FRAMED_URANIUM|&dFramed Uranium|gem||green
FUSION_REACTOR|&fFusion Reactor|cube|atom|
HUMAN_SKULL|&cHuman Skull|orb|skull|white
INFINITY_CAPACITOR|&bInfinite Capacitor|can|bolt|
VOID_CAPACITOR|&8Void Capacitor|can|bolt|
PANDORAS_BOX|&5Pandora"s Box|cube|star4|
RTG_1|&4Radioisotope Thermoelectric Generator I|can|atom|
RTG_2|&4Radioisotope Thermoelectric Generator II|can|atom|orange
STARDUST_METEOR|&6Stardust Meteor|orb|star4|
STEEL_ROTOR|&bSteel Rotor|orb|gear|white
THERMOMETER|&eTermómetro|can|thermo|
QUIRP_UP|&aQuirp Up|slab|up|
QUIRP_DOWN|&aQuirp Down|slab|down|
QUIRP_LEFT|&aQuirp Left|slab|left|
QUIRP_RIGHT|&aQuirp Right|slab|right|
QUIRPCONDENSATE|&5Quirp Condensate|orb|spiral|
QUIRP_SCATTERER|&cQuirp Scatterer|slab|star4|
ZOT_UP|&aZot Up|slab|up|
ZOT_DOWN|&aZot Down|slab|down|
ZOT_LEFT|&aZot Left|slab|left|
ZOT_RIGHT|&aZot Right|slab|right|
ZOT_UP_2|&cZot Up|slab|up|
ZOT_DOWN_2|&cZot Down|slab|down|
ZOT_LEFT_2|&cZot Left|slab|left|
ZOT_RIGHT_2|&cZot Right|slab|right|
COMMON_RELIC_CTHONIAN_PEARL|&aCthonian Pearl|orb||
COMMON_RELIC_FISHING_SACK|&aFishing Sack|slab|sack|
COMMON_RELIC_HEALING_POTION|&aHealing Potion|slab|potion|
COMMON_RELIC_LEATHER_HELMET|&aLeather helmet|slab|helmet|orange
COMMON_RELIC_MUSHROOM|&aMushroom|slab|mushroom|
COMMON_RELIC_PETTY_MARBLE_BLOCK|&aPetty Marble Block|cube||white
COMMON_RELIC_RING_OF_SUFFERING|&aRing of Suffering|slab|ring|
COMMON_RELIC_VOIDER|&aCommon Relic Voider|slab|spiral|
UNCOMMON_RELIC_AGED_WINE|&7Aged Wine|slab|potion|red
UNCOMMON_RELIC_BLUE_GLOWSTONE|&7Blue Glowstone|gem||blue
UNCOMMON_RELIC_CTHONIAN_TOKEN|&7Cthonian Token|slab|coin|gold
UNCOMMON_RELIC_GRAY_BERRY|&7Gray Berry|orb||
UNCOMMON_RELIC_PINK_SALT|&7Pink Salt|gem||pink
UNCOMMON_RELIC_SKULL_HAT|&7Skull Hat|slab|skull|
UNCOMMON_RELIC_TANZANITE_BLOCK|&7Tanzanite Block|cube||purple
UNCOMMON_RELIC_VOIDER|&7Uncommon Relic Voider|slab|spiral|
RARE_RELIC_BLAZE_ASHES|&9Blaze Ashes|slab|flame|orange
RARE_RELIC_CERULEAN_GEM|&9Cerulean Gem|gem||
RARE_RELIC_CROSSED_SWORDS|&9Crossed Swords|slab|swords|
RARE_RELIC_GOLDEN_JAR|&9Golden Jar|slab|jar|gold
RARE_RELIC_HORN_OF_TAURUS|&9Horn of Taurus|slab|horn|gold
RARE_RELIC_MARRIAGE_RING|&9Marriage Ring|slab|ring|pink
RARE_RELIC_TERRACOTTA_POT|&9Terracotta Pot|slab|jar|orange
RARE_RELIC_VOIDER|&9Rare Relic Voider|slab|spiral|
EPIC_RELIC_BOTTLE_O_POWER|&dBottle o Power|slab|potion|green
EPIC_RELIC_FERVOR_HELMET|&dFervor Helmet|slab|helmet|orange
EPIC_RELIC_FLAWLESS_AQUA_GEM|&dFlawless Aqua Gem|gem||cyan
EPIC_RELIC_LUMINOUS_PEARL|&dLuminous Pearl|orb||white
EPIC_RELIC_THUNDER_IN_A_BOTTLE|&dThunder In A Bottle|orb|bolt|blue
EPIC_RELIC_VALIANT_TALISMAN|&dValiant Talisman|slab|shield|gold
EPIC_RELIC_VOIDER|&dEpic Relic Voider|slab|spiral|
LEGENDARY_RELIC_EYE_OF_SAURON|&6Eye of Sauron|orb|eye|red
LEGENDARY_RELIC_GLAZING_PEARL|&6Glazing Pearl|orb||
LEGENDARY_RELIC_MAGMA_GAUNTLET|&6Magma Gauntlet|slab|flame|red
LEGENDARY_RELIC_MYSTERIOUS_HOLOCRON|&6Mysterious Holocron|cube|star4|cyan
LEGENDARY_RELIC_SAPPHIRE_RING|&6Sapphire Ring|slab|ring|blue
LEGENDARY_RELIC_SKULL_OF_PROMETHEUS|&6Skull of Prometheus|orb|skull|
LEGENDARY_RELIC_VOIDER|&6Legendary Relic Voider|slab|spiral|
"""
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
TIER_THEMES = ["gray", "white", "green", "cyan", "blue", "purple", "pink", "gold"]
POW_THEMES = ["gray", "white", "green", "cyan", "blue", "purple", "pink", "red", "orange", "gold", "white", "dark"]


def items():
    out = []
    for ln in ITEMS.strip().splitlines():
        i, name, cont, gl, th = ln.split("|")
        th = th or CODE_THEME[name[1]]
        out.append((i.lower(), name, cont, gl, th, None))
    for t in range(8):
        out.append((f"fn_fal_generator_tier{t + 1}", f"&dFN Solar Generator Tier {ROMAN[t]}", "panel", None, TIER_THEMES[t], t + 1))
    for n in range(1, 13):
        out.append((f"fn_power_xpansion_power_r{n}", f"&d&lFN Power Xpansion R{n}", "cell", None, POW_THEMES[n - 1], n))
    return out


def draw(cont, gl, th, n):
    g = {}
    if cont == "panel":
        panel(g, th, n if n else int(gl))
    elif cont == "cell":
        cell(g, th, n)
    else:
        CONT[cont](g, th, gl or None)
    for (x, y) in list(g):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p = (x + dx, y + dy)
            if p not in g and 0 <= p[0] < 16 and 0 <= p[1] < 16:
                g[p] = OUT
    return g


def svg(px):
    r = "".join(f'<rect x="{x}" y="{y}" width="1" height="1" fill="{c}"/>' for (x, y), c in sorted(px.items(), key=lambda k: (k[0][1], k[0][0])))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" shape-rendering="crispEdges">{r}</svg>\n'


def component(name):
    """Nombre legacy (&c, &l) -> cuerpo de 'when' como lo emite Paper (mismo formato que el resto del pack)."""
    extra, color, bold, buf = [], None, False, ""

    def flush():
        if buf:
            e = {"text": buf, "obfuscated": False, "italic": False, "underlined": False, "strikethrough": False}
            if color:
                e["color"] = color
            e["bold"] = bold
            extra.append(e)
    parts = re.split(r"&([0-9a-fk-or])", name)
    buf = parts[0]
    for k in range(1, len(parts), 2):
        flush()
        code, buf = parts[k], parts[k + 1]
        if code in CODE_COLOR:
            color, bold = CODE_COLOR[code], False
        elif code == "l":
            bold = True
        elif code == "r":
            color, bold = None, False
    flush()
    return {"text": "", "extra": extra}


PREFIX = "slimefun/drakes_heads/"


def patch_items_json(path, lines):
    t = path.read_text(encoding="utf-8")
    t = "\n".join(l for l in t.split("\n") if PREFIX not in l)
    m = re.search(r'\n\s*\],\s*\n\s*"fallback"', t)
    head = t[:m.start()].rstrip().rstrip(",")
    t = head + ",\n\n\t\t" + ",\n\t\t".join(lines) + t[m.start():]
    json.loads(t)  # valida
    path.write_text(t, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--no-png", action="store_true")
    a = ap.parse_args()
    R = a.root
    tex, svgd = R / "assets/drakescraft/textures/heads", R / "assets/drakescraft/textures/heads/svg"
    mod = R / "assets/minecraft/models/slimefun/drakes_heads"
    for d in (tex, svgd, mod):
        d.mkdir(parents=True, exist_ok=True)
    lines, seen = [], set()
    for i, name, cont, gl, th, n in items():
        px = draw(cont, gl, th, n)
        (svgd / f"{i}.svg").write_text(svg(px))
        if not a.no_png:
            subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", str(svgd / f"{i}.svg"), "-o", str(tex / f"{i}.png")], check=True)
        (mod / f"{i}.json").write_text(json.dumps({"parent": "item/generated", "author": "Jackstar (DrakesCraft Labs)",
                                                   "textures": {"layer0": f"drakescraft:heads/{i}"}}, indent="\t") + "\n")
        w = json.dumps(component(name), ensure_ascii=False, separators=(",", ":"))
        if w in seen:
            continue
        seen.add(w)
        lines.append('{"when": %s,"model":{"type":"minecraft:model","model":"%s%s"}}' % (w, PREFIX, i))
    targets = [R / "assets/minecraft/items/player_head.json"] + sorted(R.glob("overlay_*/assets/minecraft/items/player_head.json"))
    for p in targets:
        patch_items_json(p, lines)
    print(f"{len(lines)} cases en {len(targets)} archivo(s); {len(items())} texturas")


if __name__ == "__main__":
    main()
