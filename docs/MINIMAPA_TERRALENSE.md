# Minimapa sin mods con TerraLense (investigacion, 2026-11-12)

Estado: fork parcheado y assets fusionados en el repo (ver seccion 7). Falta prueba en cliente y despliegue. Lo siguiente fue la investigacion original. Se leyo el codigo de https://github.com/AlphaNodesDev/TerraLense (clon superficial, solo lectura). No se probo en un cliente real: lo marcado como "por probar" hay que verificarlo en Horizon 26.3 y en un cliente vanilla 26.2.

## 1. Resumen

- TerraLense es un plugin Paper 26.2+ / Java 25 (MIT, 2026). Dibuja el mapa como **glifos de fuente** en la **boss bar** (o action bar). **No usa core shaders.** Por eso el problema de ShaderC de 26.3 no le afecta, y no choca con `assets/minecraft/shaders/core/*`.
- Su pack son solo: `pack.mcmeta` + 2 fuentes JSON + ~136 PNG. Se puede fusionar en `t2-vN.zip` sin conflictos reales.
- Limitacion de diseno: el servidor no conoce la resolucion ni el GUI scale del cliente, asi que **no puede fijar el mapa a la esquina**. Queda arriba y centrado (boss bar de 182 px); el jugador lo mueve a izquierda/derecha con `/tl position`. "Panel a la izquierda" real (pegado al borde) solo se logra con core shaders (NMinimap), que son frágiles en 26.3.
- Por defecto **arranca activado para todos**; hay que parchear 1 linea para que arranque apagado (ver 1.6).
- Escala: dos cosas distintas. `map.zoom` (bloques por celda, 1-16) es **por jugador** (`/tl zoom N`). El tamano en pantalla (`hud.size`, 32-168 px) es **global y va horneado en el pack** (fuente); cambiarlo obliga a regenerar y volver a fusionar el pack.

### 1.1 Como genera el pack (`resourcepack/PackGenerator.java`, `PackLayout.java`, `HudGlyphs.java`)

Se genera en `plugins/TerraLense/pack/TerraLense-Pack.zip` (determinista, fecha fija, SHA-1 calculado). Contenido:

| Ruta en el zip | Que es |
|---|---|
| `pack.mcmeta` | `min_format`/`max_format` = `resource-pack.pack-format` (88 = 26.2). **No se copia.** |
| `assets/minecraft/font/terralense_hud.json` | fuente con ascent = alto (para anclar abajo / action bar) |
| `assets/minecraft/font/terralense_hud_top.json` | misma fuente con ascent 0 (para boss bar, arriba) |
| `assets/terralense/textures/font/cell_0..23.png` | 24 texturas de celda de terreno (una por fila) |
| `assets/terralense/textures/font/arrow_0..15.png` | flecha del jugador, 16 rotaciones |
| `assets/terralense/textures/font/marker_{diamond,dot,ring,cross}_0..23.png` | 96 iconos de marcadores/waypoints |

Glifos: rango privado BMP `U+E000` (filas), `E200`/`E280` (espacios), `E2F0` (kern), `E300` (flechas), `E400` (marcadores). Grilla fija de 24x24 celdas (`GRID_SIZE`). Sin shaders, sin overlays, sin modelos, sin lang. Textura de glifo max 256 px (limite del cliente).

### 1.2 Servidor TCP del pack y como apagarlo

- Por defecto abre un HTTP propio en el puerto **8123** (`resource-pack.self-host`, sin autenticacion, sirve un solo fichero, solo GET/HEAD) y envia el pack con `required(false)` y `replace(false)` al entrar.
- Para que **no** sirva ni envie su pack: `resource-pack.mode: external`. En ese modo `initialise()` sale antes de generar nada y no abre el puerto (confirmado en `ResourcePackService.initialise`). Tampoco manda el pack (`send()` exige `active`).
- Ojo: en `external` **tampoco genera** el zip. Para obtener los assets hay que generarlo una vez con `mode: generate` + `self-host.enabled: false` + `url: ''`: genera el zip y luego avisa "no hay forma de entregarlo" y queda inactivo (sin puerto, sin envio). Se copia el zip y se vuelve a `external`.
- Tambien sirve `mode: auto` si el servidor ya manda su propio pack (genera y se retira); no depender de eso porque Odysseia puede enviarlo por API y no por `server.properties`.
- Cerrar/no abrir el puerto 8123 en el firewall del VPS.

### 1.3 Configuracion, comandos, permisos, persistencia

- Comando `/terralense` (alias `/tl`, `/minimap`). Subcomandos: `toggle`, `zoom <1-16>`, `mode <north|player>`, `position <left|right|center>`, `map [zoom]` (mapa grande; tambien doble toque de F), `waypoint add|remove|list|tp <nombre>`, `death [clear]`, `status`, `debug`, `reload`.
- Permisos: `terralense.use` / `.toggle` / `.waypoint` / `.radar` (default true); `.waypoint.teleport`, `.reload`, `.debug`, `.status`, `.admin` (op).
- Persistencia: SQLite `plugins/TerraLense/terralense.db` (preferencias por jugador + waypoints, 64 por jugador). El driver `org.xerial:sqlite-jdbc` lo descarga Paper al primer arranque (necesita salida a Maven Central).
- `config.yml` relevante: `hud.size` (32-168), `hud.shape` (circle/rounded-square/square), `hud.anchor` (boss-bar | action-bar), `hud.position`, `hud.pin-to-bar-edge`, `hud.horizontal-offset` (-160..160 celdas), `map.orientation`, `map.zoom.{default,minimum,maximum}`, `general.join-message`, `markers.*`, `worlds.blacklist`.
- Posicion: `pin-to-bar-edge: true` ancla el mapa al extremo izquierdo de la boss bar (~91 px a la izquierda del centro, no del borde de pantalla). Para acercarlo mas: `horizontal-offset` negativo global y `/tl position left` por jugador (se guarda por jugador; depende del GUI scale).
- Choque con boss bars: usa la boss bar de cada jugador mientras esta activo (`hud.anchor: action-bar` lo evita pero parpadea/se reenvia). Ver si Odysseia/eventos usan boss bar.

### 1.4 Versiones, dependencias, licencia

- Paper API 26.2 (compila contra `26.2.build.112`), Java 25, `api-version: 1.21`, sin NMS. Purpur (fork de Paper) sirve. Folia no soportado. BungeeCord bloquea el pack (Velocity ok): irrelevante si el pack lo manda Odysseia.
- Dependencias: solo `sqlite-jdbc` (descarga de Paper). Comprueba actualizaciones contra Spigot al arrancar (`general.update-check.enabled: false` para apagar la llamada de red).
- Licencia: **MIT** ("TerraLense contributors"). Se pueden copiar sus assets generados al pack; conservar el aviso de copyright MIT en `RIGHTS_AND_ATTRIBUTION.md` del repo.
- Jar: Spigot (https://www.spigotmc.org/resources/terralense.138116/) o compilar del repo con Gradle (`./gradlew build`). No se descargo nada.

### 1.5 Conflictos con nuestro pack

| Elemento | Nuestro pack | TerraLense | Conflicto / accion |
|---|---|---|---|
| `assets/minecraft/shaders/core/*` | el repo **no tiene** shaders; los shaders de la base (Horizon/StarSuites) los mueve `scripts/build_t2_pack.py` a `overlay_legacy_shaders` (<= format 88) | no usa shaders | **Ninguno.** No tocar el overlay. El mapa no depende de ShaderC. |
| `assets/minecraft/font/default.json` | 36 providers, glifos en plano 15 (`U+CE000...`), `space:font/splitter.png` | no toca `default.json` | **Ninguno.** Usa fuentes propias `terralense_hud*` (archivos nuevos). Los codepoints BMP E000-E4xx viven en fuentes distintas, no chocan con los `U+CExxx`. |
| `assets/minecraft/font/alt.json`, `monospace.json` | existen | no los toca | Ninguno. |
| `assets/terralense/` | no existe | namespace propio | Copiar tal cual. Comprobar que no haya `assets/terralense` ya (no lo hay). |
| `pack.mcmeta` | formato 15-120 + overlays (`overlay_1_21_6_plus`, `overlay_1_21_11`, `overlay_legacy_shaders`) | `min/max_format` 88 | **No copiar** su `pack.mcmeta`. Nuestro rango ya cubre 88. |
| Overlays | `overlay_*` con modelos/items/shaders | no usa | Las fuentes y texturas van en la **raiz** `assets/` (valen para todas las versiones). No ponerlas dentro de un overlay de rango limitado. |
| `build_t2_pack.py` | `is_shader()` y `extra_files` solo acepta rutas `assets/...` | | Pasar los ~138 ficheros via `extra_files` (o commit en `assets/`). Sin cambios de logica. |
| 26.3 ShaderC | rechaza reconstruir si hay shaders en overlays no auditados | irrelevante | TerraLense no anade shaders, no dispara esa guarda. |

Conflicto potencial real: **tamano del glifo**. `hud.size` cambia `ascent/height` y los `advances` de los espacios en la fuente. Si se cambia `hud.size`, `hud.position` o `hud.margin` en TerraLense hay que **regenerar y recopiar** `terralense_hud*.json` (las texturas no cambian salvo cambio de lift). Si el JSON de la fuente del pack no coincide con el que espera el plugin, el mapa sale desalineado. Fijar `hud.size` antes de fusionar y versionar el pack con el.

### 1.6 Desactivado por defecto + activacion con /mapa

- `hud.enabled: false` **no sirve**: es un interruptor maestro (`MinimapService.updatePlayer`: `!prefs.minimapEnabled() || !current.hudEnabled()` -> no se dibuja para nadie) y ningun jugador podria activarlo.
- `PlayerPreferences.defaultsFrom` toma el valor inicial de `hud.enabled`. **No hay opcion de config** para "off por defecto".
- **Parche minimo (1 linea)** en `player/PlayerPreferences.java`:
  `return new PlayerPreferences(false, config.orientation(), config.defaultZoom(), config.markerPlayers());` (primer argumento `false` en vez de `config.hudEnabled()`). Los jugadores nuevos arrancan apagados; el estado se guarda en la BD y persiste.
- Extra recomendado (parche pequeño): en `ToggleCommand` aceptar `on|off` ademas del conmutador; y `general.join-message: false` (o cambiar el texto).
- Alias sin parchear el plugin, en `commands.yml` de Paper (`/mapa` y `/wp` deben coincidir con los comandos propuestos):
  ```yaml
  aliases:
    mapa: ["tl toggle"]
    mapazoom: ["tl zoom $1"]
    mapapos: ["tl position $1"]
    wp: ["tl waypoint $1-"]
  ```
  Alias de `commands.yml` no ramifican por subcomando; para `/mapa on|off|escala|pos` de verdad, registrar `mapa` como alias real en `plugin.yml` y que `TerraLenseCommand` mapee `mapa [sub]` -> subcomandos (parche ~15 lineas). Fork propio recomendado (MIT lo permite).
- Bedrock/Geyser: bloquear `/mapa` para jugadores Floodgate (ver 3).

## 2. Pasos de integracion

1. Compilar o bajar el jar de TerraLense en un directorio aparte (no instalar aun en prod). En un servidor de pruebas Paper 26.2: poner `resource-pack.mode: generate`, `self-host.enabled: false`, `url: ''`, `hud.size/shape/anchor` definitivos (`anchor: boss-bar`, `pin-to-bar-edge: true`).
2. Arrancar una vez; copiar `plugins/TerraLense/pack/TerraLense-Pack.zip` y anotar su SHA-1.
3. Extraer solo: `assets/minecraft/font/terralense_hud.json`, `assets/minecraft/font/terralense_hud_top.json`, `assets/terralense/textures/font/*.png` (136 ficheros). Descartar `pack.mcmeta`.
4. Copiarlos al repo `drakescraft-texture-pack` bajo `assets/` (misma ruta). No tocar `default.json` ni shaders ni overlays. Anadir MIT/atribucion a `RIGHTS_AND_ATTRIBUTION.md`.
5. Reconstruir `t2-vN+1.zip` con `scripts/build_t2_pack.py` (las rutas de `assets/` pasan por `extra_files` o ya estan en la base). Verificar que la salida lista `legacy_shaders` igual que antes y que los 138 ficheros estan en la raiz, no en un overlay.
6. Test automatico: ampliar `scripts/test_build_t2_pack.py` para comprobar que existen ambas fuentes, 24 `cell_*` y que ningun fichero nuevo quedo dentro de `overlay_legacy_shaders`.
7. En prod: instalar el jar con `resource-pack.mode: external`, `self-host.enabled: false` (sin puerto 8123), `general.update-check.enabled: false`, `join-message: false`, aplicar el parche de default-off.
8. Odysseia sigue enviando el unico pack (`t2-vN+1.zip`). Probar: sin `/mapa` no se ve nada; `/mapa` muestra el mapa; reconectar conserva el estado.
9. Probar en: cliente vanilla 26.2, Horizon 26.3, un cliente 1.21.x por ViaVersion y un jugador Bedrock por Geyser (3.1/3.2).
10. Anuncio y web segun el flujo de despliegue (commit, push, jar, anuncio, web). Reinicios solo con `scripts/reinicio_seguro.py`.

## 3. Compatibilidad de versiones (no verificada en cliente real)

### 3.1 Clientes Java < 26.2 (ViaVersion)

- Como TerraLense **solo usa fuentes y boss bar**, es mucho mas tolerante que los minimapas por shader: los providers `bitmap` y `space` y el campo `font` de un componente existen desde 1.16. Probable que **funcione** en 1.20.x/1.21.x si el pack se carga.
- Lo que se rompe o es dudoso:
  - Texturas de glifo grandes (hasta 256 px de alto) y `space` con avances negativos grandes: validos, pero en versiones muy antiguas (<1.19.3) los `advances` negativos o el limite de tamano pueden diferir. Por probar.
  - El zip con `min_format 15` y overlays exige 1.20.2+ para overlays; clientes mas viejos ignoran los overlays y siguen viendo el pack base (hay que confirmar que Via no los rechace).
  - La boss bar con `font` pasa por Via, que reescribe componentes; hay reportes de perdidas de `font` en saltos muy grandes de version. Por probar en 1.20.4 y 1.21.4.
  - Si el pack no carga (rechazado por formato), el jugador verá **cuadrados/glifos privados** en la boss bar solo mientras tenga `/mapa` activo.
- Comparacion: NMinimap soporta 1.21.11 a 26.3 y VanillaMinimaps 1.21.11+: los shader-minimaps no funcionan por debajo de eso. TerraLense tiene el piso de ViaVersion como unico riesgo, no los shaders.

### 3.2 Bedrock / Geyser

- Bedrock **no aplica** los resource packs Java del servidor ni las fuentes Java; recibira la boss bar con caracteres privados no renderizables (cuadros/vacios). NMinimap y VanillaMinimaps declaran lo mismo (sin Bedrock).
- Medida: bloquear `/mapa` para Floodgate (`FloodgateApi.isFloodgatePlayer`) o con permiso `terralense.use` denegado al grupo Bedrock (LuckPerms contexto `floodgate:true`).
- Iris/OptiFine con shaderpacks: no afecta a fuentes (a diferencia de VanillaMinimaps/NMinimap, que se rompen).

### 3.3 Texto de aviso

ES: "Minimapa (opcional, `/mapa`): solo Java 26.2 o superior con el pack del servidor aceptado. En versiones anteriores puede verse mal o no verse; en Bedrock no esta disponible. Si ves cuadrados en la parte superior, escribe `/mapa off`."

EN: "Minimap (optional, `/map`): Java 26.2+ with the server resource pack accepted. On older versions it may look wrong or not show; not available on Bedrock. If you see squares at the top, type `/mapa off`."

## 4. Otros desarrolladores/proyectos

- El jugador menciono "Chagy" con "Multiverse Programming". En GitHub no existe un usuario con esos dos datos; el match real es **`SlimefunNewHorizons/MultiverseProgramming`** (org de Slimefun), autor **Chagui68** (ortografia correcta), con credito a "DrakesCraft Labs". Es un plugin Paper/Purpur (MC 1.21.11, 26.1, 26.2; Java 21 bytecode; 85 commits, 1.0.8) que agrega computadores y tortugas programables en **Lua 5.2**, perifericos y un portal web ("Blueprint Nexus") para construir `.litematic`/`.nbt`.
- Lo relacionado con mapas: modulo **Cartographer & Map Renderer** = radar geografico, consulta de biomas, creacion de `FILLED_MAP` vanilla y un mapa de terreno en vivo de 128x128 con jugadores moviendose, mostrado en **monitores** (displays de texto flotante). **No es un minimapa HUD**: no hay pack, shaders ni fuentes de HUD. Licencia: badge GPL-3.0 pero el README prohibe reventa y quitar atribucion (contradictorio; leer el LICENSE antes de reutilizar nada). Sus otros repos (ElectroSpin, Project-Diva-Manager, etc.) no tienen nada de mapas.
- Tecnica util de ahi: mapas vanilla (`MapCanvas`/packet) y displays; sirve para un **mapa grande/consulta**, no para un HUD siempre visible.

| Proyecto | Tecnica | Shaders | Versiones | Bedrock | Pack | Waypoints | Licencia |
|---|---|---|---|---|---|---|---|
| TerraLense | glifos en boss/action bar | no | Paper 26.2+ | no | simple (fuentes+PNG), se fusiona facil | si (64/jugador, SQLite) | MIT |
| NMinimap | core shader + item frames por paquetes; escala 1/2/4/8, izquierda/derecha | si | 1.21.11-26.3 | bloqueado por plugin | `built-pack.zip`, hay que fusionar | marcadores del servidor | GPL-3.0 |
| VanillaMinimaps (JNNGL/Next/Slom0414) | shaders + entidades de capa | si | 1.21.11+ | no | dificil de fusionar (shaders) | planeado | GPL-3.0 |
| MultiverseProgramming (Chagui68) | mapa vanilla/monitor, no HUD | no | 1.21.11-26.2 | n/a | n/a | n/a | GPL-3.0 con restricciones |

Recomendacion: TerraLense (pack trivial de fusionar, sin riesgo ShaderC, MIT, waypoints persistentes), con parches propios de default-off, `on|off` y alias `/mapa`. Si se exige "pegado al borde izquierdo de verdad", la alternativa es NMinimap (shader), con riesgo en 26.3 y GPL.

## 5. Comandos propuestos

- `/mapa` (alternar) | `/mapa on` | `/mapa off`  -> `tl toggle` con on/off
- `/mapa escala <1-16>` -> `tl zoom` (bloques por celda; por jugador)
- `/mapa pos <left|right|center>` -> `tl position`
- `/mapa modo <north|player>` -> `tl mode` (opcional)
- `/mapa grande` -> `tl map`
- `/wp add <nombre>` | `/wp del <nombre>` | `/wp list` -> `tl waypoint add|remove|list`
- Permisos: dar `terralense.use`, `.toggle`, `.waypoint` a `default`; denegar a Bedrock. `terralense.waypoint.teleport` solo admin.

## 6. Pendiente / riesgos

- Verificar en Horizon 26.3 y cliente vanilla 26.2 antes de anunciar.
- Decidir `hud.size` definitivo (se hornea en el pack).
- Mapa no pegado a la esquina: aceptado o buscar alternativa shader.
- Comprobar uso de boss bars por otros plugins (Odysseia, eventos).
- Fork propio de TerraLense para el parche (default-off, `on|off`, alias `/mapa`, `/wp`).

## 7. Hecho (2026-11-12) y config final

Fork: https://github.com/SlimefunNewHorizons/TerraLense-Drake (rama `main`, MIT conservado, cambios documentados en su README). Commit `a98efa6`.

- Parches: mapa apagado por defecto; `/mapa on|off|escala|pos|modo|grande` y `/wp add|del|list|tp` (alias que reescriben a `/terralense`, mismos permisos); bloqueo Bedrock via Floodgate (softdepend por reflexion); mensajes `es` por defecto + `en` (`general.language`); aviso "requiere cliente 26.2, ViaVersion no garantizado" al entrar y en `/mapa on`.
- Compilacion: `./gradlew build` con Java 25: OK. 269 tests, 0 fallos (incluye alias, claves es/en iguales, default apagado, Floodgate ausente).
- Arranque real: Purpur 26.2 local temporal (puerto 25999, fuera de Dallas/Star) carga el jar sin errores; en `mode: generate` + `self-host.enabled: false` genero el zip y **no abrio el 8123**.
- Pack: zip generado con 139 entradas (pack.mcmeta + 2 fuentes + 136 PNG); SHA-1 del zip `b63f3903d90f6832bbeddf4cdaab29f9f97e10fa` (hud.size 96, circle, boss-bar, pin-to-bar-edge). Fusionados 138 ficheros (sin pack.mcmeta): `assets/minecraft/font/terralense_hud.json`, `terralense_hud_top.json` y `assets/terralense/textures/font/` (24 `cell_*`, 16 `arrow_*`, 96 `marker_*`). `default.json` intacto, sin shaders ni overlays.
- Reproducible: `python3 scripts/merge_terralense.py --zip <TerraLense-Pack.zip> [--check]` valida conteos, namespace y texturas. Construir el pack con `python3 scripts/build_t2_pack.py ... --with-terralense` (los ficheros van en la raiz de `assets/`, no en overlay). Test: `scripts/test_build_t2_pack.py`.
- Si se cambia `hud.size/shape/margin/position` hay que regenerar y volver a correr el merge (las fuentes se hornean).

Config final recomendada en prod (`plugins/TerraLense/config.yml`):
```yaml
general: {language: es, join-message: true, update-check: {enabled: false}}
resource-pack: {mode: external, url: '', pack-format: 88, self-host: {enabled: false}}   # 8123 cerrado
hud: {size: 96, shape: circle, anchor: boss-bar, pin-to-bar-edge: true}
```
Plugin jar: construir del fork (`build/libs/TerraLense-0.1.0.jar`). Odysseia sigue enviando el unico pack (`t2-vN+1.zip` construido con `--with-terralense`).

Pendiente: prueba en cliente (vanilla 26.2, Horizon 26.3, 1.21.x por Via, Bedrock bloqueado); decidir `hud.size` definitivo; boss bars de otros plugins; luego despliegue/anuncio segun el flujo (no hecho aqui).
