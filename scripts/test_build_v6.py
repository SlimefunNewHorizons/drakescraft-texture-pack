import json
import unittest

from build_v6 import apply_missing_model_fallbacks


class MissingModelFallbackTest(unittest.TestCase):
    def setUp(self):
        self.files = {
            "assets/svm_ep/items/katana_fire.json": json.dumps(
                {"model": {"type": "minecraft:model", "model": "minecraft:item/custom/item/fire_katana"}}),
            "overlay_x/assets/minecraft/items/stick.json": json.dumps(
                {"model": {"type": "minecraft:select", "cases": [{"model": {"model": "item/custom/item/fire_katana"}}],
                           "fallback": {"type": "minecraft:model", "model": "item/stick"}}}),
            "assets/svm_ep/items/katana.json": json.dumps({"model": {"model": "minecraft:item/custom/item/katana"}}),
            "assets/minecraft/models/item/warped_fungus_on_a_stick.json": json.dumps(
                {"parent": "item/handheld_rod", "overrides": [
                    {"predicate": {"custom_model_data": 1}, "model": "item/custom/item/fire_katana"},
                    {"predicate": {"custom_model_data": 2}, "model": "item/custom/item/fire_katana2"}]}),
            "assets/minecraft/models/item/custom/item/fire_katana2.json": "{}",
            "assets/minecraft/models/item/custom/item/katana.json": "{}",
        }
        self.fallbacks = {"minecraft:item/custom/item/fire_katana": "minecraft:item/custom/item/fire_katana2"}

    def run_fallbacks(self, fallbacks=None):
        return apply_missing_model_fallbacks(lambda p: self.files[p], set(self.files), fallbacks or self.fallbacks)

    def test_rewrites_modern_items_in_any_namespace_and_overlay(self):
        changed = self.run_fallbacks()
        self.assertEqual(set(changed), {"assets/svm_ep/items/katana_fire.json",
                                        "overlay_x/assets/minecraft/items/stick.json",
                                        "assets/minecraft/models/item/warped_fungus_on_a_stick.json"})
        rod = json.loads(changed["assets/minecraft/models/item/warped_fungus_on_a_stick.json"])
        self.assertEqual([o["model"] for o in rod["overrides"]],
                         ["minecraft:item/custom/item/fire_katana2", "item/custom/item/fire_katana2"])
        self.assertEqual(json.loads(changed["assets/svm_ep/items/katana_fire.json"])["model"]["model"],
                         "minecraft:item/custom/item/fire_katana2")
        stick = json.loads(changed["overlay_x/assets/minecraft/items/stick.json"])["model"]
        self.assertEqual(stick["cases"][0]["model"]["model"], "minecraft:item/custom/item/fire_katana2")
        self.assertEqual(stick["fallback"]["model"], "item/stick")

    def test_rejects_missing_target_and_existing_source(self):
        with self.assertRaises(SystemExit):
            self.run_fallbacks({"minecraft:item/custom/item/fire_katana": "minecraft:item/custom/item/nope"})
        with self.assertRaises(SystemExit):
            self.run_fallbacks({"minecraft:item/custom/item/katana": "minecraft:item/custom/item/fire_katana2"})


if __name__ == "__main__":
    unittest.main()
