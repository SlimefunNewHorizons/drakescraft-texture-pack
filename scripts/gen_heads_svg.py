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


GLYPHS.update({
    "leaf": [".....XX", "...XXXX", "..XXXX.", ".XXXX..", ".XXX...", "X.X....", "X......"],
    "bee": [".X...X.", "XXX.XXX", ".XXXXX.", "X.X.X.X", "XXXXXXX", ".XXXXX.", "...X..."],
    "seed": [".......", "...X...", "..XXX..", ".XXXXX.", "..XXX..", "...X...", "...X..."],
    "book": ["XXXXXXX", "X.....X", "X.XXX.X", "X.....X", "X.XXX.X", "X.....X", "XXXXXXX"],
    "fish": [".......", "..XXX.X", ".XXXXXX", "XXX.XXX", ".XXXXXX", "..XXX.X", "......."],
    "crown": ["X.X.X.X", "XXXXXXX", "XXXXXXX", ".XXXXX.", ".......", ".......", "......."],
    "egg": ["..XXX..", ".XXXXX.", ".XXXXX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX.."],
})
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


def chest(g, th, gl):
    b, l, d = THEMES[th]
    bevel(g, 2, 5, 13, 13, th)
    rect(g, 3, 4, 12, 4, b)
    rect(g, 2, 8, 13, 8, d)
    rect(g, 7, 7, 8, 10, "#e0ad3a")
    g[(7, 7)] = "#fff1a8"
    if gl:
        glyph(g, gl, 4, 6, l)


CONT = {"slab": slab, "cube": cube, "orb": orb, "gem": gem, "can": can, "chest": chest}

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
FN_GEM_FINE_JASPER_CRAFTING|&dFine Jasper Gemstone|gem||red
FN_GEM_UPGRADES_DISPLAY_ITEM|&dGem Tier Upgrades|gem||gold
FN_GEM_DOWNGRADE_DISPLAY_ITEM|&dGem Tier Downgrades|gem||gray
THORIUM|Thorium|gem||green
FOOD_SYNTHESIZER|Food Synthesizer|cube|mushroom|orange
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
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
TIER_THEMES = ["gray", "white", "green", "cyan", "blue", "purple", "pink", "gold", "red"]
POW_THEMES = ["gray", "white", "green", "cyan", "blue", "purple", "pink", "red", "orange", "gold", "white", "dark"]

CATALOG = Path(__file__).with_name("heads_catalog.json")

# ---- reglas automaticas (addons con muchas cabezas): primera coincidencia gana, sobre "id nombre" en minusculas
THEME_KW = [
    ("dark|black|obsidian|netherite|wither|shadow|bat|spider|nether(?!o)|blackstone|void(?!.*lens)", "dark"),
    ("red|redstone|fire|ignis|magma|lava|tomato|pepper|chilli|cayenne|jalapeno|strawberry|radish|raddish|radicchio|blaze|ignited|volcanic|berserk|rhubarb|crimson|cinnab|combust|heat", "red"),
    ("orange|terra|clay|dirt|terracotta|carrot|pumpkin|copper|cinnamon|ginger|red sand|cocoa|rust|tarnish", "orange"),
    ("gold|yellow|wheat|corn|mustard|honey|wealth|sweet|valuable|treasure|lux|mace|vanilla|nugget|sand|royal|imperial|majestic|noble|cetrus lumium|golden", "gold"),
    ("blue|lapis|water|aqua|wet|drowned|guardian|squid|ocean|sea|beach|nori|wave", "blue"),
    ("cyan|diamond|air|ventus|ice|chilly|polar|crystalline|echo|nitrogen|quantum|mechanical|frozen|snow|spectrum|common", "cyan"),
    ("purple|amethyst|void|ender|end stone|purpur|ethereal|hexed|enchanted|magic|arcane|power|philosoph|mythical|shulker|soul|spirit|celestial|lavender|grape|aubergine|eggplant|unique", "purple"),
    ("pink|rainbow|prismatic|cute|porky|pig|bacon|kaleido|polychrom|motley|epic", "pink"),
    ("white|light|quartz|milk|salt|iron|silver|steel|bone|skeleton|goat|chicken|feldspar|onion|garlic|cauliflower|turnip|parsnip|rice|cow|sheep|uncommon|human", "white"),
    ("gray|grey|stone|cobble|gravel|diorite|granite|andesite|coal|deepslate|basalt|concrete|dust|scrap|metallic|smooth|stray|husky|alchemical|historical", "gray"),
    ("green|emerald|grass|leaf|bush|lettuce|creeper|zombie|frog|slime|jungle|swamp|moss|vine|mint|basil|plant|sapling|forest|turtle|spinach|kale|cabbage|broccoli|celery|pea|bean|herb|cucumber|courgette|meadows|rare|animal|rotten", "green"),
]
GLYPH_KW = [
    ("reina|queen|princess", "crown"), ("zángano|drone|bee", "bee"), ("seed", "seed"), ("rune|glass of milk", "star4"),
    ("input|inlet", "left"), ("output|outlet", "right"), ("connector|home|wireless", "plus"),
    ("golem", "helmet"), ("android", "chip"), ("miner|excavator|pickaxe|woodcutter|peeler|eater", "pick"),
    ("farmer|flower|mangrove|cultivat|bush|plant|flora|vine|leaf|grass|sapling|moss|rose", "leaf"), ("fisher|fish|cod|salmon", "fish"),
    ("butcher|sword|berserk|barbed|warfare", "swords"), ("mushroom|popcorn", "mushroom"),
    ("turbine|rotor|motor|wheel|gear|cogwheel|piston|spring|crafter|forge|bench|winder|hydraulic|cushion", "gear"),
    ("solar|radiant|lunar|sun|stimulator", "sun"), ("wind|air|cloud|lightning|receptor", "cloud"),
    ("liquid|water|sprinkler|nitrogen|coolant|milk", "drop"), ("fire|lava|coal gen|ignis|blaze|magma|thermal", "flame"),
    ("uranium|atom|nano|molecul|cyclotron|singularity|quantum|gamma|graviton|neutron|plutonium|thorium|element|carbyne|palladium|elemental|reactor|stellar|fabricator|accelerator", "atom"),
    ("generator|battery|cell|capacitor|energy|electric|diode|magnet|power|press|dank", "bolt"),
    ("skull|zombie|skeleton|death|inhibidor|repeller|enderman|terrifying|hate|spectrometer", "skull"),
    ("shield|helmet|suit|armor|mask|jets|life support|sinks", "shield"), ("eye|intelligent|spectro", "eye"),
    ("book|guide|how to", "book"), ("ring|band|charm", "ring"), ("lens|focus", "eye"),
    ("control|module|chip|computer|intelligence|program|automation|cargo|manager|auto|synthes|chamber|regulator|extractor|producer|putrif|tree|trash", "chip"),
    ("ore|alloy|shard|fossil|nugget|supreme|core of", "star4"), ("chicken|cow|pig|sheep|rabbit|squid|frog|goat|turtle|villager|animal|mob|egg|pet", "egg"),
]
CONT_KW = [
    ("crystal|gem|diamond|emerald|ore|alloy|shard|lens|relic|lith |meso |neo |axi |prism|quartz|amethyst", "gem"),
    ("rune|rune ", "slab"),
    ("chest|cofre|caja|pack|basket|backpack|sack|vault|bóveda", "chest"),
    ("seed|bush|plant|pearl|orb|soul|fossil|egg|sphere|reina|zángano|drone|bee|supreme|core of|moss|ring", "orb"),
    ("cell|battery|capacitor|coolant|cartridge|liquid|nitrogen|power cell|steam|turbine", "can"),
]
ADDON_AUTO = {  # addons que se auto-generan desde heads_catalog.json (el resto de cabezas esta en ITEMS o ya mapeado por nombre)
    "Cultivation", "Supreme", "CrystamaeHistoria", "Netheopoiesis", "SlimeFrame", "SlimyBees", "Slimefun", "DankTech2",
    "PrivateStorage", "SlimefunWarfare", "DynaTech", "EcoPower", "DrakesNanotech", "IDreamOfEasy", "MagicXpansion",
    "InfinityExpansion", "GeneticChickengineering", "EquivalencyTech", "NetworksV6-Drake", "SlimefunLuckyBlocks", "ExoticGarden",
    "VillagerUtil", "NotEnoughAddons", "DemonicExpansion", "Bump", "AlchimiaVitae", "SlimefunOreChunks", "Galaxyfun", "FoxyMachines",
    "FluffyMachines", "LiteXpansion", "FNAmplifications", "DrakesTech", "NetworksExpansion", "Gastronomicon", "Coronalis",
}
ADDON_CONT = {"Cultivation": "orb", "Supreme": "orb", "CrystamaeHistoria": "gem", "Netheopoiesis": "orb", "SlimyBees": "orb",
              "DankTech2": "chest", "PrivateStorage": "chest", "SlimeFrame": "cube"}
KIND_GLYPH = {"efficien": "bolt", "cloner": "plus", "accelerat": "up", "intellig": "eye", "berserk": "flame"}


def h32(s):
    v = 2166136261
    for ch in s:
        v = ((v ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return v


def tier_of(name):
    m = re.search(r"\b(IX|VIII|VII|VI|IV|V|III|II|I)\s*$", name)
    if m:
        return ROMAN.index(m.group(1)) + 1
    m = re.search(r"(?:tier|r)\s*(\d+)\s*$", name, re.I)
    if m:
        return int(m.group(1))
    if name.endswith("★"):
        return 9
    return 0


def auto_spec(i, name, addon):
    t = (i + " " + name).lower().replace("_", " ")
    n = name.lower()
    gl = next((g for k, g in GLYPH_KW if re.search(k, n)), None)
    if "bee" in n or "golem" in n:
        gl = next((g for k, g in KIND_GLYPH.items() if k in n), gl)
    cont = next((c for k, c in CONT_KW if re.search(k, n)), ADDON_CONT.get(addon, "cube"))
    if re.search(r"\bcell\b|\bpower cell\b", n) and addon in ("SlimeFrame", "DankTech2"):
        cont = "can"
    if "golem" in n and "bee" not in n:
        cont = "cube"
    if re.search(r"module|control|neural|nexus|cogwheel|void shard", n):
        cont = "cube"
    if cont in ("gem", "orb") and gl in ("chip", "gear") and not re.search(r"supreme", n):
        cont = "cube"
    tr = tier_of(name)
    if tr:
        th = TIER_THEMES[(tr - 1) % len(TIER_THEMES)]
    else:
        th = next((c for k, c in THEME_KW if re.search(k, t)), None) or sorted(THEMES)[h32(i) % len(THEMES)]
    # sin glifo en orbes/gemas: queda liso; cubos sin glifo -> chip
    if cont == "cube" and not gl:
        gl = "chip"
    if cont == "slab" and not gl:
        gl = "star4"
    if cont in ("orb", "gem", "chest") and gl in ("chip", "gear") and addon in ("Cultivation", "Supreme"):
        gl = None
    return cont, gl or "", th


def load_catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def build_catalog(dump, base_json):
    import gzip
    d = json.load(gzip.open(dump))
    base = Path(base_json).read_text(encoding="utf-8")
    out = []
    for x in d["items"]:
        if x["material"] != "PLAYER_HEAD":
            continue
        covered = ('"text":"%s"' % x["name"]) in base
        out.append({"id": x["id"], "name": x["name"], "addon": x["addon"], "covered": covered})
    CATALOG.write_text(json.dumps(out, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    print(len(out), "cabezas en catalogo")


def items():
    """-> lista (id, nombre legacy o plano, contenedor, glifo, tema, n, resuelto_por_id)"""
    cat = {c["id"]: c for c in load_catalog()}
    out, seen = [], set()
    for ln in ITEMS.strip().splitlines():
        i, name, cont, gl, th = ln.split("|")
        th = th or CODE_THEME[name[1]]
        out.append((i, name, cont, gl, th, None, i in cat))
        seen.add(i)
    for t in range(8):
        i = f"FN_FAL_GENERATOR_TIER{t + 1}"
        out.append((i, f"&dFN Solar Generator Tier {ROMAN[t]}", "panel", None, TIER_THEMES[t], t + 1, i in cat))
        seen.add(i)
    for n in range(1, 13):
        i = f"FN_POWER_XPANSION_POWER_R{n}"
        out.append((i, f"&d&lFN Power Xpansion R{n}", "cell", None, POW_THEMES[n - 1], n, i in cat))
        seen.add(i)
    base = {o[0]: o for o in out}
    for i, c in cat.items():  # variantes _SCRAP de las piezas FN: misma forma, tono oscuro
        if i.startswith("FN_") and i.endswith("_SCRAP") and i not in seen and i[:-6] in base:
            b = base[i[:-6]]
            out.append((i, c["name"], b[2], b[3], "dark", None, True))
            seen.add(i)
    for i, c in cat.items():
        if i in seen or c["covered"] or c["addon"] not in ADDON_AUTO:
            continue
        cont, gl, th = auto_spec(i, c["name"], c["addon"])
        out.append((i, c["name"], cont, gl, th, None, True))
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
    extra, color, bold = [], None, False
    parts = re.split(r"&([0-9a-fk-or])", name)
    buf = parts[0]

    def flush():
        if buf:
            e = {"text": buf, "obfuscated": False, "italic": False, "underlined": False, "strikethrough": False}
            if color:
                e["color"] = color
            e["bold"] = bold
            extra.append(e)
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
# Estructura: entries[0] = select por custom_data (id Slimefun, nuestros cases) -> fallback = select por custom_name (original) -> player_head.
ID_HEAD = '{"threshold":0,"model":{"type":"minecraft:select","property":"minecraft:component","component":"minecraft:custom_data","cases":['
NAME_HEAD = '{"threshold":0,"model":{"type":"minecraft:select","property":"minecraft:component","component":"minecraft:custom_name",'
ID_END = '\n\t],"fallback":'


def patch_items_json(path, id_lines, name_lines):
    t = path.read_text(encoding="utf-8")
    t = "\n".join(l for l in t.split("\n") if PREFIX not in l)  # quita cases propios previos (por id y por nombre)
    if ID_HEAD not in t:  # primera vez: envuelve el select por nombre
        assert NAME_HEAD in t and t.count(NAME_HEAD) == 1
        t = t.replace(NAME_HEAD, ID_HEAD + ID_END + NAME_HEAD[len('{"threshold":0,"model":'):])
        tail = re.search(r'("scale":\s*\[1,1,1\]\}\}\})\}(\s*\]\s*\},\s*"oversized_in_gui")', t)
        assert tail, "cola inesperada"
        t = t[:tail.end(1)] + "}}" + t[tail.start(2):]
    a = t.index(ID_HEAD) + len(ID_HEAD)
    b = t.index(ID_END, a)
    t = t[:a] + "\n\t\t" + ",\n\t\t".join(id_lines) + t[b:]
    m = re.search(r'\n\s*\],\s*\n\s*"fallback": \{"type": "minecraft:special"', t)
    head = t[:m.start()].rstrip().rstrip(",")
    if name_lines:
        head += ",\n\n\t\t" + ",\n\t\t".join(name_lines)
    t = head + t[m.start():]
    json.loads(t)  # valida
    path.write_text(t, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--build-catalog", nargs=2, metavar=("DUMP_GZ", "BASE_PLAYER_HEAD_JSON"),
                    help="regenera scripts/heads_catalog.json desde Slimefun-Knowledge-Drake/data/slimefun-dump.json.gz")
    a = ap.parse_args()
    if a.build_catalog:
        build_catalog(*a.build_catalog)
        return
    R = a.root
    tex, svgd = R / "assets/drakescraft/textures/heads", R / "assets/drakescraft/textures/heads/svg"
    mod = R / "assets/minecraft/models/slimefun/drakes_heads"
    for d in (tex, svgd, mod):
        d.mkdir(parents=True, exist_ok=True)
    id_lines, name_lines, seen, n_all = [], [], set(), 0
    for i, name, cont, gl, th, n, by_id in items():
        f = i.lower()
        px = draw(cont, gl, th, n)
        (svgd / f"{f}.svg").write_text(svg(px))
        if not a.no_png:
            subprocess.run(["rsvg-convert", "-w", "16", "-h", "16", str(svgd / f"{f}.svg"), "-o", str(tex / f"{f}.png")], check=True)
        (mod / f"{f}.json").write_text(json.dumps({"parent": "item/generated", "author": "Jackstar (DrakesCraft Labs)",
                                                   "textures": {"layer0": f"drakescraft:heads/{f}"}}, indent="\t") + "\n")
        n_all += 1
        model = '"model":{"type":"minecraft:model","model":"%s%s"}' % (PREFIX, f)
        if by_id:
            id_lines.append('{"when": {"PublicBukkitValues":{"slimefun:slimefun_item":"%s"}},%s}' % (i, model))
        else:  # respaldo por nombre: id no presente en el dump del servidor
            w = json.dumps(component(name), ensure_ascii=False, separators=(",", ":"))
            if w not in seen:
                seen.add(w)
                name_lines.append('{"when": %s,%s}' % (w, model))
    targets = [R / "assets/minecraft/items/player_head.json"] + sorted(R.glob("overlay_*/assets/minecraft/items/player_head.json"))
    for p in targets:
        patch_items_json(p, id_lines, name_lines)
    print(f"{len(id_lines)} cases por id + {len(name_lines)} por nombre en {len(targets)} archivo(s); {n_all} texturas")


if __name__ == "__main__":
    main()
