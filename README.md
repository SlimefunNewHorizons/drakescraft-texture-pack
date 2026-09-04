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

## ⚖️ Upstream Attribution & License / Licencia y Créditos

- **Original Project / Upstream**: Slimefun4 Community Addon.
- **Port & Maintenance**: DrakesCraft Labs team (Compatibility for Paper / Purpur 1.21.11).
- **License**: GPL-3.0 / MIT.
- **Source Code**: [GitHub Repository](https://github.com/DrakesCraft-Labs/drakescraft-texture-pack)
- **Support & Issues**: [GitHub Issues](https://github.com/DrakesCraft-Labs/drakescraft-texture-pack/issues) | [Discord](https://discord.gg/rv3vtXZTk7)

*This project is an open-source derivative work maintained by DrakesCraft Labs under the terms of its original license. All original assets and concepts belong to their respective creators.*
