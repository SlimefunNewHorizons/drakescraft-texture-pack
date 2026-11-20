#!/usr/bin/env python3
"""Genera una placa SVG->PNG por cada rango de DrakesRankup (ranks.yml) y las registra en
assets/minecraft/font/default.json (U+E160..). Reusa el estilo de gen_greek_badges_and_auras.py.
Uso: gen_rankup_badges.py ranks.yml zip_entrada zip_salida [dir_salida_assets]"""
import importlib.util, json, re, shutil, sys, tempfile, zipfile
from pathlib import Path
import yaml

sys.path.insert(0, str(Path(__file__).parent)); import rank_badges as rb; gb = rb.gb

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

LEVEL = {"helper": 3, "tutorsf": 3, "builder": 3, "mod": 4, "dev": 4, "jefedev": 5, "admin": 5, "owner": 6, "polis": 3, "streamer": 4, "creador": 4,
         "oldschool": 5, "sfmaster": 4, "booster": 5, "rankup": 3, "zeus": 6, "titan": 6, "penelope": 6, "odiseo": 6}
NUEVOS = [("rank_odiseo", "ODISEO", 0xE1C9, "#38BDF8", "#E0F2FE", "sword", "#3F1170", "#1D0638"),
          ("rank_titanoceanus", "OCEANUS", 0xE1C4, "#22D3EE", "#CFFAFE", "trident", "#32136E", "#160736"),
          ("rank_titanjapeto", "JAPETO", 0xE1C5, "#A3E635", "#ECFCCB", "shield", "#3D126B", "#1B0736"),
          ("rank_titanhiperion", "HIPERION", 0xE1C6, "#FDE047", "#FEF9C3", "star", "#4F1173", "#240638"),
          ("rank_titancronos", "CRONOS", 0xE1C7, "#FB923C", "#FED7AA", "eye", "#4F0F6E", "#260536"),
          ("rank_titancaos", "CAOS", 0xE1C8, "#C084FC", "#F3E8FF", "moon", "#2B0B4A", "#12041F")]
def staff():
    out = []
    for bid, lab, cp, c1, c2, ic, b1, b2 in [(b[0], b[1], int(b[2], 16), b[3], b[4], b[5], b[6], b[7]) for b in rb.gb.BADGES] + NUEVOS:
        key = bid[5:]; lvl = LEVEL.get(key, 6 if key.startswith("titan") else 5)
        out.append((bid, rb.badge(lab, c1, c2, ic, b1, b2, lvl), cp))
    return out

def main(ranks_yml, zin, zout, outdir=None):
    ranks = yaml.safe_load(open(ranks_yml))["ranks"]
    tmp = Path(tempfile.mkdtemp()); tex = tmp / "assets/drakescraft/textures/font"; (tex / "svg").mkdir(parents=True)
    prov, mapa = [], {}
    for i, (rid, r) in enumerate(sorted(ranks.items(), key=lambda kv: kv[1]["tier"])):
        cp = 0xE160 + i; name = f"rankup_{rid}"
        m = re.search(r"&([0-9a-f])", r["display-name"]); c1 = COL[m.group(1) if m else "f"]
        div = min(10, 1 + (r["tier"] - 1) // 10)
        t = r["tier"]; lvl = 0 if t <= 15 else 1 if t <= 30 else 2 if t <= 50 else 3 if t <= 70 else 4 if t <= 90 else 5
        svg, w, h = rb.badge(OVER.get(rid) or label(r["display-name"]), c1, "#FFFFFF", ICON[div], "#4A1173", "#210638", lvl)
        (tex / "svg" / f"{name}.svg").write_text(svg, encoding="utf-8")
        gb.svg_to_png(svg, tex / f"{name}.png", w, h)
        prov.append({"type": "bitmap", "file": f"drakescraft:font/{name}.png", "ascent": 9, "height": 11, "chars": [chr(cp)]})
        mapa[rid] = {"tier": r["tier"], "glyph": f"\\u{cp:04x}", "label": OVER.get(rid) or label(r["display-name"])}
    for bid, (svg, w, h), cp in staff():
        (tex / "svg" / f"{bid}.svg").write_text(svg, encoding="utf-8"); gb.svg_to_png(svg, tex / f"{bid}.png", w, h)
        prov.append({"type": "bitmap", "file": f"drakescraft:font/{bid}.png", "ascent": 9, "height": 11, "chars": [chr(cp)]}); mapa["_" + bid] = {"glyph": f"\\u{cp:04x}"}
    nuevos = {p["file"] for p in prov}
    zi = zipfile.ZipFile(zin); zo = zipfile.ZipFile(zout, "w", zipfile.ZIP_DEFLATED)
    for it in zi.infolist():
        data = zi.read(it.filename)
        if it.filename == "assets/minecraft/font/default.json":
            d = json.loads(data); d["providers"] = [p for p in d["providers"] if p.get("file") not in nuevos] + prov
            data = json.dumps(d, indent=2, ensure_ascii=False).encode()
        if not any(it.filename == f"assets/drakescraft/textures/font/{n.split('/')[1][5:] if False else n.split(':')[1][5:]}" or it.filename == f"assets/drakescraft/textures/font/svg/{n.split(':')[1][5:-4]}.svg" for n in nuevos): zo.writestr(it, data)
    for f in tmp.rglob("*"):
        if f.is_file(): zo.write(f, f.relative_to(tmp))
    zo.close()
    if outdir: shutil.copytree(tmp / "assets", Path(outdir) / "assets", dirs_exist_ok=True); (Path(outdir) / "rankup_glyphs.json").write_text(json.dumps(mapa, indent=1, ensure_ascii=False))
    print(len(prov), "placas; ejemplo:", list(mapa.items())[:2], "ultimo:", list(mapa.items())[-1])

main(*sys.argv[1:])
