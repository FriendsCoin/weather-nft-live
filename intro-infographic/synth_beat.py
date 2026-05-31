#!/usr/bin/env python3
"""Deterministic 120 BPM electronic beat for the WeatherNFT VJ intro.
Kick on every beat, hats on 8ths, clap backbeat, driving saw bass, acid blips,
plus crash/impact hits aligned to the visual scene cuts and a riser into the CTA.
"""
import numpy as np, subprocess, sys

SR = 44100
DUR = 31.0
BEAT = 0.5           # 120 BPM
N = int(DUR * SR)
t = np.arange(N) / SR
mix = np.zeros(N)
rng = np.random.default_rng(7)   # seeded -> deterministic

def add(buf, start, sig):
    i = int(start * SR)
    j = min(N, i + len(sig))
    if i < N:
        buf[i:j] += sig[: j - i]

def env(length, tau, attack=0.002):
    n = int(length * SR)
    e = np.exp(-np.arange(n) / (tau * SR))
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e

def kick(start):
    n = int(0.30 * SR)
    tt = np.arange(n) / SR
    f = 45 + (120 - 45) * np.exp(-tt / 0.03)      # pitch drop
    ph = 2 * np.pi * np.cumsum(f) / SR
    add(mix, start, 1.05 * np.sin(ph) * env(0.30, 0.11))

def hat(start, amp):
    n = int(0.05 * SR)
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0.0)            # crude high-pass
    add(mix, start, amp * noise * env(0.05, 0.012))

def clap(start):
    n = int(0.18 * SR)
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0.0)
    tone = 0.3 * np.sin(2 * np.pi * 190 * (np.arange(n) / SR))
    add(mix, start, 0.55 * (noise + tone) * env(0.18, 0.07))

def saw(freq, length, amp):
    n = int(length * SR)
    tt = np.arange(n) / SR
    s = np.zeros(n)
    for h in range(1, 9):                          # band-limited-ish saw
        s += (1.0 / h) * np.sin(2 * np.pi * freq * h * tt)
    return amp * s * env(length, length * 0.6)

def blip(freq, start, amp):
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * freq * tt))
    add(mix, start, amp * sq * env(0.12, 0.04))

def crash(start):
    n = int(0.7 * SR)
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0.0)
    add(mix, start, 0.5 * noise * env(0.7, 0.42))
    boom = 0.7 * np.sin(2 * np.pi * 55 * (np.arange(int(0.4 * SR)) / SR))
    add(mix, start, boom * env(0.4, 0.3))

def riser(start, length):
    n = int(length * SR)
    tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0.0)
    swell = (tt / length) ** 2
    tone = 0.3 * np.sin(2 * np.pi * (200 + 900 * (tt / length)) * tt)
    add(mix, start, (0.4 * noise + tone) * swell)

CUTS = [4.8, 9.1, 14.4, 19.2, 24.2]
# bass pattern (Hz) over an 8-beat / 4s phrase — minor, root-heavy
BASS = [55.0, 55.0, 73.42, 55.0, 82.41, 55.0, 65.41, 73.42]
ARP = [220.0, 329.63, 277.18, 440.0]

nbeats = int(DUR / BEAT)
for k in range(nbeats):
    bt = k * BEAT
    kick(bt)
    hat(bt, 0.16)
    hat(bt + 0.25, 0.22 if k % 2 == 0 else 0.14)   # accent off-beat hat
    if k % 2 == 1:
        clap(bt)                                   # backbeat (beats 2 & 4)
    add(mix, bt, saw(BASS[k % len(BASS)], 0.46, 0.32))
    if k % 4 == 2:                                  # sparse acid blips
        blip(ARP[k % len(ARP)], bt + 0.25, 0.10)

for c in CUTS:
    crash(c)
riser(23.2, 1.0)                                   # build into the CTA cut
crash(0.0)                                          # intro hit
crash(30.4)                                         # outro hit

# soft saturation + normalize
mix = np.tanh(mix * 0.8)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.92
pcm = (mix * 32767).astype(np.int16)

raw = "beat.raw"
pcm.tofile(raw)
subprocess.run(
    ["ffmpeg", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", raw,
     "-c:a", "aac", "-b:a", "192k", "beat.m4a"],
    check=True, stderr=subprocess.DEVNULL,
)
print("wrote beat.m4a", round(DUR, 2), "s")
