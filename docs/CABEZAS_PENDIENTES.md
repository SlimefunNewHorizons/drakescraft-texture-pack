# Cabezas Slimefun: estado del pack

## Cómo se emparejan (por id)
`assets/minecraft/items/player_head.json` ahora tiene, en `entries[0]`, un `select` por `minecraft:custom_data`
(`{"PublicBukkitValues":{"slimefun:slimefun_item":"<ID>"}}`, mismo formato que `Slimefun-Texture-Drake/pack/.../player_head.json`).
Su `fallback` es el `select` por `custom_name` original del pack (respaldo) y el de ese, la cabeza de jugador.
Orden de resolución: id Slimefun, luego nombre, luego cabeza normal.

- Modelos: `assets/minecraft/models/slimefun/drakes_heads/<id>.json` (id en minúscula), textura `drakescraft:heads/<id>`.
- Texturas: `assets/drakescraft/textures/heads/<id>.png`; SVG editables en `.../heads/svg/`.
- Overlays (`overlay_*`): no existen en este repo; el script los parchea solos si aparecen.
- Respaldo por nombre (12 ids que no están en el dump del servidor): `CORONALIS_*`, `AIR_QUALITY_METER`, `CINNABARITE`, `RTG_1/2`, `THERMOMETER`.

## Hecho (1191 cabezas: 1179 por id + 12 por nombre)
- Curadas a mano en `ITEMS` (~140): FN-FAL (generadores I-VIII, Power Xpansion R1-R12, runas, piezas y sus `_SCRAP`, altar...), RelicsOfCthonia (38), TranscEndence (Zot/Quirp/Daxi), ChestTerminal, AdvancedTech, InfinityExpansion, RTG, nodos ender, `THORIUM`, `FOOD_SYNTHESIZER`, `FN_GEM_*`.
- Automáticas por reglas (`auto_spec`) desde `scripts/heads_catalog.json`: Cultivation (257), Supreme (248), CrystamaeHistoria (141), Netheopoiesis (73), SlimeFrame (65), SlimyBees (52), Slimefun núcleo (29), DankTech2 (27), PrivateStorage (24), SlimefunWarfare (22), DynaTech, EcoPower, DrakesNanotech, IDreamOfEasy, MagicXpansion, GCE, EquivalencyTech, Networks, LuckyBlocks y otros menores.
- Resueltos al emparejar por id: `_SCRAP` (id propio), `THORIUM`, `FOOD_SYNTHESIZER`, `Dank Pack`/`Prismatic Seed` duplicados por nombre.

## Falta
- SlimeTinker (1136 cabezas: moldes `DIE_*`, partes por material): se resuelven mejor por material/tipo; no tocadas.
- Ya mapeadas por nombre en el pack original y no migradas a id: DyedBackpacks, ExoticGarden, SoulJars, MobCapturer, ElectricSpawners, HotbarPets (conviven por el respaldo de nombre).
- Fuera del dump del servidor (sin id verificable): Simple-Storage (`BLOCK_CHEST_*`, `MATERIAL_*`, `UPGRADE_BARREL`...), Better-Nuclear-Generator (`HEATED_COOLANT`, `REACTOR_HATCH`), Gastronomicon, DrakesTech `CustomHeads`. Se añaden con una línea en `ITEMS` cuando aparezcan en el dump.
- Las reglas automáticas son heurísticas por palabra clave: retocar a mano (`ITEMS` tiene prioridad) los ítems con dibujo poco representativo.
- Validar en cliente 1.21.6+ que el `select` por custom_data hace match (en prod `custom_data` debe contener solo `PublicBukkitValues`).

## Cómo continuar
1. Actualizar catálogo: `python3 scripts/gen_heads_svg.py --build-catalog <Slimefun-Knowledge-Drake>/data/slimefun-dump.json.gz <player_head.json original sin cases propios>` (marca como `covered` los ya mapeados por nombre).
2. Cabeza manual: línea en `ITEMS` `ID|&nombre|contenedor|glifo|tema` (contenedores slab, cube, orb, gem, can, chest, panel, cell; glifos en `GLYPHS`; temas en `THEMES`). Sobrescribe a las reglas.
3. `python3 scripts/gen_heads_svg.py` desde la raíz (idempotente, ~1 min por el rasterizado; `--no-png` para saltarlo).
