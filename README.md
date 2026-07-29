# DrakesCraft Resource Pack

Overrides and validation rules for the DrakesCraft resource pack. The complete
Slimefun texture base is intentionally kept out of Git; release builds start
from a verified base ZIP and overlay the tracked files in this repository.

The production pack is **SF-only**: it may define Slimefun item selectors and
their models/textures, but it must never replace a vanilla model or texture.
The builder rejects legacy `custom_model_data` dispatches and non-Slimefun
namespaces in SF-only item definitions. This prevents ordinary blocks from
rendering as missing magenta-and-black models.

## Build

```bash
python3 scripts/build_resource_pack.py \
  --base /path/to/verified-base.zip \
  --slimefun-assets ../drakes-slimefun-labs/PortTextura/Jackstar-Slimefun-Drakecraft/assets/slimefun \
  --output dist/DrakesCraft-resource-pack.zip
```

The build rejects malformed JSON and missing `slimefun:` model textures. Do not
publish a ZIP that has not passed this command and been checked with `unzip -t`.
The optional Slimefun directory supplies only assets missing from the verified
base, so it does not replace current custom variants.

## Production SF-only build

```bash
python3 scripts/build_resource_pack.py \
  --sf-only \
  --slimefun-assets ../drakes-slimefun-labs/PortTextura/Jackstar-Slimefun-Drakecraft/assets/slimefun \
  --output dist/Slimefun-DrakesCraft-SF-only.zip
```

`pack.mcmeta` targets Java 1.21.11 resource-pack format `75.0`. Publish only
after this command succeeds and `unzip -t` reports no archive errors.
