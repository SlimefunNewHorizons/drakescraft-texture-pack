#!/usr/bin/env python3
"""Texturas Slimefun vectoriales de DrakesCraft, mapeadas POR ID (custom_data slimefun:slimefun_item).

Fuente: volcado del plugin (Slimefun-Knowledge-Drake/data/slimefun-dump.json.gz: id, name, addon, group, class,
material, lore). Cada id se clasifica (diseno / variante / fantasma / cabeza / cubierto); los disenos se dibujan como
SVG 128x128 (degradados, relieve, brillos, borde #0d0a14) con una biblioteca de motivos (scripts/slimefun_vector.py:
PCB, chip, generador con turbina, panel solar, cable con aislante, tanque con liquido, lingote, gema, ampolla,
armaduras, herramientas, comida, libro...) elegidos por nombre/id/grupo/lore y teñidos por material, addon o planta.
Los SVG identicos se comparten entre ids; PNG 128x128 RGBA cuantizado (96 colores) para el peso.

Salida:
  build/slimefun_svg/<addon>/<id>.svg                              fuente editable (no versionada, regenerable)
  assets/slimefun/textures/item/drakes_proc/<addon>/<id>.png       128x128
  assets/minecraft/models/slimefun/drakes_proc/<addon>/<id>.json   item/generated
  assets/minecraft/items/<material>.json   select por custom_data (id) con fallback = definicion previa
Variantes: cofres de ender de colores = 5 PNG + 2 modelos, color en `tints` constantes por case.
No toca player_head.json (cabezas: otro agente) ni ids ya cubiertos por Slimefun-Texture-Drake.
Uso: gen_slimefun_svg.py [--addon NOMBRE ...] [--sheet hoja.png] [--sin-cablear]   (idempotente, por lotes)
"""
import argparse
import collections
import glob
import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slimefun_vector as V  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = "#0d0a14"
GOLD, GOLD_D, PURPLE = "#e0ad3a", "#8f6a1c", "#7c3aed"
FRAME, FRAME_L, SCREEN, WHITE = "#3b3350", "#5a4f73", "#1a1330", "#f4f0ff"
WOOD = "#6b4a2b"
CYAN, MAGENTA = "#38bdf8", "#d946ef"

# ---------------------------------------------------------------- temas (H principal, h luz, d sombra, E acento)
TEMAS = {
    "copper": ("#c8763a", "#f0a468", "#8a4520", "#38bdf8"),
    "tin": ("#b8c4cf", "#eaf1f7", "#7d8a98", "#38bdf8"),
    "gold": ("#f2c14e", "#fff1a8", "#b8862a", "#fffbe0"),
    "iron": ("#aeb7c8", "#eef2fb", "#6b7488", "#38bdf8"),
    "silver": ("#cfd6e6", "#ffffff", "#8b93ab", "#a78bfa"),
    "lead": ("#6f7384", "#9a9fb3", "#43465a", "#8b5cf6"),
    "aluminum": ("#d6dbe6", "#ffffff", "#99a0b3", "#22d3ee"),
    "zinc": ("#8fa4b8", "#c4d4e2", "#566a7e", "#22d3ee"),
    "magnesium": ("#e6e2d4", "#fffdf0", "#a8a390", "#fde047"),
    "diamond": ("#3ed6e6", "#c2fbff", "#1b8fa0", "#a855f7"),
    "emerald": ("#34d399", "#b7f7da", "#0f8a5f", "#fde68a"),
    "netherite": ("#4a3d5c", "#7a6a96", "#26202f", "#d946ef"),
    "coal": ("#3a3a44", "#5e5e6c", "#1c1c22", "#f59e0b"),
    "redstone": ("#e23b3b", "#ff8a8a", "#8c1a1a", "#fca5a5"),
    "lapis": ("#2f55d4", "#7fa0ff", "#1a2f8a", "#a5f3fc"),
    "quartz": ("#eee8e0", "#ffffff", "#b5aca0", "#f9a8d4"),
    "uranium": ("#7fbf3f", "#c5ec8a", "#4a7a22", "#d9f99d"),
    "thorium": ("#7a8c78", "#b4c4b0", "#47564a", "#bef264"),
    "void": ("#3a2468", "#6a44b0", "#1c0f38", "#d946ef"),
    "infinity": ("#7c3aed", "#b794ff", "#4a1fa0", "#22d3ee"),
    "fire": ("#e8601c", "#ffb15c", "#8a2c0a", "#ffd23a"),
    "water": ("#2f86e8", "#8cc4ff", "#1a4f9e", "#a5f3fc"),
    "carbon": ("#3a3a48", "#62627a", "#1e1e28", "#38bdf8"),
    "iridium": ("#e4e2f0", "#ffffff", "#a39fc0", "#f0abfc"),
    "scrap": ("#7a6a52", "#a8946f", "#4a3e2e", "#d6b36a"),
    "uu": ("#c026d3", "#f0abfc", "#7e1590", "#fde047"),
    "soul": ("#3fd0e0", "#b8f5ff", "#1b7f90", "#e0f2fe"),
    "ender": ("#2e8f86", "#7fe0d4", "#17554f", "#d946ef"),
    "obsidian": ("#2b1d4a", "#4f3a7e", "#150d28", "#8b5cf6"),
    "arcanium": ("#b0268f", "#f06ccc", "#6a1456", "#fde047"),
    "shulker": ("#a06ad0", "#d4a6f5", "#6a3a94", "#f0abfc"),
    "rubber": ("#3d3d3d", "#666666", "#1f1f1f", "#fde047"),
    "stone": ("#8d93a6", "#c9cee0", "#4b5064", "#8b5cf6"),
    "basic": ("#5d82c8", "#9fbdf0", "#344f8a", "#38bdf8"),
    "advanced": ("#e0ad3a", "#ffe08a", "#8f6a1c", "#38bdf8"),
    "hybrid": ("#8b5cf6", "#c4b0ff", "#5028b0", "#fde047"),
    "ultimate": ("#d946ef", "#f5a8ff", "#8a1fa0", "#fde047"),
    "celestial": ("#fde68a", "#ffffff", "#c9962a", "#d946ef"),
    "poseidon": ("#26b5c8", "#8fecf6", "#12717f", "#fde68a"),
    "reaper": ("#2a2438", "#4c4264", "#14101e", "#34d399"),
}
CLAVES = [  # primer patron del id que coincida decide el tema
    ("INFINIT", "infinity"), ("VOID", "void"), ("COPPER", "copper"), ("TIN(?![A-Z])", "tin"), ("GOLD", "gold"),
    ("IRON", "iron"), ("SILVER", "silver"), ("LEAD", "lead"), ("ALUMINUM", "aluminum"), ("ZINC", "zinc"),
    ("MAGNESIUM", "magnesium"), ("DIAMOND", "diamond"), ("EMERALD", "emerald"), ("NETHERITE", "netherite"),
    ("COAL", "coal"), ("REDSTONE", "redstone"), ("LAPIS|LAPOTRON", "lapis"), ("QUARTZ", "quartz"),
    ("URANIUM", "uranium"), ("THORIUM", "thorium"), ("IRIDIUM", "iridium"), ("CARBON", "carbon"),
    ("SCRAP", "scrap"), ("UU_|MASS_FAB", "uu"), ("SOUL", "soul"), ("ENDER|END(?![A-Z])", "ender"),
    ("OBSIDIAN|BEDROCK", "obsidian"), ("ARCANIUM", "arcanium"), ("SHULKER", "shulker"), ("RUBBER", "rubber"),
    ("FIRE|FLAME|BLAZE|GEOTHERMAL|PIGLIN|PYRO|NETHER|SMELT|SLAG|FORGE|INFERNAL", "fire"),
    ("HYDRO|WATER|FREEZER|SOLIDIFIER|MELTER|LIQUID|AQUATIC", "water"), ("POSEIDON", "poseidon"),
    ("REAPER", "reaper"), ("CELESTIAL", "celestial"), ("ULTIMATE", "ultimate"), ("HYBRID", "hybrid"),
    ("ADVANCED", "advanced"), ("BASIC", "basic"),
]


def tema(iid, base):
    for pat, nombre in CLAVES:
        if re.search(r"(?<![A-Z])(?:" + pat + ")", iid):
            return TEMAS[nombre]
    for pat, nombre in (("gold", "gold"), ("iron", "iron"), ("diamond", "diamond"), ("netherite", "netherite"),
                        ("emerald", "emerald"), ("lapis|blue", "lapis"), ("red", "redstone"), ("quartz", "quartz"),
                        ("coal|black", "coal"), ("purple", "hybrid"), ("lime", "uranium"), ("orange|yellow", "advanced"),
                        ("magma|blaze|fire|lava", "fire"), ("prismarine|light_blue", "water")):
        if re.search(pat, base):
            return TEMAS[nombre]
    return TEMAS["stone"]


# ---------------------------------------------------------------- formas nuevas (comida, semillas, procesos...)
import colorsys
import hashlib

PALETA_COMIDA = ["#e23b3b", "#f59e0b", "#fde047", "#84cc16", "#16a34a", "#0d9488", "#38bdf8", "#6366f1",
                 "#a855f7", "#ec4899", "#b45309", "#78350f", "#f5f5f4", "#9ca3af", "#dc2626", "#65a30d"]


def hue_tema(texto, sat=0.62):
    n = int(hashlib.md5(texto.encode()).hexdigest()[:6], 16)
    h = (n % 360) / 360.0

    def hx(l, s=sat):
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return "#%02x%02x%02x" % (round(r * 255), round(g * 255), round(b * 255))
    e = colorsys.hls_to_rgb((h + 0.5) % 1, 0.62, 0.8)
    return (hx(0.5), hx(0.75), hx(0.3), "#%02x%02x%02x" % tuple(round(v * 255) for v in e))


# ---------------------------------------------------------------- motivos: reglas nombre -> (motivo, parametro)
def _n(*a):
    return a


PROCESOS = {"chopped": ("pieces", None), "mashed": ("bowl", None), "sliced": ("slices", None), "ground": ("dust", None),
            "blended": ("glass", None), "boiled": ("pot", None), "fried": ("pan", None), "grilled": ("fillet", None)}

# (regex sobre el nombre en minusculas, (motivo, parametro)); el primero que coincide gana.
REGLAS = [
    (r"helmet|crown|\bhat\b|\bcap\b", ("helmet", None)),
    (r"chestplate|\bvest\b|tunic|\bjacket", ("chest", None)),
    (r"leggings|\bpants\b", ("legs", None)),
    (r"\bboots\b|shoes", ("boots", None)),
    (r"crossbow", ("bow", "cross")),
    (r"\bbow\b|\barco\b", ("bow", None)),
    (r"\bshield|aegis", ("shield", None)),
    (r"sword|blade|katana|dagger|saber|rapier|\bspear|\bknife", ("sword", None)),
    (r"pickaxe|handheld digger|\bpick\b", ("pick", None)),
    (r"\baxe\b|hatchet", ("axe", None)),
    (r"shovel|spade", ("shovel", None)),
    (r"\bhoe\b|treetap|sickle", ("hoe", None)),
    (r"scythe", ("scythe", None)),
    (r"drill|cutter|chainsaw", ("drill", None)),
    (r"hammer|mallet|\bmace\b", ("hammer", None)),
    (r"trident", ("trident", None)),
    (r"\bwand\b|staff|sceptre|scepter|\brod of|blaze rod|\bcane\b", ("staff", None)),
    (r"missile|rocket|\bnuke|warhead", ("rocket", None)),
    (r"uninsulated .*cable|bare (wire|cable)", ("cable", "bare")),
    (r"cable|wire|conduit", ("cable", None)),
    (r"circuit board|\bpcb\b|circuit|\bboard\b|motherboard|\bmicro", ("pcb", None)),
    (r"\bchip\b|processor|\bcpu\b|memory core|\bcore chip", ("chip", None)),
    (r"\bupgrade|\bmodule\b|\bcartridge|\bboost\b|\bmod\b|\bplugin\b", ("module", None)),
    (r"capacitor", ("capacitor", None)),
    (r"battery|\bcell\b|accumulator", ("battery", None)),
    (r"item casing|casing|\bshell plate", ("plate", None)),
    (r"\bplates?\b|\bsheet\b", ("plate", None)),
    (r"\bnugget", ("nugget", None)),
    (r"\balloy\b|amalgam", ("alloy", None)),
    (r"ingot|\bbar\b|bronze\b|steel\b$|brass\b$", ("ingot", None)),
    (r"\bdust\b|powder|pigment|\bsugar\b|\bflour|\bsalt\b|\bgrit\b|\bash\b", ("dust", None)),
    (r"singularity|\bpearl|\borb\b|\bball\b|sphere", ("orb", None)),
    (r"gem\b|crystal|\bshard|\blens|sapphire|ruby|amethyst|topaz|carbonado|emerald|diamond$", ("gem", None)),
    (r"\bmatrix|\bflame\b|\bember", ("flame", None)),
    (r"essence", ("flame", None)),
    (r"scrap|\bslag\b|\brubble", ("scrap", None)),
    (r"\bfibre|\bfiber|\bthread|\bstring\b", ("fibre", None)),
    (r"\bmesh\b|\bnet\b", ("mesh", None)),
    (r"shulker shell|\bshell\b|\bscale\b|\bcarapace", ("shell", None)),
    (r"spellbook|\bbook\b|\btome\b|codex|manual|\bnotes?\b|grimoire", ("book", "star")),
    (r"\bscroll|\brecipe|\bparchment", ("scroll", None)),
    (r"talisman|\bcharm\b|amulet|\bpendant|medallion", ("talisman", None)),
    (r"\bring\b", ("ring", None)),
    (r"relic|\brune\b|ancient", ("rune", "star")),
    (r"backpack|\bbag\b|pouch|satchel", ("backpack", None)),
    (r"\bmotor\b|piston|engine", ("motor", None)),
    (r"trash|dustbin|\bbin\b", ("trash", None)),
    (r"\bfish\b|salmon|\bcod\b|pufferfish|chicken|\bmeat\b|mutton|beef|pork|steak|rabbit", ("fillet", None)),
    (r"flower|poppy|dandelion|daisy|allium|tulip|orchid|\brose\b|\blily", ("flower", None)),
    (r"\bcake\b|\bpie\b|\bcookie|\bbread\b|muffin", ("fruit", None)),
    (r"\bmushroom|\bshroom|\bfungus", ("mush", None)),
    (r"\bseeds?\b|\bspore|\bsapling|\bkernel|\bgrain\b", ("seed", None)),
    (r"\bnuts?\b|\bbeans?\b|\bpeas\b|\bpod\b|\bpeanut|\bcocoa|\bvanilla\b|\bcorn\b", ("pod", None)),
    (r"pepper|chili|chilli|carrot|\bcucumber|\bzucchini|\beggplant|\bcelery|\basparagus|\bradish", ("pepper", None)),
    (r"\bleaf\b|\bleaves\b|\bherb|\bmint\b|\btea\b|\bbasil|\bhops\b|\bvine\b|\bgrass\b|\bfern\b", ("leaf", None)),
    (r"apple|berry|berries|banana|lemon|orange|pineapple|mango|peach|apricot|pear\b|cherry|kiwi|lime\b|chestnut"
     r"|hazelnut|pecan|grape|strawberry|tomato|potato|onion|garlic|rice|lettuce|pumpkin|melon|plum|fig\b|olive|coconut"
     r"|avocado|cabbage|cauliflower|beet|turnip|ginger|fruit|walnut|almond|cranberr|raspberr|blueberr|currant"
     r"|rapeseed|juice|clove|coffee|tobacco|cotton|spinach|squash|yam", ("fruit", None)),
    (r"potion|elixir|liquor|licor|brew|bottle|vial|\bflask|\bjar\b|molten|\bliquid|\bsoup|\bfluid", ("vial", None)),
    (r"\bpaste\b|\bjam\b|\bstew\b|\bgel\b|\bresin|\bsyrup", ("bowl", None)),
    (r"\begg\b|\bhuevo", ("egg", None)),
    (r"\bkit\b|\bpack\b|\bbundle", ("kit", None)),
    (r"\bcard\b|\bticket|\bvoucher|\bcoupon|\bnote\b", ("card", "star")),
    (r"\bkey\b|\blockpick", ("key", None)),
    (r"\bframe\b", ("frame", None)),
    (r"apiary|\bhive\b", ("apiary", None)),
    (r"banner|\bflag\b|\bpennant", ("banner", None)),
    (r"\bdoor\b", ("door", None)),
    (r"trophy|\bidol\b|\bdecoy\b", ("talisman", None)),
    (r"whisky|whiskey|bourbon|pivo|vodka|\bwine\b|\bbeer\b|\brum\b|\bale\b|drug|morphine|infusion|\btonic", ("vial", None)),
    (r"\bcoin\b|\bmedal\b", ("nugget", None)),
    (r"comb\b|honey|jelly|pollen|beeswax|\bwax\b|slimemeal", ("bowl", None)),
    (r"\bnest\b", ("apiary", None)),
    (r"\brock\b|meteor|\bpellet|\bfloor\b|ventstone|\bconcrete\b|\bcast\b", ("cube", None)),
    (r"shears|chisel|\btongs|\bwrench", ("hammer", None)),
    (r"\bclock\b|compass|alarm|\belevator|\bfoundry|\bholder|\bdispenser", ("machine", "ring")),
    (r"\bfan\b|nose cone|\bmagnetoid", ("motor", None)),
    (r"phantom membrane|\bmembrane|\bwings?\b", ("leaf", None)),
    (r"refined iron|mixed metal", ("ingot", None)),
    (r"iridium", ("gem", None)),
    (r"\bconver", ("machine", "arrows")),
    (r"bullet|ammo|\bshell casing", ("bullet", None)),
    (r"grenade|granada", ("grenade", None)),
    (r"\bwool\b|\bcloth|\bfabric|\bcarpet", ("wool", None)),
    (r"\bdirt\b|\bsoil\b|\bcrux\b|\bnetherrack|\bsand\b|\bgravel|\bstone\b|\bcobble|\bobsidian\b", ("cube", None)),
    (r"\bstick\b|\brod\b|\btwig", ("stick", None)),
    (r"scope|polarizer|\blens\b|\bmonocle|\bbinocular", ("lens", None)),
    (r"rubber|plastic|resin\b", ("pieces", None)),
    (r"\bradio\b|\binfo\b", ("machine", "ring")),
    (r"\bglass\b|\bpane\b|window", ("pane", None)),
    (r"carbon\b|\bcoal\b|charcoal|\bcoke\b", ("carbon", None)),
    (r"machine block|\bcore\b|\bnexus\b|\bheart\b|\bblock\b", ("core", None)),
    (r"solar|\bpanel\b|photovolt", ("panel", None)),
    (r"quarry|miner\b|\bmine\b|excavat|drill rig|extractor|borer", ("miner", None)),
    (r"hydro|\bpump|\btank\b|\bwater\b|\bfluid|centrifuge|\bboiler|\bliquid|\bdrain|\bbrewer|\bdistill", ("tank", "drop")),
    (r"geotherm|smelt|forge|furnace|crucible|melter|incinerat|\bkiln|\boven\b|\bgrill\b|\bburner|\blava", ("forge", None)),
    (r"freez|\bcooler|refriger|\bcryo|\bfrost|\bice\b", ("tank", "snow")),
    (r"reactor|\bturbine|\bgenerator|\bdynamo|power plant|\benergy gen", ("generator", "bolt")),
    (r"charger|\bsupercap|\btransformer|\binverter|\benergy|\bpower\b", ("reactor", None)),
    (r"enchant|disenchant|altar|ritual|\binfuser|\bpedestal|\bshrine|\bobelisk|\bbeacon|\bsummon|\bruneforge", ("pedestal", "star")),
    (r"\bcrafter|workbench|assembler|fabricator|constructor|synthesi|\banvil|\bcrafting", ("machine", "anvil")),
    (r"crush|grind|\bmill\b|macerat|pulveri|compress|\bpress\b|decompress|\bsaw\b|\bsifter", ("machine", ("gear", "hopper"))),
    (r"\bfarm|grower|harvest|garden|compost|\bplanter|\bgreenhouse|\bbonemeal|\btree\b|\borchard|incubator", ("machine", "leaf")),
    (r"spawner|\bmob\b|\bsoul|\bcapture|\bpet\b|\bcage|\bchicken", ("machine", "skull")),
    (r"teleport|portal|\bgps\b|\bwarp\b|\bwaypoint|\bdimension|\bgate\b|\bradar|\bscanner|\bsensor", ("machine", "ring")),
    (r"sorter|cargo|\bpipe\b|network|router|\bnode\b|\bbridge|\bgrabber|\bpusher|\binterface|\bterminal|\bcontroller", ("machine", "arrows")),
    (r"drawer|barrel|storage|\bchest\b|\bcrate\b|container|\bvault|\bsafe\b|\bshelf|\bcabinet|\blocker", ("crate", "chest")),
    (r"\bturret|\bcannon|\blauncher|\bgun\b|\brifle|\bbomb|\btnt\b|\bexplosive", ("machine", "skull")),
    (r"\bsimulat|\bchamber|\bstrainer|\bfilter|\bpurif|\bwasher|\bwash\b", ("machine", "wave")),
    (r"\bsun\b|\blight\b|\blamp|\blantern|\bglow|\blaser|\bbeam|\bprism|\bunibeam", ("machine", "sun")),
    (r"\bmachine\b|\bstation|\bunit\b|\bcenter|\bfactory|\bplant\b|\bworkshop|\brefiner|\bprocessor", ("machine", "bolt")),
]
# pista por grupo del item (carpeta de la guia) cuando el nombre no basta
GRUPOS = [
    (r"armor|equipment", ("chest", None)), (r"weapon", ("sword", None)), (r"tool", ("pick", None)),
    (r"food|produce|plants|fruit|bush|seeds|flower", ("fruit", None)), (r"by-products", ("bowl", None)),
    (r"potion|pastes", ("vial", None)), (r"resources|materials|molten|ores?", ("ingot", None)), (r"talisman", ("talisman", None)),
    (r"magic|rune|spell|soul|relic|crystal", ("rune", "star")), (r"electric|energy|generator|power|nanotech|tech", ("machine", "bolt")),
    (r"machine|basic_machines|workstation", ("machine", "gear")), (r"cargo|network", ("machine", "arrows")),
    (r"misc|useful|gadget|component|part", ("module", None)), (r"element", ("orb", None)), (r"card|chicken|egg", ("egg", None)),
    (r"upgrade", ("module", None)), (r"ghost|decor", ("pane", None)),
]

BLOQUES_BASE = ("_block", "_wall", "_terracotta", "_concrete", "_bricks", "_stairs", "_slab")
BLOQUES_NOM = ("furnace", "blast_furnace", "smoker", "dispenser", "dropper", "barrel", "lodestone", "smithing_table",
               "crafting_table", "piston", "beacon", "observer", "hopper", "cauldron", "spawner", "beehive", "obsidian",
               "crying_obsidian", "glass", "stone", "smooth_stone", "glowstone", "sea_lantern", "target", "respawn_anchor")
PREDETERMINADOS = collections.Counter()


def texto_de(i):
    return (i["name"] + " " + i["id"].replace("_", " ")).lower()


def forma(i):
    """-> (motivo, parametro, origen) con origen en nombre|id|grupo|material|DEFECTO"""
    n = i["name"].lower()
    cls = i["class"].split(".")[-1]
    if cls == "ByProduct" and n.split() and n.split()[0] in PROCESOS:
        return (*PROCESOS[n.split()[0]], "clase")
    for pat, m in REGLAS:
        if re.search(pat, n):
            return (*m, "nombre")
    for pat, m in REGLAS:
        if re.search(pat, texto_de(i)):
            return (*m, "id")
    g = i["group"].lower() + " " + cls.lower() + " " + " ".join(i.get("lore", [])).lower()
    for pat, m in GRUPOS:
        if re.search(pat, g):
            return (*m, "grupo")
    base = i["material"].lower()
    if base.endswith(BLOQUES_BASE) or base in BLOQUES_NOM:
        return ("machine", "bolt", "material")
    if base.endswith("_dye") or base in ("sugar", "gunpowder", "glowstone_dust", "redstone", "blaze_powder"):
        return ("dust", None, "material")
    if base.endswith(("_ingot", "brick", "nether_brick", "netherite_scrap")):
        return ("ingot", None, "material")
    if base.endswith("_helmet"):
        return ("helmet", None, "material")
    return ("gem", None, "DEFECTO")

ADDON_TEMA = {  # tema por defecto de cada addon cuando el nombre no dice nada
    "Cultivation": "uranium", "Netheopoiesis": "fire", "CrystamaeHistoria": "shulker", "DrakesNanotech": "aluminum",
    "FNAmplifications": "gold", "ElementManipulation": "lapis", "SlimeFrame": "iridium", "DynaTech": "copper",
    "GeneticChickengineering": "quartz", "SlimeTinker": "iron", "SensibleToolbox": "basic", "NetworksV6-Drake": "diamond",
    "Galaxyfun": "obsidian", "FoxyMachines": "arcanium", "Supreme": "netherite", "LiteXpansion": "copper",
    "InfinityExpansion": "infinity", "SoulJars": "soul", "IDreamOfEasy": "tin", "BetterChests": "gold",
    "Bump": "scrap", "SlimefunWarfare": "carbon", "AlchimiaVitae": "ender", "SlimyBees": "gold",
    "ObsidianExpansion": "obsidian", "BreweryMenu": "scrap", "PotionExpansion": "hybrid", "FlowerPower": "emerald",
    "FastMachines": "advanced", "MagicXpansion": "arcanium", "SimpleMaterialGenerators": "stone", "DyeBench": "ultimate",
    "FluffyMachines": "quartz", "TranscEndence": "void", "Nexcavate": "coal", "NotEnoughAddons": "silver",
    "Slimefun": "stone", "ExtraTools": "iron", "InfernalExpansion": "fire", "DemonicExpansion": "redstone",
}
FRUTALES = r"apple|berry|berries|banana|lemon|orange|pineapple|mango|peach|apricot|pear|cherry|kiwi|lime|grape|tomato|pepper|carrot|potato|onion|garlic|pumpkin|melon|plum|olive|coconut|avocado|cabbage|beet|beans?|seeds?|nut|rice|corn|clove|coffee|lettuce|pea|celery|salmon|cod|chicken|mutton|beef|pork|rabbit|fish|egg|mushroom|leaf|leaves|herb|flower"


def tema_item(i):
    n = i["name"].lower()
    cls = i["class"].split(".")[-1]
    if cls in ("ByProduct", "CustomFood", "Juice", "Food", "ExoticGardenFruit", "HarvestableSeed", "HarvestableBush",
               "HarvestablePlant", "ProduceCore", "Paste") or re.search(FRUTALES, n):
        # el color lo da la planta (ultima palabra) para que "Chopped X" y "Boiled X" coincidan
        palabras = [w for w in re.split(r"[^a-z]+", n) if w and w not in PROCESOS and w not in ("netheo", "paste", "terrifying")]
        clave = palabras[-1] if palabras else n
        return hue_tema(clave)
    m = re.search(r"\(([^)]+)\)", i["name"])
    if m and m.group(1).lower() in COLORES_NOMBRE:
        return COLORES_NOMBRE[m.group(1).lower()]
    t = tema(i["id"] + " " + n.upper(), "")
    if t is TEMAS["stone"]:
        a = ADDON_TEMA.get(i["addon"])
        return TEMAS[a] if a else tema("", i["material"].lower())
    return t


COLORES_NOMBRE = {
    "white": ("#f0f0f0", "#ffffff", "#aab0b8", "#38bdf8"), "orange": ("#f9801d", "#ffc27a", "#a04a08", "#fde047"),
    "magenta": ("#c74ebd", "#f0a0ea", "#7e2a78", "#fde047"), "light blue": ("#3ab3da", "#a0e0f5", "#1c6f8c", "#fde047"),
    "yellow": ("#fed83d", "#fff3a0", "#b89418", "#7c3aed"), "lime": ("#80c71f", "#c8f080", "#4a7a0c", "#fde047"),
    "pink": ("#f38baa", "#ffc8d8", "#a94a68", "#fde047"), "gray": ("#6b7280", "#a0a6b0", "#3b4048", "#38bdf8"),
    "light gray": ("#9d9d97", "#d4d4ce", "#5e5e58", "#38bdf8"), "cyan": ("#169c9c", "#70e0e0", "#0a5a5a", "#fde047"),
    "purple": ("#8932b8", "#c488e8", "#52186f", "#fde047"), "blue": ("#3c44aa", "#8890e8", "#1e2268", "#fde047"),
    "brown": ("#835432", "#b88860", "#4c2e18", "#fde047"), "green": ("#5e7c16", "#98c038", "#344808", "#fde047"),
    "red": ("#b02e26", "#f07068", "#6a1410", "#fde047"), "black": ("#2a2a30", "#555560", "#101014", "#d946ef"),
}



# ---------------------------------------------------------------- render vectorial
def tier(i):
    """variantes numeradas (I, II, 2...): n gemas doradas en la base"""
    m = re.search(r"(?:\b|_)(i{1,3}|iv|v|\d)\s*$", i["name"].lower().strip(" )")) or re.search(r"[_ ](\d)$", i["id"])
    if not m:
        return 0
    v = m.group(1)
    n = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5}.get(v) or (int(v) if v.isdigit() else 0)
    return n if 1 <= n <= 5 else 0


def pips_svg(n):
    return "".join(f'<path d="M{20 + k * 10} 119 l4 -5 l4 5 l-4 4 Z" fill="url(#g)" stroke="{V.OUT}" stroke-width="1.5"/>' for k in range(n))


def render(i):
    motivo, param, origen = forma(i)
    t = V.tema(tema_item(i))
    cuerpo = V.MOTIVOS[motivo](t, param)
    n = tier(i)
    if n:
        cuerpo += pips_svg(n)
    if origen in ("DEFECTO", "material"):
        PREDETERMINADOS[(origen, motivo)] += 1
    return V.doc(cuerpo, t), (motivo, origen)


# ---------------------------------------------------------------- cofres de ender de colores (variantes)
DYES = ["#f9fffe", "#f9801d", "#c74ebd", "#3ab3da", "#fed83d", "#80c71f", "#f38baa", "#474f52", "#9d9d97", "#169c9c",
        "#8932b8", "#3c44aa", "#835432", "#5e7c16", "#b02e26", "#1d1d21"]
ENDER_RE = re.compile(r"^COLORED_ENDER_CHEST_(SMALL|BIG)_(\d+)_(\d+)_(\d+)$")


def svg_ender(big):
    t = V.tema(TEMAS["ender"])
    b = V.P("M12 52 C12 24 116 24 116 52 V108 H12 Z", "url(#mh)") + V.R(12, 50, 104, 12, "url(#fr)", 3)
    if big:
        b += V.R(8, 40, 112, 10, "url(#gv)", 4) + V.R(8, 100, 112, 10, "url(#gv)", 4)
    b += V.R(52, 56, 24, 24, "url(#g)", 5) + V.C(64, 68, 4, "#14101e", 2) + V.glow(64, 40, 18)
    b += V.HL("M18 50 C20 36 40 30 60 30", 0.5, 3)
    return V.doc(b, t)


def svg_banda(k):
    x = (24, 52, 80)[k]
    t = V.tema(("#ffffff", "#ffffff", "#c8c8c8", "#ffffff"))
    b = f'<rect x="{x}" y="64" width="24" height="40" rx="3" fill="url(#mv)" stroke="none" opacity=".95"/>'
    b += f'<path d="M{x + 4} 68 V100" stroke="#fff" stroke-width="3" opacity=".8"/>'
    return V.doc(b, t, sombra=False).replace('<ellipse', '<ellipse', 1)


def tex_ender(destino_tex, destino_svg):
    """4 PNG + 2 modelos para 8.192 variantes: el color va en `tints` constantes del case."""
    guardar(svg_ender(False), destino_tex / "ender_chest_small.png", destino_svg / "ender_chest_small.svg")
    guardar(svg_ender(True), destino_tex / "ender_chest_big.png", destino_svg / "ender_chest_big.svg")
    for k in range(3):
        guardar(svg_banda(k), destino_tex / f"ender_chest_band{k + 1}.png", destino_svg / f"ender_chest_band{k + 1}.svg")


TAM = 128


def guardar(svg_text, png, svgp):
    """SVG fuente + PNG 128x128 RGBA cuantizado a paleta (peso bajo, sin banding visible con dither desactivado)."""
    svgp.parent.mkdir(parents=True, exist_ok=True)
    svgp.write_text(svg_text)
    png.parent.mkdir(parents=True, exist_ok=True)
    raw = subprocess.run(["rsvg-convert", "-w", str(TAM), "-h", str(TAM), str(svgp)], check=True, capture_output=True).stdout
    from io import BytesIO
    from PIL import Image
    im = Image.open(BytesIO(raw)).convert("RGBA")
    q = im.quantize(colors=128, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    q.save(png, optimize=True)


TEXROOT = ROOT / "assets/slimefun/textures/item/drakes_proc"
MODROOT = ROOT / "assets/minecraft/models/slimefun/drakes_proc"
SVGROOT = ROOT / "build/slimefun_svg"  # fuentes editables regenerables; fuera de assets/ para no engordar el pack
TD = Path.home() / "Documentos/Desarrollo/Repositorios/drakescraft/Slimefun-Texture-Drake/pack"
DUMP = Path.home() / "Documentos/Desarrollo/Repositorios/personal/Slimefun-Knowledge-Drake/data/slimefun-dump.json.gz"
KEY = "slimefun:slimefun_item"
# materiales con tinte/estado/especial: si no hay definicion previa NO se crea una (se rompe el vanilla)
ESPECIALES = re.compile(r"(potion|tipped_arrow|crossbow|leaves$|banner|_bed$|sign$|skull|_head$|shulker_box|chest$|"
                        r"firework|map$|shield|spawn_egg|decorated_pot|conduit|bell$|lectern|brewing|trapdoor|fence|"
                        r"button|pressure_plate|_door$|stained_glass_pane|torch|lantern|campfire|candle|cake|"
                        r"grass|fern|vine|lily|bamboo|sapling|flower|tulip|orchid|rail$|cauldron|bundle)")
CUBOS = re.compile(r"(_block$|_concrete$|_terracotta$|_wool$|_planks$|_log$|_wood$|_hyphae$|_stem$|bricks$|^stone$|"
                   r"^smooth_|^polished_|^chiseled_|_ore$|^dirt$|^sand$|^gravel$|^obsidian$|^bedrock$|^netherrack$|"
                   r"^glowstone$|^target$|^clay$|^sea_lantern$|^magma_block$|^lodestone$|^moss_block$|_stained_glass$|"
                   r"^glass$|_nylium$|^basalt$|^cobblestone$|^soul_sand$|^soul_soil$|^mycelium$|^tuff$|^granite$|^diorite$|"
                   r"^andesite$|^sandstone$|^blackstone$|^sponge$|^mud$|^packed_mud$|^packed_ice$|^blue_ice$|^dark_prismarine$|"
                   r"^deepslate_tiles$|^gilded_blackstone$|^quartz_pillar$|^purpur_pillar$|^podzol$|^rooted_dirt$|^tinted_glass$|"
                   r"^copper_grate$|^muddy_mangrove_roots$|^jukebox$)")
ITEMS = re.compile(r"(_dye$|_ingot$|_nugget$|_shard$|_scrap$|^brick$|^nether_brick$|^stick$|^sugar$|^gunpowder$|"
                   r"^redstone$|^glowstone_dust$|_powder$|^emerald$|^diamond$|^quartz$|^coal$|^charcoal$|^paper$|"
                   r"^snowball$|^kelp$|^leather$|^string$|^feather$|^bone$|^slime_ball$|^ghast_tear$|^fire_charge$|"
                   r"_seeds$|^wheat$|^egg$|_stew$|^cooked_|^apple$|^golden_apple$|^bread$|^cookie$|^pumpkin_pie$|"
                   r"_boots$|_leggings$|_helmet$|_chestplate$|_sword$|_pickaxe$|_axe$|_shovel$|_hoe$|^bow$|^trident$|"
                   r"^blaze_rod$|^lapis_lazuli$|_bucket$|^compass$|^clock$|^book$|^enchanted_book$|^name_tag$|^heart_of_the_sea$|"
                   r"^nether_star$|^phantom_membrane$|^echo_shard$|^honeycomb$|^glass_bottle$|^lead$|^rabbit_hide$|^flint$|"
                   r"^dried_kelp$|^raw_iron$|^raw_gold$|^clay_ball$|^ink_sac$|^spider_eye$|^melon_slice$|^sweet_berries$|"
                   r"^poisonous_potato$|^breeze_rod$|^dragon_breath$|^disc_fragment_5$|^experience_bottle$|"
                   r"^enchanted_golden_apple$|^diamond_horse_armor$|^end_crystal$|^amethyst_shard$|^slime_ball$)")


def fallback_vanilla(base):
    if base.endswith("_wall"):
        return f"minecraft:block/{base}_inventory"
    if base.endswith(("_stairs", "_carpet", "_slab")) or CUBOS.search(base):
        return f"minecraft:block/{base}"
    if ITEMS.search(base):
        return f"minecraft:item/{base}"
    return None


def buscar_fallback(base):
    """fallback vanilla para el material: definicion existente en este pack, en Slimefun-Texture-Drake o heuristica"""
    p = TD / "assets/minecraft/items" / f"{base}.json"
    if p.exists():
        fb = json.loads(p.read_text(encoding="utf-8"))["model"].get("fallback")
        if fb:
            return fb
    f = fallback_vanilla(base)
    if f and not ESPECIALES.search(base):
        return {"type": "minecraft:model", "model": f}
    return None


FB_ENDER = {"type": "minecraft:special", "base": "minecraft:item/ender_chest",
            "model": {"type": "minecraft:chest", "texture": "minecraft:ender"}}


def es_envoltura(m):
    return isinstance(m, dict) and m.get("type") == "minecraft:select" and m.get("component") == "minecraft:custom_data" \
        and m.get("property") == "minecraft:component"


def cablear(por_base, quitar_ids):
    """Para cada material: select por custom_data (ids) con fallback = definicion previa (cases por nombre / vanilla)."""
    omitidos, hechos = {}, 0
    for base, casos in por_base.items():
        p = ROOT / "assets/minecraft/items" / f"{base}.json"
        if p.exists():
            doc = json.loads(p.read_text(encoding="utf-8"))
            antes = doc["model"]
        else:
            fb = FB_ENDER if base == "ender_chest" else buscar_fallback(base)
            if fb is None:
                omitidos[base] = len(casos)
                continue
            doc = {"oversized_in_gui": True}
            antes = fb
        if es_envoltura(antes):
            cases, fallback = antes["cases"], antes.get("fallback")
        else:
            cases, fallback = [], antes
        ya = {c["when"]["PublicBukkitValues"][KEY]: c for c in cases if "PublicBukkitValues" in c.get("when", {})}
        for iid, modelo in casos.items():
            ya[iid] = {"when": {"PublicBukkitValues": {KEY: iid}}, "model": modelo}
        cases = [ya[k] for k in sorted(ya)]
        modelo = {"type": "minecraft:select", "property": "minecraft:component", "component": "minecraft:custom_data",
                  "cases": cases}
        if fallback is not None:
            modelo["fallback"] = fallback
        doc = {"model": modelo, **{k: v for k, v in doc.items() if k != "model"}}
        # cases en una linea cada uno: 8.192 variantes ocupan ~2 MB en vez de ~10
        head = {k: v for k, v in modelo.items() if k not in ("cases", "fallback")}
        out = "{\n\t\"model\": {" + json.dumps(head, ensure_ascii=False)[1:-1] + ",\n\t\"cases\": [\n"
        out += ",\n".join("\t\t" + json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in cases)
        out += "\n\t]"
        if fallback is not None:
            out += ",\n\t\"fallback\": " + json.dumps(fallback, ensure_ascii=False, separators=(",", ":"))
        out += "\n\t}"
        for k, v in doc.items():
            if k != "model":
                out += ",\n\t" + json.dumps(k) + ": " + json.dumps(v)
        out += "\n}\n"
        json.loads(out)
        p.write_text(out, encoding="utf-8")
        hechos += len(casos)
    return hechos, omitidos


def ids_cubiertos():
    ids = set()
    for f in glob.glob(str(TD / "**/items/*.json"), recursive=True):
        ids |= set(re.findall(r'"slimefun:slimefun_item"\s*:\s*"([A-Z0-9_]+)"', Path(f).read_text(encoding="utf-8")))
    return ids


def nombres_cubiertos():
    cov = set()

    def walk(o):
        if isinstance(o, dict):
            w = o.get("when")
            if isinstance(w, dict) and "extra" in w:
                cov.add("".join(e.get("text", "") for e in w["extra"] if isinstance(e, dict)).strip())
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for p in glob.glob(str(ROOT / "assets/minecraft/items/*.json")):
        walk(json.loads(Path(p).read_text(encoding="utf-8")))
    return cov


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60] or "item"


def clasificar(i, cub, nombres_dup):
    """-> 'cabeza' | 'cubierto' | 'fantasma' | 'variante-ender' | 'diseno'"""
    cls = i["class"].split(".")[-1]
    if i["material"] == "PLAYER_HEAD":
        return "cabeza"
    if cls == "ColoredEnderChest":
        return "variante-ender"
    if cls == "GhostBlock":
        return "fantasma"
    if i["id"] in cub:
        return "cubierto"
    return "diseno"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", type=Path, default=DUMP)
    ap.add_argument("--addon", action="append", help="solo estos addons (repetible); por defecto todos")
    ap.add_argument("--sheet", type=Path, help="hoja de contacto PNG de lo generado")
    ap.add_argument("--sin-cablear", action="store_true")
    ap.add_argument("--informe", type=Path, default=ROOT / "scripts/slimefun_cobertura.json")
    a = ap.parse_args()
    d = json.loads(gzip.open(a.dump).read())
    items = [i for i in d["items"] if not i["id"].startswith("_UI_")]
    cub = ids_cubiertos()
    por_base, unicos, ya_hash, informe = {}, 0, {}, collections.defaultdict(collections.Counter)
    muestras, origen, motivos, defecto = [], collections.Counter(), collections.Counter(), []
    if not a.addon:
        import shutil
        for d_ in (TEXROOT, MODROOT, SVGROOT):
            shutil.rmtree(d_, ignore_errors=True)
    for i in items:
        if a.addon and i["addon"] not in a.addon:
            continue
        k = clasificar(i, cub, None)
        informe[i["addon"]][k] += 1
        base = i["material"].lower()
        if k == "variante-ender":
            m = ENDER_RE.match(i["id"])
            if not m:
                continue
            tam, x, y, z = m.group(1).lower(), *(int(v) for v in m.groups()[1:])
            tint = lambda col: {"type": "minecraft:constant", "value": int(col.lstrip("#"), 16)}
            por_base.setdefault("ender_chest", {})[i["id"]] = {
                "type": "minecraft:model", "model": f"slimefun/drakes_proc/ender_chest_{tam}",
                "tints": [tint("#ffffff"), tint(DYES[x]), tint(DYES[y]), tint(DYES[z])]}
            continue
        if k != "diseno":
            continue
        px, meta = render(i)
        h = hashlib.md5(px.encode()).hexdigest()
        origen[meta[1]] += 1
        motivos[meta[0]] += 1
        if meta[1] in ("DEFECTO", "material"):
            defecto.append(f"{i['addon']}:{i['id']} ({meta[0]})")
        if h not in ya_hash:
            nombre = f"{slug(i['addon'])}/{slug(i['id'])}"
            ya_hash[h] = nombre
            png = TEXROOT / f"{nombre}.png"
            guardar(px, png, SVGROOT / f"{nombre}.svg")
            m = MODROOT / f"{nombre}.json"
            m.parent.mkdir(parents=True, exist_ok=True)
            m.write_text(json.dumps({"parent": "item/generated", "author": "DrakesCraft Labs",
                                     "textures": {"layer0": f"slimefun:item/drakes_proc/{nombre}"}}) + "\n")
            unicos += 1
            muestras.append((nombre, png))
        por_base.setdefault(base, {})[i["id"]] = {"type": "minecraft:model", "model": f"slimefun/drakes_proc/{ya_hash[h]}"}
    if any(k == "ender_chest" for k in por_base):
        tex_ender(TEXROOT, SVGROOT)
        for tam in ("small", "big"):
            (MODROOT / f"ender_chest_{tam}.json").write_text(json.dumps(
                {"parent": "item/generated", "author": "DrakesCraft Labs", "textures": {
                    "layer0": f"slimefun:item/drakes_proc/ender_chest_{tam}",
                    "layer1": "slimefun:item/drakes_proc/ender_chest_band1",
                    "layer2": "slimefun:item/drakes_proc/ender_chest_band2",
                    "layer3": "slimefun:item/drakes_proc/ender_chest_band3"}}) + "\n")
    hechos, omitidos = (0, {}) if a.sin_cablear else cablear(por_base, None)
    tot = collections.Counter()
    for ad in informe.values():
        tot.update(ad)
    rep = {"total": sum(tot.values()), "por_clase": dict(tot), "por_addon": {k: dict(v) for k, v in informe.items()},
           "texturas_unicas": unicos, "cases_nuevos": hechos, "materiales_omitidos": omitidos,
           "origen_del_motivo": dict(origen), "motivos": dict(motivos), "ids_en_motivo_por_defecto": defecto}
    a.informe.write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in rep.items() if k not in ("por_addon", "ids_en_motivo_por_defecto", "materiales_omitidos")}, ensure_ascii=False))
    if a.sheet:
        hoja(muestras[:600], a.sheet)


def hoja(muestras, destino, lado=64, cols=24):
    from PIL import Image
    filas = (len(muestras) + cols - 1) // cols
    img = Image.new("RGBA", (cols * (lado + 2), filas * (lado + 2)), (60, 56, 80, 255))
    for k, (_, png) in enumerate(muestras):
        im = Image.open(png).convert("RGBA").resize((lado, lado), Image.LANCZOS)
        img.alpha_composite(im, ((k % cols) * (lado + 2), (k // cols) * (lado + 2)))
    img.save(destino)


if __name__ == "__main__":
    main()
