"""Reel 02 'Swiss story: the Meiringen legend'. Alpine sky-blue look, mascot with a tiny
hiking backpack and walking stick, Matterhorn photo, Meiringen -> Meringue word gag,
real box photos, navy end card. Run: python3 reel02.py out.mp4 | python3 reel02.py preview p.png"""
import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg import *
from PIL import Image, ImageDraw, ImageFilter

SKY_T = (150, 196, 228); SKY_B = (222, 238, 246); NAVY = (28, 46, 74); NAVY_L = (190, 205, 222)
ROCK = (110, 128, 150); ROCK_D = (88, 104, 126); SNOW = (250, 252, 255); GRASS = (128, 160, 96)
PACK = (205, 70, 50); PACK_D = (160, 50, 38); WOOD = (140, 96, 58)
IMG = os.path.join(REPO, 'images') + '/'
ALPS = Image.open(IMG + 'switzerland.jpg').convert('RGB')
BOX = Image.open(IMG + 'box-open.jpg').convert('RGB')
CARD = Image.open(IMG + 'story-card.jpg').convert('RGB')

def sky(top=SKY_T, bot=SKY_B):
    g = Image.linear_gradient('L').resize((W * SS, H * SS))
    return Image.composite(Image.new('RGB', g.size, bot), Image.new('RGB', g.size, top), g)

def mountains(d, base, cols=(ROCK, ROCK_D), alpha=255, shift=0):
    S = SS
    for i, (x, w, h) in enumerate([(-80, 620, 520), (330, 700, 760), (760, 560, 470)]):
        x += shift * (0.5 + i * 0.25)
        top = (x + w / 2, base - h)
        d.polygon([((x) * S, base * S), (top[0] * S, top[1] * S), ((x + w) * S, base * S)], fill=cols[i % 2] + (alpha,))
        # snow cap
        k = 0.30
        d.polygon([(top[0] * S, top[1] * S), ((top[0] - w / 2 * k) * S, (top[1] + h * k) * S),
                   ((top[0] - w * 0.06) * S, (top[1] + h * k * 0.8) * S), (top[0] * S, (top[1] + h * k) * S),
                   ((top[0] + w * 0.08) * S, (top[1] + h * k * 0.8) * S), ((top[0] + w / 2 * k) * S, (top[1] + h * k) * S)], fill=SNOW + (alpha,))

def hiker(d, cx, cy, r, t, blink=0.0, mood='smile', look=(0.6, -0.2), stick=True):
    """mascot with a tiny red backpack (behind, on its left) and a walking stick."""
    S = SS
    bx, by = cx - r * 0.95, cy - r * 0.95
    d.rounded_rectangle([bx * S, by * S, (bx + r * 0.55) * S, (by + r * 0.85) * S], radius=r * 0.14 * S, fill=PACK_D)
    d.rounded_rectangle([(bx - r * 0.04) * S, (by + r * 0.05) * S, (bx + r * 0.45) * S, (by + r * 0.80) * S], radius=r * 0.12 * S, fill=PACK)
    d.rounded_rectangle([(bx + r * 0.02) * S, (by + r * 0.42) * S, (bx + r * 0.36) * S, (by + r * 0.70) * S], radius=r * 0.06 * S, fill=PACK_D)
    d.ellipse([(bx + r * 0.05) * S, (by - r * 0.16) * S, (bx + r * 0.42) * S, (by + r * 0.12) * S], fill=(120, 150, 90))   # rolled mat
    draw_meringue(d, cx, cy, r, blink=blink, mood=mood, look=look)
    # strap across the body
    d.line([((cx - r * 0.50) * S, (cy - r * 0.98) * S), ((cx - r * 0.56) * S, (cy - r * 0.12) * S)], fill=PACK_D, width=int(r * 0.08 * S))
    if stick:
        sw = math.sin(t * 7) * 0.08
        x0, y0 = cx + r * 0.95, cy - r * 0.75
        d.line([((x0 - r * 0.25 * sw) * S, y0 * S), ((x0 + r * 0.25 + r * sw) * S, (cy + r * 0.12) * S)], fill=WOOD, width=int(r * 0.07 * S))
        d.ellipse([(x0 - r * 0.10) * S, (y0 - r * 0.10) * S, (x0 + r * 0.08) * S, (y0 + r * 0.08) * S], fill=MER)   # little hand

def pin(d, x, y, s, alpha=255):
    S = SS
    d.ellipse([(x - s) * S, (y - 2.6 * s) * S, (x + s) * S, (y - 0.6 * s) * S], fill=RED + (alpha,))
    d.polygon([((x - s * 0.85) * S, (y - 1.3 * s) * S), ((x + s * 0.85) * S, (y - 1.3 * s) * S), (x * S, y * S)], fill=RED + (alpha,))
    d.ellipse([(x - s * 0.38) * S, (y - 2.0 * s) * S, (x + s * 0.38) * S, (y - 1.24 * s) * S], fill=(255, 255, 255, alpha))

def full_photo(img, u, dur, fy=0.5, z0=1.0, z1=1.08):
    pw, ph = img.size; z = z0 + (z1 - z0) * u / dur
    cw = min(pw, ph * W / H) / z; ch = cw * H / W
    x = (pw - cw) / 2; y = min(max(fy * ph - ch / 2, 0), ph - ch)
    return img.transform((W * SS, H * SS), Image.EXTENT, (x, y, x + cw, y + ch), Image.BICUBIC)

def framed(img, u, dur, box, fy=0.5):
    """photo in a white polaroid-like frame, slowly zooming."""
    x0, y0, w, h = box; pw, ph = img.size; z = 1.0 + 0.06 * u / dur
    cw = min(pw, ph * w / h) / z; ch = cw * h / w
    x = (pw - cw) / 2; y = min(max(fy * ph - ch / 2, 0), ph - ch)
    return img.transform((w * SS, h * SS), Image.EXTENT, (x, y, x + cw, y + ch), Image.BICUBIC)

DUR = 19.5
CUTS = [4.0, 7.8, 11.4, 14.4, 16.6]
def frame(t):
    if t < 4.0:
        # 1. alpine sky, mascot hikes in with backpack and stick, "Did you know?"
        im = sky(); d = ImageDraw.Draw(im, 'RGBA')
        mountains(d, 1500, shift=-t * 10)
        d.rectangle([0, 1480 * SS, W * SS, H * SS], fill=GRASS)
        k = ease(clamp01(t / 1.6))
        x = -200 + 740 * k
        hop = abs(math.sin(t * 9)) * 26 if t < 1.6 else abs(math.sin((t - 1.6) * 5)) * 10
        hiker(d, x, 1600 - hop, 200, t, blink=blink_at(t, [2.5]), mood='open' if 1.8 < t < 2.4 else 'smile', look=(0.8, -0.3))
        text(d, 'SWISS STORIES', 210, 42, 'sans', NAVY, 700)
        if t > 1.9:
            bubble(d, 260, 690, 600, 220, 'Did you know?', size=72, alpha=clamp01((t - 1.9) / 0.3))
    elif t < 7.8:
        # 2. Matterhorn photo full screen, pin drops: Meiringen ~1720
        u = t - 4.0
        im = full_photo(ALPS, u, 3.8, fy=0.45)
        d = ImageDraw.Draw(im, 'RGBA')
        for i in range(60):   # soft dark band for text
            a = int(150 * (i / 60) ** 1.4)
            d.rectangle([0, (H - 700 + i * 700 / 60) * SS, W * SS, (H - 700 + (i + 1) * 700 / 60) * SS], fill=(15, 25, 40, a))
        text(d, 'In the Swiss Alps, a village called', 1400, 46, 'sans', (235, 240, 246), 600, alpha=clamp01((u - 0.6) / 0.4))
        kp = ease(clamp01((u - 1.0) / 0.4)); bounce = math.sin(clamp01((u - 1.4) / 0.4) * math.pi) * 14
        pin(d, 215, 1585 - 160 * (1 - kp) - bounce, 26, int(255 * kp))
        text(d, 'Meiringen', 1470, 130, 'serif', SNOW, 600, alpha=clamp01((u - 1.1) / 0.4))
        text(d, 'around 1720', 1650, 66, 'serif-i', SNOW, 500, alpha=clamp01((u - 1.6) / 0.4))
    elif t < 11.4:
        # 3. word gag: Meiringen -> Meringue, mascot proud
        u = t - 7.8
        im = sky(SKY_B, (240, 246, 250)); d = ImageDraw.Draw(im, 'RGBA')
        mountains(d, 1920, cols=(NAVY_L, (205, 217, 230)), shift=0)
        text(d, 'Legend says the meringue', 260, 70, 'serif', NAVY, 600)
        text(d, 'took its name from the village.', 345, 70, 'serif', NAVY, 600)
        k1 = clamp01((u - 0.4) / 0.4)
        text(d, 'MEIRINGEN', 560, 104, 'sans', NAVY, 700, alpha=k1)
        ka = ease(clamp01((u - 1.0) / 0.4))
        if ka > 0:
            S = SS; ax = W / 2; ay0, ay1 = 700, 700 + 120 * ka
            d.line([(ax * S, ay0 * S), (ax * S, ay1 * S)], fill=RED, width=8 * S)
            if ka > 0.9:
                d.polygon([((ax - 26) * S, (ay1 - 10) * S), ((ax + 26) * S, (ay1 - 10) * S), (ax * S, (ay1 + 26) * S)], fill=RED)
        k2 = clamp01((u - 1.5) / 0.3); pop = 1 + 0.18 * math.sin(math.pi * k2) if k2 < 1 else 1
        if k2 > 0:
            text(d, 'MERINGUE', 870 - 10 * (pop - 1) * 10, int(118 * pop), 'sans', RED, 750, alpha=k2)
        jump = abs(math.sin((u - 1.8) * 6)) * 60 if 1.8 < u < 2.9 else 0
        hiker(d, W / 2, 1640 - jump, 220, u, blink=blink_at(u, [3.0]), mood='open' if 1.8 < u < 2.9 else 'smile', look=(0, -1), stick=False)
    elif t < 14.4:
        # 4. "Historians still debate it..." mascot shrugs with question marks
        u = t - 11.4
        im = Image.new('RGB', (W * SS, H * SS), (236, 228, 210)); d = ImageDraw.Draw(im, 'RGBA')
        text(d, 'Legend or history?', 330, 100, 'serif', INK, 600)
        text(d, 'Historians still debate it...', 470, 60, 'serif-i', (120, 100, 70), 500, alpha=clamp01((u - 0.5) / 0.4))
        tilt = math.sin(u * 2.2) * 0.9
        hiker(d, W / 2, 1450, 230, u, blink=blink_at(u, [1.2, 2.6]), mood='o', look=(tilt, -0.6), stick=False)
        f = font('serif', 120, 700)
        for i, (qx, qy, t0) in enumerate([(250, 900, 0.6), (790, 820, 0.9), (860, 1100, 1.2)]):
            a = clamp01((u - t0) / 0.3)
            if a > 0:
                dy = math.sin(u * 4 + i) * 12
                d.text((qx * SS, (qy + dy) * SS), '?', font=f, fill=NAVY + (int(255 * a),))
        text(d, '...but the Swiss sure love their meringues!', 1680, 50, 'sans', INK, 650, alpha=clamp01((u - 1.6) / 0.4))
    elif t < 16.6:
        # 5. real photos: open box + story card, mascot peeks from the bottom
        u = t - 14.4
        im = Image.new('RGB', (W * SS, H * SS), SKY_B); d = ImageDraw.Draw(im, 'RGBA')
        text(d, 'MADE IN TEMECULA, THE SWISS WAY', 200, 38, 'sans', NAVY, 700)
        text(d, 'Our PETITES', 260, 100, 'serif', NAVY, 600)
        S = SS
        d.rectangle([90 * S, 460 * S, 990 * S, 1090 * S], fill='white')
        im.paste(framed(BOX, u, 2.2, (110, 480, 860, 590)), (110 * S, 480 * S))
        k = ease(clamp01((u - 0.5) / 0.5))
        y2 = 1150 + 200 * (1 - k)
        d.rectangle([150 * S, y2 * S, 930 * S, (y2 + 520) * S], fill=(255, 255, 255, int(255 * k)))
        if k > 0:
            ph = framed(CARD, u, 2.2, (170, int(y2) + 20, 740, 480))
            m = Image.new('L', ph.size, int(255 * k))
            im.paste(ph, (170 * S, (int(y2) + 20) * S), m)
        d = ImageDraw.Draw(im, 'RGBA')
        kp = ease(clamp01((u - 1.0) / 0.4))
        hiker(d, 900, 1990 - 230 * kp, 140, u, blink=blink_at(u, [1.8]), mood='smile', look=(-0.8, -0.8), stick=False)
    else:
        # 6. navy end card with Swiss cross, snowy peaks and the hiker waving
        u = t - 16.6
        im = Image.new('RGB', (W * SS, H * SS), NAVY); d = ImageDraw.Draw(im, 'RGBA')
        mountains(d, 1920, cols=((48, 70, 104), (40, 60, 92)))
        cross(d, W / 2, 430, 70)
        text(d, 'MERINGUE SUISSE', 530, 92, 'serif', IVORY, 500)
        text(d, 'Swiss meringues, handcrafted in Temecula', 660, 44, 'sans', NAVY_L, 500)
        text(d, 'meringuesuisse.com', 760, 60, 'sans', IVORY, 650, alpha=clamp01((u - 0.3) / 0.4))
        hiker(d, W / 2, 1500 - abs(math.sin(u * 5)) * 30, 190, u, blink=blink_at(u, [1.5]), mood='smile', look=(0, -0.3))
        text(d, 'Grüezi from Temecula!', 1580, 60, 'serif-i', IVORY, 600, alpha=clamp01((u - 0.8) / 0.4))
    out = im.resize((W, H), Image.LANCZOS)
    if t < 0.25: out = Image.blend(Image.new('RGB', (W, H), SKY_T), out, t / 0.25)
    return out

def render(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', path], stdin=subprocess.PIPE)
    X = 0.35
    for i in range(int(DUR * FPS)):
        t = i / FPS; f = frame(t)
        for c in CUTS:
            if c - X < t < c:
                f = Image.blend(f, frame(c + 0.001 + (t - (c - X))), (t - (c - X)) / X)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        ts = [1.0, 3.0, 6.5, 10.0, 13.5, 16.0, 18.5]
        ims = [frame(t).resize((300, 533)) for t in ts]
        c = Image.new('RGB', (310 * len(ims), 533), 'white')
        for i, im in enumerate(ims): c.paste(im, (i * 310, 0))
        c.save(sys.argv[2])
    else:
        render(sys.argv[1])
