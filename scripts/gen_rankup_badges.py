#!/usr/bin/env python3
"""Genera una placa SVG->PNG por cada rango de DrakesRankup (ranks.yml) y las registra en
assets/minecraft/font/default.json (U+E160..). Reusa el estilo de gen_greek_badges_and_auras.py.
Uso: gen_rankup_badges.py ranks.yml zip_entrada zip_salida [dir_salida_assets]"""
import importlib.util, json, re, shutil, sys, tempfile, zipfile
from pathlib import Path
import yaml

GEN = Path.home() / "Documentos/Desarrollo/Repositorios/drakescraft/Slimefun-Texture-Drake/tools/gen_greek_badges_and_auras.py"
spec = importlib.util.spec_from_file_location("gb", GEN); gb = importlib.util.module_from_spec(spec); spec.loader.exec_module(gb)

SC = dict(zip("ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
COL = {"0":"#9CA3AF","1":"#60A5FA","2":"#4ADE80","3":"#22D3EE","4":"#F87171","5":"#C084FC","6":"#FBBF24","7":"#D1D5DB",
       "8":"#9CA3AF","9":"#60A5FA","a":"#4ADE80","b":"#67E8F9","c":"#FB7185","d":"#F472B6","e":"#FDE047","f":"#F8FAFC"}
ICON = {1:"book",2:"star",3:"bolt",4:"moon",5:"flame",6:"sword",7:"wing",8:"eye",9:"crown",10:"diamond"}  # por division
def label(dn):
    s = re.sub(r"&[0-9a-fk-or]", "", dn)
    s = re.split(r"[:︱]", s)[0].strip()
    s = "".join(SC.get(c, c) for c in s)
    s = s.replace("-", " ").replace("''", "").upper()
    s = s.translate(str.maketrans("ÁÉÍÓÚŌŪ", "AEIOUOU")).replace("Ṓ", "O")
    s = re.sub(r"[^A-Z0-9 ]", "", s).strip()
    while len(s) > 16 and " " in s: s = s.rsplit(" ", 1)[0]  # sin cortar palabras
    return s[:16] or "RANGO"
OVER = {"ichigo_mugetsu": "ICHIGO MUGETSU", "gogeta_blue": "GOGETA BLUE", "vegito_blue": "VEGITO BLUE", "zeno_omni_supremo": "ZENO OMNI",
        "luffy_gear5": "LUFFY GEAR 5", "shanks_kamisari": "SHANKS", "gon_adulto": "GON ADULTO", "shadow_monarch_ashborn": "ASHBORN"}

def main(ranks_yml, zin, zout, outdir=None):
    ranks = yaml.safe_load(open(ranks_yml))["ranks"]
    tmp = Path(tempfile.mkdtemp()); tex = tmp / "assets/drakescraft/textures/font"; (tex / "svg").mkdir(parents=True)
    prov, mapa = [], {}
    for i, (rid, r) in enumerate(sorted(ranks.items(), key=lambda kv: kv[1]["tier"])):
        cp = 0xE160 + i; name = f"rankup_{rid}"
        m = re.search(r"&([0-9a-f])", r["display-name"]); c1 = COL[m.group(1) if m else "f"]
        div = min(10, 1 + (r["tier"] - 1) // 10)
        svg, w, h = gb.make_badge_svg(OVER.get(rid) or label(r["display-name"]), c1, "#FFFFFF", ICON[div], "#4A1173", "#210638")
        (tex / "svg" / f"{name}.svg").write_text(svg, encoding="utf-8")
        gb.svg_to_png(svg, tex / f"{name}.png", w, h)
        prov.append({"type": "bitmap", "file": f"drakescraft:font/{name}.png", "ascent": 9, "height": 11, "chars": [chr(cp)]})
        mapa[rid] = {"tier": r["tier"], "glyph": f"\\u{cp:04x}", "label": OVER.get(rid) or label(r["display-name"])}
    zi = zipfile.ZipFile(zin); zo = zipfile.ZipFile(zout, "w", zipfile.ZIP_DEFLATED)
    for it in zi.infolist():
        data = zi.read(it.filename)
        if it.filename == "assets/minecraft/font/default.json":
            d = json.loads(data); d["providers"] = [p for p in d["providers"] if not p.get("file", "").startswith("drakescraft:font/rankup_")] + prov
            data = json.dumps(d, indent=2, ensure_ascii=False).encode()
        if not it.filename.startswith("assets/drakescraft/textures/font/rankup_"): zo.writestr(it, data)
    for f in tmp.rglob("*"):
        if f.is_file(): zo.write(f, f.relative_to(tmp))
    zo.close()
    if outdir: shutil.copytree(tmp / "assets", Path(outdir) / "assets", dirs_exist_ok=True); (Path(outdir) / "rankup_glyphs.json").write_text(json.dumps(mapa, indent=1, ensure_ascii=False))
    print(len(prov), "placas; ejemplo:", list(mapa.items())[:2], "ultimo:", list(mapa.items())[-1])

main(*sys.argv[1:])
