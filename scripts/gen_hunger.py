#!/usr/bin/env python3
"""Barra de hambre: muslo dorado con hueso, 36px (sprites GUI se escalan a 9x9). food_{full,half,empty}[_hunger].png"""
import subprocess
from pathlib import Path
OUT = Path("assets/minecraft/textures/gui/sprites/hud")
def shape(meat0, meat1, bone, line, uid, fill=True):
    m = f'url(#m{uid})' if fill else "#1b1426"
    b = bone if fill else "#2a2038"
    gl = f'<ellipse cx="14" cy="12" rx="5" ry="2.6" fill="#fff" opacity="0.35" transform="rotate(-35 14 12)"/>' if fill else ""
    return f'''<defs><linearGradient id="m{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{meat0}"/><stop offset="1" stop-color="{meat1}"/></linearGradient></defs>
<g stroke="{line}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round">
<path d="M22 22 L29.5 29.5" stroke-width="4.4" stroke="{line}" fill="none"/>
<path d="M22 22 L29.5 29.5" stroke-width="2" stroke="{b}" fill="none"/>
<circle cx="31.4" cy="27" r="2.3" fill="{b}"/><circle cx="27" cy="31.4" r="2.3" fill="{b}"/>
<path d="M5 14 C3 6 10 2.5 17 4.5 C25 6.5 29.5 14.5 24.5 21 C20.5 26 13 25.5 9.5 21.5 C7.5 19.5 5.5 17 5 14Z" fill="{m}"/></g>{gl}'''
def svg(kind, hunger):
    pal = ("#b9d36a", "#5d7a1e", "#d9e6a3", "#12200a") if hunger else ("#f6c453", "#b5602a", "#f4ead2", "#2a1204")
    if kind == "empty":
        body = shape("", "", "", "#4a3a66", "e", fill=False)
    elif kind == "full":
        body = shape(pal[0], pal[1], pal[2], pal[3], "f")
    else:
        body = (f'<g>{shape("", "", "", "#4a3a66", "e2", fill=False)}</g><g clip-path="url(#h)">{shape(pal[0], pal[1], pal[2], pal[3], "h")}</g>'
                '<defs><clipPath id="h"><rect x="0" y="0" width="18" height="36"/></clipPath></defs>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36">{body}</svg>'
OUT.mkdir(parents=True, exist_ok=True)
sv = Path("assets/drakescraft/textures/gear/svg_hud"); sv.mkdir(parents=True, exist_ok=True)
for kind in ("full", "half", "empty"):
    for h in (False, True):
        n = f"food_{kind}{'_hunger' if h else ''}"
        (sv/f"{n}.svg").write_text(svg(kind, h))
        subprocess.run(["rsvg-convert", "-w", "36", "-h", "36", str(sv/f"{n}.svg"), "-o", str(OUT/f"{n}.png")], check=True)
print("ok")
