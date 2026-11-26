"""Reel 03 'Happy Thanksgiving + three flavors'. Cranberry look, three mascots (classic white,
coffee beige, chocolate with cocoa dots) wearing tiny knit scarves, one spotlight per flavor
with its real photo and price, a 'pick me!' line-up gag, cranberry end card.
Run: python3 reel03.py out.mp4 | python3 reel03.py preview p.png"""
import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tg
from tg import *
from PIL import Image, ImageDraw

CRAN = (122, 30, 48); CRAN_L = (244, 222, 222); GOLD = (232, 186, 96)
IMG = os.path.join(REPO, 'images') + '/'
FLAV = {
    'classic':   dict(body=(252, 249, 241), sh=(226, 217, 198), scarf=(196, 64, 52), bg=(247, 241, 228), photo='closeup.jpg', name='Classic', price='$14.90', line='Pure, light and crisp.'),
    'coffee':    dict(body=(226, 196, 160), sh=(196, 162, 124), scarf=(84, 110, 76), bg=(236, 222, 202), photo='coffee-open.jpg', name='Coffee', price='$15.90', line='A little latte moment.'),
    'chocolate': dict(body=(146, 98, 72), sh=(116, 74, 54), scarf=(222, 150, 50), bg=(92, 60, 46), photo='choc-open.jpg', name='Chocolate', price='$15.90', line='Cocoa, delicate and crunchy.'),
}
PH = {k: Image.open(IMG + v['photo']).convert('RGB') for k, v in FLAV.items()}
ORDER = ['classic', 'coffee', 'chocolate']

def mascot(d, flavor, cx, cy, r, t=0.0, blink=0.0, mood='smile', look=(0, 0)):
    f = FLAV[flavor]
    tg.MER, tg.MER_SH = f['body'], f['sh']
    draw_meringue(d, cx, cy, r, blink=blink, mood=mood, look=look)
    tg.MER, tg.MER_SH = (252, 249, 241), (226, 217, 198)
    S = SS
    if flavor == 'chocolate':   # cocoa dots
        for dx, dy in [(-0.62, -0.30), (0.55, -0.42), (-0.25, -1.05), (0.15, -1.25), (0.70, -0.18), (-0.78, -0.12), (0.38, -0.95)]:
            x, y = cx + dx * r, cy + dy * r
            d.ellipse([(x - r * 0.035) * S, (y - r * 0.035) * S, (x + r * 0.035) * S, (y + r * 0.035) * S], fill=(70, 42, 30))
    # tiny knit scarf with a fluttering tail
    col = f['scarf']; dk = tuple(int(c * 0.78) for c in col)
    y0, y1 = cy - r * 0.17, cy - r * 0.03
    d.rounded_rectangle([(cx - r * 0.86) * S, y0 * S, (cx + r * 0.86) * S, y1 * S], radius=r * 0.08 * S, fill=col)
    for i in range(7):
        x = cx - r * 0.72 + i * r * 0.24
        d.line([(x * S, (y0 + r * 0.02) * S), (x * S, (y1 - r * 0.02) * S)], fill=dk, width=max(2, int(r * 0.025 * S)))
    sw = math.sin(t * 6) * r * 0.06
    tx = cx + r * 0.45
    d.polygon([(tx * S, y1 * S), ((tx + r * 0.20) * S, y1 * S), ((tx + r * 0.26 + sw) * S, (y1 + r * 0.34) * S), ((tx + r * 0.04 + sw) * S, (y1 + r * 0.34) * S)], fill=col)
    for k in range(4):
        x = tx + r * 0.05 + k * r * 0.06 + sw
        d.line([(x * S, (y1 + r * 0.33) * S), (x * S, (y1 + r * 0.42) * S)], fill=dk, width=max(2, int(r * 0.03 * S)))

def leaves_bg(d, t):   # gentle falling leaves in gold tones
    leaves(d, t, alpha=0.55)

def photo_top(img, u, dur, h=820):
    pw, ph = img.size; z = 1.0 + 0.07 * u / dur
    cw = min(pw, ph * W / h) / z; ch = cw * h / W
    x = (pw - cw) / 2; y = (ph - ch) / 2
    return img.transform((W * SS, h * SS), Image.EXTENT, (x, y, x + cw, y + ch), Image.BICUBIC)

DUR = 16.0
SPOT0, SPOTD = 3.6, 2.4
CUTS = [3.6, 6.0, 8.4, 10.8, 13.6]
def frame(t):
    if t < 3.6:
        # 1. cranberry bg, "Happy Thanksgiving!", three mascots pop up one by one
        im = Image.new('RGB', (W * SS, H * SS), CRAN); d = ImageDraw.Draw(im, 'RGBA')
        leaves_bg(d, t)
        text(d, 'Happy', 330, 110, 'serif-i', GOLD, 600, alpha=clamp01(t / 0.4))
        text(d, 'Thanksgiving!', 450, 130, 'serif', IVORY, 600, alpha=clamp01((t - 0.2) / 0.4))
        for i, fl in enumerate(ORDER):
            k = clamp01((t - 0.8 - 0.35 * i) / 0.35)
            if k <= 0: continue
            pop = 1 + 0.2 * math.sin(math.pi * k) if k < 1 else 1
            x = 220 + i * 320; y = 1500 - 40 * math.sin(math.pi * k) * (k < 1)
            mascot(d, fl, x, y, 150 * pop, t, blink=blink_at(t, [2.6 + 0.1 * i]), mood='open' if 2.1 < t < 2.7 else 'smile', look=(0, -0.5))
        text(d, 'from the three of us', 1700, 56, 'sans', CRAN_L, 600, alpha=clamp01((t - 2.2) / 0.4))
    elif t < 10.8:
        # 2. one spotlight per flavor: real photo on top, mascot + name + price below
        i = min(int((t - SPOT0) / SPOTD), 2); u = t - SPOT0 - i * SPOTD; fl = ORDER[i]; f = FLAV[fl]
        dark = fl == 'chocolate'; fg = IVORY if dark else INK; acc = GOLD if dark else CRAN
        im = Image.new('RGB', (W * SS, H * SS), f['bg']); d = ImageDraw.Draw(im, 'RGBA')
        im.paste(photo_top(PH[fl], u, SPOTD), (0, 0))
        d = ImageDraw.Draw(im, 'RGBA')
        d.rectangle([0, 800 * SS, W * SS, 830 * SS], fill=f['scarf'])
        text(d, f'{i + 1} / 3', 900, 40, 'sans', acc, 700)
        text(d, f['name'], 950, 120, 'serif', fg, 600)
        text(d, f['line'], 1100, 50, 'serif-i', fg, 500, alpha=clamp01((u - 0.3) / 0.3))
        k = ease(clamp01(u / 0.45))
        x = W / 2 + 600 * (1 - k) * (1 if i % 2 else -1)
        hop = abs(math.sin(u * 7)) * 30 if u > 0.45 else 0
        mascot(d, fl, x, 1660 - hop, 170, u, blink=blink_at(u, [1.5]), mood='smile', look=(0, -0.4))
        # price tag swinging in
        kp = clamp01((u - 0.6) / 0.3)
        if kp > 0:
            S = SS; px, py = 830, 1350
            d.rounded_rectangle([(px - 120) * S, (py - 50) * S, (px + 120) * S, (py + 50) * S], radius=22 * S, fill=acc + (int(255 * kp),))
            fnt = font('sans', 50, 700); tw = d.textlength(f['price'], font=fnt)
            d.text((px * S - tw / 2, (py - 32) * S), f['price'], font=fnt, fill=(CRAN if dark else IVORY) + (int(255 * kp),))
    elif t < 13.6:
        # 3. 'pick me!' gag: they take turns jumping, then all look at the viewer
        u = t - 10.8
        im = Image.new('RGB', (W * SS, H * SS), CRAN_L); d = ImageDraw.Draw(im, 'RGBA')
        text(d, 'Which one is yours?', 300, 100, 'serif', CRAN, 600)
        text(d, 'Tell us in the comments!', 440, 56, 'sans', INK, 600, alpha=clamp01((u - 1.6) / 0.4))
        for i, fl in enumerate(ORDER):
            ph = u - 0.35 * i
            jump = abs(math.sin(ph * 4.5)) * 160 if 0 < ph < 1.4 else 0
            x = 220 + i * 320
            mascot(d, fl, x, 1350 - jump, 140, u, blink=blink_at(u, [2.3 + 0.08 * i]), mood='open' if jump > 60 else 'smile', look=(0, -1) if u > 1.6 else (0, 0))
            if jump > 60:
                bubble(d, x - 130, 720, 260, 120, 'Me!', size=60)
    else:
        # 4. cranberry end card with the trio
        u = t - 13.6
        im = Image.new('RGB', (W * SS, H * SS), CRAN); d = ImageDraw.Draw(im, 'RGBA')
        cross(d, W / 2, 420, 66)
        text(d, 'MERINGUE SUISSE', 520, 92, 'serif', IVORY, 500)
        text(d, 'Classic $14.90 · Coffee & Chocolate $15.90', 650, 44, 'sans', CRAN_L, 600)
        text(d, 'meringuesuisse.com', 740, 60, 'sans', IVORY, 650, alpha=clamp01((u - 0.3) / 0.4))
        for i, fl in enumerate(ORDER):
            bob = abs(math.sin(u * 5 + i * 1.1)) * 25
            mascot(d, fl, 260 + i * 280, 1420 - bob, 120, u, blink=blink_at(u, [1.4 + 0.1 * i]), mood='smile')
        text(d, 'Happy Thanksgiving!', 1560, 64, 'serif-i', GOLD, 600, alpha=clamp01((u - 0.7) / 0.4))
    out = im.resize((W, H), Image.LANCZOS)
    if t < 0.25: out = Image.blend(Image.new('RGB', (W, H), CRAN), out, t / 0.25)
    return out

def render(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    X = 0.3
    for i in range(int(DUR * FPS)):
        t = i / FPS; f = frame(t)
        for c in CUTS:
            if c - X < t < c:
                f = Image.blend(f, frame(c + 0.001 + (t - (c - X))), (t - (c - X)) / X)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        ts = [3.0, 5.0, 7.4, 9.8, 11.5, 13.2, 15.0]
        ims = [frame(t).resize((300, 533)) for t in ts]
        c = Image.new('RGB', (310 * len(ims), 533), 'white')
        for i, im in enumerate(ims): c.paste(im, (i * 310, 0))
        c.save(sys.argv[2])
    else:
        render(sys.argv[1])
