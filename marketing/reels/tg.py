"""Cartoon Thanksgiving reel: a cute little meringue character. 1080x1920, 30 fps."""
import math, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 2          # SS = supersampling factor
import os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
FD = os.path.join(HERE, 'fonts') + '/'
IVORY = (247, 243, 234); INK = (42, 42, 39); SAGE = (95, 109, 82); RED = (213, 43, 30)
MER = (252, 249, 241); MER_SH = (226, 217, 198)
ORANGE = (214, 120, 45); CRUST = (196, 140, 78); CRUST_D = (160, 105, 55)
LEAF = [(201, 84, 36), (222, 140, 40), (176, 58, 34), (196, 155, 60)]

def font(kind, size, weight=600):
    p = {'serif': 'CormorantGaramond[wght].ttf', 'serif-i': 'CormorantGaramond-Italic[wght].ttf', 'sans': 'Figtree[wght].ttf'}[kind]
    f = ImageFont.truetype(FD + p, size * SS)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f

def ease(t): t = min(max(t, 0), 1); return 0.5 - 0.5 * math.cos(math.pi * t)
def clamp01(t): return min(max(t, 0), 1)

def meringue_pts(cx, cy, r, sx=1.0, sy=1.0, tilt=0.0):
    """kiss-shaped meringue outline. cx,cy = middle of the base, r = half width."""
    pts = []
    n = 120
    for i in range(n + 1):
        u = i / n                    # 0..1 left base -> top -> right base
        a = math.pi * u
        x = -math.cos(a)             # -1..1
        # body: dome + pointy peak
        h = 0.95 * (1 - x * x) ** 0.55 + 0.75 * math.exp(-(x / 0.22) ** 2)
        lean = 0.10 * math.exp(-(x / 0.25) ** 2)        # peak leans a bit
        pts.append((cx + (x + lean) * r * sx, cy - h * r * sy))
    # little curl at the tip
    return pts

def draw_meringue(d, cx, cy, r, sx=1, sy=1, blink=0.0, mood='smile', look=(0, 0), hat=False, cheeks=True):
    s = SS
    cx, cy, r = cx * s, cy * s, r * s
    # shadow
    d.ellipse([cx - r * 1.05 * sx, cy - r * 0.12, cx + r * 1.05 * sx, cy + r * 0.14], fill=(0, 0, 0, 40))
    pts = meringue_pts(cx, cy, r, sx, sy)
    d.polygon(pts, fill=MER_SH)
    pts2 = [(x - r * 0.06 * sx, y - r * 0.03) for x, y in meringue_pts(cx, cy, r * 0.97, sx, sy)]
    d.polygon(pts2, fill=MER)
    # ridges (piping swirl)
    for k in (0.38, 0.62):
        y = cy - r * sy * k
        d.arc([cx - r * sx * (1 - k * 0.8), y - r * 0.12, cx + r * sx * (1 - k * 0.8), y + r * 0.12], 200, 340, fill=MER_SH, width=int(3 * s))
    # curl on top
    tx, ty = cx + 0.10 * r * sx, cy - 1.70 * r * sy
    d.arc([tx - r * 0.10, ty - r * 0.08, tx + r * 0.16, ty + r * 0.16], 180, 330, fill=MER_SH, width=int(5 * s))
    # face
    ey = cy - r * sy * 0.55; ex = r * sx * 0.30; er = r * 0.105
    lx, ly = look[0] * er * 0.35, look[1] * er * 0.35
    for side in (-1, 1):
        x = cx + side * ex
        if blink > 0.5:
            d.arc([x - er, ey - er * 0.6, x + er, ey + er * 0.6], 20, 160, fill=INK, width=int(5 * s))
        else:
            hh = er * (1 - blink * 1.6)
            d.ellipse([x - er, ey - hh, x + er, ey + hh], fill=INK)
            d.ellipse([x - er * 0.35 + lx, ey - er * 0.55 + ly, x + er * 0.15 + lx, ey - er * 0.05 + ly], fill='white')
        if cheeks:
            d.ellipse([x + side * er * 0.6 - er * 0.75, ey + er * 1.3, x + side * er * 0.6 + er * 0.75, ey + er * 2.0], fill=(240, 170, 160))
    my = ey + er * 1.9
    if mood == 'smile':
        d.arc([cx - er * 1.3, my - er * 1.1, cx + er * 1.3, my + er * 0.9], 20, 160, fill=INK, width=int(5 * s))
    elif mood == 'open':
        d.chord([cx - er * 1.1, my - er * 0.6, cx + er * 1.1, my + er * 1.3], 0, 180, fill=(120, 40, 40))
    elif mood == 'o':
        d.ellipse([cx - er * 0.45, my - er * 0.1, cx + er * 0.45, my + er * 0.9], fill=(120, 40, 40))
    if hat:   # little pilgrim hat
        hx, hy = cx + r * 0.05 * sx, cy - r * sy * 1.32
        hw, hh = r * 0.58, r * 0.62
        d.polygon([(hx - hw * 0.62, hy), (hx + hw * 0.62, hy), (hx + hw * 0.5, hy - hh), (hx - hw * 0.5, hy - hh)], fill=(45, 40, 38))
        d.rectangle([hx - hw, hy - r * 0.05, hx + hw, hy + r * 0.07], fill=(45, 40, 38))
        d.rectangle([hx - hw * 0.6, hy - hh * 0.32, hx + hw * 0.6, hy - hh * 0.14], fill=(150, 120, 70))
        d.rectangle([hx - hw * 0.14, hy - hh * 0.36, hx + hw * 0.14, hy - hh * 0.10], outline=(230, 200, 90), width=int(5 * s))

def draw_pie(d, cx, cy, r, slice_gone=False):
    s = SS; cx, cy, r = cx * s, cy * s, r * s
    d.ellipse([cx - r * 1.08, cy - r * 0.42 + r * 0.30, cx + r * 1.08, cy + r * 0.42 + r * 0.30], fill=(0, 0, 0, 35))
    d.rectangle([cx - r, cy, cx + r, cy + r * 0.28], fill=CRUST_D)
    d.ellipse([cx - r, cy - r * 0.40 + r * 0.28, cx + r, cy + r * 0.40 + r * 0.28], fill=CRUST_D)
    d.ellipse([cx - r, cy - r * 0.40, cx + r, cy + r * 0.40], fill=CRUST)
    d.ellipse([cx - r * 0.86, cy - r * 0.32, cx + r * 0.86, cy + r * 0.32], fill=ORANGE)
    # crust scallops
    for i in range(22):
        a = 2 * math.pi * i / 22
        x, y = cx + math.cos(a) * r * 0.93, cy + math.sin(a) * r * 0.37
        d.ellipse([x - r * 0.07, y - r * 0.04, x + r * 0.07, y + r * 0.04], fill=CRUST_D)

def leaf(d, x, y, size, ang, col):
    s = SS; x, y, size = x * s, y * s, size * s
    pts = []
    for i in range(5):
        a = ang + i * 2 * math.pi / 5
        pts.append((x + math.cos(a) * size, y + math.sin(a) * size))
        b = a + math.pi / 5
        pts.append((x + math.cos(b) * size * 0.45, y + math.sin(b) * size * 0.45))
    d.polygon(pts, fill=col)
    d.line([(x, y), (x + math.cos(ang + math.pi) * size * 1.1, y + math.sin(ang + math.pi) * size * 1.1)], fill=(110, 60, 30), width=int(3 * s))

random.seed(4)
LEAVES = [(random.uniform(0, W), random.uniform(-H, 0), random.uniform(22, 40), random.uniform(0, 6.28), random.choice(LEAF),
           random.uniform(140, 260), random.uniform(0.5, 1.5)) for _ in range(11)]

def leaves(d, t, alpha=1.0):
    for x0, y0, sz, a0, col, speed, sw in LEAVES:
        y = (y0 + t * speed) % (H + 200) - 100
        x = x0 + math.sin(t * sw + a0) * 60
        leaf(d, x, y, sz, a0 + t * sw, col + (int(255 * alpha),))

def text(d, s, y, size=84, kind='serif', col=INK, weight=600, alpha=1.0, maxw=960):
    f = font(kind, size, weight); lines = s.split('\n'); lh = size * 1.12 * SS
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f)
        d.text(((W * SS - tw) / 2, y * SS + i * lh), l, font=f, fill=col + (int(255 * alpha),))

def bubble(d, x, y, w, h, s, size=58, alpha=1.0):
    S = SS; a = int(255 * alpha)
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=40 * S, fill=(255, 255, 255, a), outline=SAGE + (a,), width=4 * S)
    d.polygon([((x + w * 0.30) * S, (y + h) * S - 2), ((x + w * 0.42) * S, (y + h) * S - 2), ((x + w * 0.30) * S, (y + h + 50) * S)], fill=(255, 255, 255, a))
    d.line([((x + w * 0.30) * S, (y + h) * S), ((x + w * 0.30) * S, (y + h + 50) * S), ((x + w * 0.42) * S, (y + h) * S)], fill=SAGE + (a,), width=4 * S)
    f = font('sans', size, 600); lines = s.split('\n'); lh = size * 1.25 * S
    y0 = y * S + (h * S - len(lines) * lh) / 2 + 6
    for i, l in enumerate(lines):
        tw = d.textlength(l, font=f); d.text(((x + w / 2) * S - tw / 2, y0 + i * lh), l, font=f, fill=INK + (a,))

def cross(d, cx, cy, s):
    S = SS; cx, cy, s = cx * S, cy * S, s * S
    d.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2], fill=RED); a, b = s * 0.19, s * 0.6
    d.rectangle([cx - a / 2, cy - b / 2, cx + a / 2, cy + b / 2], fill='white'); d.rectangle([cx - b / 2, cy - a / 2, cx + b / 2, cy + a / 2], fill='white')

def blink_at(t, times): return 1.0 if any(abs(t - b) < 0.06 for b in times) else 0.0

# ---------------- timeline ----------------
DUR = 19.5
REAL = Image.open(os.path.join(REPO, 'images/classic.jpg')).convert('RGB')

def real_scene(u):
    pw, ph = REAL.size; z = 1.0 + 0.06 * u / 3.0
    cw, ch = pw / z, ph / z; x = (pw - cw) / 2; y = (ph - ch) / 2
    tw, th = W * SS, int(W * SS * ph / pw)
    pic = REAL.transform((tw, th), Image.EXTENT, (x, y, x + cw, y + ch), Image.BICUBIC)
    im = Image.new('RGB', (W * SS, H * SS), IVORY); im.paste(pic, (0, int(620 * SS)))
    d = ImageDraw.Draw(im, 'RGBA')
    text(d, 'Meet the real one.', 330, 100, 'serif', INK, 600)
    text(d, 'Light, crisp and handmade in Temecula.', 470, 46, 'sans', SAGE, 600)
    text(d, 'Classic · Coffee · Chocolate', 1430, 50, 'serif-i', INK, 600)
    return im.resize((W, H), Image.LANCZOS)

PHOTO = Image.open(os.path.join(REPO, 'images/picnic.jpg')).convert('RGB')

def photo_scene(u):
    z = 1.0 + 0.06 * u / 3.4
    pw, ph = PHOTO.size; asp = W / H
    ch = ph / z; cw = ch * asp
    if cw > pw: cw = pw / z; ch = cw / asp
    cx, cy = pw * 0.5, ph * 0.47
    x = min(max(cx - cw / 2, 0), pw - cw); y = min(max(cy - ch / 2, 0), ph - ch)
    im = PHOTO.transform((W * SS, H * SS), Image.EXTENT, (x, y, x + cw, y + ch), Image.BICUBIC)
    d = ImageDraw.Draw(im, 'RGBA')
    d.rectangle([0, 1520 * SS, W * SS, 1800 * SS], fill=IVORY + (225,))
    text(d, 'Order now for Thanksgiving', 1560, 64, 'serif', INK, 600)
    text(d, 'meringuesuisse.com', 1670, 54, 'sans', SAGE, 650)
    return im.resize((W, H), Image.LANCZOS)

def frame(t):
    im = Image.new('RGB', (W * SS, H * SS), IVORY); d = ImageDraw.Draw(im, 'RGBA')
    # warm autumn table band at the bottom
    d.rectangle([0, 1380 * SS, W * SS, H * SS], fill=(233, 220, 196, 255))
    d.line([(0, 1380 * SS), (W * SS, 1380 * SS)], fill=(214, 196, 166, 255), width=4 * SS)
    leaves(d, t, 0.55)
    if t < 4.2:
        # 1. meringue bounces in
        k = clamp01(t / 1.0)
        x = -200 + (W / 2 + 200) * ease(k)
        hop = abs(math.sin(t * 7)) * 120 * (1 - k) if k < 1 else 0
        land = clamp01((t - 1.0) / 0.25); sq = 1 - 0.15 * math.sin(math.pi * land) if 1.0 < t < 1.25 else 1
        draw_meringue(d, x, 1360 - hop, 210, sx=2 - sq, sy=sq, blink=blink_at(t, [2.1, 3.6]), mood='smile', hat=t > 2.6)
        if t > 1.3:
            a = clamp01((t - 1.3) / 0.3)
            if t < 2.6: bubble(d, 230, 520, 620, 230, "Hi! I'm a little\nSwiss meringue.", alpha=a)
            else: bubble(d, 230, 520, 620, 230, "...and I'm ready\nfor Thanksgiving!", alpha=clamp01((t - 2.6) / 0.3))
        text(d, 'MERINGUE SUISSE', 180, 64, 'serif', INK, 500)
    elif t < 9.4:
        # 2. pie appears, meringue hops on top
        u = t - 4.2
        pa = clamp01(u / 0.5)
        draw_pie(d, W / 2, 1290, 330 * (0.6 + 0.4 * ease(pa)))
        text(d, 'Pumpkin pie?', 330, 104, 'serif', INK, 600, alpha=clamp01(u / 0.4))
        if u < 1.4:
            draw_meringue(d, W / 2 + 330, 1500, 150, blink=0, mood='o', look=(-1, -0.5), hat=True)
        else:
            k = clamp01((u - 1.4) / 0.8)
            x = W / 2 + 330 - 330 * ease(k); y = 1500 - 240 * ease(k) - math.sin(math.pi * k) * 260
            sq = 1.0
            if 2.2 < u < 2.5: sq = 1 - 0.18 * math.sin(math.pi * (u - 2.2) / 0.3)
            draw_meringue(d, x, y, 150, sx=2 - sq, sy=sq, blink=blink_at(u, [3.4]), mood='open' if 2.2 < u < 3.2 else 'smile', hat=True)
            if u > 2.6:
                text(d, '...with a meringue\non top! ✦'.replace(' ✦', ''), 470, 84, 'serif-i', SAGE, 600, alpha=clamp01((u - 2.6) / 0.4))
        if u > 3.7:
            text(d, 'Light, crisp, and a little bit Swiss.', 1640, 46, 'sans', INK, 500, alpha=clamp01((u - 3.7) / 0.4))
    elif t < 11.6:
        # 3. message
        u = t - 9.4
        a = clamp01(u / 0.4)
        text(d, 'This Thanksgiving,', 420, 92, 'serif', INK, 600, alpha=a)
        text(d, 'add a little crunch\nto your dessert table.', 560, 72, 'serif-i', SAGE, 600, alpha=clamp01((u - 0.4) / 0.4))
        bob = math.sin(u * 5) * 18
        draw_meringue(d, W / 2 - 230, 1330 + bob, 120, blink=blink_at(u, [1.2]), mood='smile', hat=True)
        draw_meringue(d, W / 2, 1330 - bob, 135, blink=blink_at(u, [1.6]), mood='smile')
        draw_meringue(d, W / 2 + 230, 1330 + bob, 120, blink=blink_at(u, [0.9]), mood='smile')
        text(d, 'Pies · cheesecakes · fruit · ice cream', 1640, 44, 'sans', INK, 500, alpha=clamp01((u - 0.8) / 0.4))
    else:
        # 4. end card
        u = t - 14.1
        a = clamp01(u / 0.4)
        cross(d, W / 2, 520, 70)
        text(d, 'MERINGUE SUISSE', 600, 92, 'serif', INK, 500, alpha=a)
        text(d, 'Swiss meringues · Temecula, CA', 730, 50, 'serif-i', INK, 500, alpha=a)
        text(d, 'Order now for Thanksgiving', 860, 58, 'sans', SAGE, 650, alpha=clamp01((u - 0.3) / 0.4))
        text(d, 'meringuesuisse.com', 960, 54, 'sans', INK, 600, alpha=clamp01((u - 0.5) / 0.4))
        draw_meringue(d, W / 2, 1360 + math.sin(u * 6) * 10, 170, blink=blink_at(u, [1.5]), mood='smile', hat=True)
    out = im.resize((W, H), Image.LANCZOS)
    if 11.0 <= t < 14.1:
        out = Image.blend(out, real_scene(t - 11.0), clamp01((t - 11.0) / 0.6))
    elif 14.1 <= t < 14.7:
        out = Image.blend(real_scene(t - 11.0), out, clamp01((t - 14.1) / 0.6))
    if t >= 16.6:
        ph = photo_scene(t - 16.6)
        out = Image.blend(out, ph, clamp01((t - 16.6) / 0.6))
    if t < 0.3: out = Image.blend(Image.new('RGB', (W, H), IVORY), out, t / 0.3)
    return out

def render(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    n = int(DUR * FPS); prev = None
    for i in range(n):
        t = i / FPS
        f = frame(t)
        # short cross-fades between the 4 parts
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'preview':
        ts = [8.8, 10.6, 11.3, 12.5, 14.4, 15.5, 19.0]
        ims = [frame(t).resize((300, 533)) for t in ts]
        c = Image.new('RGB', (310 * len(ims), 533), 'white')
        for i, im in enumerate(ims): c.paste(im, (i * 310, 0))
        c.save(sys.argv[2])
    else:
        render(sys.argv[1])
