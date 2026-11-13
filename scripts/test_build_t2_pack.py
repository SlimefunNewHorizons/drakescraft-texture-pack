import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from build_t2_pack import build, OVERLAY


class LegacyShaderIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name) / "base.zip"
        self.output = Path(self.tmp.name) / "fixed.zip"
        self.entries = {
            "pack.mcmeta": json.dumps({"pack": {"pack_format": 64, "min_format": [64, 0],
                "max_format": [107, 99]}, "overlays": {"entries": [{"directory": "modern",
                "formats": {"min_inclusive": 75, "max_inclusive": 500}}]}}).encode(),
            "assets/minecraft/shaders/core/item.fsh": b"#moj_import <minecraft:fog.glsl>",
            "assets/stellarity/shaders/include/animated_text.glsl": b"legacy include",
            "assets/slimefun/textures/item/machine.png": b"texture bytes",
            "modern/assets/minecraft/items/test.json": b'{"model":{}}',
        }

    def write_base(self):
        with zipfile.ZipFile(self.base, "w") as z:
            for name, data in self.entries.items():
                z.writestr(name, data)
        return hashlib.sha256(self.base.read_bytes()).hexdigest()

    def test_legacy_resources_only_visible_through_26_2(self):
        result = build(self.base, self.output, self.write_base())
        with zipfile.ZipFile(self.output) as z:
            meta = json.loads(z.read("pack.mcmeta"))
            overlay = meta["overlays"]["entries"][-1]
            for version, active in [(64, True), (75, True), (84, True), (88, True),
                                    (89, False), (97, False), (100, False)]:
                with self.subTest(format=version):
                    self.assertEqual(overlay["min_format"][0] <= version <= overlay["max_format"][0], active)
                    self.assertEqual(overlay["formats"]["min_inclusive"] <= version <= overlay["formats"]["max_inclusive"], active)
            self.assertEqual(meta["pack"], json.loads(self.entries["pack.mcmeta"])["pack"])
            self.assertEqual(len(z.namelist()), len(self.entries))
            for name, data in self.entries.items():
                if name == "pack.mcmeta":
                    continue
                if "/shaders/" in name:
                    self.assertNotIn(name, z.namelist())
                    name = f"{OVERLAY}/{name}"
                self.assertEqual(z.read(name), data)
        self.assertEqual(len(result["legacy_shaders"]), 2)

    def test_rejects_wrong_base_without_output(self):
        self.write_base()
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            build(self.base, self.output, "0" * 64)
        self.assertFalse(self.output.exists())

    def test_preserves_input_and_builds_deterministically(self):
        digest = self.write_base()
        with self.assertRaisesRegex(ValueError, "preserved"):
            build(self.base, self.base, digest)
        build(self.base, self.output, digest)
        first = self.output.read_bytes()
        build(self.base, self.output, digest)
        self.assertEqual(first, self.output.read_bytes())
        self.assertEqual(hashlib.sha256(self.base.read_bytes()).hexdigest(), digest)

    def test_rejects_unaudited_overlay_shaders(self):
        self.entries["modern/assets/minecraft/shaders/core/item.fsh"] = b"legacy shader"
        with self.assertRaisesRegex(ValueError, "Audit shaders"):
            build(self.base, self.output, self.write_base())
        self.assertFalse(self.output.exists())

    def test_language_patch_preserves_other_keys_resources_and_placeholders(self):
        en = "assets/stellarity/lang/en_us.json"
        es = "assets/stellarity/lang/es_es.json"
        self.entries[en] = b'{"title":"title","tooltip":"%1$s: %2$s","other":"Keep"}'
        self.entries[es] = b'{"title":"title","tooltip":"tooltip","other":"Conservar"}'
        patches = {en: {"title": "Journey's End"}, es: {
            "title": "El final del viaje", "tooltip": "%1$s: %2$s"}}
        build(self.base, self.output, self.write_base(), patches)
        with zipfile.ZipFile(self.output) as z:
            self.assertEqual(json.loads(z.read(es)), {
                "title": "El final del viaje", "tooltip": "%1$s: %2$s", "other": "Conservar"})
            self.assertEqual(z.read("assets/slimefun/textures/item/machine.png"), b"texture bytes")
            self.assertEqual(set(json.loads(z.read(en))), {"title", "tooltip", "other"})

    def test_invalid_language_patch_leaves_output_untouched(self):
        en = "assets/stellarity/lang/en_us.json"
        self.entries[en] = b'{"tooltip":"%1$s: %2$s"}'
        digest = self.write_base()
        for patches in [{en: {"tooltip": "%1$s"}}, {en: {"missing": "text"}},
                        {en: {"tooltip": "tooltip"}}, {"../pack.mcmeta": {}},
                        {en: {"tooltip": " "}}]:
            with self.subTest(patches=patches):
                self.output.write_bytes(b"previous artifact")
                with self.assertRaises(ValueError):
                    build(self.base, self.output, digest, patches)
                self.assertEqual(self.output.read_bytes(), b"previous artifact")

    def test_model_patch_repairs_missing_texture_and_preserves_model(self):
        name = "assets/stellarity/models/block/ender_grass_block_snowy.json"
        model = {"parent": "minecraft:block/cube_bottom_top", "textures": {
            "side": "stellarity:block/missing", "top": "minecraft:block/snow"},
            "display": {"gui": {"scale": [0.5, 0.5, 0.5]}}}
        self.entries[name] = json.dumps(model).encode()
        png = "assets/stellarity/textures/block/ender_grass_block_side_snow.png"
        self.entries[png] = b"snow texture"
        patches = {name: {"side": "stellarity:block/ender_grass_block_side_snow"}}
        result = build(self.base, self.output, self.write_base(), model_patches=patches)
        with zipfile.ZipFile(self.output) as z:
            expected = json.loads(json.dumps(model))
            expected["textures"]["side"] = patches[name]["side"]
            self.assertEqual(json.loads(z.read(name)), expected)
            self.assertEqual(z.read(png), self.entries[png])
            self.assertEqual(z.read("assets/slimefun/textures/item/machine.png"), b"texture bytes")
        self.assertEqual(result["patched_models"], [name])

    def test_invalid_model_patch_leaves_output_untouched(self):
        name = "assets/stellarity/models/block/snowy.json"
        self.entries[name] = b'{"textures":{"side":"stellarity:block/missing"}}'
        digest = self.write_base()
        for patches in [{name: {"side": "stellarity:block/absent"}},
                        {name: {"unknown": "minecraft:block/snow"}},
                        {name: {"side": "stellarity:block/../snow"}},
                        {name: {"side": "#side"}}, {"../pack.mcmeta": {}}]:
            with self.subTest(patches=patches):
                self.output.write_bytes(b"previous artifact")
                with self.assertRaises(ValueError):
                    build(self.base, self.output, digest, model_patches=patches)
                self.assertEqual(self.output.read_bytes(), b"previous artifact")

    def add_legacy_carrier(self, modern=False):
        self.carrier = "assets/minecraft/models/item/red_dye.json"
        self.item = "assets/minecraft/items/red_dye.json"
        self.entries[self.carrier] = json.dumps({"parent": "minecraft:item/generated",
            "overrides": [{"predicate": {"custom_model_data": value},
                           "model": f"svm:item/power{value}"} for value in (1, 3, 7)]}).encode()
        for value in (1, 3, 7):
            self.entries[f"assets/svm/models/item/power{value}.json"] = b'{"parent":"item/generated"}'
        if modern:
            self.entries[self.item] = json.dumps({"hand_animation_on_swap": False, "model": {
                "type": "minecraft:select", "property": "minecraft:component",
                "component": "minecraft:custom_data", "cases": [{"when": {"sf": "KEEP"},
                    "model": {"type": "model", "model": "slimefun:keep"}}],
                "fallback": {"type": "model", "model": "item/red_dye"}}}).encode()

    def test_legacy_bridge_matches_old_threshold_selection_and_preserves_source(self):
        self.add_legacy_carrier()
        digest = self.write_base()
        result = build(self.base, self.output, digest, legacy_item_bridges=["red_dye"])
        with zipfile.ZipFile(self.output) as z:
            dispatch = json.loads(z.read(self.item))["model"]
            for value in (0, 0.5, 1, 2, 3, 4, 6.99, 7, 100):
                with self.subTest(cmd=value):
                    expected = "minecraft:item/red_dye"
                    for threshold in (1, 3, 7):
                        if value >= threshold:
                            expected = f"svm:item/power{threshold}"
                    actual = dispatch["fallback"]["model"]
                    for entry in dispatch["entries"]:
                        if value >= entry["threshold"]:
                            actual = entry["model"]["model"]
                    self.assertEqual(actual, expected)
            self.assertEqual(z.read(self.carrier), self.entries[self.carrier])
            for name, data in self.entries.items():
                if name != "pack.mcmeta" and "/shaders/" not in name:
                    self.assertEqual(z.read(name), data)
        first = self.output.read_bytes()
        build(self.base, self.output, digest, legacy_item_bridges=["red_dye"])
        self.assertEqual(self.output.read_bytes(), first)
        self.assertEqual(result["bridged_items"], [self.item])

    def test_legacy_bridge_preserves_slimefun_cases_and_vanilla_fallback(self):
        self.add_legacy_carrier(modern=True)
        before = json.loads(self.entries[self.item])
        build(self.base, self.output, self.write_base(), legacy_item_bridges=["red_dye"])
        with zipfile.ZipFile(self.output) as z:
            after = json.loads(z.read(self.item))
            self.assertEqual(after["model"]["fallback"]["fallback"], before["model"]["fallback"])
            after["model"]["fallback"] = before["model"]["fallback"]
            self.assertEqual(after, before)

    def test_invalid_legacy_bridge_preserves_previous_output(self):
        self.add_legacy_carrier(modern=True)
        original = dict(self.entries)
        for failure in ("missing", "extra_predicate", "descending", "duplicate", "zero", "nan", "overlay", "fallback"):
            with self.subTest(failure=failure):
                self.entries = dict(original)
                legacy = json.loads(self.entries[self.carrier])
                if failure == "missing":
                    del self.entries["assets/svm/models/item/power1.json"]
                elif failure == "extra_predicate":
                    legacy["overrides"][0]["predicate"]["damage"] = 0.5
                elif failure == "descending":
                    legacy["overrides"].reverse()
                elif failure == "duplicate":
                    legacy["overrides"][1]["predicate"]["custom_model_data"] = 1
                elif failure in ("zero", "nan"):
                    legacy["overrides"][0]["predicate"]["custom_model_data"] = 0 if failure == "zero" else float("nan")
                elif failure == "overlay":
                    self.entries["modern/" + self.item] = self.entries[self.item]
                else:
                    item = json.loads(self.entries[self.item])
                    item["model"]["fallback"]["model"] = "slimefun:preserve"
                    self.entries[self.item] = json.dumps(item).encode()
                self.entries[self.carrier] = json.dumps(legacy).encode()
                digest = self.write_base()
                self.output.write_bytes(b"previous artifact")
                with self.assertRaises(ValueError):
                    build(self.base, self.output, digest, legacy_item_bridges=["red_dye"])
                self.assertEqual(self.output.read_bytes(), b"previous artifact")

    def test_explicit_missing_model_fallback_only_changes_modern_selection(self):
        self.add_legacy_carrier(modern=True)
        del self.entries["assets/svm/models/item/power3.json"]
        fallbacks = {"svm:item/power3": "svm:item/power7"}
        digest = self.write_base()
        with self.assertRaisesRegex(ValueError, "Missing legacy model"):
            build(self.base, self.output, digest, legacy_item_bridges=["red_dye"])
        result = build(self.base, self.output, digest, legacy_item_bridges=["red_dye"],
                       missing_model_fallbacks=fallbacks)
        with zipfile.ZipFile(self.output) as z:
            before = json.loads(self.entries[self.item])
            after = json.loads(z.read(self.item))
            dispatch = after["model"]["fallback"]
            self.assertEqual([e["threshold"] for e in dispatch["entries"]], [1, 3, 7])
            self.assertEqual([e["model"]["model"] for e in dispatch["entries"]],
                             ["svm:item/power1", "svm:item/power7", "svm:item/power7"])
            after["model"]["fallback"] = before["model"]["fallback"]
            self.assertEqual(after, before)
            self.assertEqual(z.read(self.carrier), self.entries[self.carrier])
            self.assertEqual(z.read("assets/svm/models/item/power7.json"),
                             self.entries["assets/svm/models/item/power7.json"])
        self.assertEqual(result["missing_model_fallbacks"], fallbacks)

    def test_fallback_rejects_typos_existing_models_and_missing_targets_before_output(self):
        self.add_legacy_carrier()
        del self.entries["assets/svm/models/item/power3.json"]
        digest = self.write_base()
        for fallbacks in (["svm:item/power3"],
                          {"svm:item/power3": "svm:item/absent"},
                          {"svm:item/power1": "svm:item/power7"},
                          {"svm:item/power3": "svm:item/../power7"},
                          {"svm:item/../power3": "svm:item/power7"},
                          {"svm:item/power3": "svm:item/power7", "svm:item/typo": "svm:item/power7"}):
            with self.subTest(fallbacks=fallbacks):
                self.output.write_bytes(b"previous artifact")
                with self.assertRaises(ValueError):
                    build(self.base, self.output, digest, legacy_item_bridges=["red_dye"],
                          missing_model_fallbacks=fallbacks)
                self.assertEqual(self.output.read_bytes(), b"previous artifact")

    def test_terralense_assets_land_in_root_not_overlay_and_keep_default_font(self):
        from merge_terralense import collect, EXPECTED, FONTS, TEX_DIR
        files = collect()
        self.assertTrue(FONTS <= files.keys())
        self.assertEqual(sum(n.startswith(TEX_DIR) for n in files), sum(EXPECTED.values()))
        self.entries["assets/minecraft/font/default.json"] = b'{"providers": []}'
        result = build(self.base, self.output, self.write_base(), extra_files=files)
        with zipfile.ZipFile(self.output) as z:
            names = z.namelist()
            for name, data in files.items():
                self.assertIn(name, names)
                self.assertEqual(z.read(name), data)
            self.assertFalse([n for n in names if n.startswith(OVERLAY + "/") and "terralense" in n])
            self.assertEqual(z.read("assets/minecraft/font/default.json"), b'{"providers": []}')
            self.assertNotIn("assets/terralense/pack.mcmeta", names)
        self.assertEqual(len(result["legacy_shaders"]), 2)

    def test_extra_shaders_cannot_bypass_legacy_isolation(self):
        digest = self.write_base()
        for name in ("assets/minecraft/shaders/core/item.fsh",
                     "assets/stellarity/shaders/core/end_gateway.fsh",
                     "assets/stellarity/shaders/include/extra.glsl"):
            with self.subTest(name=name):
                self.output.write_bytes(b"previous artifact")
                with self.assertRaisesRegex(ValueError, "supplemental shaders"):
                    build(self.base, self.output, digest, extra_files={name: b"legacy GLSL"})
                self.assertEqual(self.output.read_bytes(), b"previous artifact")

    def test_extra_paths_cannot_escape_assets_or_disguise_shaders(self):
        digest = self.write_base()
        for name in ("assets/minecraft/../../pack.mcmeta", "assets/minecraft//shaders/core/item.fsh",
                     "assets/minecraft/shaders/../models/a.json", "assets/minecraft/models/./a.json",
                     "assets/minecraft/models/", "assets/minecraft\\shaders\\core\\item.fsh",
                     "pack.mcmeta", "assets/Minecraft/models/a.json"):
            with self.subTest(name=name):
                self.output.write_bytes(b"previous artifact")
                with self.assertRaisesRegex(ValueError, "safe resource paths"):
                    build(self.base, self.output, digest, extra_files={name: b"unexpected"})
                self.assertEqual(self.output.read_bytes(), b"previous artifact")


if __name__ == "__main__":
    unittest.main()
