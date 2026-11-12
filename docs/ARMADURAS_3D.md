# Armaduras puestas Kintsugi y herramientas 3D (26.x)

## Hecho
**Armaduras puestas** (`scripts/gen_armor_layers.py`, determinista, sin shader): netherita, diamante, hierro, oro y cota de malla.
- `assets/minecraft/textures/entity/equipment/humanoid/<mat>.png` (capa 1: casco/peto/botas) y `humanoid_leggings/<mat>.png` (capa 2), 64x32, UV vanilla (cabeza 0,0; torso 16,16; brazo 40,16; pierna 0,16).
- Estilo: placas oscuras con juntas, grietas de oro (paseo aleatorio), estrellitas en cruz y brillos de pixel claro; ribete dorado en casco y cinturon en pantalones.
- `assets/minecraft/equipment/<mat>.json` (humanoid + humanoid_leggings; en netherita/diamante/hierro/oro tambien horse_body y nautilus_body apuntando a texturas vanilla para no perder esas capas).
- Variante propia `drakescraft:kintsugi`: `assets/drakescraft/equipment/kintsugi.json` + texturas en `assets/drakescraft/textures/entity/equipment/...`. Uso: `/give @s iron_chestplate[equippable={slot:"chest",asset_id:"drakescraft:kintsugi"}]`.
- SVG fuente: `assets/drakescraft/textures/gear/svg/armor_<mat>_layer{1,2}.svg`.

**Herramientas 3D** (`scripts/gen_tool_models_3d.py`): espada, pico y hacha de netherita y diamante (6 modelos).
- Modelos: `assets/drakescraft/models/item/gear3d/<mat>_<tool>.json` (cuboides; piezas verticales giradas -45 en Z; `display` equivalente a handheld; gui con leve giro y `gui_light: front`).
- Textura atlas 16x16 por material (`assets/drakescraft/textures/item/gear3d/<mat>.png`, SVG en `.../gear/svg/gear3d_<mat>.svg`, rasterizado con rsvg-convert).
- `assets/minecraft/items/<mat>_<tool>.json`: los dos `fallback` pasan de `minecraft:item/<id>` a `drakescraft:item/gear3d/<id>`; los cases Slimefun/custom_name no se tocaron. Los `models/item/<id>.json` legacy (1.21.3-) siguen igual.
- El script valida JSON, rutas de texturas, UV y limites de elementos (0 errores). Aviso: 41 modelos Slimefun/jackstar citados por esos items no existen en este worktree (preexistente, vienen de otras ramas/merge).

## Limitaciones
- Una armadura vanilla (`iron_chestplate`...) no puede cambiar de modelo por item sin tocar el asset: aqui se sobrescribe el id vanilla, asi que TODA la armadura de ese material se ve Kintsugi (servidor completo, tambien mobs que la lleven). Para uso selectivo: `equippable.asset_id = drakescraft:kintsugi` en el item (plugin/loot).
- No se ha probado en cliente: la orientacion de los cuboides (-45 en Z) y el `display` estan calculados, no renderizados; revisar en Horizon 26.3 / Blockbench.
- Los brillos son pixeles pintados, no emiten luz. Sin trims/leather overlay propios; los trims vanilla se dibujan encima.
- Slimefun/custom_name conserva su 2D. El pico de netherita no tenia `models/item` legacy (se mantiene asi).

## Que falta / emision mas adelante
- Emision: tecnica alpha=254 (Emissive Library / Emissive Trims): poner alpha 254 en los pixeles brillantes de las capas y anadir core shader de entidad. NO se hizo por el riesgo ShaderC de 26.3 (ticket #576); probar primero en Horizon.
- Resto de herramientas (pala, azada, hierro, oro, piedra, madera) y armaduras 3D (item en mano/suelo) siguen en 2D.
- Fusionar en `t2-vN.zip` (`build_t2_pack.py`) y probar en cliente.
