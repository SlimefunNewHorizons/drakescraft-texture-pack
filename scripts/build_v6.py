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
    "assets/drakescraft/", "assets/terralense/", "assets/minecraft/sounds/", "assets/minecraft/equipment/",
    "assets/minecraft/textures/entity/equipment/", "assets/minecraft/textures/models/armor/",
    "assets/minecraft/models/slimefun/drakes_heads/", "assets/minecraft/textures/item/", "assets/minecraft/textures/gui/sprites/hud/food_",
    "assets/minecraft/models/slimefun/drakes_proc/", "assets/slimefun/textures/item/drakes_proc/",
)
ADD_EXACT = ("assets/minecraft/font/terralense_hud.json", "assets/minecraft/font/terralense_hud_top.json")
GEAR_PREFIX = "assets/minecraft/items/"


def wrap_tool_item(path, data):
    """data: items/<id>.json del base. Envuelve fallback item/<id> -> select display_context."""
    id_ = Path(path).stem
    changed = 0

    def is_plain(v):
        return isinstance(v, dict) and v.get("type") in ("model", "minecraft:model") and v.get("model") in (f"item/{id_}", f"minecraft:item/{id_}")

    def walk(o):
        nonlocal changed
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if k == "fallback" and is_plain(v):
                    o[k] = {"type": "minecraft:select", "property": "minecraft:display_context",
                            "cases": [{"when": ["gui", "ground", "fixed", "on_shelf"], "model": {"type": "minecraft:model", "model": f"item/{id_}"}}],
                            "fallback": {"type": "minecraft:model", "model": f"drakescraft:item/gear3d/{id_}"}}
                    changed += 1
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    return changed


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

    # fuente default: referencia a drakescraft:holo (iconos/ornamentos para hologramas y TAB)
    fd = json.loads(base.read("assets/minecraft/font/default.json"))
    ref = {"type": "reference", "id": "drakescraft:holo"}
    if ref not in fd["providers"]:
        fd["providers"].append(ref)
    add["assets/minecraft/font/default.json"] = json.dumps(fd, ensure_ascii=True, indent=1).encode()

    # player_head
    bh = json.loads(base.read("assets/minecraft/items/player_head.json"))
    bcases, _ = head_cases(bh)
    rh = json.loads((repo / "assets/minecraft/items/player_head.json").read_text())
    rcases, _ = head_cases(rh)
    have = {json.dumps(c["when"], sort_keys=True) for c in bcases}
    new = [copy.deepcopy(c) for c in (rcases or []) if json.dumps(c["when"], sort_keys=True) not in have]
    bcases.extend(new)
    add["assets/minecraft/items/player_head.json"] = json.dumps(bh, ensure_ascii=False, indent=1).encode()
    report["cabezas_nuevas_por_id"] = len(new)

    # herramientas: envolver fallback en items del base
    tool_ids = [t for t in a.tool_ids.split(",") if t] or sorted(
        p.stem for p in (repo / "assets/minecraft/items").glob("*.json") if "gear3d" in p.read_text())
    wrapped = 0
    pending_prune = []
    for id_ in tool_ids:
        path = f"{GEAR_PREFIX}{id_}.json"
        if path in names:
            d = json.loads(base.read(path))
            if wrap_tool_item(path, d):
                add[path] = json.dumps(d, ensure_ascii=False, indent=1).encode()
                wrapped += 1
        else:
            doc = json.loads((repo / path).read_text())
            pending_prune.append((path, doc))  # item nuevo (p. ej. cobre, lanza, maza): se poda al final
    report["items_herramienta_ajustados"] = wrapped

    # arco/ballesta/tridente/escudo 3D: se reemplaza el FALLBACK vanilla (los cases Slimefun del base se conservan)
    def M(n): return {"type": "minecraft:model", "model": f"drakescraft:item/gear3d/{n}"}
    FLAT = ["gui", "ground", "fixed", "on_shelf"]
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
        if p.name == "player_head.json" or "drakes_proc" not in p.read_text():
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

    a.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as out:
        for info in base.infolist():
            if info.filename in add:
                continue
            out.writestr(copy.copy(info), base.read(info.filename))
        dt = base.getinfo("pack.mcmeta").date_time
        for n_, b in sorted(add.items()):
            zi = zipfile.ZipInfo(n_, date_time=dt)
            zi.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(zi, b)
    z = zipfile.ZipFile(a.out)
    bad = z.testzip()
    report.update({"archivos_anadidos_o_reemplazados": len(add), "reemplazan_base": len([n for n in add if n in names]),
                   "entradas": len(z.namelist()), "bytes": a.out.stat().st_size, "crc": bad or "ok"})
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
