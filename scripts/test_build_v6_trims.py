import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_v6 import split_trim_atlas  # noqa: E402

MODERN = {"sources": [
    {"type": "minecraft:directory", "prefix": "item/", "source": "item"},
    {"type": "minecraft:paletted_permutations", "palette_key": "minecraft:trim_base",
     "permutations": {"iron": "minecraft:trim/iron", "chorus": "stellarity:trim/chorus"},
     "textures": ["minecraft:trims/items/helmet_trim"]}]}


class SplitTrimAtlasTest(unittest.TestCase):
    def test_modern_atlas_is_split(self):
        raw = json.dumps(MODERN).encode()
        legacy, modern = split_trim_atlas(raw)
        self.assertEqual(modern, raw)
        src = json.loads(legacy)["sources"][1]
        self.assertEqual(src["palette_key"], "minecraft:trims/color_palettes/trim_palette")
        self.assertEqual(src["permutations"], {"iron": "minecraft:trims/color_palettes/iron",
                                               "chorus": "stellarity:palettes/trim/chorus"})
        self.assertEqual(src["textures"], ["minecraft:trims/items/helmet_trim"])

    def test_legacy_atlas_untouched(self):
        legacy, _ = split_trim_atlas(json.dumps(MODERN).encode())
        self.assertIsNone(split_trim_atlas(legacy))


if __name__ == "__main__":
    unittest.main()
