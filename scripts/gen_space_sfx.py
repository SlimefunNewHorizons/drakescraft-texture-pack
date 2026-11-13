#!/usr/bin/env python3
"""Biblioteca de sonidos espaciales oscuros (dark ambient sci-fi) para DrakesCraft: reactores, drones, ionizacion,
compuertas, radar. Sintesis pura con numpy (sin samples ajenos) -> OGG Vorbis estereo 44.1 kHz.

Salida: assets/drakescraft/sounds/space/<nombre>.ogg   (camas *_loop = bucles sin costura; el resto, one-shots)
Uso:   python3 scripts/gen_space_sfx.py [--out DIR] [--seed N]
Los usa el motor de audio del stream (Star: /opt/stacks/youtube-stream/sfx) y, si se quiere, sounds.json del pack.
"""
import argparse
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
RNG = np.random.default_rng(7)


# ------------------------------------------------------------------ utilidades
def t_of(sec):
    return np.arange(int(sec * SR)) / SR


def white(sec):
    return RNG.standard_normal(int(sec * SR))


def fft_filter(x, lo=None, hi=None, slope_db=0.0, order=4):
    """Filtro de fase cero por FFT: paso-banda suave [lo,hi] Hz y pendiente espectral (dB/octava, + = brillante)."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi:
        g *= 1 / (1 + (np.maximum(f, 1e-3) / hi) ** (2 * order))
    if slope_db:
        g *= (np.maximum(f, 20.0) / 1000.0) ** (slope_db / 6.0206)
    return np.fft.irfft(X * g, n)


def pink(sec):
    return fft_filter(white(sec), lo=20, slope_db=-3.0)


def lfo(sec, hz, phase=0.0):
    return np.sin(2 * np.pi * hz * t_of(sec) + phase)


def smooth_noise(sec, hz):
    """Modulador aleatorio lento (0..1), cambia ~hz veces por segundo."""
    n = int(sec * SR)
    k = max(2, int(sec * hz) + 2)
    pts = RNG.random(k)
    x = np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)
    return fft_filter(x, hi=hz * 1.5)


def env_ad(n, a=0.01, d=0.5, curve=3.0):
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6), np.exp(-(t - a) * curve / max(d, 1e-6)))
    return e


def reverb(x, sec=3.0, wet=0.35, damp=4500.0, pre=0.02):
    """Reverb por convolucion con una respuesta sintetica (ruido exponencial, oscurecida)."""
    n_ir = int(sec * SR)
    t = np.arange(n_ir) / SR
    ir = RNG.standard_normal(n_ir) * np.exp(-t * (6.9 / sec))
    ir = fft_filter(ir, hi=damp)
    ir[: int(pre * SR)] *= 0.0
    ir /= np.sqrt((ir ** 2).sum()) + 1e-9
    n = len(x) + n_ir
    N = 1 << (n - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:n]
    y = y[: len(x) + n_ir // 2]
    out = np.zeros(len(y))
    out[: len(x)] += x * (1 - wet)
    return out + y * wet * 2.5


def stereo(l, r=None, width=0.0):
    """Estereo compatible con mono: graves (<220 Hz) identicos en L y R (sin contrafase), agudos decorrelados (Haas 11 ms)."""
    if r is None:
        low = fft_filter(l, hi=220, order=2)
        hi = l - low
        d = int(0.011 * SR)
        r = low + np.concatenate([np.zeros(d), hi[:-d]])
        l = low + hi
    m, s = (l + r) / 2, (l - r) / 2
    s *= 1 + width
    return np.stack([m + s, m - s], axis=1)


def loopify(x, fade_sec=3.0):
    """Hace el bucle sin costura: solapa la cola sobre la cabeza con crossfade equipotencia."""
    f = int(fade_sec * SR)
    n = x.shape[0] - f
    head, tail = x[:f], x[n:n + f]
    w = np.linspace(0, 1, f)[:, None] if x.ndim == 2 else np.linspace(0, 1, f)
    mix = head * np.sin(w * np.pi / 2) + tail * np.cos(w * np.pi / 2)
    y = x[:n].copy()
    y[:f] = mix
    return y


def norm(x, peak_db=-3.0):
    p = np.abs(x).max() + 1e-9
    return x * (10 ** (peak_db / 20) / p)


def fade_io(x, ms=15):
    n = int(ms * SR / 1000)
    w = np.linspace(0, 1, n)
    x = x.copy()
    x[:n] *= w[:, None] if x.ndim == 2 else w
    x[-n:] *= w[::-1][:, None] if x.ndim == 2 else w[::-1]
    return x


# ------------------------------------------------------------------ camas (bucles)
def reactor_core_loop():
    d = 36
    t = t_of(d)
    base = 55.0
    s = np.zeros_like(t)
    for k, a in zip((1, 2, 3, 4, 6, 8), (1.0, 0.55, 0.30, 0.22, 0.10, 0.05)):
        det = 1 + 0.0007 * k * lfo(d, 0.05 * k, k)
        s += a * np.sin(2 * np.pi * base * k * det * t + k)
    s *= 0.75 + 0.25 * lfo(d, 0.25)                      # latido lento del nucleo
    rumble = fft_filter(white(d), hi=140) * 3.0
    hiss = fft_filter(white(d), lo=2500, hi=9000) * 0.06 * (0.5 + smooth_noise(d, 0.3))
    l = s * 0.5 + rumble * 0.6 + hiss
    r = s * 0.5 + fft_filter(white(d), hi=140) * 1.8 + fft_filter(white(d), lo=2500, hi=9000) * 0.06
    return loopify(stereo(reverb(l, 2.2, 0.25)[: len(t)], reverb(r, 2.4, 0.25)[: len(t)]), 3.0)


def deep_space_drone_loop():
    d = 48
    t = t_of(d)
    chord = (41.2, 61.7, 82.4, 123.5)                     # E1 - B1 - E2 - B2: quinta vacia, oscura
    s = np.zeros_like(t)
    for i, f in enumerate(chord):
        for det in (-0.4, 0.0, 0.5):
            vib = 1 + 0.002 * lfo(d, 0.07 + 0.03 * i, i)
            s += (0.9 / (1 + i)) * np.sin(2 * np.pi * (f + det) * vib * t + RNG.random() * 6)
    air = fft_filter(white(d), lo=300, hi=2200, slope_db=-6) * (0.4 + 0.6 * smooth_noise(d, 0.08)) * 0.35
    shimmer = fft_filter(white(d), lo=4000, hi=11000) * 0.025 * (0.3 + smooth_noise(d, 0.12))
    sig = s * 0.35 + air + shimmer
    L = reverb(sig, 6.0, 0.55, 3000)[: len(t)]
    R = reverb(np.roll(sig, int(0.017 * SR)), 6.5, 0.55, 3000)[: len(t)]
    return loopify(np.stack([L, R], axis=1), 4.0)


def cosmic_wind_loop():
    d = 40
    out = []
    for _ in range(2):
        n = white(d)
        m = 0.25 + 0.75 * smooth_noise(d, 0.15)
        band = fft_filter(n, lo=120, hi=900, slope_db=-4) * m
        band2 = fft_filter(white(d), lo=1500, hi=5000) * 0.12 * (0.2 + smooth_noise(d, 0.25))
        out.append(band + band2)
    return loopify(np.stack(out, axis=1), 3.0)


def coolant_flow_loop():
    d = 30
    out = []
    for _ in range(2):
        n = pink(d)
        flow = fft_filter(n, lo=180, hi=1800) * (0.55 + 0.45 * smooth_noise(d, 2.5))
        bub = fft_filter(white(d), lo=800, hi=3000) * (smooth_noise(d, 7) ** 4) * 0.5
        out.append(flow + bub)
    return loopify(np.stack(out, axis=1), 2.5)


def server_hall_loop():
    d = 30
    t = t_of(d)
    out = []
    for c in range(2):
        fan = fft_filter(white(d), lo=250, hi=3500, slope_db=-3) * 0.7
        blade = sum(a * np.sin(2 * np.pi * f * (1 + 0.0015 * lfo(d, 0.2 + c * 0.03, c)) * t)
                    for f, a in ((118.0 + c * 2, 0.5), (236.0 + c * 3, 0.3), (354.0, 0.15)))
        low = fft_filter(white(d), hi=90) * 1.2
        out.append(fan * 0.45 + blade * 0.35 + low * 0.5)
    return loopify(np.stack(out, axis=1), 2.5)


def cryo_chamber_loop():
    d = 36
    t = t_of(d)
    hum = np.sin(2 * np.pi * 48 * t) * 0.6 + np.sin(2 * np.pi * 96.3 * t) * 0.3
    whistle = np.sin(2 * np.pi * (2200 + 40 * lfo(d, 0.09)) * t) * 0.012 * (0.3 + smooth_noise(d, 0.2))
    mist = fft_filter(white(d), lo=3000, hi=9000) * 0.05 * (0.3 + smooth_noise(d, 0.4))
    sig = hum * 0.45 + whistle + mist
    return loopify(stereo(reverb(sig, 3.5, 0.35)[: len(t)]), 3.0)


# ------------------------------------------------------------------ one-shots
def airlock_hiss():
    d = 3.4
    n = white(d)
    sweep = np.linspace(7000, 900, len(n))
    # filtro variable aproximado: mezcla de bandas con envolvente
    bands = [fft_filter(n, lo=lo, hi=hi) for lo, hi in ((4500, 11000), (1800, 5000), (600, 2000), (250, 900))]
    t = t_of(d)
    out = np.zeros_like(n)
    for i, b in enumerate(bands):
        c = np.clip(1 - np.abs(t / d * 3.0 - i * 0.75) / 1.1, 0, 1)
        out += b * c
    out *= env_ad(len(out), 0.04, d * 0.55, 3.2)
    return fade_io(stereo(reverb(out, 1.2, 0.2)))


def airlock_clunk():
    d = 3.2
    t = t_of(d)
    thud = np.sin(2 * np.pi * (70 - 25 * (1 - np.exp(-t * 9))) * t) * np.exp(-t * 9) * 1.4
    metal = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dc) for f, a, dc in
                ((310, 0.35, 5.0), (587, 0.25, 7.0), (1130, 0.18, 9.0), (2390, 0.1, 12.0)))
    tick = fft_filter(white(d), lo=1500, hi=6000) * np.exp(-t * 60) * 0.5
    s = thud + metal + tick
    return fade_io(stereo(reverb(s, 2.2, 0.35, 3500)))


def reactor_pulse():
    d = 3.0
    t = t_of(d)
    sweep = np.sin(2 * np.pi * (34 + 80 * np.exp(-t * 11)) * t) * np.exp(-t * 3.2) * 1.4
    sub = np.sin(2 * np.pi * 42 * t) * np.exp(-t * 2.0) * 0.5
    air = fft_filter(white(d), lo=200, hi=1200) * np.exp(-t * 6) * 0.35
    return fade_io(stereo(reverb(sweep + sub + air, 2.6, 0.35, 2500)))


def radar_ping():
    d = 4.5
    t = t_of(d)
    p = np.sin(2 * np.pi * 1180 * t) * env_ad(len(t), 0.004, 0.28, 3.0)
    p += 0.35 * np.sin(2 * np.pi * 2360 * t) * env_ad(len(t), 0.004, 0.12, 3.0)
    echo = np.zeros_like(p)
    for k, (dl, g) in enumerate(((0.33, 0.45), (0.71, 0.25), (1.2, 0.12))):
        i = int(dl * SR)
        echo[i:] += p[: len(p) - i] * g
    return fade_io(stereo(reverb(p + echo, 3.0, 0.4, 5000) * 0.6))


def sonar_deep():
    d = 6.5
    t = t_of(d)
    f = 520 * np.exp(-t * 0.45)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env_ad(len(t), 0.02, 0.5, 2.4) * 0.8
    s += 0.25 * np.sin(2 * ph) * env_ad(len(t), 0.02, 0.25, 2.4)
    return fade_io(stereo(reverb(s, 5.0, 0.6, 2800), reverb(s, 5.0, 0.6, 2800)))   # dos IR independientes: ancho sin comb


def ion_crackle():
    d = 5.0
    out = np.zeros(int(d * SR))
    for _ in range(70):
        i = int(RNG.random() * (len(out) - 6000))
        L = int(SR * (0.002 + RNG.random() * 0.01))
        tt = np.arange(L) / SR
        c = np.sin(2 * np.pi * (2500 + RNG.random() * 6000) * tt) * np.exp(-tt * (500 + RNG.random() * 700))
        out[i:i + L] += c * (0.2 + RNG.random() * 0.8)
    out += fft_filter(white(d), lo=5000, hi=12000) * 0.02
    a = out
    b = np.roll(out, int(RNG.random() * 0.02 * SR))
    return fade_io(stereo(reverb(a, 1.0, 0.15), reverb(b, 1.0, 0.15)))


def alarm_distant():
    d = 7.0
    t = t_of(d)
    tone = np.sin(2 * np.pi * 440 * t) * (lfo(d, 1.2) > 0) + np.sin(2 * np.pi * 330 * t) * (lfo(d, 1.2) <= 0)
    tone = tone * 0.5
    tone = fft_filter(tone, hi=900)
    return fade_io(stereo(reverb(tone * env_ad(len(t), 0.1, 5.0, 1.1), 4.5, 0.65, 1800)))


def metal_creak():
    d = 4.0
    t = t_of(d)
    f = 180 + 120 * smooth_noise(d, 2.5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = (np.sin(ph) + 0.5 * np.sin(3.01 * ph) + 0.3 * np.sin(5.2 * ph)) * (smooth_noise(d, 3.0) ** 2)
    s = fft_filter(s, lo=120, hi=3000) * env_ad(len(t), 0.2, 2.4, 1.6)
    return fade_io(stereo(reverb(s * 0.8, 3.0, 0.45, 3000)))


def relay_clicks():
    d = 3.0
    out = np.zeros(int(d * SR))
    pos = 0.0
    while pos < d - 0.2:
        i = int(pos * SR)
        L = int(0.012 * SR)
        tt = np.arange(L) / SR
        c = (np.sin(2 * np.pi * 3200 * tt) + 0.5 * np.sin(2 * np.pi * 5100 * tt)) * np.exp(-tt * 380)
        out[i:i + L] += c * (0.4 + 0.6 * RNG.random())
        pos += 0.07 + RNG.random() * 0.35
    return fade_io(stereo(reverb(out, 0.8, 0.2)))


def energy_swell():
    d = 7.0
    t = t_of(d)
    f = 60 * np.exp(t / d * np.log(30))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * (t / d) ** 2.2
    air = fft_filter(white(d), lo=400, hi=6000, slope_db=4) * (t / d) ** 3 * 0.8
    tail = np.where(t > d - 0.4, np.exp(-(t - (d - 0.4)) * 7), 1.0)
    return fade_io(stereo(reverb((s * 0.6 + air * 0.5) * tail, 3.0, 0.35)), 30)


def signal_static():
    d = 2.6
    t = t_of(d)
    bursts = (smooth_noise(d, 9) > 0.55).astype(float)
    n = fft_filter(white(d), lo=600, hi=7000) * bursts * 0.7
    n += np.sin(2 * np.pi * (900 + 600 * smooth_noise(d, 5)) * t) * bursts * 0.1
    return fade_io(stereo(reverb(n, 0.6, 0.15)))


def station_heartbeat():
    d = 6.0
    out = np.zeros(int(d * SR))
    for beat in range(6):
        for off, g in ((0.0, 1.0), (0.32, 0.65)):
            i = int((beat * 1.0 + off) * SR)
            L = int(0.5 * SR)
            tt = np.arange(L) / SR
            out[i:i + L] += np.sin(2 * np.pi * (52 - 14 * tt * 4) * tt) * np.exp(-tt * 11) * g
    return fade_io(stereo(reverb(out, 2.0, 0.3, 1500)))


BANK = {
    # camas
    "reactor_core_loop": (reactor_core_loop, -23),
    "deep_space_drone_loop": (deep_space_drone_loop, -24),
    "cosmic_wind_loop": (cosmic_wind_loop, -27),
    "coolant_flow_loop": (coolant_flow_loop, -28),
    "server_hall_loop": (server_hall_loop, -27),
    "cryo_chamber_loop": (cryo_chamber_loop, -27),
    # one-shots
    "airlock_hiss": (airlock_hiss, -23),
    "airlock_clunk": (airlock_clunk, -21),
    "reactor_pulse": (reactor_pulse, -21),
    "radar_ping": (radar_ping, -25),
    "sonar_deep": (sonar_deep, -24),
    "ion_crackle": (ion_crackle, -26),
    "alarm_distant": (alarm_distant, -30),
    "metal_creak": (metal_creak, -25),
    "relay_clicks": (relay_clicks, -28),
    "energy_swell": (energy_swell, -21),
    "signal_static": (signal_static, -28),
    "station_heartbeat": (station_heartbeat, -24),
}


def measure_lufs(path):
    import re
    r = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(i[-1]) if i else -70.0


def soft_limit(x, ceiling=0.89):
    """Limitador suave (tanh) solo por encima de ~0.6 para no recortar."""
    k = 0.6
    y = x.copy()
    m = np.abs(y) > k
    y[m] = np.sign(y[m]) * (k + (ceiling - k) * np.tanh((np.abs(y[m]) - k) / (ceiling - k)))
    return y


def write_ogg(path, x, q=5):
    x = np.clip(x, -1, 1)
    wav = path.with_suffix(".wav")
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis", "-q:a", str(q), str(path)], check=True)
    wav.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("assets/drakescraft/sounds/space"))
    ap.add_argument("--solo", nargs="*")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for name, (fn, target) in BANK.items():
        if a.solo and name not in a.solo:
            continue
        x = fn()
        if x.ndim == 1:
            x = stereo(x)
        x = x - x.mean(axis=0)
        x = x / (np.abs(x).max() + 1e-9) * 0.5
        write_ogg(a.out / f"{name}.ogg", x)
        for _ in range(3):                              # converge al LUFS objetivo (con limitador suave)
            g = 10 ** ((target - measure_lufs(a.out / f"{name}.ogg")) / 20)
            x = soft_limit(x * g)
            write_ogg(a.out / f"{name}.ogg", x)
        print(f"{name:24s} {len(x) / SR:5.1f}s  {measure_lufs(a.out / f'{name}.ogg'):6.1f} LUFS  pico {20 * np.log10(np.abs(x).max()):5.1f} dBFS")


if __name__ == "__main__":
    main()
