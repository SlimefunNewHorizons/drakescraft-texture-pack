# Cabezas Slimefun: estado del pack

## Cómo se emparejan
`assets/minecraft/items/player_head.json` usa `select` por `minecraft:custom_name` (texto + color + negrita exactos), no por id.
Por eso el nombre en `ITEMS` de `scripts/gen_heads_svg.py` debe ser idéntico al display name de Slimefun (código legacy `&`).
Modelos nuevos: `assets/minecraft/models/slimefun/drakes_heads/<id>.json`; texturas: `assets/drakescraft/textures/heads/<id>.png` (SVG en `heads/svg/`).
Los overlays (`overlay_1_21_6_plus`, `overlay_1_21_11`, `overlay_26_1_2`) están en `pack.mcmeta` pero NO existen en el repo: el script los parchea solos si aparecen (`overlay_*/assets/minecraft/items/player_head.json`).

## Hecho (139 cabezas)
- FN-FAL Amplifications (49): generadores solares I-VIII, Power Xpansion R1-R12, 12 runas, piezas de maquinaria, altar, ensamblaje, reciclador, chatarra.
- RelicsOfCthonia (38): comunes a legendarias + voiders.
- TranscEndence (14 + 5 Daxi): Zot x8, Quirp x4, condensado, scatterer.
- Coronalis (7), ChestTerminal (4), InfinityExpansion (3), AdvancedTech (5), GlobalWarming (3), SlimeChem RTG (2), Galactifun (2), FluffyMachines nodos ender (2), varios (Pandora, Human Skull, Steel Rotor, Stardust Meteor).

## Falta
- Simple-Storage (cofres, celdas, upgrades, chunks/materiales): el nombre sale vacío del código (se construye en runtime); hay que leer el nombre real en juego.
- Duplicados por nombre: `Component Part`/`Funnel Part`/... y sus `_SCRAP` comparten nombre; una sola textura. Si en prod difieren, usar `custom_data`.
- Ítems sin color legacy (`Thorium`, `Food Synthesizer`): el case por nombre es ambiguo, hacerlos por id con `custom_data`.
- Nombres traducidos o con tokens dinámicos (ej. Better-Nuclear-Generator, `HEATED_COOLANT`, `REACTOR_HATCH`).
- Addons no inventariados a fondo: PrivateStorage (parcial), FN-FAL display items, SlimeTinker, Gastronomicon, SlimeFrame, MissileWarfare, Magic-8-Ball, SmallSpace, LuckyBlocks, DrakesNanotech/DrakesTech (`CustomHeads`).
- Validar en cliente real que el nombre emitido por Paper coincide (italic/bold); ajustar `component()` si no.

## Cómo continuar
1. Añadir una línea a `ITEMS`: `ID|&nombre|contenedor|glifo|tema` (contenedores: slab, cube, orb, gem, can, panel, cell; glifos en `GLYPHS`; temas en `THEMES`).
2. `python3 scripts/gen_heads_svg.py` desde la raíz (idempotente; regenera SVG, PNG, modelos y cases).
3. Inventario: `rg 'new SlimefunItemStack\(' <repo>` y comparar nombres con `player_head.json`.
