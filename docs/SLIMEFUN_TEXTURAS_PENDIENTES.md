# Slimefun: texturas por id, estado y pendientes

Mapeo por **id** (`custom_data` -> `PublicBukkitValues` -> `slimefun:slimefun_item`), no por nombre. Fuente de ids:
volcado del plugin `Slimefun-Knowledge-Drake/data/slimefun-dump.json.gz` (14-oct-2026, **15986 items, 64 addons**).

## Qué se hizo

- Arte **vectorial** (SVG 128x128 con degradados, relieve, brillos de arista, sombra suave, borde #0d0a14) exportado a PNG
  128x128 con `rsvg-convert` y cuantizado a 128 colores (PIL) para el peso. Compatible 1.20-26.2 (cualquier tamaño cuadrado).
- `scripts/slimefun_vector.py`: biblioteca de motivos combinables y parametrizables por tema (luz/medio/sombra/acento):
  PCB con pistas/chip/conector, chip, generador con turbina y bobina, panel solar con celdas, cable aislado/desnudo con
  conectores, tanque con liquido, reactor, forja, cantera con taladro, pedestal/altar, maquina con pantalla y 22 glifos,
  baterias/condensadores, lingote/pepita/placa/polvo/gema/orbe/nucleo, ampolla, cuenco, olla, sarten, vaso, fruta, semilla,
  vaina, hoja, seta, filete, huevo, flor, armaduras (casco, peto, grebas, botas), escudo, herramientas, arcos, tridente,
  baston, libro, pergamino, carta, llave, talisman, anillo, runa, mochila, kit, modulo, marco, estandarte, panal...
- `scripts/gen_slimefun_svg.py`: clasifica cada id y elige motivo por **nombre, id, grupo de la guia, clase y lore** del volcado,
  con tinte por material/addon/planta (ej. `Chopped|Mashed|Sliced|Ground|Blended|Boiled|Fried|Grilled X` comparten el color de X
  y cambian de forma); tiers I-V/1-5 anaden gemas doradas. Los SVG identicos se comparten entre ids. Salidas:
  `assets/slimefun/textures/item/drakes_proc/<addon>/`, `assets/minecraft/models/slimefun/drakes_proc/`, SVG fuente en
  `build/slimefun_svg/` (no versionado, regenerable: pesa 12 MB, fuera del pack).
- Cableado: cada `items/<material>.json` pasa a `select` sobre `custom_data` (cases ordenados por id) con **fallback = la
  definicion previa** (cases por nombre o vanilla); nada anterior se pierde. Se crean 228 definiciones nuevas de material con
  el fallback vanilla copiado de `Slimefun-Texture-Drake` o de una lista segura. No se toca `player_head.json`.
- Variantes: los 8.192 `COLORED_ENDER_CHEST_{SMALL|BIG}_a_b_c` usan 5 PNG + 2 modelos; el color (16 tintes de dye) va en
  `tints` constantes de cada case (3 bandas teñibles). Cero PNG por variante.
- Ids ya presentes en `Slimefun-Texture-Drake` (1156): se omiten para no duplicar.
- Validar: `python3 scripts/validar_slimefun_ids.py` (JSON valido, modelo y textura existentes, PNG 128x128 con alfa).

## Cobertura (15986 ids)

| Clase | Ids | Estado |
|---|---|---|
| Diseño unico procedural | 3327 | 1619 PNG unicos tras deduplicar |
| Variante (cofre ender de colores) | 8192 | 5 PNG + tints |
| Ya cubierto (Slimefun-Texture-Drake) | 1156 | sin cambios |
| Cabeza (`player_head`) | 2935 | otro agente |
| Fantasma (`GhostBlock`, FoxyMachines) | 376 | sin textura propia: el item **es** el bloque vanilla (`Ghost Block: Acacia Log` = tronco); el vanilla ya es correcto |

Con textura propia o de familia tras esto: **12541** de 15986 (78 %). Quedan fuera solo las cabezas
(otro agente), los fantasmas (vanilla correcto) y 134 ids por material sin fallback vanilla seguro (ver abajo).
Origen del motivo elegido: nombre 1622, clase 1016, grupo/lore 477, id 191,
material 3, **defecto 18**. Motivos usados: machine 406, dust 203, fillet 154, orb 150, bowl 144, pieces 129, seed 127, slices 127, glass 127, pot 127, pan 127, ingot 115, gem 113, pick 90, cube 81, fruit 64, core 64, module 58, generator 55, crate 50, vial 48, plate 42, rune 39, apiary 38, staff 36, alloy 30, nugget 27, chest 26, forge 26, talisman 25, pedestal 24, reactor 23, sword 23, kit 22, helmet 21, cable 21, egg 21, leaf 20, tank 19, pane 18, pcb 16, flower 14, miner 14, stick 14, motor 12, legs 11, boots 11, battery 11, panel 11, flame 11, bow 11, backpack 9, frame 9, book 8, shield 8, carbon 7, bullet 6, hoe 6, shell 6, rocket 6, scrap 5, wool 5, mesh 5, pod 5, ring 5, drill 4, fibre 4, hammer 4, capacitor 4, trident 3, lens 3, chip 3, card 2, mush 2, scroll 2, shovel 2, grenade 1, pepper 1, axe 1, trash 1, scythe 1, door 1, banner 1, key 1.

### Peso
PNG 3688 KiB (128 px, 128 colores) + modelos 229 KiB + definiciones `items/` 4,4 MB (de los cuales `ender_chest.json` 3 MB por
8.192 cases) = **~8,3 MB** nuevos sobre el pack de ~31 MB. Si el pack pesa demasiado: bajar `TAM` a 64 en
`gen_slimefun_svg.py` (PNG a ~1/3) o restringir `--addon`. Para menos peso en `ender_chest.json` habria que reducir variantes.

## Por addon

| Addon | Ids | Diseño | Ender | Cubierto | Cabeza | Fantasma |
|---|---|---|---|---|---|---|
| ColoredEnderChests | 8192 | 0 | 8192 | 0 | 0 | 0 |
| Cultivation | 1401 | 1077 | 0 | 46 | 278 | 0 |
| SlimeTinker | 1376 | 96 | 0 | 144 | 1136 | 0 |
| Slimefun | 554 | 10 | 0 | 421 | 123 | 0 |
| Supreme | 510 | 66 | 0 | 196 | 248 | 0 |
| FoxyMachines | 452 | 72 | 0 | 2 | 2 | 376 |
| CrystamaeHistoria | 319 | 178 | 0 | 0 | 141 | 0 |
| Netheopoiesis | 273 | 200 | 0 | 0 | 73 | 0 |
| ExoticGarden | 264 | 0 | 0 | 115 | 149 | 0 |
| FNAmplifications | 193 | 134 | 0 | 0 | 59 | 0 |
| SlimeFrame | 178 | 113 | 0 | 0 | 65 | 0 |
| DrakesNanotech | 158 | 143 | 0 | 0 | 15 | 0 |
| InfinityExpansion | 156 | 53 | 0 | 94 | 9 | 0 |
| SoulJars | 130 | 43 | 0 | 0 | 87 | 0 |
| ElementManipulation | 126 | 126 | 0 | 0 | 0 | 0 |
| DynaTech | 123 | 104 | 0 | 0 | 19 | 0 |
| GeneticChickengineering | 104 | 98 | 0 | 0 | 6 | 0 |
| Galaxyfun | 100 | 73 | 0 | 0 | 27 | 0 |
| SlimefunWarfare | 98 | 35 | 0 | 41 | 22 | 0 |
| DyedBackpacks | 96 | 0 | 0 | 0 | 96 | 0 |
| SensibleToolbox | 88 | 88 | 0 | 0 | 0 | 0 |
| SlimyBees | 83 | 31 | 0 | 0 | 52 | 0 |
| NetworksV6-Drake | 80 | 75 | 0 | 0 | 5 | 0 |
| MobCapturer | 78 | 1 | 0 | 0 | 77 | 0 |
| LiteXpansion | 64 | 62 | 0 | 0 | 2 | 0 |
| ExtraGear | 59 | 1 | 0 | 58 | 0 | 0 |
| IDreamOfEasy | 52 | 39 | 0 | 0 | 13 | 0 |
| FluffyMachines | 52 | 16 | 0 | 32 | 4 | 0 |
| RelicsOfCthonia | 38 | 0 | 0 | 0 | 38 | 0 |
| Bump | 38 | 37 | 0 | 0 | 1 | 0 |
| BetterChests | 38 | 38 | 0 | 0 | 0 | 0 |
| TranscEndence | 34 | 15 | 0 | 0 | 19 | 0 |
| AlchimiaVitae | 33 | 32 | 0 | 0 | 1 | 0 |
| HotbarPets | 31 | 4 | 0 | 0 | 27 | 0 |
| MagicXpansion | 30 | 20 | 0 | 0 | 10 | 0 |
| DankTech2 | 29 | 2 | 0 | 0 | 27 | 0 |
| ElectricSpawners | 27 | 0 | 0 | 0 | 27 | 0 |
| ObsidianExpansion | 26 | 26 | 0 | 0 | 0 | 0 |
| PrivateStorage | 24 | 0 | 0 | 0 | 24 | 0 |
| FlowerPower | 23 | 22 | 0 | 0 | 1 | 0 |
| BreweryMenu | 23 | 23 | 0 | 0 | 0 | 0 |
| PotionExpansion | 22 | 22 | 0 | 0 | 0 | 0 |
| FastMachines | 22 | 22 | 0 | 0 | 0 | 0 |
| SimpleMaterialGenerators | 19 | 19 | 0 | 0 | 0 | 0 |
| EcoPower | 18 | 1 | 0 | 0 | 17 | 0 |
| DyeBench | 17 | 17 | 0 | 0 | 0 | 0 |
| SlimyTreeTaps | 14 | 6 | 0 | 6 | 2 | 0 |
| Nexcavate | 13 | 13 | 0 | 0 | 0 | 0 |
| NotEnoughAddons | 12 | 11 | 0 | 0 | 1 | 0 |
| SlimefunOreChunks | 11 | 0 | 0 | 0 | 11 | 0 |
| RandomExpansion | 9 | 9 | 0 | 0 | 0 | 0 |
| DemonicExpansion | 9 | 8 | 0 | 0 | 1 | 0 |
| ChestTerminal | 9 | 5 | 0 | 0 | 4 | 0 |
| AdvancedTech | 9 | 4 | 0 | 0 | 5 | 0 |
| InfernalExpansion | 8 | 8 | 0 | 0 | 0 | 0 |
| ExtraTools | 8 | 8 | 0 | 0 | 0 | 0 |
| EquivalencyTech | 8 | 2 | 0 | 0 | 6 | 0 |
| VillagerUtil | 7 | 6 | 0 | 0 | 1 | 0 |
| Obsidian-Armor | 5 | 5 | 0 | 0 | 0 | 0 |
| SlimefunLuckyBlocks | 4 | 0 | 0 | 0 | 4 | 0 |
| SimpleUtils | 4 | 3 | 0 | 1 | 0 | 0 |
| SFPortalGunsExtension | 3 | 3 | 0 | 0 | 0 | 0 |
| WorldEditSlimefun | 1 | 1 | 0 | 0 | 0 | 0 |
| Drugfun | 1 | 1 | 0 | 0 | 0 | 0 |

## Lo que falta (por prioridad)

1. **Addons nuevos**: el staging 26.2 carga 102 addons / 19.876 items de addons; el volcado trae 64 / 15.986 (faltan ~4.445
   items y 38 addons). Refrescar el volcado con `Slimefun-Knowledge-Drake/dump-plugin` en un servidor de pruebas
   (staging `~/workspace/season2-staging` en Star; **no Dallas**), sustituir `slimefun-dump.json.gz` y volver a correr
   `gen_slimefun_svg.py` (reescribe cases por id; `--addon X` para lotes). Lista de addons nuevos: diff de `addon` entre
   volcados.
2. **Materiales omitidos** (134 ids): sin definicion previa y con modelo vanilla especial (tipped_arrow 34, item_frame 6,
   armor_stand 5, soul_lantern 4, saplings, signs, shulker boxes, torches, banderas, velas...). Hace falta extraer el
   `items/<material>.json` vanilla de un cliente 1.21.11/26.x y usarlo de fallback (`buscar_fallback`). Detalle en
   `scripts/slimefun_cobertura.json` (`materiales_omitidos`). Las texturas ya se generan; solo falta el cableado.
3. **Motivo por defecto** (18 ids, revisar o añadir regla en `REGLAS`/`GRUPOS`):
- SlimefunWarfare:NITROGEN_TRIIODIDE (dust)
- SlimefunWarfare:AZIDOAZIDE_AZIDE (dust)
- SlimyBees:BEEALYZER (gem)
- DemonicExpansion:DX_NAPALM (dust)
- ChestTerminal:MILKY_QUARTZ (gem)
- Bump:BUMP_MECHA_GEAR (gem)
- Bump:BUMP_KSF_STUFF (gem)
- Bump:BUMP_APPRAISAL_PAPER_DAMAGE (gem)
- BreweryMenu:TMAVY_LEZAK (gem)
- BreweryMenu:CERVENE_VINO (gem)
- BreweryMenu:BILE_VINO (gem)
- BreweryMenu:MEDOVINA (gem)
- BreweryMenu:JABLECNA_MEDOVINA (gem)
- BreweryMenu:JABLECNY_MOST (gem)
- BreweryMenu:GIN (gem)
- BreweryMenu:TEQUILA2 (gem)
- BreweryMenu:ABSINTH (gem)
- BreweryMenu:ZELENY_ABSINTH (gem)
- BreweryMenu:BRAMBOROVA_POLEVKA (gem)
- BreweryMenu:KAVA (gem)
- BetterChests:BC_TTTTTTTTTTTTTTTTTTTTIP_ITEM (gem)
4. **Calidad**: los motivos son por categoria; "heroes" a mano pendientes para lo mas usado (maquinas de
   InfinityExpansion/LiteXpansion, armaduras de FNAmplifications y Supreme). Añadir un `m_*` en `slimefun_vector.py` y una regla
   mas especifica antes de la generica. `mesh` y `pane` son los motivos mas pobres.
5. **Cabezas** (2935 ids `PLAYER_HEAD`): agente aparte (`player_head.json`).
6. Prueba visual en cliente 1.21.11/26.2 (solo validacion estatica aqui). `select` sobre `custom_data` y `tints` requieren
   1.21.5+; el pack de produccion ya exige 1.21.5+ (ver README).

## Cómo continuar

```
python3 scripts/gen_slimefun_svg.py --dump RUTA/slimefun-dump.json.gz [--addon Cultivation ...] [--sheet hoja.png]
python3 scripts/validar_slimefun_ids.py
```
Sin `--addon` limpia y regenera todo `drakes_proc/`; con `--addon` solo añade/actualiza esos ids. Idempotente.
