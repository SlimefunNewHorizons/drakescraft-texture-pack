# Armaduras puestas Kintsugi/Dragon y herramientas 3D (26.x)

Vista previa: `docs/previews/armaduras_kintsugi_dragon.png` (iconos dragon + capas de cada material).

## Estilo (decidido por el dueño)
Base OSCURA con micro-variacion de tono, bordes de placa marcados, remaches discretos y pocos acentos (grietas finas de 1 px, estrellitas sueltas tenues; brillo <= ~7% de la capa). Por material: netherita casi negra con puntos magenta tenues; diamante azul-petroleo con vetas; hierro oscuro con manchas de oxido; cota de malla gris oscuro con eslabones; oro envejecido apagado; cobre oscuro con cardenillo verdeazulado; tortuga verde oscuro; cuero gris neutro (se tiñe) + overlay solo con grietas/brillos. Sin shader: los brillos son pixeles pintados.

## Armaduras puestas (`scripts/gen_armor_layers.py`)
- Materiales vanilla de 26.x del jar (client.jar 26.3): leather, chainmail, iron, gold, diamond, netherite, copper, turtle_scute (casco). Propios: `drakescraft:kintsugi` y `drakescraft:dragon`.
- Capas: `humanoid` y `humanoid_leggings` (64x32, por caras con el UV vanilla); `humanoid_baby` (64x64), `horse_body` (64x64), `nautilus_body` (128x128) y `wolf_body` (64x32) se pintan sobre la MASCARA alpha del PNG vanilla del jar (no se conoce/depende del UV). Lobo: mascara del armadillo; vanilla solo trae armadura de lobo con escudo de armadillo, aqui hay `wolf_body/<mat>.png` para todos (se usa con `equippable.asset_id` + `allowed_entities: wolf`).
- Equipment JSON: `assets/minecraft/equipment/<mat>.json` parte del JSON REAL del jar (conserva humanoid_baby, trim_overrides, dyeable, horse/nautilus) y solo anade `wolf_body`. Cuero: capas teñibles + `leather_overlay` (tambien baby/caballo/lobo). `turtle_scute` y `armadillo_scute`: solo la textura, sin JSON.
- Copper: espada/pico/hacha/pala/azada/lanza, casco/peto/pantalon/botas y armadura de caballo/lobo/nautilus (cobre oscuro con cardenillo).
- Dragon: escamas superpuestas (acento magenta/cian tenue por escama), cresta y cuernos barridos en el casco, espinas/gema en el peto, huesos de ala sutiles en la espalda, garras en botas. Iconos 2D: `assets/drakescraft/textures/item/dragon_{helmet,chestplate,leggings,boots}.png` + `models/item` + `items/` (`item_model: drakescraft:dragon_helmet`...). Uso: `/give @s netherite_helmet[item_model="drakescraft:dragon_helmet",equippable={slot:"head",asset_id:"drakescraft:dragon"}]`. Existen tambien caballo/nautilus/lobo/baby de `drakescraft:dragon` (`horse_body`, `nautilus_body`, `wolf_body`).
- SVG fuente: `assets/drakescraft/textures/gear/svg/`. Regenerar: `python3 scripts/gen_armor_layers.py [--jar client.jar]` (por defecto el del launcher Horizon, 26.3).

## Herramientas 3D (`scripts/gen_tool_models_3d.py`)
- 7 materiales (wooden, stone, iron, golden, diamond, netherite, copper) x espada, pico, hacha, pala, azada y lanza (lanza con modelo extra `_in_hand` y el `display` de `spear_in_hand` del jar) + maza = 50 modelos en `assets/drakescraft/models/item/gear3d/`. Atlas 16x16 por material (SVG -> PNG con rsvg-convert).
- `assets/minecraft/items/<id>.json`: si ya existia (con cases Slimefun) solo se cambia el `fallback` a `drakescraft:item/gear3d/<id>`; si no existia se crea (misma estructura vanilla, la lanza con `select` por display_context y `swap_animation_scale`).
- Valida JSON, texturas, UV y limites: 0 errores (134 refs Slimefun/jackstar preexistentes sin modelo en este worktree, solo aviso).

## Limitaciones
- Sobrescribir el id vanilla cambia TODO el material en el servidor; para uso selectivo usar `drakescraft:kintsugi`/`dragon` via `equippable.asset_id`.
- Nada probado en cliente: la geometria 3D (giro -45 en Z) y los display estan calculados, no renderizados; revisar en Horizon 26.3 o Blockbench. Caballo/nautilus/lobo/baby usan estilo por mascara (sin motivos por cara como cresta/alas).
- NO hecho: arco, ballesta, tridente y escudo (arco/ballesta tienen 4-6 modelos por estado; tridente y escudo son modelos especiales de entidad, no hay JSON que extender). Sin trims propios.
- Los brillos no emiten luz: emision mas adelante con alpha=254 en los pixeles brillantes + core shader de entidad (Emissive Library); no se hizo por riesgo ShaderC en 26.3 (ticket #576).
- Se sobrescribio `humanoid/leather_overlay.png` y `humanoid_leggings/leather_overlay.png` del pack (eran casi transparentes).
- Fusionar en `t2-vN.zip` (`build_t2_pack.py`) y probar en cliente.
