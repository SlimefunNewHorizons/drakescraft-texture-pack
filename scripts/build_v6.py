#!/usr/bin/env python3
"""Ensambla el pack servido (t2-vN) a partir del zip servido actual + los assets nuevos del repo, SIN pisar lo que ya trae.

Uso: build_v6.py --base t2-v5.zip --out t2-v6.zip [--repo .]
Reglas:
  * Se agregan/reemplazan archivos nuevos: assets/drakescraft/**, assets/terralense/**, font/terralense_*.json, sonidos (ogg),
    texturas de item (HD), equipment/ + entity/equipment/ + models/armor/ (armaduras), models/slimefun/drakes_heads/, models/item/ propios.
  * sounds.json: fusion por evento (los del repo ganan solo si el base no los tiene o si el repo los define).
  * items/player_head.json: se anaden al select por custom_data los ids que el base no tenga (el base manda).
  * items/<tool>.json del base: se envuelve el fallback `item/<id>` en select por display_context (HD en GUI, 3D en mano).
  * items/*.json NUEVOS del repo (ids por Slimefun, etc.): solo se anaden si el base no los tiene.
"""
import argparse
import copy
import json
import zipfile
from pathlib import Path

ADD_PREFIXES = (
    "assets/drakescraft/", "assets/terralense/", "assets/jackstar/", "assets/minecraft/sounds/", "assets/minecraft/equipment/",
    "assets/minecraft/textures/entity/equipment/", "assets/minecraft/textures/models/armor/",
    "assets/minecraft/models/slimefun/", "assets/minecraft/textures/item/",
    "assets/minecraft/textures/gui/", "assets/minecraft/textures/painting/", "assets/minecraft/textures/entity/",
    "assets/slimefun/",
    "assets/minecraft/optifine/", "assets/minecraft/models/item/",
)
ADD_EXACT = ("assets/minecraft/font/terralense_hud.json", "assets/minecraft/font/terralense_hud_top.json")
GEAR_PREFIX = "assets/minecraft/items/"

ATLAS_ITEMS = "assets/minecraft/atlases/items.json"
TRIM_OVERLAY = "overlay_26_3_trims"
TRIM_OVERLAY_MIN = 97  # 26.3: paletas de trims pasan a textures/palettes/ (trim_base, trim/<material>)


def split_trim_atlas(raw):
    """Atlas de items en formato 26.3 -> (raiz en formato <=26.2, original para el overlay 26.3), o None.

    En 26.2 (resource 88) minecraft:trim_base no existe: el cliente registra 'Failed to load palette image' y
    pierde todos los trims de armadura en items. 26.3 lee las paletas relativas a textures/palettes/.
    """
    doc = json.loads(raw)
    changed = False
    for src in doc.get("sources", []):
        if src.get("type") != "minecraft:paletted_permutations" or src.get("palette_key") != "minecraft:trim_base":
            continue
        src["palette_key"] = "minecraft:trims/color_palettes/trim_palette"
        for k, v in src.get("permutations", {}).items():
            ns, _, path = v.partition(":")
            if path.startswith("trim/"):
                mat = path[len("trim/"):]
                src["permutations"][k] = (f"minecraft:trims/color_palettes/{mat}" if ns == "minecraft"
                                          else f"{ns}:palettes/trim/{mat}")
        changed = True
    if not changed:
        return None
    return (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode(), raw


def merge_sounds(base, repo):
    out = dict(base)
    n = 0
    for k, v in repo.items():
        if k not in out or out[k] != v:
            out[k] = v
            n += 1
    return out, n


def head_cases(doc):
    m = doc.get("model", {})
    if m.get("property") == "minecraft:component" and m.get("component") == "minecraft:custom_data":
        return m["cases"], m
    for e in (m.get("entries") or []):
        mm = e.get("model", {})
        if mm.get("property") == "minecraft:component":
            return mm["cases"], mm
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--donor", type=Path, help="zip antiguo del que rescatar modelos/texturas que los items.json del repo referencian y el base no trae")
    ap.add_argument("--tool-ids", default="", help="lista separada por comas de ids de items/ a envolver (por defecto, los de gear3d del repo)")
    a = ap.parse_args()
    repo = a.repo
    base = zipfile.ZipFile(a.base)
    names = set(base.namelist())
    add = {}
    for p in sorted((repo / "assets").rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(repo).as_posix()
        if rel in ADD_EXACT or rel.startswith(ADD_PREFIXES):
            if rel == "assets/minecraft/sounds.json":
                continue
            add[rel] = p.read_bytes()
    report = {}

    # sounds.json
    bs = json.loads(base.read("assets/minecraft/sounds.json"))
    rs = json.loads((repo / "assets/minecraft/sounds.json").read_text())
    merged, n = merge_sounds(bs, rs)
    add["assets/minecraft/sounds.json"] = json.dumps(merged, ensure_ascii=False, indent=1).encode()
    report["sounds_eventos_cambiados"] = n
    drs = repo / "assets/drakescraft/sounds.json"
    if drs.exists():
        add["assets/drakescraft/sounds.json"] = drs.read_bytes()

    # pack.mcmeta y pack.png desde el repo (garantiza compatibilidad 1.20 - 26.2+)
    if (repo / "pack.mcmeta").exists():
        add["pack.mcmeta"] = (repo / "pack.mcmeta").read_bytes()
    if (repo / "pack.png").exists():
        add["pack.png"] = (repo / "pack.png").read_bytes()

    # Atlas de trims: raiz compatible con 26.2 y el formato 26.3 (palettes/) solo en su overlay
    atlas_raw = add.get(ATLAS_ITEMS) or (base.read(ATLAS_ITEMS) if ATLAS_ITEMS in names else None)
    split = split_trim_atlas(atlas_raw) if atlas_raw else None
    if split:
        add[ATLAS_ITEMS], add[f"{TRIM_OVERLAY}/{ATLAS_ITEMS}"] = split
        meta = json.loads(add.get("pack.mcmeta") or base.read("pack.mcmeta"))
        entries = meta.setdefault("overlays", {}).setdefault("entries", [])
        if not any(e.get("directory") == TRIM_OVERLAY for e in entries):
            entries.append({"directory": TRIM_OVERLAY,
                            "formats": {"min_inclusive": TRIM_OVERLAY_MIN, "max_inclusive": 500},
                            "min_format": [TRIM_OVERLAY_MIN, 0], "max_format": [500, 0]})
        add["pack.mcmeta"] = (json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode()
    report["atlas_trims_26_3_a_overlay"] = bool(split)

    # fuente default: utilizar la definicion maestra del repo (con todos los rangos, grecas y drakescraft:holo)
    if (repo / "assets/minecraft/font/default.json").exists():
        fd = json.loads((repo / "assets/minecraft/font/default.json").read_text())
        ref = {"type": "reference", "id": "drakescraft:holo"}
        if ref not in fd.get("providers", []):
            fd["providers"].append(ref)
        add["assets/minecraft/font/default.json"] = json.dumps(fd, ensure_ascii=True, indent=1).encode()
    if (repo / "assets/drakescraft/font/holo.json").exists():
        add["assets/drakescraft/font/holo.json"] = (repo / "assets/drakescraft/font/holo.json").read_bytes()

    # player_head
    canonical_skull_fallback = {
        "type": "minecraft:special",
        "base": "minecraft:item/template_skull",
        "model": {"type": "minecraft:head", "kind": "player"}
    }
    bh = json.loads(base.read("assets/minecraft/items/player_head.json"))
    bcases, bmodel = head_cases(bh)
    rh = json.loads((repo / "assets/minecraft/items/player_head.json").read_text())
    rcases, _ = head_cases(rh)
    have = {json.dumps(c["when"], sort_keys=True) for c in bcases}
    new = [copy.deepcopy(c) for c in (rcases or []) if json.dumps(c["when"], sort_keys=True) not in have]
    bcases.extend(new)
    # Asegurar fallback 1.21.4+ canonical para que todas las cabezas personalizadas rendericen su skin
    if bmodel and "fallback" in bmodel:
        bmodel["fallback"] = canonical_skull_fallback
    if "fallback" in bh.get("model", {}):
        bh["model"]["fallback"] = canonical_skull_fallback
    add["assets/minecraft/items/player_head.json"] = json.dumps(bh, ensure_ascii=False, indent=1).encode()
    report["cabezas_nuevas_por_id"] = len(new)

    # Anadir directamente todos los items/*.json del repo (con modelos 3D gear3d en mano y HD en GUI)
    items_repo_count = 0
    for p in sorted((repo / "assets/minecraft/items").glob("*.json")):
        path = f"{GEAR_PREFIX}{p.name}"
        add[path] = p.read_bytes()
        items_repo_count += 1
    report["items_json_repo_anadidos"] = items_repo_count

    # arco/ballesta/tridente/escudo 3D en mano
    def M(n): return {"type": "minecraft:model", "model": f"drakescraft:item/gear3d/{n}"}
    FLAT = ["gui", "ground", "fixed"]
    def flat_or(m3d, flat):
        return {"type": "minecraft:select", "property": "minecraft:display_context",
                "cases": [{"when": FLAT, "model": {"type": "minecraft:model", "model": flat}}], "fallback": m3d}
    ranged = {
        "bow": {"type": "minecraft:condition", "property": "minecraft:using_item",
                "on_true": {"type": "minecraft:range_dispatch", "property": "minecraft:use_duration", "scale": 0.05,
                            "entries": [{"threshold": 0.65, "model": M("bow_pull_1")}, {"threshold": 0.9, "model": M("bow_pull_2")}],
                            "fallback": M("bow_pull_0")},
                "on_false": flat_or(M("bow"), "minecraft:item/bow")},
        "crossbow": {"type": "minecraft:condition", "property": "minecraft:using_item",
                     "on_true": {"type": "minecraft:range_dispatch", "property": "minecraft:crossbow/pull",
                                 "entries": [{"threshold": 0.58, "model": M("crossbow_pull_1")}, {"threshold": 1.0, "model": M("crossbow_pull_2")}],
                                 "fallback": M("crossbow_pull_0")},
                     "on_false": {"type": "minecraft:select", "property": "minecraft:charge_type",
                                  "cases": [{"when": "arrow", "model": flat_or(M("crossbow_arrow"), "minecraft:item/crossbow_arrow")},
                                            {"when": "rocket", "model": flat_or(M("crossbow_firework"), "minecraft:item/crossbow_firework")}],
                                  "fallback": flat_or(M("crossbow"), "minecraft:item/crossbow")}},
        "trident": {"type": "minecraft:select", "property": "minecraft:display_context",
                    "cases": [{"when": FLAT, "model": {"type": "minecraft:model", "model": "minecraft:item/trident"}}],
                    "fallback": {"type": "minecraft:condition", "property": "minecraft:using_item",
                                 "on_false": M("trident_in_hand"), "on_true": M("trident_throwing")}},
        "shield": {"type": "minecraft:condition", "property": "minecraft:using_item",
                   "on_false": M("shield"), "on_true": M("shield_blocking")},

    }
    n_ranged = 0
    for id_, fb in ranged.items():
        path = f"{GEAR_PREFIX}{id_}.json"
        src = add[path] if path in add else (base.read(path) if path in names else None)
        if src is None:
            continue
        d = json.loads(src)
        m = d["model"]
        if m.get("component") in ("custom_data", "minecraft:custom_data") and "cases" in m:
            m["fallback"] = fb
        else:
            d["model"] = fb
        add[path] = json.dumps(d, ensure_ascii=False, indent=1).encode()
        n_ranged += 1
    report["items_ranged_3d"] = n_ranged

    # Slimefun por id (procedural): select por custom_data de ids nuevos; el modelo del BASE pasa a ser el fallback
    proc = 0
    for p in sorted((repo / "assets/minecraft/items").glob("*.json")):
        path = f"{GEAR_PREFIX}{p.name}"
        if p.name == "player_head.json":
            continue
        if p.name.endswith("_bed.json") or p.name in ("snow_block.json", "spore_blossom.json", "dragon_egg.json"):
            add[path] = p.read_bytes()
            proc += 1
            continue
        if "drakes_proc" not in p.read_text():
            continue
        if path not in names and path not in add:
            continue  # item nuevo: lo trata el bloque siguiente (con comprobacion de modelos)
        base_doc = json.loads(add[path]) if path in add else json.loads(base.read(path))
        repo_doc = json.loads(p.read_text())
        m = repo_doc.get("model", {})
        if m.get("type") != "minecraft:select" or m.get("component") != "minecraft:custom_data":
            continue
        m = copy.deepcopy(m)
        m["fallback"] = base_doc.get("model", m.get("fallback"))
        out_doc = dict(base_doc)
        out_doc["model"] = m
        add[path] = json.dumps(out_doc, ensure_ascii=False, indent=1).encode()
        proc += 1
    report["items_slimefun_por_id_fusionados"] = proc

    # Parchear overlays (overlay_1_21_6_plus, overlay_1_21_11, overlay_26_1_2, ...) para que NO pisen los modelos 3D gear3d
    # ni pierdan los casos drakes_proc en Minecraft 1.21.6+ / 1.21.11 / 26.1.2 / 26.2+.
    gear3d_ids = {p.stem for p in (repo / "assets/drakescraft/models/item/gear3d").glob("*.json")}
    repo_proc_cases = {}
    for p in sorted((repo / "assets/minecraft/items").glob("*.json")):
        if p.name == "player_head.json":
            continue
        txt = p.read_text()
        if "drakes_proc" not in txt:
            continue
        rm = json.loads(txt).get("model", {})
        if rm.get("type") == "minecraft:select" and rm.get("component") == "minecraft:custom_data" and isinstance(rm.get("cases"), list):
            repo_proc_cases[p.stem] = rm["cases"]

    def _is_display_context_select(node):
        return (
            isinstance(node, dict)
            and node.get("type") in ("select", "minecraft:select")
            and node.get("property") in ("display_context", "minecraft:display_context")
            and isinstance(node.get("cases"), list)
        )

    def _strip_on_shelf(node):
        """Elimina 'on_shelf' (introducido en 1.21.9) de cases.when y de model.display para compatibilidad 1.21.4-1.21.8."""
        changed = False
        if isinstance(node, dict):
            disp = node.get("display")
            if isinstance(disp, dict) and "on_shelf" in disp:
                del disp["on_shelf"]
                changed = True
            if _is_display_context_select(node):
                new_cases = []
                for c in node["cases"]:
                    if isinstance(c, dict):
                        w = c.get("when")
                        if w == "on_shelf":
                            changed = True
                            continue
                        if isinstance(w, list) and "on_shelf" in w:
                            c["when"] = [x for x in w if x != "on_shelf"]
                            changed = True
                            if not c["when"]:
                                continue
                    new_cases.append(c)
                node["cases"] = new_cases
            for v in node.values():
                if _strip_on_shelf(v):
                    changed = True
        elif isinstance(node, list):
            for v in node:
                if _strip_on_shelf(v):
                    changed = True
        return changed

    def _flatten_display_context_select(node):
        """Desenvuelve minecraft:select(display_context) anidados redundantes."""
        changed = False
        if isinstance(node, dict):
            if _is_display_context_select(node):
                for c in node["cases"]:
                    if not isinstance(c, dict):
                        continue
                    inner = c.get("model")
                    while _is_display_context_select(inner) and len(inner["cases"]) == 1:
                        inner_case = inner["cases"][0]
                        if inner.get("fallback") == node.get("fallback"):
                            c["model"] = inner_case.get("model")
                            inner = c["model"]
                            changed = True
                        else:
                            break
            for v in node.values():
                if _flatten_display_context_select(v):
                    changed = True
        elif isinstance(node, list):
            for v in node:
                if _flatten_display_context_select(v):
                    changed = True
        return changed

    def _replace_flat_leaf(node, item_id, replacement):
        """Reemplaza hojas {'type': 'model'|'minecraft:model', 'model': 'item/<id>'|'minecraft:item/<id>'} por replacement
        sin re-envolver select(display_context) que ya envuelven este item."""
        replaced = 0
        targets = (f"item/{item_id}", f"minecraft:item/{item_id}")
        if isinstance(node, dict):
            if _is_display_context_select(node) and node.get("fallback") == replacement.get("fallback"):
                # Ya está envuelto en select(display_context) con el mismo fallback 3D; no re-envolver
                return 0
            for k in list(node.keys()):
                v = node[k]
                if isinstance(v, dict) and v.get("type") in ("model", "minecraft:model") and v.get("model") in targets:
                    node[k] = copy.deepcopy(replacement)
                    replaced += 1
                else:
                    replaced += _replace_flat_leaf(v, item_id, replacement)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                if isinstance(v, dict) and v.get("type") in ("model", "minecraft:model") and v.get("model") in targets:
                    node[i] = copy.deepcopy(replacement)
                    replaced += 1
                else:
                    replaced += _replace_flat_leaf(v, item_id, replacement)
        return replaced

    def _inject_custom_data_cases(node, extra_cases):
        """Inserta casos custom_data que falten en el primer select(component=custom_data) encontrado."""
        if not extra_cases or not isinstance(node, dict):
            return 0
        if node.get("type") in ("select", "minecraft:select") and node.get("component") in ("custom_data", "minecraft:custom_data") and isinstance(node.get("cases"), list):
            have_w = {json.dumps(c.get("when"), sort_keys=True) for c in node["cases"]}
            added = 0
            for c in extra_cases:
                key = json.dumps(c.get("when"), sort_keys=True)
                if key not in have_w:
                    node["cases"].append(copy.deepcopy(c))
                    have_w.add(key)
                    added += 1
            return added
        for k in ("on_false", "fallback"):
            if k in node:
                res = _inject_custom_data_cases(node[k], extra_cases)
                if res:
                    return res
        return 0

    def _replace_trident_special(node, replacement):
        """Reemplaza el bloque display_context/special vanilla del tridente por el selector 3D."""
        if not isinstance(node, dict):
            return 0
        # En overlay_1_21_11 / overlay_26_1_2, el fallback de custom_data es un select(display_context) con special minecraft:trident
        if node.get("type") in ("select", "minecraft:select") and node.get("component") in ("custom_data", "minecraft:custom_data"):
            fb = node.get("fallback")
            if isinstance(fb, dict) and "minecraft:trident" in json.dumps(fb):
                node["fallback"] = copy.deepcopy(replacement)
                return 1
        replaced = 0
        for k in ("on_false", "fallback"):
            if k in node:
                replaced += _replace_trident_special(node[k], replacement)
        return replaced

    ov_patched = 0
    ov_proc_injected = 0
    for ov_path in sorted(names):
        if not ov_path.startswith("overlay_") or "/assets/minecraft/items/" not in ov_path or not ov_path.endswith(".json"):
            continue
        item_id = Path(ov_path).stem
        if item_id == "player_head":
            continue
        ov_doc = json.loads(base.read(ov_path))
        changed = False
        if item_id == "trident":
            if _replace_trident_special(ov_doc.get("model", {}), ranged["trident"]):
                changed = True
            inj = _inject_custom_data_cases(ov_doc.get("model", {}), repo_proc_cases.get("trident", []))
            if inj:
                ov_proc_injected += inj
                changed = True
        elif item_id in gear3d_ids:
            if _flatten_display_context_select(ov_doc.get("model", {})):
                changed = True
            fb_3d = flat_or(M(item_id), f"minecraft:item/{item_id}")
            if _replace_flat_leaf(ov_doc.get("model", {}), item_id, fb_3d):
                changed = True
            inj = _inject_custom_data_cases(ov_doc.get("model", {}), repo_proc_cases.get(item_id, []))
            if inj:
                ov_proc_injected += inj
                changed = True
        elif item_id in repo_proc_cases:
            inj = _inject_custom_data_cases(ov_doc.get("model", {}), repo_proc_cases[item_id])
            if inj:
                ov_proc_injected += inj
                changed = True
        if _strip_on_shelf(ov_doc):
            changed = True
        if changed:
            add[ov_path] = json.dumps(ov_doc, ensure_ascii=False, indent=1).encode()
            ov_patched += 1
    report["overlays_items_parcheados_3d"] = ov_patched
    report["overlays_cases_drakes_proc_inyectados"] = ov_proc_injected

    # items nuevos por id (Slimefun) que el base no tiene: solo si TODOS sus modelos existen (si no, el item pasaria de
    # vanilla a 'modelo faltante')
    avail = names | set(add)

    def refs(o, acc):
        if isinstance(o, dict):
            m = o.get("model")
            if isinstance(m, str):
                acc.add(m)
            for v in o.values():
                refs(v, acc)
        elif isinstance(o, list):
            for v in o:
                refs(v, acc)

    def model_exists(ref):
        ns, _, pth = ref.rpartition(":")
        ns = ns or "minecraft"
        if ns == "minecraft" and pth.split("/")[0] in ("item", "block", "builtin"):
            return True
        return f"assets/{ns}/models/{pth}.json" in avail

    def prune(o):
        """quita cases/entries cuyo modelo no existe; devuelve nº podados"""
        n = 0
        if isinstance(o, dict):
            for key in ("cases", "entries"):
                if isinstance(o.get(key), list):
                    keep = []
                    for c in o[key]:
                        acc = set()
                        refs(c, acc)
                        if all(model_exists(r) for r in acc):
                            keep.append(c)
                        else:
                            n += 1
                    o[key] = keep
            for v in o.values():
                n += prune(v)
        elif isinstance(o, list):
            for v in o:
                n += prune(v)
        return n

    pending_prune = []
    pruned = 0
    for path, doc in pending_prune:
        pruned += prune(doc)
        add[path] = json.dumps(doc, ensure_ascii=False, indent=1).encode()
    report["cases_podados_por_modelo_faltante"] = pruned

    rescued = 0
    if a.donor:
        dz = zipfile.ZipFile(a.donor); dn = set(dz.namelist())

        def take(path):
            nonlocal rescued
            if path in avail or path not in dn:
                return
            add[path] = dz.read(path); avail.add(path); rescued += 1
            if path.endswith(".json") and "/models/" in path:
                m = json.loads(dz.read(path))
                if isinstance(m.get("parent"), str):
                    ns, _, q = m["parent"].rpartition(":")
                    take(f"assets/{ns or 'minecraft'}/models/{q}.json")
                for t in (m.get("textures") or {}).values():
                    if isinstance(t, str) and not t.startswith("#"):
                        ns, _, q = t.rpartition(":")
                        take(f"assets/{ns or 'minecraft'}/textures/{q}.png")
                        take(f"assets/{ns or 'minecraft'}/textures/{q}.png.mcmeta")

        for p_ in sorted((repo / "assets/minecraft/items").glob("*.json")):
            if f"{GEAR_PREFIX}{p_.name}" in names or p_.name == "player_head.json":
                continue
            acc = set()
            refs(json.loads(p_.read_text()), acc)
            for r in acc:
                if not model_exists(r):
                    ns, _, q = r.rpartition(":")
                    take(f"assets/{ns or 'minecraft'}/models/{q}.json")
    report["modelos_rescatados_del_donor"] = rescued

    extra_items = skipped = 0
    skipped_list = []
    for p in sorted((repo / "assets/minecraft/items").glob("*.json")):
        path = f"{GEAR_PREFIX}{p.name}"
        if path in names or path in add or p.name == "player_head.json":
            continue
        acc = set()
        refs(json.loads(p.read_text()), acc)
        missing = [r for r in acc if not model_exists(r)]
        if missing:
            skipped += 1
            skipped_list.append((p.name, missing[:2]))
            continue
        add[path] = p.read_bytes()
        extra_items += 1
    report["items_json_nuevos"] = extra_items
    report["items_json_omitidos_por_modelo_faltante"] = skipped
    report["omitidos_ejemplos"] = skipped_list[:6]

    # Parches declarativos de modelos (ej. ender_grass_block_snowy.json -> side_snow existente)
    model_patches_file = repo / "scripts/t2_model_patches.json"
    patched_models = 0
    if model_patches_file.is_file():
        model_patches = json.loads(model_patches_file.read_text(encoding="utf-8"))
        for mpath, slots in model_patches.items():
            raw = add.get(mpath) if mpath in add else (base.read(mpath) if mpath in names else None)
            if raw is None:
                continue
            doc = json.loads(raw.decode("utf-8"))
            textures = doc.get("textures")
            if not isinstance(textures, dict):
                continue
            changed = False
            for slot, tex_ref in slots.items():
                ns, _, rel = tex_ref.rpartition(":")
                png = f"assets/{ns or 'minecraft'}/textures/{rel}.png"
                if png not in names and png not in add:
                    raise SystemExit(f"Model patch target texture missing: {png} (for {mpath})")
                if textures.get(slot) != tex_ref:
                    textures[slot] = tex_ref
                    changed = True
            if changed:
                add[mpath] = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
                patched_models += 1
    report["modelos_parcheados"] = patched_models

    # Parches declarativos de idiomas (Stellarity EN/ES + espejo es_cl desde es_es)
    lang_patches_file = repo / "scripts/t2_language_patches.json"
    patched_langs = 0
    if lang_patches_file.is_file():
        lang_patches = json.loads(lang_patches_file.read_text(encoding="utf-8"))
        for lpath, entries in lang_patches.items():
            raw = add.get(lpath) if lpath in add else (base.read(lpath) if lpath in names else None)
            if raw is None:
                continue
            doc = json.loads(raw.decode("utf-8"))
            changed = False
            for k, v in entries.items():
                if doc.get(k) != v:
                    doc[k] = v
                    changed = True
            if changed:
                add[lpath] = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
                patched_langs += 1
    stellarity_es_es = "assets/stellarity/lang/es_es.json"
    stellarity_es_cl = "assets/stellarity/lang/es_cl.json"
    if stellarity_es_cl not in names and stellarity_es_cl not in add:
        es_raw = add.get(stellarity_es_es) or (base.read(stellarity_es_es) if stellarity_es_es in names else None)
        if es_raw is not None:
            add[stellarity_es_cl] = es_raw
            patched_langs += 1
    report["idiomas_parcheados"] = patched_langs

    def _sanitize_json_bytes(fname, raw):
        if not fname.endswith(".json") or b"on_shelf" not in raw:
            return raw, False
        doc = json.loads(raw.decode("utf-8"))
        c1 = _strip_on_shelf(doc)
        c2 = _flatten_display_context_select(doc)
        if c1 or c2:
            return json.dumps(doc, ensure_ascii=False, indent=1).encode("utf-8"), True
        return raw, False

    on_shelf_sanitized = 0
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as out:
        for info in base.infolist():
            if info.filename in add:
                continue
            # Politica de Jack (2026-11-20): el pack NO toca bloques vanilla (texturas, modelos ni blockstates); solo herramientas,
            # armas, armaduras, scoreboard, tab, rangos, Slimefun, interfaces y botones.
            if info.filename.startswith(("assets/minecraft/textures/block/", "assets/minecraft/models/block/", "assets/minecraft/blockstates/")):
                continue
            if info.filename in ("assets/minecraft/items/chain.json",
                                 "assets/minecraft/items/chiseled_bookshelf.json",
                                 "assets/minecraft/items/sculk_sensor.json",
                                 "assets/minecraft/items/big_dripleaf.json",
                                 "assets/minecraft/items/small_dripleaf.json"):
                continue
            # Evitar StringIndexOutOfBoundsException en InteractiveChatDiscordSrvAddon por archivos WIP sin extension bajo textures/
            if not info.is_dir() and "/textures/" in info.filename and "." not in Path(info.filename).name:
                continue
            raw_b, san = _sanitize_json_bytes(info.filename, base.read(info.filename))
            if san:
                on_shelf_sanitized += 1
            out.writestr(copy.copy(info), raw_b)
        dt = base.getinfo("pack.mcmeta").date_time
        for n_, b in sorted(add.items()):
            if n_.startswith("assets/minecraft/textures/block/"):
                continue
            b, san = _sanitize_json_bytes(n_, b)
            if san:
                on_shelf_sanitized += 1
            zi = zipfile.ZipInfo(n_, date_time=dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(zi, b)
    z = zipfile.ZipFile(a.out)
    bad = z.testzip()
    # Contract Pack Gate obligatorio (bloquea regresiones antes de publicar)
    gate_violations = []
    if bad is not None:
        gate_violations.append(f"CRC corrupto: {bad}")
    on_shelf_left = 0
    extless_tex = 0
    json_errs = 0
    rank_glyphs = 0
    has_polis = False
    for ename in z.namelist():
        if ename.endswith("/"):
            continue
        low = ename.lower()
        if "/textures/" in low and "." not in ename.rsplit("/", 1)[-1]:
            extless_tex += 1
        if low.endswith(".png") and "polis" in low:
            has_polis = True
        if low.endswith(".json") or ename == "pack.mcmeta":
            raw_b = z.read(ename)
            try:
                doc = json.loads(raw_b.decode("utf-8-sig"))
            except Exception:
                json_errs += 1
                continue
            if low == "assets/minecraft/font/default.json" and isinstance(doc, dict):
                rank_glyphs = sum(
                    1 for pr in (doc.get("providers") or [])
                    if isinstance(pr, dict) and pr.get("type") == "bitmap" and pr.get("file")
                )
            if ("/items/" in low or "/models/" in low) and b'"on_shelf"' in raw_b:
                on_shelf_left += 1
    if ATLAS_ITEMS in z.namelist() and b'"minecraft:trim_base"' in z.read(ATLAS_ITEMS):
        gate_violations.append("atlases/items.json raiz usa minecraft:trim_base (solo 26.3): trims rotos en 26.2")
    if on_shelf_left:
        gate_violations.append(f"Quedaron {on_shelf_left} JSONs con token 'on_shelf' incompatible con 1.21.4-1.21.8")
    if extless_tex:
        gate_violations.append(f"Quedaron {extless_tex} archivos sin extension bajo /textures/")
    if json_errs:
        gate_violations.append(f"Quedaron {json_errs} JSONs invalidos")
    if rank_glyphs < 134 or not has_polis:
        gate_violations.append(f"Faltan glyphs de rangos (count={rank_glyphs}, polis={has_polis})")

    report.update({"archivos_anadidos_o_reemplazados": len(add), "reemplazan_base": len([n for n in add if n in names]),
                   "on_shelf_sanitizados": on_shelf_sanitized,
                   "entradas": len(z.namelist()), "bytes": a.out.stat().st_size, "crc": bad or "ok",
                   "pack_gate": {"passed": not gate_violations, "rank_glyphs": rank_glyphs, "has_polis": has_polis,
                                 "violations": gate_violations}})
    print(json.dumps(report, indent=1))
    if gate_violations:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
