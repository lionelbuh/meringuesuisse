"""Reel 01 'Meet PETITES' with the meringue mascot. Different look from the Thanksgiving reel:
sage-green intro, 3x3 counting gag, real photos, sage end card."""
import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tg
from tg import *
from PIL import Image, ImageDraw

SAGE_BG = (95, 109, 82); SAGE_LIGHT = (221, 227, 210)
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'images') + '/'
P1 = Image.open(IMG + 'hero.jpg').convert('RGB')
P2 = Image.open(IMG + 'gift-set.jpg').convert('RGB')

def arm(d, x, y, ang, r):
    """little waving arm (a meringue drop)."""
    s = SS; x, y, r = x * s, y * s, r * s
    ex, ey = x + math.cos(ang) * r * 0.55, y - math.sin(ang) * r * 0.55
    d.line([(x, y), (ex, ey)], fill=MER, width=int(r * 0.16))
    d.ellipse([ex - r * 0.11, ey - r * 0.11, ex + r * 0.11, ey + r * 0.11], fill=MER)

def photo_card(img, u, dur, title, sub, kicker, fy=0.5):
    pw, ph = img.size; z = 1.0 + 0.07 * u / dur
    side = min(pw, ph) / z; x = (pw - side) / 2; y = min(max(fy * ph - side / 2, 0), ph - side)
    tw = W * SS; th = tw
    pic = img.transform((tw, th), Image.EXTENT, (x, y, x + side, y + side), Image.BICUBIC)
    im = Image.new('RGB', (W * SS, H * SS), IVORY); im.paste(pic, (0, 480 * SS))
    d = ImageDraw.Draw(im, 'RGBA')
    text(d, kicker, 230, 40, 'sans', SAGE, 650)
    text(d, title, 300, 96, 'serif', INK, 600)
    text(d, sub, 1640, 50, 'sans', INK, 500)
    return im, d

DUR = 15.0
def frame(t):
    if t < 3.4:
        # 1. sage background, mascot peeks up from the bottom and waves
        im = Image.new('RGB', (W * SS, H * SS), SAGE_BG); d = ImageDraw.Draw(im, 'RGBA')
        k = ease(clamp01(t / 0.9))
        y = 1900 - 520 * k
        wave = math.sin(t * 10) * 0.5 if t > 1.0 else 0
        hop = abs(math.sin((t - 1.0) * 6)) * 40 if t > 1.0 else 0
        draw_meringue(d, W / 2, y - hop, 260, blink=blink_at(t, [1.9]), mood='smile', look=(0.6, -0.4))
        if t > 1.2:
            bubble(d, 210, 560, 660, 240, "Psst... have you\nmet PETITES?", size=60, alpha=clamp01((t - 1.2) / 0.3))
        text(d, 'MERINGUE SUISSE', 200, 60, 'serif', (247, 243, 234), 500)
    elif t < 7.0:
        # 2. counting gag: nine little meringues pop into a 3x3 grid
        u = t - 3.4
        im = Image.new('RGB', (W * SS, H * SS), SAGE_LIGHT); d = ImageDraw.Draw(im, 'RGBA')
        text(d, 'Nine of us.', 300, 110, 'serif', INK, 600)
        text(d, 'One little box.', 440, 76, 'serif-i', SAGE, 600, alpha=clamp01((u - 2.4) / 0.4))
        # kraft box outline
        bx, by, bs = W / 2 - 360, 690, 720
        d.rounded_rectangle([bx * SS, by * SS, (bx + bs) * SS, (by + bs) * SS], radius=24 * SS, fill=(196, 160, 118), outline=(160, 125, 85), width=6 * SS)
        for i in range(9):
            r, c = divmod(i, 3); t0 = 0.25 * i
            k = clamp01((u - t0) / 0.25)
            if k <= 0: continue
            pop = 1 + 0.25 * math.sin(math.pi * k) if k < 1 else 1
            cx = bx + bs / 6 + c * bs / 3; cy = by + bs / 6 + r * bs / 3 + 70
            d.ellipse([(cx - 95) * SS, (cy - 30) * SS, (cx + 95) * SS, (cy + 30) * SS], fill=(150, 115, 78))
            draw_meringue(d, cx, cy, 78 * pop, blink=blink_at(u, [2.8 + 0.07 * i]), mood='smile' if i != 4 else 'open', cheeks=True)
            if 0 < u - t0 < 0.45:
                f = font('sans', 54, 700); s = str(i + 1)
                d.text(((cx + 60) * SS, (cy - 200) * SS), s, font=f, fill=SAGE + (int(255 * (1 - (u - t0) / 0.45)),))
        text(d, '...and yes, we\'re real. Look!', 1620, 52, 'sans', INK, 600, alpha=clamp01((u - 2.9) / 0.4))
    elif t < 9.8:
        u = t - 7.0
        im, d = photo_card(P1, u, 2.8, 'Light. Crisp. Delicate.', 'Handcrafted in small batches in Temecula.', 'THE REAL PETITES')
    elif t < 12.4:
        u = t - 9.8
        im, d = photo_card(P2, u, 2.6, 'Tied by hand.', 'Twine, a little tag and our story card.', 'READY TO GIVE', fy=0.5)
        # mascot peeking from the corner
        k = ease(clamp01((u - 0.6) / 0.5))
        draw_meringue(d, W - 150 + 200 * (1 - k), 1560, 110, blink=blink_at(u, [1.8]), mood='smile', look=(-1, 0))
    else:
        # 4. sage end card with the mascot waving
        u = t - 12.4
        im = Image.new('RGB', (W * SS, H * SS), SAGE_BG); d = ImageDraw.Draw(im, 'RGBA')
        cross(d, W / 2, 470, 66)
        text(d, 'MERINGUE SUISSE', 560, 92, 'serif', IVORY, 500)
        text(d, 'PETITES · box of 9 Swiss meringues', 690, 46, 'sans', SAGE_LIGHT, 500)
        text(d, 'Classic · Coffee · Chocolate', 760, 54, 'serif-i', IVORY, 600)
        text(d, 'meringuesuisse.com', 880, 56, 'sans', IVORY, 650, alpha=clamp01((u - 0.3) / 0.4))
        draw_meringue(d, W / 2, 1420 - abs(math.sin(u * 5)) * 35, 190, blink=blink_at(u, [1.6]), mood='smile')
        text(d, 'See you soon!', 1560, 60, 'serif-i', IVORY, 600, alpha=clamp01((u - 0.8) / 0.4))
    out = im.resize((W, H), Image.LANCZOS)
    if t < 0.25: out = Image.blend(Image.new('RGB', (W, H), SAGE_BG), out, t / 0.25)
    return out

CUTS = [3.4, 7.0, 9.8, 12.4]
def render(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    X = 0.35
    for i in range(int(DUR * FPS)):
        t = i / FPS; f = frame(t)
        for c in CUTS:
            if c - X < t < c:      # cross-fade into the next scene
                f = Image.blend(f, frame(c + 0.001 + (t - (c - X))), (t - (c - X)) / X)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        ts = [0.6, 2.0, 4.6, 6.6, 8.4, 11.5, 13.8]
        ims = [frame(t).resize((300, 533)) for t in ts]
        c = Image.new('RGB', (310 * len(ims), 533), 'white')
        for i, im in enumerate(ims): c.paste(im, (i * 310, 0))
        c.save(sys.argv[2])
    else:
        render(sys.argv[1])
