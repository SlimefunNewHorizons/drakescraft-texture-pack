# Plan: minimapa del servidor, armaduras Kitsugi/emisivas, luz dinámica y modelos 3D (2026-11-12)

Cliente objetivo de Jack: Horizon 26.3 (protocolo Java). Servidor: DrakesPurpur 26.2. Pack único enviado por Odysseia (`resource-pack.url` + `sha1`, ver memoria `flujo_publicar_pack_texturas`).

## 1. Minimapa sin mods (waypoints propios de cada jugador)
Candidatos (todos Paper, sin mod de cliente; la imagen se dibuja con resource pack/shaders):
- TerraLense (https://github.com/AlphaNodesDev/TerraLense): terreno, rotación, waypoints y marcadores; pide Paper 26.2+ (coincide con Dallas) y un puerto TCP propio para su pack. Mejor ajuste funcional.
- NMinimap (https://hangar.papermc.io/NezuShin/NMinimap): core shaders, marco redondo/cuadrado, escala 1x–8x, marcadores; sin Bedrock/Geyser.
- VanillaMinimaps (https://github.com/JNNGL/VanillaMinimaps) y VanillaMinimaps-Next: capas por entidad, rotación suave; no compatibles con Iris/OptiFine.
Riesgos para nosotros: (a) hay UN solo pack servido por Odysseia -> hay que FUSIONAR el pack del minimapa en `t2-vN.zip`, no servir dos; (b) los minimapas por shader chocan con el cambio a ShaderC de 26.3 (ticket #576): probar en Horizon antes de prometer; (c) Bedrock/Geyser queda fuera.
Integración con TAB: TAB no dibuja mapas; lo que sí podemos es un comando `/mapa` (alternar, escala, posición izquierda, waypoints `/wp add|del|list`) y un panel plegable en el lateral con textura propia (fuente de glifos E1xx). No se anexa "dentro" de TAB; se coordina por PlaceholderAPI.
Siguiente paso: instalar TerraLense en staging 26.2, fusionar su pack con t2 y probarlo en Horizon.
Nota: no pude identificar el plugin de "Shaggy / Multiverse Programming"; si Jack da el nombre exacto lo evaluamos igual.

## 2. Armaduras puestas en el cuerpo (estilo Kitsugi: oro entre grietas, estrellas, brillos)
- 26.x: capa de armadura en `assets/<ns>/equipment/<id>.json` + `textures/entity/equipment/humanoid/<id>.png` (y `humanoid_leggings/`), 64x32. Hay que crear una por material y atarla con el componente `equippable.asset_id` (ya hay material custom en `stellarity/` como ejemplo).
- Brillo reactivo: técnica alpha=254 en un core shader de entidad (Emissive Library / Emissive Trims, https://modrinth.com/resourcepack/emissive-library). Es cliente-solo, pero es shader: mismo riesgo ShaderC de Horizon 26.3. Alternativa sin shader: pintar "brillos" a mano, sin emisión real.
- Luz en cuevas: DynamicLights (https://modrinth.com/plugin/dynamiclight): luz por paquete (bloque de luz fantasma) para ítem en mano y casco; Paper 1.21+, sin ProtocolLib; la luz salta por bloque, no es continua. Sin shader; se puede ligar a "tiene el set Kitsugi".

## 3. Modelos 3D de herramientas/armaduras
Íconos 2D ya publicados (t2-v5, `scripts/gen_gear_svg.py`). Para 3D: modelos `items/*.json` + `models/item/*.json` (Blockbench), partiendo por 6 armas "héroe" y dejando el resto extruido de 2D.

## Orden propuesto
1) DynamicLights en staging. 2) Capas de armadura Kitsugi (sin shader) para netherita/diamante. 3) TerraLense en staging + fusión de pack + prueba en Horizon. 4) Shader emisivo solo si pasa en 26.3.
