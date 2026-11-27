# Christmas 2026 Seasonal Plan (Dec 1–31)

Lightweight, automated Christmas theming for **DrakesCraft Season 2 (MC 26.2)** using the existing resource pack (`drakescraft-texture-pack`), custom sound pipeline, `Odysseia` `navidad_2026` kit, and `drakescraft-web` seasonal automation.

> **Scope note:** No temporary Santa/Trader NPC in the Lobby (`spawnwarps`) — keep the event lightweight, automatic, and purely cosmetic/atmospheric.

## 1. Custom 2D/3D Textures for `navidad_2026`

`Odysseia/config.yml` already defines `kits.navidad_2026` (cosmetic/vanilla-only, `soulbound: true` hat, single-delivery via `PurchaseService`, Tebex ID `7800351` mapped in `drakescraft-web/server.js` as `kit-navidad`).

Target models in `drakescraft-texture-pack` (linked via `item_model` / `CustomModelData` + Geyser Bedrock mapping):

- **3D Models (Blockbench JSON):**
  - `🎄 Gorro de Navidad` (`LEATHER_HELMET`, wearable 3D Santa hat with pom-pom)
  - `Chocolate caliente` (`HONEY_BOTTLE`, 3D steaming mug)
  - `Arbolito de Navidad` (`SPRUCE_SAPLING`, 3D decorated mini-tree)
  - `Farol de Navidad` (`LANTERN`, 3D festive lantern)
- **2D Custom Sprites:**
  - `Galleta de jengibre` (`COOKIE`)
  - `Pan de Pascua` (`PUMPKIN_PIE`)
  - `Vela roja de Navidad` / `Vela verde de Navidad` (`RED_CANDLE` / `GREEN_CANDLE`)
  - `Tarjeta de Navidad 2026` (`WRITTEN_BOOK`)
  - `Cabeza de Muñeco de Nieve` (`CARVED_PUMPKIN`)

## 2. Custom Seasonal Sounds (`drakescraft:*`)

`assets/drakescraft/sounds.json` and `scripts/build_sounds.py` already manage custom `drakescraft` sound events (currently 13 `tech.*` events).

Planned additions for December (`1–31 Dec` only):

- `christmas.bells` — soft sleigh-bell chime on Lobby (`spawnwarps`) join or `navidad_2026` kit claim.
- `christmas.mug_sip` — warm sip/chime when consuming `Chocolate caliente` or festive treats.
- `christmas.snow_ambient` — optional subtle winter chime loop in `spawnwarps` (client-side via resource pack, zero server TPS cost).

## 3. Automatic Date-Gated Activation (Dec 1–31)

- **Website (`drakescraft-web`):** Already automated in `scripts/site.js`, `scripts/christmas-fx.js`, and `scripts/store.js` for `month === 11 && day >= 1 && day <= 31`.
- **In-Game (`spawnwarps` & `MiniMOTD`):**
  - Lightweight date check (`LocalDate`, `Month.DECEMBER`) in `Odysseia` or `Skript` to spawn gentle snow particles in `spawnwarps` and trigger `christmas.bells` on join.
  - Seasonal `MiniMOTD` Christmas palette during December, reverting automatically on January 1.
