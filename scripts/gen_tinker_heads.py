#!/usr/bin/env python3
"""Cabezas de SlimeTinker (PLAYER_HEAD) por id: reutiliza los motivos de gen_slimefun_svg y anade los cases a
assets/minecraft/items/player_head.json (el base manda; build_v6 solo anade los ids que falten)."""
import collections, gzip, hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import gen_slimefun_svg as G

ADDON = sys.argv[1] if len(sys.argv) > 1 else "SlimeTinker"
d = json.loads(gzip.open(G.DUMP if G.DUMP.exists() else Path.home() / "workspace/personal/Slimefun-Knowledge-Drake/data/slimefun-dump.json.gz").read())
heads = [i for i in d["items"] if i["addon"] == ADDON and i["material"] == "PLAYER_HEAD"]
ph = G.ROOT / "assets/minecraft/items/player_head.json"
data = json.loads(ph.read_text())
from importlib import import_module
sys.path.insert(0, str(Path(__file__).parent))
b = import_module("build_v6")
cases, _ = b.head_cases(data)
have = {c["when"]["PublicBukkitValues"][G.KEY] for c in cases if "PublicBukkitValues" in c["when"]}
ya, mot, nuevos, deflt = {}, collections.Counter(), 0, 0
for i in heads:
    if i["id"] in have:
        continue
    px, (m, o) = G.render(i)
    mot[m] += 1; deflt += o in ("DEFECTO", "material")
    h = hashlib.md5(px.encode()).hexdigest()
    if h not in ya:
        nombre = f"{G.slug(ADDON)}_heads/{G.slug(i['id'])}"
        ya[h] = nombre
        G.guardar(px, G.TEXROOT / f"{nombre}.png", G.SVGROOT / f"{nombre}.svg")
        mp = G.MODROOT / f"{nombre}.json"; mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps({"parent": "item/generated", "author": "DrakesCraft Labs",
                                  "textures": {"layer0": f"slimefun:item/drakes_proc/{nombre}"}}) + "\n")
    cases.append({"when": {"PublicBukkitValues": {G.KEY: i["id"]}},
                  "model": {"type": "minecraft:model", "model": f"slimefun/drakes_proc/{ya[h]}"}})
    nuevos += 1
ph.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
print(json.dumps({"cabezas": len(heads), "nuevas": nuevos, "texturas": len(ya), "defecto": deflt, "motivos": mot.most_common(12)}))
