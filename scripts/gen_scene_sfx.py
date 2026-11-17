#!/usr/bin/env python3
"""Sonidos de ambiente para TODAS las escenas del stream 24/7 (naturaleza, clima, agua, volcan, ciudad, cafe) con el mismo
tratamiento dark ambient que gen_space_sfx.py, mas las RECETAS por escena (scripts/scene_recipes.json).

  python3 scripts/gen_scene_sfx.py                 # genera los sonidos nuevos en assets/drakescraft/sounds/space/
  python3 scripts/gen_scene_sfx.py --demos DIR     # ademas renderiza una demo de 75 s por escena (OGG) en DIR
Escenas (16): array_suiza bosque desierto latam_noche montana nieve orbital reactor scp_contencion scp_exterior
              submarina tormenta volcanica veo3_manana veo3_tarde veo3_noche
"""
import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import gen_space_sfx as G  # noqa: E402

SR, RNG = G.SR, G.RNG
t_of, white, pink, fft_filter, lfo, smooth_noise = G.t_of, G.white, G.pink, G.fft_filter, G.lfo, G.smooth_noise
reverb, stereo, loopify, tape, fade_io, env_ad = G.reverb, G.stereo, G.loopify, G.tape, G.fade_io, G.env_ad


def two(fn, d):
    """Dos canales independientes (ancho natural) a partir de un generador mono."""
    return np.stack([fn(), fn()], axis=1)


# ------------------------------------------------------------------ clima y agua
def rain_loop():
    d = 32
    def ch():
        dense = fft_filter(pink(d), lo=350, hi=9500, slope_db=-1) * (0.7 + 0.3 * smooth_noise(d, 0.07))
        drops = fft_filter(white(d), lo=2500, hi=11000) * (smooth_noise(d, 22) ** 3) * 0.55
        low = fft_filter(white(d), hi=140) * 0.12
        return dense + drops + low
    return loopify(two(ch, d), 3.0)


def window_rain_loop():
    d = 30
    def ch():
        glass = fft_filter(pink(d), lo=300, hi=3800) * 0.6
        taps = np.zeros(int(d * SR))
        for _ in range(240):
            i = int(RNG.random() * (len(taps) - 3000)); L = int(0.03 * SR); tt = np.arange(L) / SR
            f = 900 + RNG.random() * 1800
            taps[i:i + L] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 140) * (0.15 + RNG.random() * 0.5)
        return glass + taps * 0.6
    return loopify(two(ch, d), 2.5)


def thunder():
    d = 10.0
    t = t_of(d)
    crack = fft_filter(white(d), lo=150, hi=4000) * np.exp(-t * 14) * 1.2
    roll = fft_filter(white(d), lo=25, hi=130, order=2) * (0.3 + 0.7 * np.abs(np.sin(2 * np.pi * 0.5 * t + 1.0))) * env_ad(len(t), 0.25, 4.5, 1.1) * 4
    mid = fft_filter(white(d), lo=120, hi=600) * env_ad(len(t), 0.15, 2.5, 1.7) * 0.7
    s = crack + roll + mid
    return fade_io(stereo(reverb(s, 5.0, 0.55, 3000), reverb(s, 5.0, 0.55, 3000)), 30)


def underwater_loop():
    d = 36
    t = t_of(d)
    def ch():
        body = fft_filter(white(d), hi=650, order=2) * (0.5 + 0.5 * smooth_noise(d, 0.07)) * 2.0
        sub = np.sin(2 * np.pi * 38 * t * (1 + 0.002 * smooth_noise(d, 0.05))) * 0.5
        swirl = fft_filter(white(d), lo=200, hi=1400) * (0.2 + 0.8 * smooth_noise(d, 0.3)) * 0.4
        return body + sub + swirl
    return loopify(tape(two(ch, d), 1.3), 3.0)


def bubbles():
    d = 3.5
    out = np.zeros(int(d * SR))
    for _ in range(14):
        i = int(RNG.random() * (len(out) - SR // 4)); L = int(0.06 * SR); tt = np.arange(L) / SR
        f0 = 250 + RNG.random() * 500
        ph = 2 * np.pi * np.cumsum(f0 * (1 + 3.0 * tt / 0.06)) / SR
        out[i:i + L] += np.sin(ph) * np.exp(-tt * 55) * (0.3 + RNG.random() * 0.7)
    return fade_io(stereo(fft_filter(reverb(out, 1.8, 0.35, 2400), hi=2600)))


# ------------------------------------------------------------------ viento y paisaje
def forest_leaves_loop():
    d = 36
    def ch():
        g = (0.25 + 0.75 * smooth_noise(d, 0.13))
        leaves = fft_filter(white(d), lo=1500, hi=7500, slope_db=-2) * g * 0.7
        wind = fft_filter(white(d), lo=90, hi=420, order=2) * g * 1.4
        return leaves + wind
    return loopify(two(ch, d), 3.0)


def crickets_loop():
    d = 30
    out = np.zeros((int(d * SR), 2))
    for _ in range(7):
        f = 4200 + RNG.random() * 1100
        pan = RNG.random()
        rate = 24 + RNG.random() * 14
        sig = np.zeros(int(d * SR))
        t = RNG.random() * 0.8
        while t < d - 0.5:
            n_chirps = int(3 + RNG.random() * 3)
            for k in range(n_chirps):
                i = int((t + k * 0.075) * SR); L = int(0.045 * SR)
                if i + L >= len(sig): break
                tt = np.arange(L) / SR
                sig[i:i + L] += np.sin(2 * np.pi * f * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * rate * tt)) * np.hanning(L)
            t += 0.55 + RNG.random() * 0.9
        out[:, 0] += sig * (1 - pan) * 0.12
        out[:, 1] += sig * pan * 0.12
    return loopify(out, 2.5)


def birds_chirp():
    d = 3.2
    out = np.zeros(int(d * SR))
    t0 = 0.1
    for _ in range(int(3 + RNG.random() * 3)):
        L = int((0.08 + RNG.random() * 0.12) * SR); tt = np.arange(L) / SR
        f0 = 2400 + RNG.random() * 2200
        sweep = f0 * (1 + 0.5 * RNG.choice([-1, 1]) * tt / (L / SR))
        ph = 2 * np.pi * np.cumsum(sweep) / SR
        i = int(t0 * SR)
        if i + L >= len(out): break
        out[i:i + L] += (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.hanning(L) * 0.5
        t0 += 0.12 + RNG.random() * 0.25
    return fade_io(stereo(reverb(out, 1.6, 0.3, 6000)))


def desert_wind_loop():
    d = 40
    def ch():
        swell = 0.2 + 0.8 * smooth_noise(d, 0.06)
        low = fft_filter(white(d), lo=70, hi=520, slope_db=-3) * swell * 1.8
        sand = fft_filter(white(d), lo=3500, hi=9000) * (0.15 + 0.85 * smooth_noise(d, 0.2)) * swell * 0.28
        return low + sand
    return loopify(tape(two(ch, d), 1.2), 3.0)


def snow_wind_loop():
    d = 40
    t = t_of(d)
    def ch():
        g = 0.25 + 0.75 * smooth_noise(d, 0.09)
        howl = fft_filter(white(d), lo=450, hi=2600, slope_db=-2) * g
        whistle = np.sin(2 * np.pi * (1100 + 300 * smooth_noise(d, 0.15)) * t) * 0.025 * g
        ice = fft_filter(white(d), lo=4500, hi=10500) * 0.05 * g
        return howl * 0.8 + whistle + ice
    return loopify(two(ch, d), 3.0)


def mountain_wind_loop():
    d = 40
    def ch():
        g = 0.15 + 0.85 * smooth_noise(d, 0.07)
        w = fft_filter(white(d), lo=110, hi=1300, slope_db=-4) * g * 1.4
        far = fft_filter(white(d), hi=90) * 0.8
        return w + far
    return loopify(tape(two(ch, d), 1.2), 3.0)


# ------------------------------------------------------------------ volcan y fuego
def magma_rumble_loop():
    d = 36
    t = t_of(d)
    def ch():
        brown = fft_filter(white(d), lo=18, hi=120, order=2) * (0.5 + 0.5 * smooth_noise(d, 0.08)) * 4.5
        mid = fft_filter(white(d), lo=140, hi=520) * (0.15 + 0.85 * smooth_noise(d, 0.12)) * 0.45
        sub = np.sin(2 * np.pi * 31 * t * (1 + 0.004 * smooth_noise(d, 0.05))) * 0.8
        return brown + mid + sub
    return loopify(tape(two(ch, d), 1.4), 3.0)


def lava_bubbling_loop():
    d = 30
    def ch():
        out = fft_filter(white(d), lo=60, hi=380) * 0.25
        for _ in range(180):
            i = int(RNG.random() * (len(out) - SR)); L = int((0.05 + RNG.random() * 0.15) * SR); tt = np.arange(L) / SR
            f = 70 + RNG.random() * 150
            out[i:i + L] += np.sin(2 * np.pi * f * (1 + 2 * tt) * tt) * np.exp(-tt * 28) * (0.2 + RNG.random() * 0.8)
        for _ in range(260):
            i = int(RNG.random() * (len(out) - 2000)); L = int(0.01 * SR)
            out[i:i + L] += fft_filter(white(0.011)[:L], lo=900, hi=5000) * np.exp(-np.arange(L) / SR * 400) * 1.2
        return out
    return loopify(two(ch, d), 2.5)


def ember_crackle():
    d = 6.0
    def ch():
        out = np.zeros(int(d * SR))
        for _ in range(110):
            i = int(RNG.random() * (len(out) - 3000)); L = int((0.004 + RNG.random() * 0.025) * SR)
            seg = fft_filter(white(L / SR + 0.001)[:L], lo=500 + RNG.random() * 800, hi=4000 + RNG.random() * 3000)
            out[i:i + L] += seg * np.exp(-np.arange(L) / SR * (180 + RNG.random() * 300)) * (0.3 + RNG.random())
        return out
    return fade_io(stereo(ch(), ch()))


# ------------------------------------------------------------------ ciudad y cafe
def night_city_loop():
    d = 36
    def ch():
        traffic = fft_filter(white(d), lo=60, hi=260, order=2) * (0.5 + 0.5 * smooth_noise(d, 0.05)) * 1.6
        air = fft_filter(pink(d), lo=300, hi=2500) * 0.18 * (0.4 + 0.6 * smooth_noise(d, 0.1))
        return traffic + air
    return loopify(two(ch, d), 3.0)


def room_tone_loop():
    d = 30
    t = t_of(d)
    def ch():
        return fft_filter(pink(d), lo=70, hi=1200) * 0.5 + np.sin(2 * np.pi * 50 * t) * 0.03
    return loopify(two(ch, d), 2.5)


def water_drip():
    d = 2.8
    t = t_of(d)
    out = np.zeros(len(t))
    for k, (dl, f, g) in enumerate(((0.05, 1400, 1.0), (1.0, 1650, 0.6))):
        i = int(dl * SR); L = int(0.5 * SR); tt = np.arange(L) / SR
        out[i:i + L] += np.sin(2 * np.pi * f * (1 + 1.2 * np.exp(-tt * 40)) * tt) * np.exp(-tt * 18) * g
    return fade_io(stereo(reverb(out, 1.6, 0.4, 5500)))


def cup_clink():
    d = 2.0
    t = t_of(d)
    s = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * dc) for f, a, dc in ((2860, 0.6, 22), (4120, 0.4, 28), (6150, 0.2, 35)))
    return fade_io(stereo(reverb(s, 1.2, 0.3, 6500)))


def clock_tick_loop():
    d = 8
    out = np.zeros(int(d * SR))
    for k in range(d):
        i = int(k * SR); L = int(0.02 * SR); tt = np.arange(L) / SR
        f = 1900 if k % 2 == 0 else 1500
        out[i:i + L] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 260) * 0.8
    return loopify(stereo(reverb(out, 0.7, 0.15, 5000)), 0.05)


# ------------------------------------------------------------------ cafe: gente, vajilla, calle de noche
def crowd_murmur_loop():
    d = 40
    t = t_of(d)
    def ch():
        mix = np.zeros(len(t))
        for _ in range(9):
            f0 = 95 + RNG.random() * 130
            f = f0 * (1 + 0.05 * smooth_noise(d, 2.5))
            src = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + white(d) * 0.25
            v1 = fft_filter(src, lo=350 + RNG.random() * 300, hi=900 + RNG.random() * 300)
            v2 = fft_filter(src, lo=1400 + RNG.random() * 500, hi=2600) * 0.5
            gate = np.clip((smooth_noise(d, 0.35 + RNG.random() * 0.3) - 0.15) * 3, 0, 1) * (0.4 + 0.6 * smooth_noise(d, 4.0 + RNG.random() * 2))
            mix += (v1 + v2) * gate
        return fft_filter(mix, hi=3600)
    return loopify(two(ch, d), 3.0)


def cafe_dishes():
    d = 14.0
    def ch():
        out = np.zeros(int(d * SR))
        for _ in range(9):
            i = int(RNG.random() * (len(out) - SR)); L = int(0.6 * SR); tt = np.arange(L) / SR
            f = 2400 + RNG.random() * 2600
            g = 0.25 + RNG.random() * 0.75
            out[i:i + L] += sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt * dc * (1 + m * 0.4)) for m, a, dc in ((1, 0.6, 20), (1.51, 0.35, 26), (2.4, 0.2, 34))) * g
        for _ in range(5):
            i = int(RNG.random() * (len(out) - SR)); L = int(0.09 * SR); tt = np.arange(L) / SR
            out[i:i + L] += fft_filter(white(0.1)[:L], lo=120, hi=900) * np.exp(-tt * 55) * 1.2
        return reverb(out, 1.4, 0.3, 6000)
    return fade_io(stereo(ch(), ch()))


def espresso_steam():
    d = 6.0
    t = t_of(d)
    s = fft_filter(white(d), lo=2200, hi=9500) * env_ad(len(t), 0.5, 2.6, 1.5) * 0.8 + fft_filter(white(d), lo=200, hi=900) * env_ad(len(t), 0.4, 2.0, 1.2) * 0.3
    return fade_io(stereo(reverb(s, 1.4, 0.25, 5000), reverb(s, 1.4, 0.25, 5000)))


def car_pass():
    d = 9.0
    t = t_of(d)
    c = d * 0.5
    env = np.exp(-((t - c) / 1.5) ** 2)
    road = fft_filter(white(d), lo=90, hi=1400, slope_db=-3) * env * 1.4
    eng = np.sin(2 * np.pi * np.cumsum(55 * (1 - 0.12 * np.tanh((t - c) * 1.2))) / SR) * env * 0.5
    s = fft_filter(road + eng, hi=1800)
    pan = 0.5 + 0.5 * np.tanh((t - c) * 0.9)
    out = np.stack([s * np.sqrt(1 - pan), s * np.sqrt(pan)], axis=1)
    return fade_io(out)


def far_traffic_loop():
    d = 36
    def ch():
        hum = fft_filter(white(d), lo=40, hi=300, order=2) * (0.5 + 0.5 * smooth_noise(d, 0.04)) * 1.3
        swish = fft_filter(white(d), lo=500, hi=3000) * (smooth_noise(d, 0.15) ** 3) * 0.5
        return hum + swish
    return loopify(two(ch, d), 3.0)


def dog_bark_far():
    d = 3.5
    t = t_of(d)
    out = np.zeros(len(t))
    for dl in (0.2, 0.55, 1.6):
        i = int(dl * SR); L = int(0.18 * SR); tt = np.arange(L) / SR
        src = np.sign(np.sin(2 * np.pi * np.cumsum(420 * (1 - 0.35 * tt / 0.18)) / SR)) * 0.5 + white(0.19)[:L] * 0.3
        out[i:i + L] += fft_filter(src, lo=500, hi=1800) * np.exp(-tt * 14)
    return fade_io(stereo(reverb(fft_filter(out, hi=2500), 2.2, 0.55, 2500)))


NEW = {
    "rain_loop": (rain_loop, -24), "window_rain_loop": (window_rain_loop, -26), "thunder": (thunder, -20),
    "underwater_loop": (underwater_loop, -25), "bubbles": (bubbles, -26),
    "forest_leaves_loop": (forest_leaves_loop, -27), "crickets_loop": (crickets_loop, -31), "birds_chirp": (birds_chirp, -28),
    "desert_wind_loop": (desert_wind_loop, -26), "snow_wind_loop": (snow_wind_loop, -27), "mountain_wind_loop": (mountain_wind_loop, -26),
    "magma_rumble_loop": (magma_rumble_loop, -22), "lava_bubbling_loop": (lava_bubbling_loop, -27), "ember_crackle": (ember_crackle, -26),
    "night_city_loop": (night_city_loop, -29), "room_tone_loop": (room_tone_loop, -32), "water_drip": (water_drip, -29),
    "cup_clink": (cup_clink, -31), "clock_tick_loop": (clock_tick_loop, -36),
    "crowd_murmur_loop": (crowd_murmur_loop, -30), "cafe_dishes": (cafe_dishes, -30), "espresso_steam": (espresso_steam, -31),
    "car_pass": (car_pass, -29), "far_traffic_loop": (far_traffic_loop, -32), "dog_bark_far": (dog_bark_far, -34),
}

# Receta por escena: camas [(nombre, ganancia)] y one-shots [(nombre, cada_s, jitter_s, ganancia)]. Dark ambient: casi todas
# llevan debajo el dron oscuro (deep_space_drone_loop) a bajo nivel.
RECETAS = {
    "reactor": {"camas": [["reactor_core_loop", 1.0], ["server_hall_loop", 0.8], ["coolant_flow_loop", 0.7], ["granular_shimmer_loop", 0.8]],
                "shots": [["reactor_pulse", 10, 6, 1.0], ["relay_clicks", 8, 7, 1.0], ["airlock_hiss", 25, 10, 0.9], ["sub_drop", 34, 12, 0.9], ["ion_crackle", 21, 9, 1.0]]},
    "orbital": {"camas": [["deep_space_drone_loop", 1.1], ["granular_shimmer_loop", 1.0], ["cosmic_wind_loop", 0.8]],
                "shots": [["radar_ping", 12, 6, 1.0], ["sonar_deep", 19, 8, 1.0], ["reverse_swell", 33, 12, 1.0], ["signal_static", 16, 9, 1.0]]},
    "scp_contencion": {"camas": [["cryo_chamber_loop", 1.2], ["deep_space_drone_loop", 0.8], ["server_hall_loop", 0.5]],
                       "shots": [["alarm_distant", 17, 8, 1.0], ["metal_creak", 13, 8, 1.0], ["station_heartbeat", 15, 7, 0.9], ["airlock_clunk", 28, 10, 1.0], ["sub_drop", 37, 12, 0.9]]},
    "scp_exterior": {"camas": [["cosmic_wind_loop", 0.9], ["deep_space_drone_loop", 0.7], ["server_hall_loop", 0.35]],
                     "shots": [["alarm_distant", 18, 8, 0.8], ["ion_crackle", 14, 8, 1.0], ["metal_creak", 20, 9, 0.9], ["signal_static", 12, 8, 0.9], ["thunder", 55, 20, 0.4]]},
    "array_suiza": {"camas": [["server_hall_loop", 1.0], ["mountain_wind_loop", 0.5], ["deep_space_drone_loop", 0.5]],
                    "shots": [["relay_clicks", 9, 7, 0.9], ["signal_static", 20, 10, 0.8], ["radar_ping", 30, 12, 0.7], ["ion_crackle", 25, 10, 0.8]]},
    "bosque": {"camas": [["forest_leaves_loop", 1.0], ["crickets_loop", 0.7], ["deep_space_drone_loop", 0.4], ["granular_shimmer_loop", 0.35]],
               "shots": [["birds_chirp", 14, 9, 0.8], ["water_drip", 22, 12, 0.7], ["thunder", 60, 20, 0.3]]},
    "desierto": {"camas": [["desert_wind_loop", 1.0], ["deep_space_drone_loop", 0.5], ["cosmic_wind_loop", 0.3]],
                 "shots": [["sub_drop", 40, 15, 0.8], ["ion_crackle", 30, 10, 0.5], ["metal_creak", 35, 12, 0.5]]},
    "montana": {"camas": [["mountain_wind_loop", 1.0], ["deep_space_drone_loop", 0.45]],
                "shots": [["thunder", 50, 20, 0.5], ["birds_chirp", 30, 12, 0.5], ["sub_drop", 45, 15, 0.6]]},
    "nieve": {"camas": [["snow_wind_loop", 1.0], ["cryo_chamber_loop", 0.5], ["deep_space_drone_loop", 0.4]],
              "shots": [["metal_creak", 22, 10, 0.6], ["ion_crackle", 28, 10, 0.4], ["sub_drop", 45, 15, 0.7]]},
    "submarina": {"camas": [["underwater_loop", 1.0], ["deep_space_drone_loop", 0.6], ["coolant_flow_loop", 0.35]],
                  "shots": [["sonar_deep", 15, 8, 1.0], ["bubbles", 9, 7, 0.9], ["metal_creak", 25, 10, 0.7], ["airlock_clunk", 35, 12, 0.5]]},
    "tormenta": {"camas": [["rain_loop", 1.0], ["mountain_wind_loop", 0.6], ["deep_space_drone_loop", 0.3]],
                 "shots": [["thunder", 14, 10, 1.0], ["metal_creak", 40, 15, 0.4]]},
    "volcanica": {"camas": [["magma_rumble_loop", 1.0], ["lava_bubbling_loop", 0.9], ["deep_space_drone_loop", 0.4]],
                  "shots": [["ember_crackle", 8, 6, 0.9], ["sub_drop", 30, 12, 1.0], ["thunder", 45, 15, 0.5]]},
    "latam_noche": {"camas": [["night_city_loop", 1.0], ["crickets_loop", 0.9], ["deep_space_drone_loop", 0.3]],
                    "shots": [["thunder", 70, 25, 0.3], ["signal_static", 30, 12, 0.35], ["water_drip", 35, 15, 0.4]]},
    "veo3_manana": {"camas": [["crowd_murmur_loop", 0.8], ["room_tone_loop", 0.7], ["far_traffic_loop", 0.5], ["forest_leaves_loop", 0.2]],
                    "shots": [["cafe_dishes", 9, 6, 0.9], ["cup_clink", 14, 8, 0.6], ["espresso_steam", 40, 15, 0.8], ["car_pass", 24, 14, 0.7], ["birds_chirp", 20, 10, 0.4]]},
    "veo3_tarde": {"camas": [["crowd_murmur_loop", 1.0], ["room_tone_loop", 0.6], ["far_traffic_loop", 0.6]],
                   "shots": [["cafe_dishes", 8, 6, 1.0], ["cup_clink", 12, 7, 0.7], ["espresso_steam", 35, 15, 0.8], ["car_pass", 20, 12, 0.8], ["water_drip", 30, 12, 0.4]]},
    "veo3_noche": {"camas": [["window_rain_loop", 0.9], ["crowd_murmur_loop", 0.55], ["far_traffic_loop", 0.7], ["night_city_loop", 0.5], ["crickets_loop", 0.3], ["room_tone_loop", 0.4]],
                   "shots": [["car_pass", 16, 10, 0.9], ["cafe_dishes", 13, 8, 0.7], ["cup_clink", 20, 10, 0.5], ["dog_bark_far", 50, 20, 0.6], ["thunder", 70, 25, 0.25], ["water_drip", 28, 12, 0.4]]},
}


def render_demo(escena, receta, out_dir, total=75, seed=11):
    rng = np.random.default_rng(seed)
    D = Path("assets/drakescraft/sounds/space")

    def load(n):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(D / f"{n}.ogg"), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
        return np.frombuffer(raw, dtype="<f4").reshape(-1, 2).astype(float)

    out = np.zeros((total * SR, 2))
    for n, g in receta["camas"]:
        x = load(n)
        out += np.tile(x, (int(np.ceil(total * SR / len(x))) + 1, 1))[: total * SR] * g
    for n, every, jit, g in receta["shots"]:
        x = load(n)
        t = 2 + rng.random() * every * 0.5
        while t < total - len(x) / SR - 0.5:
            i = int(t * SR)
            out[i:i + len(x)] += x * g * (0.7 + 0.5 * rng.random())
            t += every + rng.random() * jit
    out *= min(1.0, 0.89 / (np.abs(out).max() + 1e-9))
    wav = out_dir / f"{escena}.wav"
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((out * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis", "-q:a", "5", str(out_dir / f"{escena}.ogg")], check=True)
    wav.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demos", type=Path, help="renderiza una demo de 75 s por escena en este directorio")
    ap.add_argument("--solo", nargs="*")
    ap.add_argument("--sin-generar", action="store_true")
    a = ap.parse_args()
    out_sounds = Path("assets/drakescraft/sounds/space")
    if not a.sin_generar:
        G.BANK.clear(); G.BANK.update(NEW)
        sys.argv = [sys.argv[0], "--out", str(out_sounds)] + (["--solo", *a.solo] if a.solo else [])
        G.main()
    Path("scripts/scene_recipes.json").write_text(json.dumps(RECETAS, indent=1, ensure_ascii=False) + "\n")
    if a.demos:
        a.demos.mkdir(parents=True, exist_ok=True)
        for escena, r in RECETAS.items():
            render_demo(escena, r, a.demos)
        print(len(RECETAS), "demos en", a.demos)


if __name__ == "__main__":
    main()
