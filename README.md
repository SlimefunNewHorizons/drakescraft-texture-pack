<p align="center">
  <img src="banner.svg" width="100%" alt="DRAKES RESOURCE PACK Animated Banner" />
</p>

# DrakesCraft Resource Pack

> ### 🏰 ¡Únete a la Comunidad Oficial de DrakesCraft!
> 
> * 🎮 **IP del Servidor**: `mc.drakescraft.cl` *(Java 1.21.11 & Bedrock)*
> * 💬 **Discord Oficial**: [discord.gg/drakescraft](https://discord.gg/rv3vtXZTk7)
> * 🌐 **Web & Guía**: [web.drakescraft.cl](https://web.drakescraft.cl) — 🛒 **Tienda**: [web.drakescraft.cl/store](https://web.drakescraft.cl/store.html)
> 
> *¡Juega con este addon y más de 80 expansiones optimizadas en vivo en nuestra network de supervivencia técnica!*

---

Repositorio oficial del compilador, reglas de validación y modelos 3D / texturas del paquete de recursos de **DrakesCraft**. Mantenido por **DrakesCraft Labs** para Minecraft 1.21.11.

---

## 🎯 Filosofía y Reglas de Compilación

El paquete de producción se rige por la regla estricta **SF-only**:
- Define modelos y texturas para ítems y bloques de Slimefun mediante `custom_model_data` moderno y predicados de ítems.
- **Prohibición de Overrides Vanilla**: Nunca reemplaza modelos ni texturas vanilla para evitar que bloques ordinarios muestren la textura rota de cuadros magenta y negros en clientes de jugadores.

---

## ⚡ Construcción del Resource Pack

El pipeline de construcción verifica la validez de los JSONs y la integridad de las rutas antes de empaquetar el ZIP final:

```bash
python3 scripts/build_resource_pack.py \
  --base dist/verified-base.zip \
  --output dist/DrakesCraft-resource-pack.zip
```

---

## 🛠️ Entorno

- **Compatibilidad**: Minecraft Java 1.21 - 1.21.11
- **Herramientas**: Python 3.11+ / Pillow

## T2: aislamiento de shaders antiguos (#576)

El pack combinado de T2 es distinto del SF-only de producción. Su shader
`minecraft:core/item` usa sintaxis anterior al cambio a ShaderC/SPIR-V de
[Minecraft 26.3](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3).
El constructor específico conserva todos sus recursos y mueve los tres shaders
antiguos a `overlay_legacy_shaders`, activo únicamente entre los formatos 64 y 88
(hasta 26.2). Los clientes posteriores usan sus shaders originales. El efecto
adicional de ojos brillantes del pack queda limitado a ese rango antiguo.

```bash
python3 scripts/build_t2_pack.py \
  --base /ruta/al/t2-original.zip \
  --base-sha256 d926125ce9fae17d7544e69b88d68008633c29dc371b13d8a63f6f44a810a643 \
  --output /ruta/al/t2-corregido.zip
python3 -m unittest discover -s scripts -p test_build_t2_pack.py -v
```

El ZIP base se conserva en el respaldo operativo; su hash identifica el ensamblado
previo. El constructor rechaza una base distinta, duplicados o shaders adicionales
en overlays que requieran auditoría. No incorpora los overrides del constructor
SF-only ni modifica modelos, texturas, idiomas o los otros overlays.

Validación del 4 de noviembre de 2026: cuatro pruebas automáticas correctas y
12.297 contenidos idénticos al ZIP original; solo cambia la ubicación de los tres
shaders y `pack.mcmeta`. **Pendiente: carga y comprobación visual en cliente 26.3.**
Esto no certifica compatibilidad universal de 1.21 a 26.4 (#577): el rango anunciado
por el pack base empieza en el formato 64 y debe auditarse por separado.

### T2: correcciones de idioma (#577)

El constructor acepta `--language-patches scripts/t2_language_patches.json` para
corregir 26 traducciones que devolvían su propia clave (9 en inglés y 17 en
español), y traducir el título y la descripción de `journeys_end` al español.
Los demás textos se conservan; esto no constituye una traducción completa.
Se rechazan rutas ajenas a idiomas, claves desconocidas, valores vacíos y cambios
de placeholders como `%1$s: %2$s`, antes de abrir el archivo de salida.

Validación estática: seis pruebas, mismas claves de idioma y mismos bytes de
modelos, texturas y demás recursos. El ZIP candidato conserva el mínimo 64:
no se amplía un rango solo para ocultar el aviso de incompatibilidad.
[26.2 usa el formato 88.0](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-2),
[26.3 el 97.1](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3)
y [26.4 snapshot 7 el 102.0](https://www.minecraft.net/en-us/article/minecraft-26-4-snapshot-7).
La versión final 26.4 y la carga visual por cliente siguen pendientes de prueba.
El candidato no está instalado y no modifica el pack SF-only de Dallas.

### T2: textura lateral de hierba nevada de Stellarity (#573)

El modelo `ender_grass_block_snowy.json` apuntaba a
`stellarity:block/ender_grass_block_snow`, una textura ausente. El parche opcional
`--model-patches scripts/t2_model_patches.json` usa la textura existente
`stellarity:block/ender_grass_block_side_snow`. Conserva los demás campos del
modelo y los bytes de todas las texturas. El constructor exige que cada slot
exista y que el PNG de reemplazo esté dentro del ZIP antes de abrir la salida.
Se puede combinar con `--language-patches`.

Esta referencia rota está confirmada en el pack; identificar visualmente el
bloque de la captura del reporte y cargar el candidato en cliente sigue pendiente.
El parche no amplía el rango de versiones ni está instalado en T2 o Dallas.

---

## 📄 License & Upstream Attribution

This project is a sovereign fork maintained by [**JackStar6677-1**](https://github.com/JackStar6677-1) under [**DrakesCraft Labs**](https://github.com/SlimefunNewHorizons).

- **Original Project:** Created by the upstream authors and the open-source community.
- **DrakesCraft Optimizations:** Modernized for Paper/Purpur 1.21.11+, Java 21, high concurrency, asynchronous safety, and exploit/duplication prevention.
- **License:** Distributed under the original **GNU General Public License v3.0 (GPLv3)** (or original upstream license). See the [LICENSE](LICENSE) file for complete terms.
