import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_v6 import (  # noqa: E402
    backfill_missing_model_particles,
    has_invalid_resource_location_chars,
    is_legacy_bed_item,
    is_root_shader,
    is_stale_single_frame_animation_mcmeta,
    sanitize_blocks_atlas,
    split_trim_atlas,
)

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


class SanitizeBlocksAtlasTest(unittest.TestCase):
    def test_removes_broad_entity_directory_and_preserves_subdirectories(self):
        doc = {"sources": [
            {"type": "directory", "source": "custom", "prefix": "custom/"},
            {"type": "directory", "source": "entity", "prefix": "entity/"},
            {"type": "minecraft:directory", "source": "entity/cow", "prefix": "entity/cow/"},
            {"type": "single", "resource": "slimefun:item/x"},
        ]}
        cleaned = sanitize_blocks_atlas(json.dumps(doc).encode("utf-8"))
        self.assertIsNotNone(cleaned)
        sources = json.loads(cleaned)["sources"]
        self.assertEqual([s.get("source") or s.get("resource") for s in sources],
                         ["custom", "entity/cow", "slimefun:item/x", "entity/npc", "entity/stand"])
        self.assertIsNone(sanitize_blocks_atlas(cleaned))


class BackfillMissingModelParticlesTest(unittest.TestCase):
    def test_backfills_particle_only_for_parentless_element_models_with_valid_png(self):
        files = {
            "assets/minecraft/models/item/custom/item/murasama.json": json.dumps(
                {"textures": {"2": "custom/murasama"}, "elements": [{"from": [0, 0, 0], "to": [1, 1, 1]}]}),
            "assets/minecraft/textures/custom/murasama.png": "PNG",
            "assets/minecraft/models/item/with_parent.json": json.dumps(
                {"parent": "item/generated", "textures": {"layer0": "custom/murasama"}, "elements": []}),
            "assets/minecraft/models/item/missing_png.json": json.dumps(
                {"textures": {"0": "custom/nonexistent"}, "elements": []}),
        }
        changed = backfill_missing_model_particles(lambda p: files[p], set(files))
        self.assertEqual(set(changed), {"assets/minecraft/models/item/custom/item/murasama.json"})
        patched = json.loads(changed["assets/minecraft/models/item/custom/item/murasama.json"])
        self.assertEqual(patched["textures"]["particle"], "custom/murasama")


class ResourcePathAndStaleAnimationMcmetaTest(unittest.TestCase):
    def test_detects_invalid_resource_location_chars(self):
        self.assertTrue(has_invalid_resource_location_chars("assets/svm_jojo/models/stand/c_moon/render but epic.png"))
        self.assertTrue(has_invalid_resource_location_chars("assets/minecraft/textures/item/Foo.png"))
        self.assertFalse(has_invalid_resource_location_chars("assets/minecraft/textures/item/flint_and_steel.png"))

    def test_detects_stale_single_frame_animation_mcmeta(self):
        png_128x128 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (128).to_bytes(4, "big") + (128).to_bytes(4, "big")
        png_16x80 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + (16).to_bytes(4, "big") + (80).to_bytes(4, "big")
        stale = b'{"animation": {"frametime": 2, "frames": [0, 1, 2, 3, 4]}}'
        valid_interp = b'{"animation": {"interpolate": true, "frametime": 2}}'
        self.assertTrue(is_stale_single_frame_animation_mcmeta(
            "assets/minecraft/textures/item/tipped_arrow_head.png.mcmeta",
            stale,
            lambda _: png_128x128,
        ))
        self.assertFalse(is_stale_single_frame_animation_mcmeta(
            "assets/minecraft/textures/item/tipped_arrow_head.png.mcmeta",
            stale,
            lambda _: png_16x80,
        ))
        self.assertFalse(is_stale_single_frame_animation_mcmeta(
            "assets/stellarity/textures/item/dragonblade.png.mcmeta",
            valid_interp,
            lambda _: png_128x128,
        ))


if __name__ == "__main__":
    unittest.main()

