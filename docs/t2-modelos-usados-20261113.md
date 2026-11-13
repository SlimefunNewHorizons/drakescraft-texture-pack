# T2: modelos requeridos con referencias entrantes

`--require-model` exige ahora un modelo raíz JSON no vacío y al menos una
referencia entrante desde otro recurso de ítem/modelo en la salida prevista.
Antes bastaba añadir un archivo huérfano para aprobar este control.
El informe incluye `required_model_references` con las rutas que lo referencian.

El constructor lee JSON, incluidas secuencias escapadas y nombres sin namespace
(que resuelven a minecraft). Solo cuenta recursos en `assets/*/items` y
`assets/*/models`, en raíz y overlays declarados. Ignora autorreferencias del
mismo recurso, idiomas, fuentes, overlays no declarados y JSON inválido. Usa los
bytes finales de las sustituciones y recursos suplementarios antes de crear o
reemplazar la salida; un rechazo conserva el candidato anterior.

Este control no acredita que un ítem se use en juego, que se cumplan las
condiciones de selección, ni valida ciclos entre modelos, dependencias,
geometría, procedencia original o render. Un JSON inválido ajeno se ignora al
buscar referencias: no se certifica por ello todo el pack.

Validación: `~/ai-hub/scripts/build_seguro.sh 25 "$PWD" python3 -m unittest
discover -s scripts -p test_build_t2_pack.py -v`.
**30 pruebas aprobadas**, cinco regresiones nuevas. Primer ensayo con fixtures
incorrectos de overlays; corregidos para usar el ZIP base, sin relajar controles.
Todo bajo `build_seguro.sh`, un build a la vez y sin subir el umbral de carga.
Ensayo adicional sobre el código anterior `195ff930`: acepta un modelo huérfano;
el nuevo constructor lo rechaza conservando byte a byte el candidato previo.
El ZIP público también se rechaza por el modelo ausente, conservando la salida.
[Evidencia JSON](t2-modelos-usados-20261113.json).
`graphify update . --json` final: AST y extras regenerados correctamente.

No se modifica Dallas ni el ZIP público. El GET público del 13-nov, 06:13 UTC,
confirma 30.291.477 bytes, SHA-1 `4597ead7d148fe0ef46029e643af8a82d151a0a0`,
CRC correcto, dos shaders core raíz y `fire_katana.json` ausente pero referenciado.
Nexus y Nova offline; no hay fuente recuperada del original ni render 26.2/26.3.
La tarea principal de Texturas permanece abierta.
