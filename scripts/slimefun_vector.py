"""Biblioteca de motivos vectoriales (SVG 128x128) para las texturas Slimefun de DrakesCraft.

Cada motivo `m_*(t, p)` devuelve el cuerpo SVG; `t` es el tema (L luz, M medio, D sombra, A acento) y `p` un parametro
(glifo, variante...). Los motivos se combinan: maquina = carcasa + pantalla + glifo; generador = carcasa + turbina; etc.
Estilo: degradados metalicos, aristas de luz, borde oscuro #0d0a14, sombra suave, acentos con brillo.
"""
OUT = "#0d0a14"


def _mix(c, o, f):
    c = c.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % tuple(round(v + (w - v) * f) for v, w in zip((r, g, b), o))


def lt(c, f=0.5):
    return _mix(c, (255, 255, 255), f)


def dk(c, f=0.5):
    return _mix(c, (0, 0, 0), f)


class T:
    def __init__(self, M, L, D, A):
        self.M, self.L, self.D, self.A = M, L, D, A
        self.A2 = lt(A, 0.55)


def tema(t4):
    H, h, d, E = t4
    return T(H, h, d, E)


def lg(i, stops, x1=0, y1=0, x2=1, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def defs(t):
    return (lg("m", [(0, t.L), (0.45, t.M), (1, t.D)]) + lg("mv", [(0, t.L), (0.5, t.M), (1, t.D)], 0, 0, 0, 1)
            + lg("mh", [(0, t.D), (0.3, t.L), (0.6, t.M), (1, t.D)], 0, 0, 1, 0)
            + lg("g", [(0, "#fff3b0"), (0.5, "#e0ad3a"), (1, "#8f6a1c")]) + lg("gv", [(0, "#fff3b0"), (0.5, "#e0ad3a"), (1, "#8f6a1c")], 0, 0, 0, 1)
            + lg("fr", [(0, "#6a5d88"), (1, "#2a2340")]) + lg("ab", [(0, t.A2), (1, t.A)])
            + lg("wd", [(0, "#a8794a"), (0.5, "#6b4a2b"), (1, "#3d2915")], 0, 0, 1, 0)
            + lg("gl", [(0, "#ffffff"), (1, "#a5f3fc")], 0, 0, 1, 1)
            + lg("sc", [(0, "#241a40"), (1, "#0a0712")], 0, 0, 0, 1)
            + f'<radialGradient id="gem" cx=".35" cy=".3" r=".85"><stop offset="0" stop-color="{t.L}"/><stop offset=".5" stop-color="{t.M}"/><stop offset="1" stop-color="{t.D}"/></radialGradient>'
            + f'<radialGradient id="glow" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{t.A2}" stop-opacity=".95"/><stop offset=".55" stop-color="{t.A}" stop-opacity=".45"/><stop offset="1" stop-color="{t.A}" stop-opacity="0"/></radialGradient>'
            + '<filter id="bl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="3"/></filter>')


def doc(body, t, sombra=True):
    sh = '<ellipse cx="64" cy="118" rx="36" ry="5" fill="#000" opacity=".3" filter="url(#bl)"/>' if sombra else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128" '
            f'stroke-linejoin="round" stroke-linecap="round"><defs>{defs(t)}</defs>{sh}{body}</svg>\n')


def P(d, f="url(#m)", sw=3, extra=""):
    return f'<path d="{d}" fill="{f}" stroke="{OUT}" stroke-width="{sw}" {extra}/>'


def R(x, y, w, h, f="url(#m)", rx=0, sw=3):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{OUT}" stroke-width="{sw}"/>'


def C(x, y, r, f="url(#m)", sw=3):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}" stroke="{OUT}" stroke-width="{sw}"/>'


def HL(d, o=0.55, w=2.5, c="#fff"):
    return f'<path d="{d}" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="{w}"/>'


def rivet(x, y, r=3):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#g)" stroke="{OUT}" stroke-width="1.5"/>'


def glow(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#glow)"/>'


def G(body, tr):
    return f'<g transform="{tr}">{body}</g>'


# ---------------------------------------------------------------- glifos (centrados en 0,0, ~ +-24)
def glifo(n, t):
    a, b = t.A2, t.A
    sk = f'stroke="{a}" fill="none"'
    f = f'fill="url(#ab)"'
    W = {
        "bolt": f'<path d="M7 -26 L-15 4 H-3 L-9 26 L16 -7 H3 Z" {f} stroke="{OUT}" stroke-width="1.5"/>',
        "flame": f'<path d="M0 -27 C11 -14 19 -6 17 6 C15 19 5 25 0 25 C-8 25 -17 17 -15 6 C-14 -2 -8 -5 -6 -13 C-2 -9 0 -17 0 -27 Z" {f} stroke="{OUT}" stroke-width="1.5"/><path d="M0 -2 C6 6 9 10 6 16 C3 20 -3 20 -6 16 C-8 10 -3 6 0 -2 Z" fill="#fff" fill-opacity=".8"/>',
        "drop": f'<path d="M0 -27 C12 -9 19 0 19 8 C19 18 10 25 0 25 C-10 25 -19 18 -19 8 C-19 0 -12 -9 0 -27 Z" {f} stroke="{OUT}" stroke-width="1.5"/><ellipse cx="-6" cy="8" rx="3" ry="6" fill="#fff" fill-opacity=".6"/>',
        "star": f'<path d="M0 -26 L7 -8 L26 -8 L11 3 L16 22 L0 11 L-16 22 L-11 3 L-26 -8 L-7 -8 Z" {f} stroke="{OUT}" stroke-width="1.5"/>',
        "gear": f'<circle r="15" {sk} stroke-dasharray="7 3.1" stroke-width="9"/><circle r="12" {sk} stroke-width="5"/><circle r="4" fill="{a}"/>',
        "snow": f'<g {sk} stroke-width="4"><path d="M0 -24 V24 M-21 -12 L21 12 M-21 12 L21 -12"/><path d="M-6 -20 L0 -14 L6 -20 M-6 20 L0 14 L6 20" stroke-width="3"/></g>',
        "ring": f'<circle r="18" {sk} stroke-width="5"/><circle r="7" fill="{a}"/><path d="M-26 0 H-20 M20 0 H26 M0 -26 V-20 M0 20 V26" {sk} stroke-width="4"/>',
        "plus": f'<path d="M-6 -22 H6 V-6 H22 V6 H6 V22 H-6 V6 H-22 V-6 H-6 Z" {f} stroke="{OUT}" stroke-width="1.5"/>',
        "pick": f'<path d="M-24 -6 Q0 -30 24 -6 L18 -2 Q0 -18 -18 -2 Z" {f}/><path d="M0 -14 V26" {sk} stroke-width="5"/>',
        "skull": f'<path d="M-18 4 C-22 -22 22 -22 18 4 L12 8 V18 H-12 V8 Z" {f} stroke="{OUT}" stroke-width="1.5"/><circle cx="-8" cy="0" r="5" fill="{OUT}"/><circle cx="8" cy="0" r="5" fill="{OUT}"/><path d="M-5 10 V16 M0 10 V16 M5 10 V16" stroke="{OUT}" stroke-width="2"/>',
        "leaf": f'<path d="M-22 20 C-26 -10 -2 -26 24 -24 C26 2 10 22 -22 20 Z" {f} stroke="{OUT}" stroke-width="1.5"/><path d="M-22 20 L10 -10" stroke="{OUT}" stroke-width="2" fill="none"/>',
        "sun": f'<circle r="11" fill="url(#ab)"/><g {sk} stroke-width="4"><path d="M0 -26 V-17 M0 17 V26 M-26 0 H-17 M17 0 H26 M-18 -18 L-12 -12 M12 12 L18 18 M18 -18 L12 -12 M-12 12 L-18 18"/></g>',
        "cube": f'<path d="M0 -24 L21 -12 V12 L0 24 L-21 12 V-12 Z" {f} stroke="{OUT}" stroke-width="1.5"/><path d="M0 -24 V0 L21 12 M0 0 L-21 12" stroke="{OUT}" stroke-width="1.5" fill="none"/>',
        "wave": f'<path d="M-24 -8 Q-12 -20 0 -8 T24 -8 M-24 6 Q-12 -6 0 6 T24 6 M-24 20 Q-12 8 0 20 T24 20" {sk} stroke-width="4"/>',
        "anvil": f'<path d="M-24 -18 H22 L26 -10 H10 C10 0 14 6 20 10 V20 H-20 V10 C-14 6 -10 0 -10 -10 H-24 Z" {f} stroke="{OUT}" stroke-width="1.5"/>',
        "arrows": f'<g {sk} stroke-width="4"><path d="M-24 -10 H20 M12 -18 L22 -10 L12 -2 M24 12 H-20 M-12 4 L-22 12 L-12 20"/></g>',
        "chest": f'<path d="M-24 -10 Q-24 -24 0 -24 Q24 -24 24 -10 V22 H-24 Z" {f} stroke="{OUT}" stroke-width="1.5"/><path d="M-24 -4 H24" stroke="{OUT}" stroke-width="2"/><rect x="-4" y="-8" width="8" height="10" fill="#fff3b0" stroke="{OUT}" stroke-width="1.5"/>',
        "eye": f'<path d="M-26 0 Q0 -24 26 0 Q0 24 -26 0 Z" {f} stroke="{OUT}" stroke-width="1.5"/><circle r="8" fill="{OUT}"/><circle cx="-2" cy="-2" r="3" fill="#fff"/>',
        "up": f'<path d="M0 -24 L22 0 H10 V24 H-10 V0 H-22 Z" {f} stroke="{OUT}" stroke-width="1.5"/>',
        "tree": f'<path d="M0 -26 L18 -2 H8 L22 16 H-22 L-8 -2 H-18 Z" {f} stroke="{OUT}" stroke-width="1.5"/><rect x="-4" y="16" width="8" height="10" fill="#6b4a2b"/>',
    }
    return W.get(n, W["bolt"])


# ---------------------------------------------------------------- bloques / maquinas
def m_machine(t, p):
    gl, tipo = (p if isinstance(p, tuple) else (p, ""))
    b = ""
    if tipo == "hopper":
        b += P("M30 6 H98 L84 30 H44 Z", "url(#fr)")
    if tipo == "chimney":
        b += R(86, 4, 16, 24, "url(#fr)", 2) + R(83, 2, 22, 7, "url(#mv)", 2)
    b += R(14, 20, 100, 90, "url(#m)", 9)
    b += HL("M20 30 Q20 24 28 24 H100", 0.6) + HL("M22 104 H106", 0.18, 3, "#000")
    b += R(28, 30, 72, 54, "url(#sc)", 7)
    b += f'<path d="M32 34 H70 L50 80 H32 Z" fill="#fff" opacity=".07"/>'
    b += glow(64, 57, 34) + G(glifo(gl, t), "translate(64 57) scale(1.15)")
    for i in range(5):
        b += f'<rect x="{34 + i * 13}" y="92" width="8" height="12" rx="2" fill="url(#fr)" stroke="{OUT}" stroke-width="1.5"/>'
    b += rivet(22, 28) + rivet(106, 28) + rivet(22, 102) + rivet(106, 102)
    b += f'<circle cx="104" cy="94" r="4" fill="{t.A}" stroke="{OUT}" stroke-width="1.5"/>'
    return b


def m_crate(t, p):
    b = R(14, 22, 100, 88, "url(#m)", 7)
    for x in (24, 92):
        b += R(x, 22, 12, 88, "url(#gv)", 2)
    b += R(14, 22, 100, 14, "url(#gv)", 5) + R(14, 96, 100, 14, "url(#gv)", 5)
    b += R(40, 44, 48, 44, "url(#sc)", 5) + glow(64, 66, 28) + G(glifo(p, t), "translate(64 66) scale(.85)")
    b += rivet(30, 29) + rivet(98, 29) + rivet(30, 103) + rivet(98, 103)
    b += HL("M18 40 V100", 0.3)
    return b


def m_panel(t, p):
    b = P("M20 34 H108 L120 92 H8 Z", "url(#fr)")
    for r in range(3):
        for c in range(5):
            x0, y0 = 20 + c * 17 - r * 2.5, 40 + r * 15
            b += f'<path d="M{x0} {y0} h15 l-2 12 h-15 Z" fill="url(#mv)" stroke="{OUT}" stroke-width="1.5"/><path d="M{x0 + 2} {y0 + 2} h8" stroke="#fff" stroke-opacity=".5" stroke-width="1.5"/>'
    b += '<path d="M24 36 H70 L40 92 H8 Z" fill="#fff" opacity=".1"/>'
    b += P("M56 92 H72 V102 H84 V108 H44 V102 H56 Z", "url(#fr)", 2) + glow(100, 44, 14)
    b += f'<circle cx="104" cy="44" r="4" fill="{t.A2}"/>'
    return b


def m_tank(t, p):
    b = R(28, 12, 72, 14, "url(#mv)", 5) + R(26, 100, 76, 14, "url(#mv)", 5)
    b += f'<path d="M30 24 H98 V102 H30 Z" fill="url(#mh)" stroke="{OUT}" stroke-width="3"/>'
    b += R(40, 32, 48, 62, "url(#sc)", 6)
    b += f'<path d="M42 62 H86 V90 Q86 92 84 92 H44 Q42 92 42 90 Z" fill="url(#ab)" opacity=".85"/><path d="M42 62 Q53 57 64 62 T86 62" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2"/>'
    b += G(glifo(p, t), "translate(64 76) scale(.55)").replace("url(#ab)", "#fff") if False else ""
    b += G(glifo(p, t), "translate(64 46) scale(.5)")
    b += '<path d="M44 36 V90" stroke="#fff" stroke-opacity=".3" stroke-width="3"/>'
    for y in (36, 54, 72):
        b += f'<path d="M30 {y} H36 M92 {y} H98" stroke="{OUT}" stroke-width="2"/>'
    b += R(96, 54, 14, 8, "url(#fr)", 2) + rivet(34, 20) + rivet(94, 20)
    return b


def m_generator(t, p):
    """carcasa con turbina de palas a la vista + bobina"""
    b = R(12, 28, 104, 80, "url(#m)", 10) + R(18, 34, 56, 68, "url(#sc)", 28)
    b += glow(46, 68, 30)
    blades = "".join(f'<path d="M0 0 C-6 -14 -4 -26 0 -30 C6 -24 8 -10 0 0 Z" transform="rotate({k * 60})" fill="url(#ab)" stroke="{OUT}" stroke-width="1.5"/>' for k in range(6))
    b += G(blades, "translate(46 68)") + C(46, 68, 5, "url(#g)", 2)
    b += R(82, 34, 26, 68, "url(#fr)", 5)
    for y in range(40, 98, 8):
        b += f'<path d="M84 {y} H106" stroke="url(#ab)" stroke-width="4" stroke-opacity=".9"/>'
    b += G(glifo(p if p in ("bolt", "flame", "drop", "sun", "snow") else "bolt", t), "translate(95 20) scale(.5)")
    b += R(26, 106, 76, 8, "url(#fr)", 3) + rivet(20, 34) + rivet(108, 104)
    return b


def m_pedestal(t, p):
    b = P("M20 38 H108 L102 52 H26 Z", "url(#m)") + R(40, 52, 48, 46, "url(#mh)", 3)
    for x in (50, 64, 78):
        b += f'<path d="M{x} 54 V96" stroke="{OUT}" stroke-opacity=".35" stroke-width="2"/>'
    b += P("M26 98 H102 L108 112 H20 Z", "url(#m)")
    b += glow(64, 22, 26) + G(glifo(p, t), "translate(64 22) scale(.6)")
    b += f'<ellipse cx="64" cy="38" rx="30" ry="5" fill="none" stroke="{t.A2}" stroke-width="2" opacity=".8"/>'
    return b


def m_miner(t, p):
    b = R(12, 84, 104, 26, "url(#m)", 5) + R(20, 90, 88, 12, "url(#sc)", 3)
    for x in (30, 52, 74, 96):
        b += f'<circle cx="{x}" cy="96" r="3" fill="{t.A2}"/>'
    b += P("M52 84 L58 8 H70 L76 84 Z", "url(#fr)") + R(48, 6, 32, 12, "url(#m)", 3)
    b += f'<path d="M58 24 L70 34 M58 40 L70 50 M58 56 L70 66" stroke="{t.A}" stroke-width="3"/>'
    b += P("M56 84 H72 L64 124 Z", "url(#m)") + '<path d="M58 92 L68 96 M60 102 L68 106" stroke="#fff" stroke-opacity=".5" stroke-width="2"/>'
    b += G(glifo("pick", t), "translate(98 42) scale(.55)")
    return b


def m_forge(t, p):
    b = R(14, 36, 100, 74, "url(#m)", 8) + R(86, 6, 18, 34, "url(#fr)", 3)
    b += f'<path d="M92 4 q-6 -10 4 -14" stroke="#fff" stroke-opacity=".25" stroke-width="4" fill="none"/>'
    b += P("M34 100 V68 Q34 48 64 48 Q94 48 94 68 V100 Z", "url(#sc)") + glow(64, 84, 34)
    b += G(glifo("flame", t), "translate(64 82) scale(.95)")
    b += R(26, 104, 76, 8, "url(#fr)", 3) + rivet(22, 44) + rivet(106, 44)
    return b


def m_reactor(t, p):
    b = R(30, 10, 68, 16, "url(#mv)", 6) + R(24, 100, 80, 16, "url(#mv)", 6)
    b += R(34, 24, 60, 78, "url(#mh)", 10) + C(64, 62, 26, "url(#sc)") + glow(64, 62, 34)
    b += f'<circle cx="64" cy="62" r="14" fill="url(#ab)" stroke="{OUT}" stroke-width="2"/><circle cx="58" cy="56" r="4" fill="#fff" opacity=".8"/>'
    b += f'<circle cx="64" cy="62" r="22" fill="none" stroke="{t.A2}" stroke-width="2" stroke-dasharray="4 4"/>'
    b += R(8, 52, 20, 20, "url(#fr)", 4) + R(100, 52, 20, 20, "url(#fr)", 4)
    return b


# ---------------------------------------------------------------- electronica
def m_pcb(t, p):
    b = P("M10 22 H118 V100 H10 Z", "url(#mv)", 3)
    b += f'<rect x="10" y="22" width="108" height="78" fill="#000" opacity=".15"/>'
    tr = f'stroke="{t.A2}" stroke-width="2.4" fill="none" opacity=".9"'
    b += f'<path d="M20 34 H44 V50 H62 M20 56 H34 V80 H58 M108 34 H84 V48 M108 70 H90 V86 H72 M44 90 H44 M66 30 H100" {tr}/>'
    b += R(46, 40, 34, 34, "#14101e", 3) + f'<path d="M50 44 H70" stroke="#fff" stroke-opacity=".25" stroke-width="2"/>'
    for i in range(6):
        b += f'<path d="M{50 + i * 5.5} 36 v4 M{50 + i * 5.5} 74 v4" stroke="url(#g)" stroke-width="2.4"/>'
        if i < 4:
            b += f'<path d="M42 {44 + i * 7} h4 M80 {44 + i * 7} h4" stroke="url(#g)" stroke-width="2.4"/>'
    b += f'<circle cx="55" cy="49" r="2.5" fill="{t.A2}"/>'
    b += R(16, 84, 18, 10, "#14101e", 2, 2) + R(88, 56, 16, 10, "#14101e", 2, 2)
    for x, y in ((18, 28), (110, 28), (18, 94), (110, 94)):
        b += C(x, y, 3.2, "url(#g)", 1.5)
    b += f'<circle cx="100" cy="90" r="4" fill="{t.A}"/>' + glow(100, 90, 9)
    b += R(30, 100, 70, 8, "url(#gv)", 1, 2)
    for x in range(34, 98, 6):
        b += f'<path d="M{x} 101 v6" stroke="{OUT}" stroke-width="1.2"/>'
    return b


def m_chip(t, p):
    b = ""
    for i in range(6):
        v = 32 + i * 12
        b += f'<path d="M{v} 14 V28 M{v} 100 V114 M14 {v} H28 M100 {v} H114" stroke="url(#g)" stroke-width="5"/>'
    b += R(24, 24, 80, 80, "#1b1530", 7) + R(34, 34, 60, 60, "url(#sc)", 4)
    b += glow(64, 64, 30) + f'<rect x="46" y="46" width="36" height="36" rx="4" fill="url(#ab)" stroke="{OUT}" stroke-width="2"/>'
    b += f'<path d="M52 56 H76 M52 64 H70 M52 72 H76" stroke="{OUT}" stroke-opacity=".5" stroke-width="3"/>'
    b += '<path d="M28 30 H98" stroke="#fff" stroke-opacity=".25" stroke-width="3"/><circle cx="32" cy="32" r="2.5" fill="#fff" opacity=".6"/>'
    return b


def m_module(t, p):
    b = m_chip(t, p).replace("url(#ab)", "url(#ab)")
    b += G(glifo("up", t), "translate(98 98) scale(.4)")
    return b


def m_cable(t, p):
    aislado = p != "bare"
    cond = "url(#g)" if t.M != "x" else "url(#g)"
    col = ("#3a3150", "#6a5d88", "#17122a") if aislado else (t.M, t.L, t.D)
    b = ""
    path = "M18 108 C30 64 52 112 70 70 S100 40 110 20"
    b += f'<path d="{path}" fill="none" stroke="{OUT}" stroke-width="20"/>'
    b += f'<path d="{path}" fill="none" stroke="{col[0]}" stroke-width="15"/>'
    b += f'<path d="{path}" fill="none" stroke="{col[1]}" stroke-width="4" stroke-opacity=".7" transform="translate(-3 -3)"/>'
    b += f'<path d="{path}" fill="none" stroke="{col[2]}" stroke-width="3" stroke-opacity=".7" transform="translate(4 4)"/>'
    if aislado:
        b += f'<path d="{path}" fill="none" stroke="{t.A}" stroke-width="3" stroke-dasharray="3 12" stroke-opacity=".9"/>'
    for (x, y, rot) in ((112, 16, 45), (14, 112, 225)):
        b += G(R(-9, -17, 18, 18, "url(#fr)", 3, 2) + R(-5, -34, 10, 18, "url(#g)", 2, 2) + '<path d="M-3 -33 V-19 M3 -33 V-19" stroke="#fff" stroke-opacity=".6" stroke-width="1.5"/>', f"translate({x} {y}) rotate({rot})")
    return b


def m_ingot(t, p):
    b = P("M18 82 L38 54 H110 L92 82 Z", "url(#m)")
    b += P("M18 82 H92 V100 H18 Z", "url(#mv)") + P("M92 82 L110 54 V72 L92 100 Z", f'{t.D}')
    b += f'<path d="M26 74 L42 58 H100" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="3"/>'
    b += f'<path d="M22 88 H88" stroke="#fff" stroke-opacity=".25" stroke-width="2"/>'
    b += f'<path d="M44 66 H78" stroke="{t.D}" stroke-opacity=".5" stroke-width="2"/>'
    b += f'<path d="M60 20 l3 8 l8 3 l-8 3 l-3 8 l-3 -8 l-8 -3 l8 -3 Z" fill="#fff" opacity=".85" transform="translate(30 -4)"/>'
    return b


def m_nugget(t, p):
    return (P("M30 88 C22 74 30 54 46 50 C54 38 78 40 86 54 C102 58 106 80 96 90 C84 100 44 100 30 88 Z", "url(#gem)")
            + HL("M38 70 C40 60 50 54 60 54", 0.7, 3) + HL("M48 92 H86", 0.2, 2, "#000")
            + '<path d="M70 62 l2 5 l5 2 l-5 2 l-2 5 l-2 -5 l-5 -2 l5 -2 Z" fill="#fff" opacity=".8"/>')


def m_plate(t, p):
    b = P("M14 44 L34 28 H114 L94 44 Z", "url(#m)") + P("M14 44 H94 V104 H14 Z", "url(#mv)") + P("M94 44 L114 28 V88 L94 104 Z", f"{t.D}")
    b += HL("M18 48 H90", 0.5) + HL("M20 98 H88", 0.18, 2, "#000")
    for x, y in ((24, 56), (84, 56), (24, 94), (84, 94)):
        b += rivet(x, y, 3.5)
    b += G(glifo("gear", t), "translate(54 76) scale(.5)")
    return b


def m_dust(t, p):
    b = P("M12 104 C14 84 30 68 44 62 C52 42 74 42 82 62 C98 70 116 86 116 104 Z", "url(#gem)")
    b += HL("M24 94 C30 80 40 72 52 66", 0.6, 3)
    import random
    rnd = random.Random(hash(t.M) & 0xffff)
    for _ in range(22):
        x, y = rnd.randint(22, 104), rnd.randint(70, 100)
        b += f'<circle cx="{x}" cy="{y}" r="{rnd.choice((1.5, 2, 2.5))}" fill="{rnd.choice((t.L, "#fff", t.D))}" opacity=".8"/>'
    b += f'<path d="M96 28 l3 9 l9 3 l-9 3 l-3 9 l-3 -9 l-9 -3 l9 -3 Z" fill="{t.A2}" opacity=".9"/>'
    return b


def m_gem(t, p):
    b = P("M64 8 L100 34 L116 60 L64 120 L12 60 L28 34 Z", "url(#gem)")
    b += f'<path d="M28 34 H100 M12 60 H116 M64 8 L44 34 L36 60 L64 120 M64 8 L84 34 L92 60 L64 120 M44 34 L64 60 L84 34" fill="none" stroke="{OUT}" stroke-opacity=".55" stroke-width="1.8"/>'
    b += f'<path d="M30 36 L44 34 L36 58 Z" fill="#fff" opacity=".6"/><path d="M64 12 L82 32 H46 Z" fill="#fff" opacity=".35"/>'
    b += glow(64, 56, 40)
    return b


def m_orb(t, p):
    b = glow(64, 64, 56) + C(64, 64, 38, "url(#gem)")
    b += f'<ellipse cx="64" cy="64" rx="52" ry="14" fill="none" stroke="{t.A2}" stroke-width="3" transform="rotate(-24 64 64)" opacity=".9"/>'
    b += f'<path d="M40 72 C44 56 58 46 74 48" fill="none" stroke="{t.A2}" stroke-width="3" opacity=".8"/>'
    b += '<ellipse cx="50" cy="48" rx="12" ry="7" fill="#fff" opacity=".6" transform="rotate(-35 50 48)"/>'
    b += f'<path d="M64 20 l2 6 l6 2 l-6 2 l-2 6 l-2 -6 l-6 -2 l6 -2 Z" fill="#fff" opacity=".9" transform="translate(34 -4)"/>'
    return b


def m_core(t, p):
    b = P("M64 10 L112 34 V88 L64 116 L16 88 V34 Z", "url(#m)")
    b += P("M64 10 L112 34 L64 58 L16 34 Z", f"{t.L}") + P("M64 58 L112 34 V88 L64 116 Z", f"{t.D}")
    b += glow(64, 70, 26) + C(64, 70, 13, "url(#ab)", 2) + '<circle cx="60" cy="66" r="4" fill="#fff" opacity=".85"/>'
    b += f'<path d="M64 58 V84 M44 70 H84" stroke="{OUT}" stroke-opacity=".5" stroke-width="2"/>'
    return b


def m_battery(t, p):
    b = R(50, 10, 28, 10, "url(#gv)", 3) + R(34, 18, 60, 98, "url(#mh)", 8) + R(40, 34, 48, 68, "url(#sc)", 5)
    for i in range(4):
        y = 90 - i * 16
        b += f'<rect x="46" y="{y}" width="36" height="11" rx="2" fill="{t.A if i < 3 else t.D}" stroke="{OUT}" stroke-width="1.5"/>'
    b += f'<path d="M64 24 l-5 8 h5 l-3 8 l9 -11 h-6 l3 -5 Z" fill="{t.A2}" transform="translate(0 -6)"/>' + HL("M38 26 V108", 0.35, 3)
    return b


def m_capacitor(t, p):
    b = R(32, 24, 64, 80, "url(#mh)", 12)
    b += R(32, 24, 64, 14, "url(#fr)", 6) + R(32, 90, 64, 14, "url(#fr)", 6)
    for y in (46, 62, 78):
        b += f'<path d="M36 {y} H92" stroke="{t.A}" stroke-width="5" stroke-opacity=".85"/>'
    b += f'<path d="M58 6 V24 M70 6 V24 M58 104 V122 M70 104 V122" stroke="url(#g)" stroke-width="6"/>' + glow(64, 62, 24)
    b += HL("M38 40 V88", 0.4, 3)
    return b


# ---------------------------------------------------------------- objetos varios
def m_disc(t, p):
    b = glow(64, 64, 56) + C(64, 64, 52, "url(#dk)" if False else "url(#m)")
    for r in (44, 36, 28):
        b += f'<circle cx="64" cy="64" r="{r}" fill="none" stroke="#0d0a14" stroke-opacity=".45" stroke-width="2"/>'
    b += C(64, 64, 17, "url(#gem)") + C(64, 64, 5, "#0d0a14", 1)
    b += HL("M26 54 C30 36 44 24 62 20", 0.8, 4)
    return b


def m_bell(t, p):
    b = P("M64 10 C50 10 44 22 44 36 C44 62 34 72 22 90 H106 C94 72 84 62 84 36 C84 22 78 10 64 10 Z", "url(#m)")
    b += R(18, 90, 92, 10, "url(#gold)" if False else "url(#m)", 4) + C(64, 108, 9, "url(#gem)")
    b += HL("M52 20 C48 36 48 56 38 76", 0.7, 4)
    return b


def m_vial(t, p):
    b = R(52, 6, 24, 16, "url(#wd)", 3) + P("M54 22 H74 V40 C94 52 100 72 94 94 C90 108 76 116 64 116 C52 116 38 108 34 94 C28 72 34 52 54 40 Z", "url(#gl)", 3, 'fill-opacity=".35"')
    b += f'<path d="M36 78 C38 70 44 66 52 68 C60 72 68 64 76 68 C84 70 92 72 92 80 C94 100 82 112 64 112 C46 112 34 100 36 78 Z" fill="url(#ab)" stroke="none"/>'
    b += P("M54 22 H74 V40 C94 52 100 72 94 94 C90 108 76 116 64 116 C52 116 38 108 34 94 C28 72 34 52 54 40 Z", "none")
    for x, y, r in ((56, 92, 5), (72, 84, 3.5), (66, 100, 2.5)):
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".6"/>'
    b += HL("M46 56 C42 66 40 76 42 88", 0.8, 4) + glow(64, 92, 26)
    return b


def m_bowl(t, p):
    b = P("M12 62 H116 C116 94 92 112 64 112 C36 112 12 94 12 62 Z", "url(#gv)")
    b += f'<ellipse cx="64" cy="62" rx="52" ry="13" fill="{t.D}" stroke="{OUT}" stroke-width="3"/><ellipse cx="64" cy="60" rx="46" ry="10" fill="url(#gem)"/>'
    b += HL("M28 60 Q44 54 70 54", 0.7, 3) + '<ellipse cx="50" cy="58" rx="6" ry="2.5" fill="#fff" opacity=".5"/>'
    b += HL("M22 76 C28 94 40 104 56 108", 0.35, 3)
    return b


def m_fruit(t, p):
    b = P("M64 36 C34 22 12 46 18 78 C24 106 46 120 64 112 C82 120 104 106 110 78 C116 46 94 22 64 36 Z", "url(#gem)")
    b += P("M64 36 C62 24 66 14 72 8", "none", 4, 'stroke-linecap="round"')
    b += P("M66 22 C78 6 98 8 104 14 C98 30 78 32 66 22 Z", "#4ade80") + '<path d="M70 20 L96 16" stroke="#166534" stroke-width="1.8"/>'
    b += '<ellipse cx="42" cy="58" rx="11" ry="17" fill="#fff" opacity=".4" transform="rotate(24 42 58)"/>'
    b += f'<path d="M84 100 C96 94 102 84 104 72" fill="none" stroke="{t.D}" stroke-opacity=".5" stroke-width="5"/>'
    return b


def m_seed(t, p):
    b = P("M30 112 C22 96 28 74 44 66 H84 C100 74 106 96 98 112 Z", "url(#wd)")
    b += R(40, 60, 48, 10, "url(#gv)", 4) + P("M64 60 C60 40 50 32 40 30 C40 44 48 56 64 60 Z", "#4ade80") + P("M64 60 C68 44 80 36 92 36 C90 50 80 58 64 60 Z", "#22c55e")
    for x, y in ((50, 88), (66, 94), (80, 84), (58, 76), (74, 74)):
        b += f'<ellipse cx="{x}" cy="{y}" rx="6" ry="4" fill="url(#gem)" stroke="{OUT}" stroke-width="1.5" transform="rotate(-30 {x} {y})"/>'
    return b


def m_pod(t, p):
    b = P("M16 104 C16 60 58 22 112 16 C112 66 74 110 16 104 Z", "#22c55e")
    b += P("M16 104 C16 60 58 22 112 16", "none", 3)
    for i, (x, y) in enumerate(((38, 84), (56, 70), (74, 54), (92, 40))):
        b += f'<circle cx="{x}" cy="{y}" r="9" fill="url(#gem)" stroke="{OUT}" stroke-width="2"/><circle cx="{x - 3}" cy="{y - 3}" r="3" fill="#fff" opacity=".6"/>'
    return b


def m_leaf(t, p):
    b = P("M14 112 C6 56 44 14 112 12 C118 70 80 112 14 112 Z", "url(#gem)")
    b += f'<path d="M14 112 C44 80 72 52 106 18" fill="none" stroke="{t.D}" stroke-width="3"/>'
    for (x, y, x2, y2) in ((34, 90, 50, 98), (46, 76, 62, 86), (62, 62, 80, 70), (40, 80, 30, 62), (58, 66, 52, 46), (76, 52, 74, 32)):
        b += f'<path d="M{x} {y} L{x2} {y2}" stroke="{t.D}" stroke-opacity=".7" stroke-width="2"/>'
    b += HL("M20 96 C26 62 54 30 96 18", 0.4, 3)
    return b


def m_mush(t, p):
    b = P("M44 66 H84 L88 108 Q64 116 40 108 Z", "#f5f0e6") + P("M8 68 C8 28 40 10 64 10 C88 10 120 28 120 68 C120 74 112 78 100 78 H28 C16 78 8 74 8 68 Z", "url(#gem)")
    for x, y, r in ((36, 40, 8), (68, 28, 7), (92, 50, 9), (56, 56, 5)):
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".85"/>'
    b += HL("M20 56 C24 36 40 24 60 20", 0.5, 3)
    return b


def m_pepper(t, p):
    b = P("M58 36 C30 30 24 66 40 92 C52 112 64 118 74 112 C96 98 100 56 78 38 C72 34 64 34 58 36 Z", "url(#gem)")
    b += P("M62 36 C60 24 64 14 74 8", "none", 5) + P("M54 34 C60 28 72 28 80 34 C74 40 60 40 54 34 Z", "#4ade80")
    b += '<ellipse cx="48" cy="66" rx="6" ry="16" fill="#fff" opacity=".4" transform="rotate(14 48 66)"/>'
    return b


def m_fillet(t, p):
    b = P("M10 78 C20 40 62 26 96 38 C116 46 120 76 98 92 C76 108 36 112 16 100 C8 94 8 84 10 78 Z", "url(#gem)")
    b += f'<path d="M24 76 C44 56 76 52 100 64 M28 90 C50 76 76 74 98 80" fill="none" stroke="{t.L}" stroke-width="5" stroke-opacity=".7"/>'
    b += HL("M26 62 C44 46 70 40 90 46", 0.6, 3) + '<circle cx="88" cy="70" r="4" fill="#fff" opacity=".5"/>'
    return b


def m_egg(t, p):
    b = P("M64 10 C92 10 108 52 108 78 C108 104 88 118 64 118 C40 118 20 104 20 78 C20 52 36 10 64 10 Z", "url(#gem)")
    for x, y, r in ((50, 56, 6), (74, 80, 7), (48, 90, 5), (80, 52, 4)):
        b += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{t.A}" opacity=".75"/>'
    b += '<ellipse cx="46" cy="40" rx="8" ry="16" fill="#fff" opacity=".45" transform="rotate(14 46 40)"/>'
    return b


def m_flower(t, p):
    b = P("M62 70 C60 90 66 104 64 120", "none", 5) + P("M64 100 C80 92 92 98 96 108 C84 112 72 110 64 100 Z", "#22c55e")
    for k in range(6):
        b += f'<ellipse cx="64" cy="30" rx="12" ry="22" transform="rotate({k * 60} 64 52)" fill="url(#gem)" stroke="{OUT}" stroke-width="2"/>'
    b += C(64, 52, 12, "url(#g)", 2)
    return b


def m_pieces(t, p):
    b = ""
    for x, y, r in ((30, 50, -10), (78, 40, 18), (52, 80, 6), (92, 86, -20)):
        b += G(P("M-18 -12 L16 -16 L22 10 L-12 16 Z", "url(#gem)") + HL("M-14 -8 L12 -12", 0.55, 2.5), f"translate({x} {y}) rotate({r})")
    return b


def m_slices(t, p):
    b = ""
    for x, y, r in ((40, 40, 0), (82, 56, 0), (46, 88, 0)):
        b += C(x, y, 26, "url(#gem)") + C(x, y, 17, f"{t.L}", 1.5) + f'<path d="M{x} {y - 17} V{y + 17} M{x - 17} {y} H{x + 17}" stroke="{t.D}" stroke-opacity=".5" stroke-width="1.5"/>'
    return b


def m_glass(t, p):
    b = P("M30 12 H98 L92 112 Q64 122 36 112 Z", "url(#gl)", 3, 'fill-opacity=".35"')
    b += f'<path d="M33 48 H95 L91 108 Q64 116 37 108 Z" fill="url(#ab)"/><ellipse cx="64" cy="48" rx="31" ry="5" fill="{t.L}"/>'
    b += HL("M42 20 L46 100", 0.8, 4) + R(28, 8, 72, 8, "url(#gl)", 3, 2) + '<circle cx="56" cy="78" r="4" fill="#fff" opacity=".5"/><circle cx="74" cy="68" r="3" fill="#fff" opacity=".5"/>'
    return b


def m_pot(t, p):
    b = R(10, 56, 108, 46, "url(#fr)", 14) + f'<ellipse cx="64" cy="56" rx="54" ry="12" fill="#14101e" stroke="{OUT}" stroke-width="3"/><ellipse cx="64" cy="56" rx="46" ry="8" fill="url(#gem)"/>'
    b += R(2, 62, 14, 8, "url(#fr)", 3) + R(112, 62, 14, 8, "url(#fr)", 3) + HL("M18 72 V92", 0.3, 3)
    b += '<path d="M44 40 q-6 -10 2 -18 M64 36 q-6 -10 2 -18 M84 40 q-6 -10 2 -18" stroke="#fff" stroke-opacity=".5" stroke-width="3" fill="none"/>'
    return b


def m_pan(t, p):
    b = G(R(78, -6, 62, 14, "url(#wd)", 6), "translate(30 70) rotate(-20)") if False else R(88, 66, 38, 12, "url(#wd)", 6)
    b += f'<ellipse cx="54" cy="76" rx="46" ry="30" fill="url(#fr)" stroke="{OUT}" stroke-width="3"/><ellipse cx="54" cy="72" rx="38" ry="22" fill="#14101e"/><ellipse cx="54" cy="70" rx="26" ry="14" fill="url(#gem)"/>'
    b += HL("M20 74 Q24 54 50 48", 0.45, 3)
    return b


# ---------------------------------------------------------------- equipo
def tool_group(inner, rot=45, sc=0.9):
    return G(inner, f"translate(64 64) rotate({rot}) scale({sc}) translate(0 2)")


def handle(y0, y1):
    return R(-4.5, y0, 9, y1 - y0, "url(#wd)", 3, 2.5) + "".join(f'<path d="M-4.5 {y} L4.5 {y + 5}" stroke="{OUT}" stroke-opacity=".5" stroke-width="1.5"/>' for y in range(int(y0) + 6, int(y1) - 4, 10))


def m_sword(t, p):
    b = handle(8, 44) + C(0, 48, 6, "url(#g)", 2.5)
    b += P("M0 -62 L9 -48 V6 H-9 V-48 Z", "url(#mh)") + f'<path d="M0 -56 V2" stroke="{t.D}" stroke-opacity=".6" stroke-width="3"/>' + HL("M-5 -44 V0", 0.7, 2)
    b += R(-24, 4, 48, 8, "url(#g)", 3) + f'<circle cx="0" cy="8" r="4" fill="{t.A}" stroke="{OUT}" stroke-width="1.5"/>'
    return tool_group(b, 45, 0.95)


def m_pick(t, p):
    b = handle(-18, 60) + P("M-52 -6 C-40 -38 40 -38 52 -6 L42 2 C32 -22 -32 -22 -42 2 Z", "url(#m)") + HL("M-44 -6 C-30 -30 30 -30 44 -6", 0.6, 3)
    b += R(-8, -16, 16, 14, "url(#g)", 3) + f'<circle cx="0" cy="-9" r="3" fill="{t.A}"/>'
    return tool_group(b, 45, 0.88)


def m_axe(t, p):
    b = handle(-30, 60) + P("M4 -48 C40 -52 56 -30 50 -2 C40 4 20 2 4 -6 Z", "url(#m)") + HL("M10 -42 C34 -44 46 -30 44 -10", 0.6, 3)
    b += R(-7, -24, 14, 22, "url(#g)", 3)
    return tool_group(b, 45, 0.9)


def m_shovel(t, p):
    b = handle(-4, 62) + P("M0 -58 C26 -58 30 -30 22 -12 H-22 C-30 -30 -26 -58 0 -58 Z", "url(#m)") + HL("M-12 -50 C-22 -40 -22 -24 -16 -14", 0.6, 3)
    b += R(-7, -14, 14, 12, "url(#g)", 3) + f'<path d="M0 -50 V-16" stroke="{t.D}" stroke-opacity=".5" stroke-width="2"/>'
    return tool_group(b, 45, 0.9)


def m_hoe(t, p):
    b = handle(-30, 60) + P("M4 -44 H48 C54 -44 56 -34 50 -30 L10 -18 Z", "url(#m)") + HL("M10 -40 H44", 0.6, 3)
    b += R(-7, -26, 14, 14, "url(#g)", 3)
    return tool_group(b, 45, 0.9)


def m_hammer(t, p):
    b = handle(-10, 60) + R(-30, -44, 60, 34, "url(#m)", 6) + R(-30, -44, 14, 34, "url(#fr)", 4) + R(16, -44, 14, 34, "url(#fr)", 4)
    b += HL("M-12 -40 H12", 0.6, 3) + f'<circle cx="0" cy="-27" r="5" fill="{t.A}" stroke="{OUT}" stroke-width="2"/>' + glow(0, -27, 12)
    return tool_group(b, 45, 0.88)


def m_drill(t, p):
    b = R(-12, -4, 24, 50, "url(#mh)", 6) + R(-8, 44, 16, 20, "url(#fr)", 3) + R(-14, 18, 28, 10, "url(#g)", 3)
    b += P("M-10 -4 L0 -62 L10 -4 Z", "url(#m)")
    for y in (-14, -26, -38, -50):
        b += f'<path d="M-9 {y + 6} L9 {y - 2}" stroke="{OUT}" stroke-opacity=".6" stroke-width="2.5"/>'
    b += f'<circle cx="0" cy="34" r="4" fill="{t.A}"/>'
    return tool_group(b, 45, 0.9)


def m_scythe(t, p):
    b = handle(-34, 60) + P("M2 -50 C40 -62 66 -38 62 -8 C52 -30 30 -40 2 -38 Z", "url(#m)") + HL("M6 -48 C36 -56 58 -40 58 -18", 0.7, 3)
    b += R(-6, -40, 12, 10, "url(#g)", 3)
    return tool_group(b, 35, 0.9)


def m_trident(t, p):
    b = handle(-10, 64) + R(-6, -22, 12, 14, "url(#g)", 3)
    b += P("M-22 -14 V-50 L-14 -62 L-8 -50 V-22 H8 V-50 L14 -62 L22 -50 V-14 Q0 -4 -22 -14 Z", "url(#m)") + P("M-3 -22 L0 -66 L3 -22 Z", "url(#m)")
    return tool_group(b, 45, 0.88)


def m_staff(t, p):
    b = handle(-12, 66) + R(-8, -20, 16, 10, "url(#g)", 3)
    b += glow(0, -38, 30) + P("M0 -64 L16 -50 L0 -20 L-16 -50 Z", "url(#gem)") + '<path d="M0 -64 L0 -20 M-16 -50 H16" stroke="#0d0a14" stroke-opacity=".4" stroke-width="1.5" fill="none"/>'
    b += f'<path d="M-14 -34 C-24 -40 -22 -56 -14 -60 M14 -34 C24 -40 22 -56 14 -60" fill="none" stroke="url(#g)" stroke-width="4"/>'
    return tool_group(b, 45, 0.9)


def m_bow(t, p):
    ball = p == "cross"
    if ball:
        b = R(-8, -28, 16, 76, "url(#wd)", 4) + P("M-52 -26 C-30 -46 30 -46 52 -26 L50 -18 C28 -34 -28 -34 -50 -18 Z", "url(#m)")
        b += f'<path d="M-50 -22 L0 14 L50 -22" fill="none" stroke="#e5e7eb" stroke-width="2.5"/><path d="M0 14 V-40" stroke="{t.A}" stroke-width="4"/><path d="M-4 -40 L0 -52 L4 -40 Z" fill="{t.A2}"/>'
        return tool_group(b, 45, 0.9)
    b = P("M-6 -56 C40 -40 40 40 -6 56 L-2 46 C26 30 26 -30 -2 -46 Z", "url(#m)") + HL("M-2 -50 C32 -36 32 36 -2 50", 0.5, 3)
    b += f'<path d="M-6 -56 L-6 56" stroke="#e5e7eb" stroke-width="2.5"/>' + R(-12, -8, 12, 16, "url(#g)", 3)
    return tool_group(b, 45, 0.9)


def m_shield(t, p):
    b = P("M64 10 L112 26 V62 C112 90 90 108 64 120 C38 108 16 90 16 62 V26 Z", "url(#m)")
    b += P("M64 18 L104 31 V62 C104 84 86 100 64 111 C42 100 24 84 24 62 V31 Z", "url(#mv)", 1.5)
    b += glow(64, 62, 30) + G(glifo("star", t), "translate(64 62) scale(.9)") + HL("M30 34 V62 C30 74 36 84 44 92", 0.5, 3)
    return b


def m_helmet(t, p):
    b = P("M22 100 V62 C22 30 44 14 64 14 C84 14 106 30 106 62 V100 H88 V84 H40 V100 Z", "url(#m)")
    b += R(34, 56, 60, 14, "url(#sc)", 5) + glow(64, 63, 24)
    b += P("M56 14 L64 4 L72 14 Z", "url(#g)", 2) + R(22, 88, 84, 8, "url(#gv)", 3)
    b += f'<path d="M26 62 C26 36 44 20 62 18" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="3"/><path d="M64 56 V70" stroke="{t.A2}" stroke-width="3"/>'
    return b


def m_chest(t, p):
    b = P("M8 36 L34 14 H48 C52 26 76 26 80 14 H94 L120 36 L104 52 V112 H24 V52 Z", "url(#m)")
    b += P("M48 14 C52 26 76 26 80 14", "none", 2) + R(36, 62, 56, 38, "url(#sc)", 6) + glow(64, 81, 22) + G(glifo("star", t), "translate(64 81) scale(.5)")
    b += R(24, 100, 80, 12, "url(#gv)", 3) + HL("M30 54 V98", 0.35, 3) + rivet(40, 40) + rivet(88, 40)
    return b


def m_legs(t, p):
    b = P("M26 12 H102 V46 L94 112 H70 L64 56 L58 112 H34 L26 46 Z", "url(#mh)")
    b += R(26, 12, 76, 14, "url(#gv)", 4) + R(58, 20, 12, 8, "url(#fr)", 2) + HL("M32 34 L40 104", 0.4, 3)
    b += f'<path d="M64 30 V56" stroke="{OUT}" stroke-width="2"/><circle cx="64" cy="34" r="4" fill="{t.A}"/>'
    return b


def m_boots(t, p):
    b = ""
    for dx in (0, 54):
        b += P(f"M{12 + dx} 20 H{44 + dx} V70 L{62 + dx} 84 V104 H{12 + dx} Z", "url(#m)") + R(10 + dx, 18, 36, 10, "url(#gv)", 3)
        b += f'<path d="M{16 + dx} 98 H{58 + dx}" stroke="{OUT}" stroke-width="5"/><path d="M{16 + dx} 40 H{40 + dx}" stroke="{t.A}" stroke-width="3"/>' + HL(f"M{18 + dx} 32 V90", 0.4, 3)
    return b


def m_backpack(t, p):
    b = P("M26 22 C26 8 102 8 102 22 V108 C102 114 96 118 88 118 H40 C32 118 26 114 26 108 Z", "url(#m)")
    b += R(34, 62, 60, 40, "url(#mv)", 8) + R(48, 78, 32, 10, "url(#sc)", 3) + rivet(64, 84, 4)
    b += P("M40 36 C40 26 88 26 88 36 V52 H40 Z", "url(#mv)", 2) + R(24, 54, 8, 36, "url(#gv)", 3) + R(96, 54, 8, 36, "url(#gv)", 3)
    b += HL("M32 28 V104", 0.35, 3) + f'<circle cx="64" cy="44" r="4" fill="{t.A}"/>'
    return b


def m_book(t, p):
    b = P("M18 14 H104 V108 H26 C20 108 16 104 16 98 V16 Z", "url(#m)") + R(22, 100, 84, 12, "#f5f0e6", 2, 2)
    b += R(22, 14, 10, 88, f"{t.D}", 2, 2) + glow(66, 52, 28) + G(glifo(p if isinstance(p, str) and p else "star", t), "translate(66 52) scale(.9)")
    b += f'<path d="M40 88 H96" stroke="url(#g)" stroke-width="4"/>' + HL("M38 22 H98", 0.4, 3)
    return b


def m_scroll(t, p):
    b = R(22, 26, 84, 76, "#f1e6c8", 6) + R(14, 18, 100, 14, "url(#wd)", 7) + R(14, 96, 100, 14, "url(#wd)", 7)
    b += f'<path d="M34 46 H94 M34 58 H84 M34 70 H92" stroke="{t.D}" stroke-opacity=".7" stroke-width="3"/>' + G(glifo("star", t), "translate(88 82) scale(.35)")
    return b


def m_card(t, p):
    b = R(22, 14, 84, 100, "url(#g)", 8) + R(28, 20, 72, 88, "#f5f0e6", 5, 2) + R(34, 26, 60, 46, "url(#sc)", 4)
    b += glow(64, 49, 26) + G(glifo(p if p else "star", t), "translate(64 49) scale(.7)")
    b += f'<path d="M36 84 H92 M36 94 H78" stroke="{t.D}" stroke-width="3" stroke-opacity=".7"/>'
    return b


def m_key(t, p):
    b = C(40, 42, 24, "url(#g)") + C(40, 42, 10, "#14101e", 2.5) + R(58, 36, 54, 12, "url(#g)", 4)
    b += R(90, 46, 10, 20, "url(#gv)", 3) + R(104, 46, 10, 14, "url(#gv)", 3) + HL("M26 28 C32 22 42 20 50 24", 0.7, 3)
    return b


def m_talisman(t, p):
    b = f'<path d="M30 6 C34 30 94 30 98 6" fill="none" stroke="{OUT}" stroke-width="9"/><path d="M30 6 C34 30 94 30 98 6" fill="none" stroke="url(#gv)" stroke-width="5"/>'
    b += P("M64 30 L100 52 V82 L64 118 L28 82 V52 Z", "url(#g)") + P("M64 40 L90 56 V78 L64 106 L38 78 V56 Z", "url(#gem)", 2)
    b += glow(64, 74, 22) + G(glifo("star", t), "translate(64 74) scale(.5)") + HL("M36 56 L62 38", 0.7, 3)
    return b


def m_ring(t, p):
    b = glow(64, 36, 28) + f'<ellipse cx="64" cy="76" rx="38" ry="38" fill="none" stroke="{OUT}" stroke-width="20"/><ellipse cx="64" cy="76" rx="38" ry="38" fill="none" stroke="url(#g)" stroke-width="14"/>'
    b += P("M64 18 L82 36 L64 54 L46 36 Z", "url(#gem)") + HL("M52 34 L64 24", 0.8, 3)
    return b


def m_rune(t, p):
    b = P("M64 10 L112 38 V90 L64 118 L16 90 V38 Z", "url(#mv)") + P("M64 22 L100 44 V84 L64 106 L28 84 V44 Z", "url(#sc)", 2)
    b += glow(64, 64, 34) + G(glifo(p if p else "star", t), "translate(64 64) scale(1.1)") + HL("M20 42 L62 16", 0.45, 3)
    return b


def m_kit(t, p):
    b = R(14, 36, 100, 72, "url(#m)", 8) + R(14, 36, 100, 20, "url(#mv)", 6) + R(56, 28, 16, 14, "url(#gv)", 3)
    b += R(40, 66, 48, 32, "#f5f0e6", 5) + f'<path d="M64 70 V94 M52 82 H76" stroke="{t.A}" stroke-width="9"/>' + HL("M20 48 H108", 0.35, 3)
    return b


def m_frame(t, p):
    b = R(14, 14, 100, 100, "url(#g)", 8) + R(26, 26, 76, 76, "url(#sc)", 4) + glow(64, 64, 34) + G(glifo(p if p else "eye", t), "translate(64 64)")
    b += '<path d="M30 30 H64 L30 64 Z" fill="#fff" opacity=".08"/>' + rivet(20, 20) + rivet(108, 20) + rivet(20, 108) + rivet(108, 108)
    return b


def m_door(t, p):
    b = R(28, 8, 72, 112, "url(#mh)", 5) + R(38, 18, 52, 40, "url(#mv)", 3, 2) + R(38, 66, 52, 44, "url(#mv)", 3, 2)
    b += C(86, 66, 4.5, "url(#g)", 2) + HL("M32 14 V112", 0.4, 3) + f'<path d="M44 24 H84" stroke="{t.A}" stroke-width="2.5"/>'
    return b


def m_pane(t, p):
    b = R(16, 16, 96, 96, "url(#gl)", 6, 3).replace('fill="url(#gl)"', 'fill="url(#gl)" fill-opacity=".4"')
    b += f'<path d="M16 16 H112 V112 H16 Z" fill="none" stroke="{t.A}" stroke-width="3" stroke-opacity=".7"/>' + HL("M28 30 L52 20 M28 54 L70 20", 0.85, 5)
    return b


def m_trash(t, p):
    b = R(30, 36, 68, 80, "url(#mh)", 8) + R(24, 24, 80, 14, "url(#mv)", 5) + R(50, 14, 28, 12, "url(#mv)", 4)
    for x in (44, 58, 72, 86):
        b += f'<path d="M{x} 46 V104" stroke="{OUT}" stroke-opacity=".5" stroke-width="4"/>'
    b += G(glifo("down" if False else "up", t), "translate(64 76) scale(.0)")
    return b


def m_motor(t, p):
    b = R(14, 34, 76, 60, "url(#mh)", 10) + R(86, 52, 28, 24, "url(#fr)", 4) + R(104, 56, 14, 16, "url(#g)", 3)
    for x in (28, 42, 56, 70):
        b += f'<path d="M{x} 38 V90" stroke="{OUT}" stroke-opacity=".4" stroke-width="3"/>'
    b += R(8, 90, 90, 14, "url(#fr)", 4) + f'<circle cx="46" cy="64" r="12" fill="url(#sc)" stroke="{OUT}" stroke-width="2"/>' + G(glifo("bolt", t), "translate(46 64) scale(.34)")
    return b


def m_apiary(t, p):
    b = R(14, 24, 100, 90, "url(#m)", 8)
    for r, c in ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)):
        x, y = 30 + c * 26 + (13 if r else 0), 40 + r * 30
        b += f'<path d="M{x} {y - 14} l12 7 v14 l-12 7 l-12 -7 v-14 Z" fill="url(#ab)" stroke="{OUT}" stroke-width="2"/>'
    b += R(14, 18, 100, 12, "url(#gv)", 4) + HL("M20 44 V104", 0.3, 3)
    return b


def m_banner(t, p):
    b = R(28, 6, 72, 10, "url(#wd)", 4) + P("M32 16 H96 V92 L64 112 L32 92 Z", "url(#mv)") + glow(64, 52, 26) + G(glifo("star", t), "translate(64 52) scale(.9)")
    b += HL("M38 24 V86", 0.35, 3)
    return b


def m_carbon(t, p):
    b = ""
    for x, y, s in ((28, 66, 1), (70, 52, 1.1), (50, 88, 0.9)):
        b += G(P("M-26 -4 L-14 -26 L12 -24 L28 -2 L16 24 L-12 24 Z", "url(#gem)") + HL("M-18 -6 L-10 -20 L8 -20", 0.5, 3), f"translate({x} {y}) scale({s})")
    return b


def m_scrap(t, p):
    b = P("M14 94 L22 62 L46 70 L56 38 L78 58 L98 36 L114 70 L104 100 L60 108 Z", "url(#gem)")
    b += f'<path d="M22 62 L46 86 L56 38 M78 58 L70 94 L104 100 M98 36 L84 72" fill="none" stroke="{OUT}" stroke-opacity=".55" stroke-width="2"/>' + HL("M30 70 L52 44", 0.5, 3)
    return b


def m_fibre(t, p):
    b = ""
    for i in range(7):
        x = 24 + i * 12
        b += f'<path d="M{x} 112 C{x - 14} 80 {x + 22} 50 {x + 8} 12" fill="none" stroke="{OUT}" stroke-width="9"/><path d="M{x} 112 C{x - 14} 80 {x + 22} 50 {x + 8} 12" fill="none" stroke="{t.M if i % 2 else t.L}" stroke-width="5"/>'
    return b


def m_mesh(t, p):
    b = R(14, 22, 100, 84, "url(#sc)", 4)
    for i in range(1, 8):
        b += f'<path d="M{14 + i * 12.5} 22 V106" stroke="url(#ab)" stroke-width="3.5"/>' + f'<path d="M14 {22 + i * 10.5} H114" stroke="url(#ab)" stroke-width="3.5"/>'
    b += R(14, 22, 100, 84, "none", 4)
    return b


def m_shell(t, p):
    b = P("M64 8 C100 8 116 40 108 76 C102 104 84 118 64 118 C44 118 26 104 20 76 C12 40 28 8 64 8 Z", "url(#gem)")
    b += f'<path d="M64 8 V118 M24 52 H104 M28 90 H100" fill="none" stroke="{OUT}" stroke-opacity=".45" stroke-width="2"/>' + glow(64, 62, 30) + HL("M36 30 C42 22 52 16 62 14", 0.7, 4)
    return b


def m_flame(t, p):
    return glow(64, 70, 54) + G(glifo("flame", t), "translate(64 66) scale(2.2)")


def m_star(t, p):
    return glow(64, 64, 56) + G(glifo("star", t), "translate(64 64) scale(2.2)")


def m_alloy(t, p):
    b = m_ingot(t, p)
    b += f'<path d="M30 76 C44 66 60 82 80 70" fill="none" stroke="{t.A}" stroke-width="3" opacity=".9"/>'
    return b


def m_rocket(t, p):
    b = P("M64 6 C84 24 90 52 88 84 H40 C38 52 44 24 64 6 Z", "url(#m)") + C(64, 46, 12, "url(#sc)", 3) + glow(64, 46, 14)
    b += P("M40 70 L18 100 L40 94 Z", "url(#fr)") + P("M88 70 L110 100 L88 94 Z", "url(#fr)") + P("M48 84 H80 L72 116 H56 Z", f"{t.A}", 2)
    b += glow(64, 106, 16)
    return b


def m_bullet(t, p):
    b = ""
    for dx in (-18, 18):
        b += G(R(-9, 8, 18, 50, "url(#g)", 3) + P("M-9 8 C-9 -14 -4 -28 0 -34 C4 -28 9 -14 9 8 Z", "url(#m)") + R(-9, 52, 18, 6, "url(#fr)", 2) + HL("M-5 12 V50", 0.6, 2.5), f"translate({64 + dx} 56) rotate({dx // 3})")
    return b


def m_grenade(t, p):
    b = R(52, 6, 24, 14, "url(#fr)", 3) + P("M76 12 C96 12 104 22 96 30", "none", 3) + C(64, 72, 38, "url(#gem)")
    b += f'<path d="M30 72 H98 M64 34 V110 M38 48 Q64 62 90 48 M38 96 Q64 82 90 96" stroke="{OUT}" stroke-opacity=".55" stroke-width="2.5" fill="none"/>'
    b += '<ellipse cx="48" cy="52" rx="10" ry="6" fill="#fff" opacity=".55" transform="rotate(-35 48 52)"/>' + f'<circle cx="64" cy="22" r="5" fill="{t.A}" stroke="{OUT}" stroke-width="2"/>'
    return b


def m_cube(t, p):
    import random
    b = P("M64 12 L112 36 L64 60 L16 36 Z", f"{t.L}") + P("M16 36 L64 60 V116 L16 92 Z", "url(#mv)") + P("M112 36 L64 60 V116 L112 92 Z", f"{t.D}")
    r = random.Random(sum(map(ord, t.M)))
    for _ in range(14):
        x, y = r.randint(24, 56), r.randint(66, 100)
        b += f'<rect x="{x}" y="{y}" width="5" height="4" fill="{t.D}" opacity=".6"/>'
    b += HL("M20 38 L64 16 L108 38", 0.6, 3) + f'<path d="M64 60 V116" stroke="{OUT}" stroke-width="2"/>'
    return b


def m_wool(t, p):
    b = R(14, 30, 100, 70, "url(#mv)", 14)
    for y in (46, 62, 78):
        b += f'<path d="M20 {y} Q40 {y - 8} 64 {y} T108 {y}" fill="none" stroke="{t.D}" stroke-opacity=".45" stroke-width="3"/>'
    b += R(28, 96, 72, 14, "url(#mv)", 7) + HL("M24 38 H100", 0.45, 3)
    return b


def m_stick(t, p):
    return G(handle(-60, 60) + HL("M-3 -56 V54", 0.5, 2), "translate(64 64) rotate(45) scale(1.05)")


def m_lens(t, p):
    b = C(64, 64, 46, "url(#fr)") + C(64, 64, 34, "url(#sc)", 2) + glow(64, 64, 34)
    b += f'<circle cx="64" cy="64" r="22" fill="url(#ab)" fill-opacity=".55" stroke="{t.A2}" stroke-width="2"/>' + HL("M40 48 C46 38 56 32 68 32", 0.9, 5)
    b += '<ellipse cx="80" cy="80" rx="8" ry="4" fill="#fff" opacity=".5" transform="rotate(-35 80 80)"/>'
    return b


MOTIVOS = {k[2:]: v for k, v in dict(globals()).items() if k.startswith("m_") and callable(v)}
