#!/usr/bin/env python3
"""Fuentes CC0 -> ogg -> sounds.json (+ docs/SONIDOS.md y seccion de RIGHTS_AND_ATTRIBUTION.md).

Uso:
  python3 scripts/build_sounds.py [--cache DIR] [--no-fetch] [--check]

  --cache DIR   donde se descargan/extraen los paquetes (default ~/.cache/drakescraft-sounds)
  --no-fetch    no descarga (usa lo que haya en la cache)
  --check       solo valida sounds.json contra los .ogg existentes

Solo se descargan paquetes con licencia CC0 (verificada en la pagina de OpenGameArt el 2026-11-12).
Nada de lo descargado se ejecuta; solo se extrae (unzip/7z) y se convierte con ffmpeg.
Los eventos ya existentes en sounds.json (commit e72bc24) se conservan; este script agrega/reescribe
solo los que declara abajo. Todo lo nuevo esta asignado A CIEGAS (nadie escucho los clips): ver CONF.
"""
import argparse, json, os, re, subprocess, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SND = os.path.join(ROOT, "assets", "minecraft", "sounds")
SJ = os.path.join(ROOT, "assets", "minecraft", "sounds.json")
SJ_DC = os.path.join(ROOT, "assets", "drakescraft", "sounds.json")
DOC = os.path.join(ROOT, "docs", "SONIDOS.md")
RIGHTS = os.path.join(ROOT, "RIGHTS_AND_ATTRIBUTION.md")
OGA = "https://opengameart.org/sites/default/files/"
PG = "https://opengameart.org/content/"

# id -> (pagina, autor/uploader, [archivos])    licencia: todas CC0
SOURCES = {
    "snow": (PG + "42-snow-and-gravel-footsteps", "Corsica_S (subido por qubodup)", ["corsica_s-walking_in_snow.7z"]),
    "fantozzi": (PG + "fantozzis-footsteps-grasssand-stone", "Fantozzi", ["Fantozzi-footsteps.7z"]),
    "rpgpack": (PG + "rpg-sound-pack", "artisticdude", ["rpg_sound_pack.zip"]),
    "swishes": (PG + "swishes-sound-pack", "artisticdude", ["swishes.zip"]),
    "rpg50": (PG + "50-rpg-sound-effects", "Kenney", ["RPGsounds_Kenney.zip"]),
    "iface": (PG + "interface-sounds", "Kenney", ["kenney_interfaceSounds.zip"]),
    "scifi": (PG + "sci-fi-sounds", "Kenney", ["sci-fi_sounds.zip"]),
    "digi": (PG + "63-digital-sound-effects-lasers-phasers-space-etc", "Kenney", ["Digital_SFX_Set.zip"]),
    "crunch": (PG + "7-eating-crunches", "tito", ["crunch_-_tito.zip"]),
    "bone": (PG + "deep-bone-crackbreak-sfx", "autor indicado en la pagina", ["deep_breaks.zip"]),
    "water": ("https://opengameart.org/comment/82442", "rubberduck (40 CC0 water / splash / slime SFX)", ["water-splash-slime-sfx.zip"]),
    "splash6": (PG + "6-short-water-splashes", "autor indicado en la pagina", ["ezwa-water_splash.7z"]),
    "ice": (PG + "ice-breakingshattering", "IgnasD", ["IceShatters_0.zip"]),
    "medieval1": (PG + "medieval-sound-effects-weapon-textures", "autor indicado en la pagina (parte 1 de 2)", ["medieval_sfx_textures_1_of_2.7z"]),
    "medieval2": (PG + "medieval-sound-effects-weapon-textures", "autor indicado en la pagina (parte 2 de 2)", ["medieval_sfx_textures_2_of_2.7z"]),
    "fire": (PG + "fire-crackling", "AntumDeluge", ["fire-1_0.ogg"]),
    "firestaff": (PG + "fire-staff-sound-effects", "LEGIT Audio", ["legit_audio_fire_staff_-_free_0.zip"]),
    "dungeon": (PG + "loopable-dungeon-ambience", "autor indicado en la pagina", ["dungeon_ambient_1_0.ogg"]),
    "cavern": (PG + "dark-cavern-ambient", "autor indicado en la pagina", ["dark_cavern_ambient_001.ogg", "dark_cavern_ambient_002.ogg"]),
    "elec": ("https://opengameart.org/node/150369", "Electricity Game Sound Pack",
             ["chargestart.wav", "charge.wav", "crackleelectricityloop.wav", "groundhit.wav", "hit.wav", "powerdown.wav",
              "powerup.wav", "recharge.wav", "shieldhit.wav", "snaploop.wav", "teleport_1.wav", "turbo.wav"]),
    "sp03": (PG + "soundpack-03", "autor indicado en la pagina", ["Sound03ogg.zip"]),
    "mini15": (PG + "sound-effects-mini-pack15", "autor indicado en la pagina", ["Sound effects Mini Pack1.5.zip"]),
}
# Fuentes ya usadas en el commit e72bc24 (no se vuelven a descargar aqui):
PREVIOUS = [
    ("100 CC0 metal and wood SFX", PG + "100-cc0-metal-and-wood-sfx", "CC0"),
    ("Breaking rock", PG + "breaking-rock", "CC0"),
]

CONF = {"N": "nombre del archivo coincide con el evento", "D": "derivado (pitch/filtro/recorte) de un clip analogo",
        "G": "suposicion por analogia (sin pista en el nombre)"}

# ---------------------------------------------------------------- clips
CLIPS = {}  # ruta de salida (sin .ogg, relativa a sounds/) -> dict(src, suf, t, ss, af)


def clip(out, src, suf, t=None, ss=None, af=None):
    CLIPS[out] = dict(src=src, suf=suf, t=t, ss=ss, af=af)
    return out


def series(prefix, src, sufs, **kw):
    return [clip("%s%d" % (prefix, i + 1), src, s, **kw) for i, s in enumerate(sufs)]


def fmt(pattern, nums):
    return [pattern % n for n in nums]


SNOWP = "Corsica_S-Walking_on_snow_covered_gravel_%02d.flac"
GRAVP = "Corsica_S-Walking_on_snow_covered_gravel_and_ice_%02d.flac"
sand = series("step/sand", "fantozzi", ["ogg/Fantozzi-Sand%s%d.ogg" % (s, n) for n in (1, 2, 3) for s in "LR"])
stonef = series("step/stonef", "fantozzi", ["ogg/Fantozzi-Stone%s%d.ogg" % (s, n) for n in (1, 2, 3) for s in "LR"])
snow = series("step/snow", "snow", fmt(SNOWP, range(1, 9)))
snow_dig = series("dig/snow", "snow", fmt(SNOWP, range(9, 13)))
gravel = series("step/gravel", "snow", fmt(GRAVP, range(1, 9)))
gravel_dig = series("dig/gravel", "snow", fmt(GRAVP, range(9, 13)))
cloth = series("step/cloth", "rpg50", ["cloth1.ogg", "cloth2.ogg", "cloth3.ogg", "cloth4.ogg", "clothBelt.ogg", "clothBelt2.ogg"])
cloth_dig = series("dig/cloth", "rpgpack", ["cloth.wav", "cloth-heavy.wav"])
bone = series("dig/bone", "bone", ["Deep Break %d.wav" % n for n in (1, 2, 3, 4, 9)], t=0.45)
chain = series("block/chain", "rpgpack", ["chainmail1.wav", "chainmail2.wav"])
chain_hit = series("block/chain_hit", "rpgpack", ["metal-small1.wav", "metal-small2.wav", "metal-small3.wav"])
chime = series("block/crystal_chime", "iface", ["glass_00%d.ogg" % n for n in range(1, 7)])
crystal_dig = series("dig/crystal", "ice", ["LedasLuzta.ogg", "LedasLuzta2.ogg", "LedasLuzta33.ogg", "LedasLuzta4.ogg", "LedasLuzta5.ogg"], t=0.8)
slime = series("block/slime", "water", ["slime_%02d.ogg" % n for n in range(1, 13)])
slime_ent = series("entity/slime", "rpgpack", ["slime%d.wav" % n for n in (1, 2, 3, 4, 5, 6)])
splash = series("entity/splash", "water", ["splash_%02d.ogg" % n for n in (2, 3, 6, 8, 9, 10, 12, 13)])
splash_big = series("entity/splash_big", "splash6", ["water_splash-01.flac", "water_splash-04.flac", "water_splash-06.flac"])
bubble = series("ui/bubble", "rpgpack", ["bubble.wav", "bubble2.wav", "bubble3.wav"])
bubble_w = series("block/bubble", "water", ["bubble_01.ogg", "bubble_02.ogg", "bubble_03.ogg"])
water_loop = series("block/water_loop", "water", ["loop_water_01.ogg", "loop_water_02.ogg", "loop_water_03.ogg"], t=4)
bubbles_loop = series("ambient/bubbles", "water", ["loop_bubbles_1.ogg", "loop_bubbles_02.ogg"], t=4)
lava_pop = series("block/lava_pop", "water", ["bubble_01.ogg", "bubble_02.ogg", "bubble_03.ogg"], af="lowpass=f=700")
lava_amb = series("ambient/lava", "water", ["loop_bubbles_1.ogg", "loop_bubbles_02.ogg"], t=4, af="lowpass=f=500")
hiss = series("block/extinguish", "water", ["splash_06.ogg", "splash_09.ogg"], af="highpass=f=2500")
click_on = series("block/click_on", "iface", ["toggle_00%d.ogg" % n for n in (1, 2, 3)])
click_off = series("block/click_off", "iface", ["toggle_00%d.ogg" % n for n in (4,)] + ["click_004.ogg", "click_005.ogg"])
plate_on = series("block/plate_on", "iface", ["switch_00%d.ogg" % n for n in (1, 2, 3)])
plate_off = series("block/plate_off", "iface", ["switch_00%d.ogg" % n for n in (4, 5, 6)])
metal_click = series("block/metal_click", "rpg50", ["metalClick.ogg", "metalLatch.ogg"])
wood_click = series("block/wood_click", "rpgpack", ["wood-small.wav"]) + series("block/wood_click_b", "rpg50", ["bookPlace1.ogg", "bookPlace2.ogg"])
fire_crack = [clip("block/fire_crackle%d" % (i + 1), "fire", "fire-1_0.ogg", ss=i * 0.9, t=0.9) for i in range(4)]
fire_use = series("item/fire_use", "firestaff", ["LEGIT_FIR_Fire_Staff %d-Audio.wav" % n for n in (1, 2, 3)], t=1.2)
swish_l = series("entity/swish_light", "swishes", ["swish-12.wav", "swish-13.wav", "swish-11.wav", "swish-2.wav"])
swish_h = series("entity/swish_heavy", "swishes", ["swish-%d.wav" % n for n in (3, 4, 7, 8, 9, 5, 6, 1, 10)])
swing = series("entity/swing", "rpgpack", ["swing.wav", "swing2.wav", "swing3.wav"])
slice_ = series("entity/slice", "rpg50", ["knifeSlice.ogg", "knifeSlice2.ogg"])
chop = clip("entity/chop", "rpg50", "chop.ogg")
bow_shoot = [clip("entity/bow_shoot1", "medieval1", "English Longbow Shoot.wav", t=0.9),
             clip("entity/bow_shoot2", "medieval1", "Scythian Recurve Shoot.wav", t=0.9)]
xbow_shoot = [clip("entity/crossbow_shoot1", "medieval1", "Crossbow Shoot.wav", t=0.9)]
xbow_load = [clip("item/crossbow_load1", "medieval1", "Crossbow Place Bolt.wav", t=0.6),
             clip("item/crossbow_load2", "medieval1", "Crossbow Set Nut Against Sear.wav", t=0.6),
             clip("item/crossbow_load3", "medieval1", "Crossbow Lever Trigger.wav", t=0.6)]
spear = [clip("entity/spear_swing1", "medieval2", "Spear Swing.wav", t=0.9), clip("entity/axe_swing1", "medieval2", "Axe Swing.wav", t=0.9),
         clip("entity/dagger_swing1", "medieval2", "Dagger Swing.wav", t=0.7)]
shield = series("item/shield_block", "scifi", ["impactMetal_00%d.ogg" % n for n in range(0, 5)])
pot = series("item/metal_pot", "rpg50", ["metalPot1.ogg", "metalPot2.ogg", "metalPot3.ogg"], t=0.5)
burp = clip("entity/burp", "rpgpack", "burp.wav")
eat = series("entity/eat", "crunch", ["crunch.%d.ogg" % n for n in range(1, 8)], t=0.7)
drink = series("entity/drink", "rpgpack", ["bottle.wav", "bubble.wav", "bubble2.wav"])
xp = series("entity/xp", "mini15", ["OGG/Coin%s.ogg" % s for s in ("", "1", "2", "3", "4")], t=0.3)
levelup = clip("entity/levelup", "mini15", "1up/OGG/1up.ogg")
pickup = series("entity/pickup", "iface", ["pluck_001.ogg", "pluck_002.ogg", "tick_004.ogg"])
toast = series("ui/toast", "iface", ["confirmation_001.ogg", "confirmation_002.ogg", "confirmation_003.ogg"])
select = series("ui/select", "iface", ["select_00%d.ogg" % n for n in (1, 2, 3)])
open_ = series("ui/open", "iface", ["open_001.ogg", "open_002.ogg"])
close_ = series("ui/close", "iface", ["close_001.ogg", "close_002.ogg"])
error = series("ui/error", "iface", ["error_001.ogg", "error_002.ogg"])
page = series("ui/page", "rpg50", ["bookFlip1.ogg", "bookFlip2.ogg", "bookFlip3.ogg"])
bookput = series("ui/book_put", "rpg50", ["bookPlace1.ogg", "bookPlace2.ogg", "bookPlace3.ogg"])
eq_leather = series("armor/equip_leather", "rpg50", ["handleSmallLeather.ogg", "handleSmallLeather2.ogg", "dropLeather.ogg"])
eq_cloth = series("armor/equip_cloth", "rpgpack", ["armor-light.wav", "cloth-heavy.wav"])
hum = series("tech/hum", "scifi", ["spaceEngineLow_00%d.ogg" % n for n in (0, 1, 2)], t=2.5)
engine = series("tech/engine", "scifi", ["engineCircular_00%d.ogg" % n for n in (0, 1)], t=2.5)
computer = series("tech/computer", "scifi", ["computerNoise_00%d.ogg" % n for n in (0, 1, 2)], t=1.5)
spark = (series("tech/spark", "digi", ["zap1.mp3", "zap2.mp3", "zapTwoTone.mp3"])
         + [clip("tech/spark4", "elec", "crackleelectricityloop.wav"), clip("tech/spark5", "elec", "snaploop.wav", t=0.8)])
power_up = (series("tech/power_up", "digi", ["powerUp1.mp3", "powerUp5.mp3"]) + [clip("tech/power_up3", "elec", "powerup.wav")])
power_down = [clip("tech/power_down1", "elec", "powerdown.wav"), clip("tech/power_down2", "digi", "lowDown.mp3")]
charge = [clip("tech/charge1", "elec", "charge.wav", t=2.0), clip("tech/charge2", "elec", "chargestart.wav", t=2.0)]
force = series("tech/force", "scifi", ["forceField_00%d.ogg" % n for n in (0, 1, 2)])
gear = (series("tech/gear", "rpgpack", ["metal-small1.wav", "metal-small2.wav", "metal-small3.wav"])
        + [clip("tech/gear4", "rpg50", "metalLatch.ogg")])
laser = series("tech/laser", "scifi", ["laserSmall_00%d.ogg" % n for n in (0, 1, 2)])
teleport = clip("tech/teleport", "elec", "teleport_1.wav")
explo = series("entity/explode", "sp03", ["explosion0%d.ogg" % n for n in (1, 2, 3, 4)], t=1.8)
explo_low = series("entity/explode_low", "scifi", ["lowFrequency_explosion_00%d.ogg" % n for n in (0, 1)])
cave = ([clip("ambient/cave%d" % (i + 1), "dungeon", "dungeon_ambient_1_0.ogg", ss=s, t=9) for i, s in enumerate((5, 22, 40, 58, 76))]
        + [clip("ambient/cave%d" % (i + 6), "cavern", "dark_cavern_ambient_00%d.ogg" % (1 + i % 2), ss=s, t=9)
           for i, s in enumerate((12, 33, 61))])

# ---------------------------------------------------------------- eventos
EVENTS = {}   # evento -> dict(clips=[(nombre, pitch|None)], vol, conf, stream)
EVENTS_DC = {}


def _norm(clips, pitch):
    return [(c, pitch) if isinstance(c, str) else c for c in clips]


def E(ev, clips, vol=0.7, pitch=None, conf="N", stream=False, dc=False):
    (EVENTS_DC if dc else EVENTS)[ev] = dict(clips=_norm(clips, pitch), vol=vol, conf=conf, stream=stream)


def M(mat, step, hit=None, brk=None, place=None, fall=None, vol=0.7, pitch=None, conf="N"):
    """block.<mat>.{step,hit,break,place,fall} reusando listas de clips."""
    hit = hit or step
    E("block.%s.step" % mat, step, vol * 0.8, pitch, conf)
    E("block.%s.hit" % mat, hit, vol * 0.7, pitch, conf)
    E("block.%s.break" % mat, brk or hit, vol, pitch, conf)
    E("block.%s.place" % mat, place or hit, vol * 0.85, pitch, conf)
    E("block.%s.fall" % mat, fall or step, vol * 0.7, pitch, conf)


# Suelos y materiales
M("sand", sand, brk=sand, vol=0.7)
M("gravel", gravel, hit=gravel_dig, brk=gravel_dig + gravel, place=gravel_dig, vol=0.7, conf="D")  # tierra y grava comparten block.gravel
M("snow", snow, hit=snow_dig, brk=snow_dig + snow, place=snow_dig, vol=0.7)
M("powder_snow", snow, hit=snow_dig, brk=snow_dig, place=snow_dig, vol=0.6, pitch=0.85, conf="D")
M("wool", cloth, hit=cloth_dig, brk=cloth_dig + cloth, place=cloth_dig, vol=0.7)
M("bone_block", bone, brk=bone, hit=bone, place=bone, fall=bone, vol=0.7, conf="D")
M("chain", chain, hit=chain_hit, brk=chain_hit, place=chain, fall=chain, vol=0.6)
M("amethyst_block", chime, hit=chime, brk=crystal_dig, place=chime, fall=chime, vol=0.6, conf="G")
M("amethyst_cluster", chime, hit=chime, brk=crystal_dig, place=chime, fall=chime, vol=0.6, conf="G")
M("slime_block", slime, vol=0.7)
M("honey_block", slime, vol=0.6, pitch=0.8, conf="D")
M("mud", slime, vol=0.6, pitch=0.7, conf="G")
M("soul_sand", sand, vol=0.7, pitch=0.7, conf="D")
M("soul_soil", sand, vol=0.7, pitch=0.8, conf="D")
M("netherrack", stonef, hit=stonef, brk=stonef + ["dig/stone_break1"], vol=0.75, pitch=0.8, conf="D")
M("basalt", stonef, hit=stonef, brk=stonef + ["dig/stone_break1"], vol=0.8, pitch=0.9, conf="D")
M("nether_bricks", stonef, vol=0.75, pitch=0.9, conf="D")
M("ancient_debris", chain_hit, brk=chain_hit + ["dig/metal_hit1"], vol=0.7, pitch=0.7, conf="D")
M("roots", ["step/grass1", "step/grass2", "step/grass3", "step/leaves1", "step/leaves2"], vol=0.6, pitch=0.8, conf="D")
M("hanging_roots", ["step/leaves1", "step/leaves2", "step/leaves3"], vol=0.5, pitch=0.9, conf="D")
M("rooted_dirt", gravel, hit=gravel_dig, brk=gravel_dig, vol=0.6, pitch=0.8, conf="D")
M("moss", ["step/grass4", "step/grass5", "step/grass6"], vol=0.6, pitch=0.8, conf="D")
M("vine", ["step/leaves4", "step/leaves5", "step/leaves6"], vol=0.5, pitch=0.9, conf="D")
M("bamboo", ["dig/wood_hit1", "dig/wood_hit2", "dig/wood_hit3"], brk=["dig/wood_break1", "dig/wood_break2"], vol=0.7, pitch=1.4, conf="D")
M("bamboo_wood", ["step/wood1", "step/wood2", "step/wood3"], brk=["dig/wood_break3", "dig/wood_break4"], vol=0.7, pitch=1.2, conf="D")
M("scaffolding", ["dig/wood_hit4", "dig/wood_hit5"], brk=["dig/wood_break5"], vol=0.7, pitch=1.4, conf="D")
M("cherry_wood", ["step/wood4", "step/wood5", "step/wood6"], brk=["dig/wood_break6"], vol=0.7, pitch=1.1, conf="D")
M("nether_wood", ["step/wood1", "step/wood2"], brk=["dig/wood_break1"], vol=0.7, pitch=0.8, conf="D")
M("cherry_leaves", ["step/leaves1", "step/leaves2", "step/leaves3"], vol=0.6, pitch=1.15, conf="D")
M("nether_wart", ["step/leaves1", "step/leaves2", "step/leaves3"], vol=0.6, pitch=0.75, conf="D")
M("nylium", ["step/grass1", "step/grass2", "step/grass3"], vol=0.65, pitch=0.85, conf="D")
M("wet_grass", ["step/grass4", "step/grass5", "step/grass6"], vol=0.6, pitch=0.9, conf="D")
M("sweet_berry_bush", ["step/leaves4", "step/leaves5"], vol=0.5, pitch=1.1, conf="D")
M("coral_block", stonef, vol=0.7, pitch=1.2, conf="D")
M("sculk", slime, vol=0.4, pitch=0.6, conf="G")

# Cristal de amatista (eventos extra)
E("block.amethyst_block.chime", chime, 0.6, conf="G")
E("block.amethyst_block.resonate", chime, 0.5, 0.6, conf="G")
for s in ("small", "medium", "large"):
    E("block.%s_amethyst_bud.break" % s, crystal_dig, 0.55, conf="G")
    E("block.%s_amethyst_bud.place" % s, chime, 0.5, conf="G")
E("block.amethyst_cluster.fall", chime, 0.5, conf="G")

# Liquidos, burbujas, fuego, lava
E("block.water.ambient", water_loop, 0.5, conf="D")
E("block.lava.ambient", lava_amb, 0.5, conf="D")
E("block.lava.pop", lava_pop, 0.6, conf="D")
E("block.lava.extinguish", hiss, 0.6, conf="D")
E("block.fire.extinguish", hiss, 0.5, conf="D")
E("block.fire.ambient", fire_crack, 0.5, conf="N")
E("block.furnace.fire_crackle", fire_crack, 0.5, conf="N")
E("block.blastfurnace.fire_crackle", fire_crack, 0.6, 0.85, conf="D")
E("block.smoker.smoke", fire_crack, 0.45, 1.1, conf="D")
E("block.campfire.crackle", fire_crack, 0.55, conf="N")
E("block.brewing_stand.brew", bubble_w + bubble, 0.5, conf="G")
E("block.bubble_column.bubble_pop", bubble_w, 0.5, conf="N")
E("block.bubble_column.upwards_ambient", bubbles_loop, 0.4, conf="N")
E("block.bubble_column.upwards_inside", bubbles_loop, 0.4, conf="N")
E("block.bubble_column.whirlpool_ambient", bubbles_loop, 0.4, 0.8, conf="D")
E("block.bubble_column.whirlpool_inside", bubbles_loop, 0.4, 0.8, conf="D")
E("ambient.underwater.loop.additions", bubble_w, 0.4, conf="G")
E("ambient.underwater.enter", splash, 0.5, conf="G")
E("ambient.underwater.exit", splash, 0.5, conf="G")
E("ui.hud.bubble_pop", bubble, 0.6, conf="N")
E("entity.player.splash", splash, 0.7, conf="N")
E("entity.player.splash.high_speed", splash_big, 0.8, conf="N")
E("entity.generic.splash", splash, 0.6, conf="N")
E("entity.player.swim", splash, 0.4, 1.2, conf="D")
E("entity.boat.paddle_water", splash, 0.4, 1.1, conf="D")
E("entity.fishing_bobber.splash", splash, 0.5, 1.3, conf="D")
E("entity.fishing_bobber.retrieve", splash, 0.5, 1.1, conf="D")
E("item.bucket.fill", splash, 0.6, 0.9, conf="G")
E("item.bucket.empty", splash_big, 0.7, conf="G")
E("item.bucket.fill_lava", lava_pop, 0.7, conf="D")
E("item.bucket.empty_lava", lava_pop, 0.8, 0.9, conf="D")
E("item.bottle.fill", bubble_w, 0.6, conf="G")
E("item.bottle.empty", bubble_w, 0.6, 0.9, conf="G")
E("item.firecharge.use", fire_use, 0.6, conf="G")
E("item.flintandsteel.use", fire_use, 0.5, 1.3, conf="G")
E("entity.splash_potion.break", ["step/glass1", "step/glass2"] + splash, 0.7, conf="D")
E("entity.splash_potion.throw", swish_l, 0.6, conf="G")
E("entity.slime.squish", slime_ent, 0.7, conf="N")
E("entity.slime.squish_small", slime_ent, 0.6, 1.3, conf="D")
E("entity.slime.jump", slime_ent, 0.6, conf="N")
E("entity.slime.jump_small", slime_ent, 0.5, 1.3, conf="D")
E("entity.slime.attack", slime_ent, 0.7, 0.8, conf="D")
E("entity.magma_cube.squish", slime_ent, 0.6, 0.7, conf="D")

# Botones, palancas, placas, mecanismos
E("block.stone_button.click_on", click_on, 0.6, conf="G")
E("block.stone_button.click_off", click_off, 0.6, conf="G")
E("block.wooden_button.click_on", wood_click, 0.6, conf="G")
E("block.wooden_button.click_off", wood_click, 0.5, 0.85, conf="D")
E("block.stone_pressure_plate.click_on", plate_on, 0.6, conf="G")
E("block.stone_pressure_plate.click_off", plate_off, 0.6, conf="G")
E("block.wooden_pressure_plate.click_on", wood_click, 0.6, 0.8, conf="D")
E("block.wooden_pressure_plate.click_off", wood_click, 0.5, 0.7, conf="D")
E("block.metal_pressure_plate.click_on", metal_click, 0.6, conf="G")
E("block.metal_pressure_plate.click_off", metal_click, 0.5, 0.85, conf="D")
E("block.comparator.click", click_on, 0.5, 1.3, conf="D")
E("block.dispenser.dispense", metal_click + swish_l, 0.6, conf="G")
E("block.dispenser.fail", click_off + error, 0.6, 0.8, conf="G")
E("block.dispenser.launch", swish_h, 0.7, conf="G")
E("block.ender_chest.open", force, 0.6, conf="G")
E("block.ender_chest.close", force, 0.6, 0.8, conf="D")
E("block.shulker_box.open", force, 0.5, 1.1, conf="G")
E("block.shulker_box.close", force, 0.5, 0.9, conf="D")
E("block.anvil.break", ["dig/metal_slam1"] + shield, 0.8, conf="G")
E("block.anvil.destroy", ["dig/metal_slam1"] + shield, 0.8, 0.9, conf="G")
E("block.enchantment_table.use", power_up, 0.6, conf="G")
E("block.beacon.ambient", hum, 0.4, conf="G")
E("block.beacon.activate", power_up, 0.7, conf="G")
E("block.beacon.deactivate", power_down, 0.7, conf="G")
E("block.beacon.power_select", charge, 0.7, conf="G")
E("block.conduit.ambient", force, 0.4, conf="G")
E("block.conduit.activate", power_up, 0.6, conf="G")
E("block.conduit.deactivate", power_down, 0.6, conf="G")
E("block.respawn_anchor.charge", charge, 0.7, conf="G")
E("block.respawn_anchor.deplete", power_down, 0.7, conf="G")
E("block.respawn_anchor.set_spawn", power_up, 0.7, conf="G")
E("block.end_portal.spawn", explo_low, 0.8, conf="G")
E("block.portal.travel", [teleport], 0.6, conf="G")

# Combate y armas
E("entity.player.attack.weak", swish_l + slice_ + spear[2:], 0.7, conf="G")
E("entity.player.attack.strong", swing + swish_h[:3], 0.75, conf="G")
E("entity.player.attack.sweep", swish_h + spear[1:2], 0.75, conf="G")
E("entity.player.attack.crit", shield[:3] + swing, 0.7, 1.2, conf="G")
E("entity.player.attack.knockback", ["dig/metal_slam1"] + swish_h[:2], 0.75, conf="G")
E("entity.player.attack.nodamage", click_off, 0.5, 0.8, conf="G")
E("entity.arrow.shoot", bow_shoot, 0.7, conf="N")
E("entity.arrow.hit", [chop, "dig/wood_hit1", "dig/wood_hit2"], 0.6, conf="G")
E("entity.arrow.hit_player", click_on + chime[:2], 0.6, conf="G")
E("entity.skeleton.shoot", bow_shoot, 0.6, conf="N")
E("item.crossbow.shoot", xbow_shoot, 0.75, conf="N")
E("item.crossbow.loading_start", xbow_load[:1], 0.6, conf="N")
E("item.crossbow.loading_middle", xbow_load[1:2], 0.6, conf="N")
E("item.crossbow.loading_end", xbow_load[2:], 0.6, conf="N")
E("item.crossbow.quick_charge_1", xbow_load[:1], 0.6, 1.2, conf="D")
E("item.crossbow.quick_charge_2", xbow_load[1:2], 0.6, 1.2, conf="D")
E("item.crossbow.quick_charge_3", xbow_load[2:], 0.6, 1.2, conf="D")
E("item.crossbow.hit", [chop, "dig/wood_hit3"], 0.6, conf="G")
E("item.trident.throw", spear[:1], 0.7, conf="N")
E("item.trident.hit", [chop, "dig/metal_hit1", "dig/metal_hit2"], 0.7, conf="G")
E("item.trident.hit_ground", ["dig/metal_hit3", "dig/metal_hit4"], 0.7, conf="G")
E("item.trident.return", swish_h[:3], 0.6, 1.1, conf="G")
for i, p in ((1, 1.0), (2, 0.9), (3, 0.8)):
    E("item.trident.riptide_%d" % i, swish_h + splash[:2], 0.7, p, conf="G")
E("item.trident.thunder", explo_low, 0.8, conf="G")
E("item.shield.block", shield + pot, 0.75, conf="N")
E("item.shield.break", shield[3:] + ["dig/wood_break1"], 0.8, conf="G")
E("item.elytra.flying", swish_h[4:], 0.3, 0.7, conf="G")
E("entity.item.break", shield[:3] + ["dig/metal_hit5"], 0.7, 1.3, conf="G")
E("entity.generic.explode", explo, 0.8, conf="N")
E("entity.lightning_bolt.impact", explo_low, 0.8, conf="G")
E("entity.horse.armor", chain, 0.6, conf="N")
E("entity.iron_golem.repair", ["dig/metal_hit1", "dig/metal_hit2", "item/hammer1"], 0.7, conf="G")

# Comer, beber, experiencia, objetos
E("entity.generic.eat", eat, 0.8, conf="N")
E("entity.generic.drink", drink, 0.7, conf="N")
E("entity.player.burp", [burp], 0.7, conf="N")
E("item.honey_bottle.drink", drink, 0.7, 0.9, conf="D")
E("entity.experience_orb.pickup", xp, 0.5, conf="G")
E("entity.player.levelup", [levelup], 0.7, conf="G")
E("entity.item.pickup", pickup, 0.5, conf="G")
E("item.book.page_turn", page, 0.7, conf="N")
E("item.book.put", bookput, 0.7, conf="N")
E("item.armor.equip_leather", eq_leather, 0.7, conf="N")
E("item.armor.equip_generic", eq_cloth + eq_leather[:1], 0.7, conf="G")
E("item.armor.equip_elytra", eq_cloth, 0.7, 0.9, conf="D")
E("item.armor.equip_turtle", eq_leather, 0.7, 0.8, conf="D")

# UI
E("ui.toast.in", toast, 0.6, conf="G")
E("ui.toast.out", close_, 0.5, conf="G")
E("ui.toast.challenge_complete", toast + [levelup], 0.7, conf="G")
E("ui.loom.select_pattern", select, 0.6, conf="G")
E("ui.loom.take_result", select, 0.6, 1.2, conf="G")
E("ui.stonecutter.select_recipe", select, 0.5, 0.9, conf="G")
E("ui.stonecutter.take_result", plate_on, 0.6, conf="G")
E("ui.cartography_table.take_result", page, 0.6, conf="G")
E("item.spyglass.use", open_, 0.5, conf="G")
E("item.spyglass.stop_using", close_, 0.5, conf="G")
E("item.lodestone_compass.lock", metal_click, 0.6, conf="G")

# Ambiente de cuevas y nether
E("ambient.cave", cave, 0.45, conf="G")
for biome in ("basalt_deltas", "crimson_forest", "nether_wastes", "soul_sand_valley", "warped_forest"):
    E("ambient.%s.additions" % biome, cave[3:], 0.35, 0.7, conf="G")

# Tech (eventos propios en el namespace drakescraft: /playsound drakescraft:tech.spark ...)
for name, clips, vol, conf in (
        ("tech.hum", hum, 0.5, "N"), ("tech.engine", engine, 0.5, "N"), ("tech.computer", computer, 0.5, "N"),
        ("tech.spark", spark, 0.6, "N"), ("tech.zap", spark[:3], 0.6, "N"), ("tech.power_up", power_up, 0.6, "N"),
        ("tech.power_down", power_down, 0.6, "N"), ("tech.charge", charge, 0.6, "N"), ("tech.force_field", force, 0.5, "N"),
        ("tech.gears", gear, 0.6, "G"), ("tech.laser", laser, 0.5, "N"), ("tech.teleport", [teleport], 0.6, "N"),
        ("tech.explosion", explo_low + explo[:2], 0.7, "N")):
    E(name, clips, vol, conf=conf, dc=True)

FALTA = [
    "Pasos de armadura (no existe evento vanilla; requeriria plugin/servidor que emita un sonido propio).",
    "Voz del jugador (entity.player.hurt, death, breath): no hay un pack CC0 de voces apropiado verificado.",
    "Lava real (block.lava.ambient/pop estan derivados de burbujas de agua con paso bajo): buscar grabacion CC0 de lava/barro.",
    "Tierra/dirt real: vanilla usa block.gravel.* para tierra; esta mapeado con grava+nieve (D). Falta un clip de tierra suelta.",
    "Hielo/escarcha dedicado: vanilla usa block.glass.* (ya mapeado antes) y block.powder_snow.*; los clips de hielo solo se usan en cristal de amatista.",
    "Cadena de hierro/cobre (block.iron_chain / copper_chain en versiones nuevas): solo block.chain.*.",
    "Engranajes reales (tech.gears usa metal chico + pestillo): falta grabacion CC0 de mecanismo/engranaje.",
    "Zumbido electrico sostenido (tech.hum) es el motor de la libreria Kenney; falta un hum de transformador CC0.",
    "Musica de discos, bloques de nota, campanas, truenos y mobs: fuera del alcance de este lote.",
    "Slimefun usa solo eventos vanilla (Sound.*); no hay eventos custom. Se remapearon los que mas usa (arrow.hit_player, item.break, "
    "generic.explode, lava.pop, piston, entity.player.splash, book.put/page_turn...). Eventos drakescraft:tech.* quedan listos para "
    "que un addon los emita con Bukkit playSound(\"drakescraft:tech.spark\").",
]


# ---------------------------------------------------------------- motor
def fetch(cache):
    os.makedirs(cache, exist_ok=True)
    for sid, (_, _, files) in SOURCES.items():
        d = os.path.join(cache, sid)
        os.makedirs(d, exist_ok=True)
        for f in files:
            p = os.path.join(d, f)
            if not os.path.exists(p):
                print("descargando", sid, f)
                req = urllib.request.Request(OGA + urllib.parse.quote(f), headers={"User-Agent": "Mozilla/5.0"})
                with open(p, "wb") as fh:
                    fh.write(urllib.request.urlopen(req, timeout=120).read())
            x = os.path.join(d, "x_" + f)
            if f.endswith((".zip", ".7z")) and not os.path.isdir(x):
                os.makedirs(x)
                cmd = ["unzip", "-q", "-o", p, "-d", x] if f.endswith(".zip") else ["7z", "x", "-y", "-o" + x, p]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)


_index = {}


def find(cache, src, suf):
    if src not in _index:
        ls = []
        for dp, _, fs in os.walk(os.path.join(cache, src)):
            if "__MACOSX" in dp:
                continue
            ls += [os.path.join(dp, f) for f in fs if not f.startswith("._")]
        _index[src] = ls
    hits = [p for p in _index[src] if p.endswith("/" + suf) or p == suf]
    if not hits:
        raise SystemExit("no encontrado: %s / %s" % (src, suf))
    return sorted(hits, key=len)[0]


def convert(cache):
    n = 0
    for out, c in sorted(CLIPS.items()):
        dst = os.path.join(SND, out + ".ogg")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        af = "silenceremove=start_periods=1:start_threshold=-50dB"
        if c["af"]:
            af += "," + c["af"]
        if c["t"]:
            af += ",afade=t=out:st=%.2f:d=0.08" % max(c["t"] - 0.08, 0)
        af += ",loudnorm=I=-20:TP=-3"
        cmd = ["ffmpeg", "-y", "-v", "error"]
        if c["ss"]:
            cmd += ["-ss", str(c["ss"])]
        cmd += ["-i", find(cache, c["src"], c["suf"])]
        if c["t"]:
            cmd += ["-t", str(c["t"])]
        cmd += ["-ac", "1", "-ar", "44100", "-af", af, "-c:a", "libvorbis", "-q:a", "3", dst]
        subprocess.run(cmd, check=True)
        n += 1
    print("convertidos", n)


def sound_entries(ev, ns=""):
    out = []
    for name, pitch in ev["clips"]:
        e = {"name": ns + name, "volume": round(ev["vol"], 2)}
        if pitch:
            e["pitch"] = pitch
        if ev["stream"]:
            e["stream"] = True
        out.append(e)
    return out


def write_json(path, events, replace):
    data = json.load(open(path)) if os.path.exists(path) else {}
    for k, ev in events.items():
        v = {"sounds": sound_entries(ev, "" if replace else "minecraft:")}
        if replace:
            v = {"replace": True, **v}
        data[k] = v
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return data


def check():
    bad = 0
    for path in (SJ, SJ_DC):
        if not os.path.exists(path):
            continue
        for ev, v in json.load(open(path)).items():
            for s in v["sounds"]:
                nm = s if isinstance(s, str) else s["name"]
                nm = nm.split(":", 1)[-1]
                if not os.path.exists(os.path.join(SND, nm + ".ogg")):
                    print("FALTA", ev, nm)
                    bad += 1
    print("check:", "OK" if not bad else "%d errores" % bad)
    return bad


def mb():
    tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(SND) for f in fs)
    return tot / 1048576


def docs():
    L = ["# Sonidos del pack", "",
         "Generado por `scripts/build_sounds.py` (no editar a mano). Todo lo nuevo esta asignado **A CIEGAS**: nadie escucho los clips; "
         "la asignacion sale del nombre del archivo, la duracion y la analogia con el evento vanilla. Hay que probarlo en el juego.", "",
         "Confianza: " + "; ".join("**%s** = %s" % kv for kv in CONF.items()), "",
         "Los eventos previos (commit e72bc24: rotura/golpe/puertas/cofres/yunque/herramientas/armaduras) no se listan aqui.",
         "Tierra (`dirt`) y grava comparten `block.gravel.*` en vanilla.", "",
         "## Mapa evento -> clips (vanilla, `assets/minecraft/sounds.json`)", "",
         "| Evento | Conf. | Vol | Pitch | Clips |", "|---|---|---|---|---|"]
    def rows(evs):
        for k in sorted(evs):
            e = evs[k]
            ps = sorted({p for _, p in e["clips"] if p})
            L.append("| `%s` | %s | %s | %s | %s |" % (k, e["conf"], round(e["vol"], 2), "/".join(map(str, ps)) or "-",
                                                      ", ".join(sorted({c for c, _ in e["clips"]}))))
    rows(EVENTS)
    L += ["", "## Eventos propios (`assets/drakescraft/sounds.json`, namespace `drakescraft`)", "",
          "| Evento | Conf. | Vol | Pitch | Clips |", "|---|---|---|---|---|"]
    rows(EVENTS_DC)
    L += ["", "## Fuentes (todas CC0)", ""]
    for sid, (pg, au, fs) in SOURCES.items():
        L.append("- `%s`: %s - %s - %s" % (sid, au, pg, ", ".join(fs)))
    L += ["", "## Que falta", ""] + ["- " + f for f in FALTA]
    open(DOC, "w").write("\n".join(L) + "\n")


def rights():
    B, E_ = "<!-- sounds:begin -->", "<!-- sounds:end -->"
    s = "\n".join([B, "## Sonidos CC0 ampliados (build_sounds.py, 2026-11-12)",
                   "Todos CC0 (dominio publico), licencia verificada en cada pagina de OpenGameArt. Reconvertidos a OGG mono 44.1 kHz y normalizados.",
                   ""] + ["- %s - %s - %s (CC0)" % (au, pg, ", ".join(fs)) for _, (pg, au, fs) in SOURCES.items()] + ["", E_])
    t = open(RIGHTS).read() if os.path.exists(RIGHTS) else ""
    if B in t:
        t = re.sub(re.escape(B) + ".*?" + re.escape(E_), lambda m: s, t, flags=re.S)
    else:
        t = t.rstrip("\n") + "\n\n" + s + "\n"
    open(RIGHTS, "w").write(t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.expanduser("~/.cache/drakescraft-sounds"))
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(check())
    if not a.no_fetch:
        fetch(a.cache)
    convert(a.cache)
    write_json(SJ, EVENTS, True)
    write_json(SJ_DC, EVENTS_DC, False)
    docs()
    rights()
    print("eventos nuevos: %d (+%d drakescraft); sounds/ = %.2f MB" % (len(EVENTS), len(EVENTS_DC), mb()))
    sys.exit(check())


if __name__ == "__main__":
    main()
