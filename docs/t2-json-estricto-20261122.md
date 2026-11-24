# T2: constantes JSON inválidas en el constructor

El constructor aceptaba `NaN`, `Infinity` y `-Infinity` mediante el parser de
Python, incluso en el modelo requerido y campos `display` que no recorre la
comprobación de geometría. También aceptaba estos valores en padres, fuentes de
referencias, metadatos de animación y `pack.mcmeta`. Esto permitía aprobar un
candidato con JSON fuera del estándar aunque el monitor lo rechazase.

`scripts/build_t2_pack.py` utiliza ahora un parser que rechaza estas tres
constantes en todos los JSON que inspecciona, incluidos parches de la CLI. Los
errores detienen la construcción antes de reemplazar el candidato anterior.
Los recursos ajenos copiados sin inspección no quedan certificados. Las cadenas
de texto que contienen esos nombres siguen permitidas.

Regresión: 27 combinaciones de constante y ubicación, entre ZIP base y bytes
suplementarios, más un control que preserva cadenas y bytes válidos. Se verifica
la conservación del candidato anterior en cada rechazo.

Validación sobre `81e3f7f0`: los 27 subcasos reproducen el falso éxito del
constructor anterior. Tras el cambio pasan **48/48 pruebas** (`3,401 s`),
incluidas las nuevas regresiones y el control de cadenas válidas.
`git diff --check` correcto. `build_seguro.sh` se canceló durante la espera por
carga >= 5, antes de ejecutar. Las pruebas son Python sin compilación y se
ejecutaron a prioridad baja (`nice 15`, `ionice c3`) con el mismo lock
`/tmp/saori-build.lock`, sin procesos de prueba paralelos.

## Bloqueos del pendiente global

La [inspección local](t2-json-estricto-20261122.json) del ZIP público cacheado
confirma 30.291.477 bytes, SHA-1 `4597ead7d148fe0ef46029e643af8a82d151a0a0`,
CRC correcto, dos shaders core raíz y el original `fire_katana.json` ausente
pese a sus dos referencias. No es un GET nuevo. Tampoco aparece el original
en `/tmp/t2-v30.zip` ni en el historial de esa ruta del repositorio.

Star no tiene `DISPLAY`, `/dev/dri` ni instalación en `~/.minecraft`. No se ha
ejecutado el render real 26.2/26.3 ni se acredita la recuperación del modelo.
El siguiente ítem del paquete 09, prueba de Discord, permanece bloqueado por la
necesidad de un usuario real en `#comandos-bots`, según la evidencia integrada
del 21-nov. No se enviaron mensajes ni se accedió a Dallas.

Reversión: revertir el commit de este cambio; el pack público no se modifica.
