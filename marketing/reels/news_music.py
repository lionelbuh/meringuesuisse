"""Original 'breaking news' style music bed, synthesized from scratch (no samples, royalty-free).
120 bpm, D minor, 14 s: ticking hats, kick, pulsing bass, brass-like stabs, hits on the scene cuts
(2, 6, 10 s) and a final D major chord. Writes a 44.1 kHz stereo WAV.  Run: python3 news_music.py out.wav"""
import sys, wave
import numpy as np

SR = 44100; BPM = 120; B = 60 / BPM; DUR = 14.0
N = int(SR * DUR); L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def lowpass(x, a):            # cheap smoothing: repeated moving average
    k = max(1, int(a))
    for _ in range(3): x = np.convolve(x, np.ones(k) / k, mode='same')
    return x

def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if j <= i: return
    s = sig[:j - i] * g
    L[i:j] += s * (1 - pan) * 0.5 + s * 0.5 * (pan <= 0)
    R[i:j] += s * (1 + pan) * 0.5 + s * 0.5 * (pan >= 0)

def env(n, a=0.005, d=0.2, s=0.0, rel=0.1, dur=None):
    t = np.arange(n) / SR; e = np.minimum(1, t / a)
    dur = dur or n / SR
    e *= np.where(t < dur, s + (1 - s) * np.exp(-t / d), (s + (1 - s) * np.exp(-dur / d)) * np.exp(-(t - dur) / rel))
    return e

def saw(f, n, detune=(0, 7, -7)):
    t = np.arange(n) / SR; out = np.zeros(n)
    for c in detune:
        ff = f * 2 ** (c / 1200); out += 2 * ((t * ff) % 1) - 1
    return out / len(detune)

def kick(g=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t / 0.03); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.12) * g

def hat(open_=False):
    n = int((0.12 if open_ else 0.04) * SR); x = rng.standard_normal(n)
    x = x - lowpass(x, 4)                    # crude high-pass
    x = lowpass(x, 2)
    return x * np.exp(-np.arange(n) / SR / (0.05 if open_ else 0.012)) * 0.22

def stab(notes, length=0.25, g=0.5):
    n = int((length + 0.3) * SR); x = sum(saw(hz(m), n) for m in notes) / len(notes)
    x = lowpass(x, 6) * env(n, a=0.01, d=0.18, s=0.35, rel=0.12, dur=length)
    return x * g

def hit(g=1.0):               # orchestral-ish hit: low boom + noise burst + chord
    n = int(1.2 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (45 + 30 * np.exp(-t / 0.08)) * t) * np.exp(-t / 0.4)
    nz = lowpass(rng.standard_normal(n), 20) * np.exp(-t / 0.15) * 0.6
    return (boom + nz) * g

def bass(m, length):
    n = int((length + 0.05) * SR); t = np.arange(n) / SR
    x = 0.6 * np.sin(2 * np.pi * hz(m) * t) + 0.4 * lowpass(saw(hz(m), n, (0,)), 10)
    return x * env(n, a=0.004, d=0.2, s=0.6, rel=0.04, dur=length) * 0.55

# --- intro (0-2 s): rising noise swell + ticking clock
n = int(2 * SR); t = np.arange(n) / SR
sw = lowpass(rng.standard_normal(n), 12) * (t / 2) ** 2 * 0.35
add(sw, 0)
for k in range(8): add(hat(), k * B / 2, pan=0.3, g=0.9)

# --- main groove 2-14 s (6 bars of 2 s)
CH = [[50, 57, 62, 65], [46, 53, 58, 62], [48, 55, 60, 64], [45, 52, 57, 61]]   # Dm Bb C A
BASS = [38, 34, 36, 33]
for bar in range(6):
    t0 = 2 + bar * 4 * B; c = bar % 4 if bar < 5 else 0
    for beat in range(4):
        add(kick(0.9 if beat in (0, 2) else 0.45), t0 + beat * B)
        for s16 in range(4):
            add(hat(open_=(s16 == 2 and beat == 3)), t0 + beat * B + s16 * B / 4, pan=0.4, g=0.8 if s16 % 2 == 0 else 0.5)
    if bar < 5:
        for e in range(8):     # pulsing eighth-note bass
            add(bass(BASS[c] + (12 if e in (3, 7) else 0), B / 2 * 0.85), t0 + e * B / 2)
        for pos, ln in [(0, 0.3), (1.5, 0.15), (2.0, 0.3), (3.5, 0.15)]:   # stab rhythm
            add(stab(CH[c], ln, 0.45), t0 + pos * B, pan=-0.2)
        # little 'news' bell motif on the last beat
        for i, m in enumerate([74, 77, 81]):
            n2 = int(0.5 * SR); tt = np.arange(n2) / SR
            add(np.sin(2 * np.pi * hz(m) * tt) * np.exp(-tt / 0.25) * 0.18, t0 + 3 * B + i * B / 3, pan=0.5)

for tc in (2.0, 6.0, 10.0): add(hit(0.9), tc)

# --- ending: big D major chord from 12 s, fading out
n = int(2.0 * SR); tt = np.arange(n) / SR
chord = sum(saw(hz(m), n) for m in [50, 57, 62, 66, 69]) / 5
add(lowpass(chord, 6) * np.minimum(1, tt / 0.02) * np.exp(-tt / 0.9) * 0.6, 12.0)
add(bass(38, 1.6) * 1.2, 12.0); add(hit(1.0), 12.0)

mix = np.stack([L, R], 1)
mix /= np.max(np.abs(mix)) * 1.12
fade = np.ones(N); fn = int(0.6 * SR); fade[-fn:] = np.linspace(1, 0, fn); mix *= fade[:, None]
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
