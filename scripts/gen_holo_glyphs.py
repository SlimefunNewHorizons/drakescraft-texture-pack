#!/usr/bin/env python3
"""Glifos para hologramas/TAB en la fuente default (via provider `reference` a drakescraft:holo). SVG 16x16 -> PNG 128.
Codepoints BMP privados U+E700.. (TAB usa E1xx, TerraLense E000-E4xx). Uso: gen_holo_glyphs.py"""
import json, subprocess
from pathlib import Path
G, GD, GL = "#e8b83a", "#7a5412", "#fff1a8"
P, PD, C, R = "#9b5cf6", "#3a1b78", "#5fe9ff", "#ff6b6b"
def sh(body): return f'<g stroke="#0d0a14" stroke-width="0.9" stroke-linejoin="round" stroke-linecap="round">{body}</g>'
ICONS = {
 "gear": ("E700", sh(f'<circle cx="8" cy="8" r="5.2" fill="{G}"/>' + "".join(f'<rect x="6.6" y="0.8" width="2.8" height="3" fill="{G}" transform="rotate({a} 8 8)"/>' for a in range(0,360,45)) + f'<circle cx="8" cy="8" r="2.2" fill="#2a1458"/>')),
 "pick": ("E701", sh(f'<path d="M3 5 Q8 0.5 13 5 L11.6 6 Q8 3.3 4.4 6Z" fill="{GL}"/><rect x="7.2" y="4" width="1.6" height="11" rx=".6" fill="#8a5a2b"/>')),
 "cloud": ("E702", sh(f'<path d="M4.5 12.5 A3 3 0 0 1 4.8 6.6 A4 4 0 0 1 12.2 6.2 A3.2 3.2 0 0 1 11.8 12.5Z" fill="#cfe9ff"/>')),
 "diamond": ("E703", sh(f'<path d="M8 1.5 L14 8 L8 14.5 L2 8Z" fill="{P}"/><path d="M8 1.5 L14 8 L8 8Z" fill="#c9a8ff" stroke="none"/>')),
 "brick": ("E704", sh(f'<rect x="1.5" y="3.5" width="13" height="9" fill="#c2603a"/><path d="M1.5 8H14.5M6 3.5V8M10.5 8V12.5" fill="none" stroke="#5a2410" stroke-width="0.8"/>')),
 "flask": ("E705", sh(f'<path d="M6 1.5H10V6L13.5 13Q14 14.5 12.5 14.5H3.5Q2 14.5 2.5 13L6 6Z" fill="#cdd9ee"/><path d="M4 10.5H12L13.2 13Q13.5 14 12.5 14H3.5Q2.5 14 2.8 13Z" fill="{P}" stroke="none"/>')),
 "warn": ("E706", sh(f'<path d="M8 1.5 L15 14 H1Z" fill="#ffcc33"/><rect x="7.2" y="6" width="1.6" height="4.5" fill="#0d0a14" stroke="none"/><circle cx="8" cy="12" r=".9" fill="#0d0a14" stroke="none"/>')),
 "star4": ("E707", sh(f'<path d="M8 1 L9.8 6.2 L15 8 L9.8 9.8 L8 15 L6.2 9.8 L1 8 L6.2 6.2Z" fill="{G}"/>')),
 "arrow": ("E708", sh(f'<path d="M1.5 5.5H9V2.5L14.5 8L9 13.5V10.5H1.5Z" fill="{C}"/>')),
 "shield": ("E709", sh(f'<path d="M8 1.5 L14 3.5 V8 Q14 12.5 8 14.8 Q2 12.5 2 8 V3.5Z" fill="#7b88a6"/><path d="M8 1.5 L14 3.5 V8 Q14 12.5 8 14.8Z" fill="#4a566e" stroke="none"/><path d="M8 4V12M5 7.5H11" stroke="{G}" stroke-width="1.2" fill="none"/>')),
 "scales": ("E70A", sh(f'<path d="M8 2V13M3 13H13M2 5H14" stroke="{G}" stroke-width="1.2" fill="none"/><path d="M1.5 5 L4 10 H-0 Z M14.5 5 L12 10 H16Z" fill="{G}"/>')),
 "flag": ("E70B", sh(f'<rect x="3" y="1.5" width="1.4" height="13" fill="#8a5a2b"/><path d="M4.4 2.5H13L10.8 5.5L13 8.5H4.4Z" fill="{R}"/>')),
 "star5": ("E70C", sh(f'<path d="M8 1.2 L10 6 L15 6.3 L11 9.5 L12.4 14.5 L8 11.7 L3.6 14.5 L5 9.5 L1 6.3 L6 6Z" fill="{G}"/>')),
 "check": ("E70D", sh(f'<path d="M2.5 8.5 L6.2 12.2 L13.5 3.8" stroke="#4dff88" stroke-width="2.6" fill="none"/>')),
 "pencil": ("E70E", sh(f'<path d="M2.5 13.5 L3.2 10 L11.5 1.8 L14.2 4.5 L6 12.8Z" fill="{G}"/><path d="M2.5 13.5 L3.2 10 L6 12.8Z" fill="#f5d9b5"/>')),
 "home": ("E70F", sh(f'<path d="M1.5 8 L8 2 L14.5 8 H12.5 V14 H3.5 V8Z" fill="#d9b26a"/><rect x="6.5" y="9" width="3" height="5" fill="#5a3a1a"/>')),
 "orn_mid": ("E720", f'<rect x="0" y="7" width="16" height="2" fill="{G}"/><rect x="0" y="7" width="16" height="0.7" fill="{GL}"/><rect x="0" y="9" width="16" height="0.6" fill="{GD}"/>'),
 "orn_l": ("E721", f'<rect x="6" y="7" width="10" height="2" fill="{G}"/><rect x="6" y="7" width="10" height="0.7" fill="{GL}"/><path d="M6 8 L2 4.5 M6 8 L2 11.5" stroke="{G}" stroke-width="1.4" fill="none"/><circle cx="2" cy="8" r="1.6" fill="{P}"/>'),
 "orn_r": ("E722", f'<rect x="0" y="7" width="10" height="2" fill="{G}"/><rect x="0" y="7" width="10" height="0.7" fill="{GL}"/><path d="M10 8 L14 4.5 M10 8 L14 11.5" stroke="{G}" stroke-width="1.4" fill="none"/><circle cx="14" cy="8" r="1.6" fill="{P}"/>'),
 "orn_c": ("E723", f'<rect x="0" y="7" width="16" height="2" fill="{G}"/><path d="M8 1.5 L13 8 L8 14.5 L3 8Z" fill="{P}" stroke="#0d0a14" stroke-width="0.9"/><path d="M8 4 L10.4 8 L8 12 L5.6 8Z" fill="{C}"/>'),
}
root = Path(".")
tex = root/"assets/drakescraft/textures/font/holo"; tex.mkdir(parents=True, exist_ok=True)
svgd = root/"assets/drakescraft/textures/gear/svg_holo"; svgd.mkdir(parents=True, exist_ok=True)
prov = []
for n, (cp, body) in ICONS.items():
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="128" height="128">{body}</svg>'
    (svgd/f"{n}.svg").write_text(svg)
    subprocess.run(["rsvg-convert", "-w", "128", "-h", "128", str(svgd/f"{n}.svg"), "-o", str(tex/f"{n}.png")], check=True)
    prov.append({"type": "bitmap", "file": f"drakescraft:font/holo/{n}.png", "ascent": 8, "height": 9, "chars": [chr(int(cp, 16))]})
fd = root/"assets/drakescraft/font"; fd.mkdir(parents=True, exist_ok=True)
(fd/"holo.json").write_text(json.dumps({"providers": prov}, indent=1, ensure_ascii=True))
json.dump({n: cp for n, (cp, _) in ICONS.items()}, open(root/"scripts/holo_glyphs.json", "w"), indent=1)
print(len(ICONS), "glifos")
