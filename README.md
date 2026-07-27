# DrakesCraft Resource Pack

Overrides and validation rules for the DrakesCraft resource pack. The complete
Slimefun texture base is intentionally kept out of Git; release builds start
from a verified base ZIP and overlay the tracked files in this repository.

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
