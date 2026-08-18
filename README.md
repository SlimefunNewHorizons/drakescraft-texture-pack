<p align="center">
  <img src="banner.svg" width="100%" alt="DRAKES RESOURCE PACK Animated Banner" />
</p>

# DrakesCraft Resource Pack

> ### 🏰 ¡Únete a la Comunidad Oficial de DrakesCraft!
> 
> * 🎮 **IP del Servidor**: `play.drakescraft.net` *(Java 1.21.11 & Bedrock)*
> * 💬 **Discord Oficial**: [discord.gg/drakescraft](https://discord.gg/rR7FbfCt9Y)
> * 🌐 **Web & Guía**: [drakescraft.net](https://drakescraft.net) — 🛒 **Tienda**: [tienda.drakescraft.net](https://tienda.drakescraft.net)
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
