import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_v6 import is_legacy_bed_item, is_root_shader, split_trim_atlas  # noqa: E402

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


class LegacyBedItemTest(unittest.TestCase):
    LEGACY = b'{"model":{"type":"minecraft:special","base":"minecraft:item/template_bed",' \
             b'"model":{"type":"minecraft:bed","texture":"minecraft:black"}}}'
    MODERN = b'{"model":{"type":"minecraft:composite","models":[{"type":"minecraft:model",' \
             b'"model":"minecraft:block/black_bed_head"}]}}'

    def test_legacy_special_bed_dropped(self):
        self.assertTrue(is_legacy_bed_item("assets/minecraft/items/black_bed.json", self.LEGACY))

    def test_modern_and_custom_kept(self):
        self.assertFalse(is_legacy_bed_item("assets/minecraft/items/black_bed.json", self.MODERN))
        self.assertFalse(is_legacy_bed_item("assets/lunareclipse.watching/items/deathbed.json", self.LEGACY))


class RootShaderTest(unittest.TestCase):
    def test_root_shaders_detected(self):
        self.assertTrue(is_root_shader("assets/minecraft/shaders/core/item.fsh"))
        self.assertTrue(is_root_shader("assets/stellarity/shaders/include/animated_text.glsl"))

    def test_overlay_and_non_shader_ignored(self):
        self.assertFalse(is_root_shader("overlay_legacy_shaders/assets/minecraft/shaders/core/item.fsh"))
        self.assertFalse(is_root_shader("assets/minecraft/textures/shaders/x.png"))
        self.assertFalse(is_root_shader("assets/minecraft/shaders/"))


if __name__ == "__main__":
    unittest.main()
