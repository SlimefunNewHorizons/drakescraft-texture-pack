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


if __name__ == "__main__":
    unittest.main()
