"""'Breaking news' reel: Meringue Suisse is now on FrontStreetMakers.com. News-studio look
(navy + red), mascot as news anchor with a tiny tie and a microphone, scrolling ticker, LIVE
report with a real photo, end card. Original synthesized music from news_music.py.
Run: python3 news.py out.mp4 | python3 news.py preview p.png"""
import sys, os, math, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tg import *
from PIL import Image, ImageDraw

NAVY = (16, 30, 58); NAVY2 = (26, 48, 90); BLUE = (52, 98, 170); NRED = (205, 32, 38); WHITE = (255, 255, 255)
DESK = (34, 40, 52); GOLDN = (240, 196, 80)
IMG = os.path.join(REPO, 'images') + '/'
LIVE = Image.open(IMG + 'box-closed.jpg').convert('RGB')
LIVE2 = Image.open(IMG + 'hero.jpg').convert('RGB')
SITE = 'FrontStreetMakers.com'
TICK = '   MERINGUE SUISSE NOW ON FRONTSTREETMAKERS.COM  •  SWISS MERINGUES HANDCRAFTED IN TEMECULA  •  PETITES: BOX OF 9  •  CLASSIC · COFFEE · CHOCOLATE  •  ALSO AT MERINGUESUISSE.COM  •'

def studio_bg(t):
    im = Image.new('RGB', (W * SS, H * SS), NAVY); d = ImageDraw.Draw(im, 'RGBA')
    S = SS
    for i in range(14):   # rotating light beams
        a = t * 0.25 + i * math.pi / 7
        x2, y2 = W / 2 + math.cos(a) * 2200, 760 + math.sin(a) * 2200
        x3, y3 = W / 2 + math.cos(a + 0.12) * 2200, 760 + math.sin(a + 0.12) * 2200
        d.polygon([(W / 2 * S, 760 * S), (x2 * S, y2 * S), (x3 * S, y3 * S)], fill=BLUE + (28,))
    for k in range(3):   # globe lines
        r = 330 + k * 4
        d.ellipse([(W / 2 - r) * S, (760 - r) * S, (W / 2 + r) * S, (760 + r) * S], outline=BLUE + (90,), width=3 * S)
    for k in range(-2, 3):
        w = abs(math.cos(t * 0.6 + k * 0.6)) * 330
        d.ellipse([(W / 2 - w) * S, (760 - 330) * S, (W / 2 + w) * S, (760 + 330) * S], outline=BLUE + (60,), width=2 * S)
        y = 760 + k * 120; hw = math.sqrt(max(0, 330 ** 2 - (k * 120) ** 2))
        d.line([((W / 2 - hw) * S, y * S), ((W / 2 + hw) * S, y * S)], fill=BLUE + (60,), width=2 * S)
    return im, d

def ticker(d, t, y=1780):
    S = SS
    d.rectangle([0, y * S, W * S, (y + 90) * S], fill=WHITE)
    f = font('sans', 40, 700)
    tw = d.textlength(TICK, font=f) / S
    x = W - (t * 260) % (tw)
    for k in (0, 1):
        d.text(((x + k * tw - 0) * S, (y + 20) * S), TICK, font=f, fill=NAVY)
    d.rectangle([0, y * S, 200 * S, (y + 90) * S], fill=NRED)
    f2 = font('sans', 40, 800); s = 'NEWS'; w2 = d.textlength(s, font=f2)
    d.text(((100) * S - w2 / 2, (y + 20) * S), s, font=f2, fill=WHITE)

def banner(d, y, label, head, sub, k=1.0):
    """lower-third: red label + white headline bar."""
    S = SS; x = -1080 * (1 - ease(k))
    d.rectangle([(x + 40) * S, y * S, (x + 380) * S, (y + 70) * S], fill=NRED)
    f = font('sans', 42, 800); d.text(((x + 62) * S, (y + 12) * S), label, font=f, fill=WHITE)
    d.rectangle([(x + 40) * S, (y + 70) * S, (x + 1040) * S, (y + 230) * S], fill=WHITE)
    f = font('sans', 52, 800)
    d.text(((x + 64) * S, (y + 86) * S), head, font=f, fill=NAVY)
    f = font('sans', 38, 600)
    d.text(((x + 64) * S, (y + 160) * S), sub, font=f, fill=BLUE)

def tie(d, cx, cy, r):
    S = SS; y = cy - r * 0.26
    d.polygon([((cx - r * 0.10) * S, y * S), ((cx + r * 0.10) * S, y * S), ((cx + r * 0.05) * S, (y + r * 0.08) * S), ((cx - r * 0.05) * S, (y + r * 0.08) * S)], fill=NRED)
    d.polygon([((cx - r * 0.05) * S, (y + r * 0.08) * S), ((cx + r * 0.05) * S, (y + r * 0.08) * S), ((cx + r * 0.10) * S, (y + r * 0.26) * S), (cx * S, (y + r * 0.32) * S), ((cx - r * 0.10) * S, (y + r * 0.26) * S)], fill=NRED)

def mic(d, x, y, r, ang=0.0):
    S = SS
    ex, ey = x + math.sin(ang) * r * 0.5, y - math.cos(ang) * r * 0.5
    d.line([(x * S, y * S), (ex * S, ey * S)], fill=(40, 40, 44), width=int(r * 0.09 * S))
    d.ellipse([(ex - r * 0.14) * S, (ey - r * 0.16) * S, (ex + r * 0.14) * S, (ey + r * 0.12) * S], fill=(70, 72, 80))
    d.rectangle([(x - r * 0.10) * S, (y - r * 0.05) * S, (x + r * 0.10) * S, (y + r * 0.10) * S], fill=NRED)

def fit(img, w, h, u, dur, z1=1.08):
    pw, ph = img.size; z = 1 + (z1 - 1) * u / dur
    cw = min(pw, ph * w / h) / z; ch = cw * h / w; x = (pw - cw) / 2; y = (ph - ch) / 2
    return img.transform((int(w * SS), int(h * SS)), Image.EXTENT, (x, y, x + cw, y + ch), Image.BICUBIC)

DUR = 14.0
CUTS = [2.0, 6.0, 10.0]
def frame(t):
    if t < 2.0:
        # 1. intro: globe spins, BREAKING NEWS slams in
        im, d = studio_bg(t * 3)
        k = ease(clamp01((t - 0.3) / 0.4)); S = SS
        sc = 1 + 0.6 * (1 - k)
        if k > 0:
            h = 150 * sc
            d.rectangle([0, (700 - h / 2) * S, W * S, (700 + h / 2) * S], fill=NRED + (int(255 * k),))
            text(d, 'BREAKING', 700 - 62 * sc, int(110 * sc), 'sans', WHITE, 850, alpha=k)
        k2 = ease(clamp01((t - 0.9) / 0.4))
        d.rectangle([(W / 2 - 300 * k2) * S, 800 * S, (W / 2 + 300 * k2) * S, 900 * S], fill=WHITE)
        if k2 > 0.6: text(d, 'NEWS', 812, 74, 'sans', NAVY, 850)
        text(d, 'MERINGUE NEWS NETWORK', 1100, 40, 'sans', (180, 196, 224), 700, alpha=clamp01((t - 1.2) / 0.3))
    elif t < 6.0:
        # 2. anchor desk: mascot with tie, lower third with the headline
        u = t - 2.0
        im, d = studio_bg(u + 6); S = SS
        mood = 'open' if (int(u * 6) % 2 == 0 and 0.6 < u < 2.6) else 'smile'
        draw_meringue(d, W / 2, 1290, 250, blink=blink_at(u, [1.1, 3.2]), mood=mood, look=(0, 0))
        tie(d, W / 2, 1290 + 15, 250)
        d.rectangle([60 * S, 1285 * S, 1020 * S, 1440 * S], fill=DESK)
        d.rectangle([60 * S, 1285 * S, 1020 * S, 1305 * S], fill=BLUE)
        text(d, 'MNN', 1325, 70, 'sans', (180, 196, 224), 800)
        mic(d, W / 2 + 290, 1285, 220, ang=-0.3)
        d.rectangle([60 * S, 230 * S, 330 * S, 290 * S], fill=NRED)
        if int(u * 2) % 2 == 0: d.ellipse([84 * S, 246 * S, 110 * S, 272 * S], fill=WHITE)
        f = font('sans', 38, 800); d.text((124 * S, 238 * S), 'LIVE', font=f, fill=WHITE)
        bubble(d, 560, 330, 440, 170, 'This just in!', size=56, alpha=clamp01((u - 0.3) / 0.3))
        banner(d, 1490, 'BREAKING', 'Now on ' + SITE, 'Meringue Suisse · Swiss meringues from Temecula', k=clamp01((u - 0.8) / 0.5))
        ticker(d, t)
    elif t < 10.0:
        # 3. live report: photo in a TV frame, reporter mascot with a microphone
        u = t - 6.0
        im, d = studio_bg(u + 12); S = SS
        text(d, 'LIVE FROM TEMECULA', 200, 46, 'sans', WHITE, 800)
        d.rectangle([70 * S, 300 * S, 1010 * S, 960 * S], fill=WHITE)
        ph = LIVE if u < 2.0 else LIVE2
        im.paste(fit(ph, 920, 640, u % 2.0, 2.0), (80 * S, 310 * S))
        d = ImageDraw.Draw(im, 'RGBA')
        if int(u * 2) % 2 == 0:
            d.ellipse([110 * S, 340 * S, 140 * S, 370 * S], fill=NRED)
        f = font('sans', 34, 800); d.text((152 * S, 336 * S), 'LIVE', font=f, fill=WHITE)
        k = ease(clamp01(u / 0.5))
        x = 300 - 500 * (1 - k)
        draw_meringue(d, x, 1450, 190, blink=blink_at(u, [2.4]), mood='open' if int(u * 5) % 2 == 0 and u < 2.5 else 'smile', look=(0.7, -0.3))
        mic(d, x + 200, 1330, 260, ang=-0.5)
        bubble(d, 470, 1040, 560, 230, 'Our PETITES are\nnow on ' + 'FrontStreet\nMakers.com!', size=46, alpha=clamp01((u - 0.5) / 0.3))
        banner(d, 1520, 'LIVE', 'Swiss meringues, made in', 'Temecula · Classic · Coffee · Chocolate', k=clamp01((u - 0.2) / 0.5))
        ticker(d, t)
    else:
        # 4. end card
        u = t - 10.0
        im, d = studio_bg(u + 18); S = SS
        cross(d, W / 2, 330, 66)
        text(d, 'MERINGUE SUISSE', 420, 88, 'serif', WHITE, 500)
        text(d, 'NOW ON', 640, 56, 'sans', (180, 196, 224), 800, alpha=clamp01((u - 0.2) / 0.3))
        k = clamp01((u - 0.4) / 0.3); pop = 1 + 0.15 * math.sin(math.pi * k) if k < 1 else 1
        d.rectangle([60 * S, 730 * S, 1020 * S, 870 * S], fill=NRED + (int(255 * k),))
        text(d, SITE, 762 - 4 * (pop - 1) * 10, int(72 * pop), 'sans', WHITE, 850, alpha=k)
        text(d, 'and always at meringuesuisse.com', 920, 46, 'sans', WHITE, 600, alpha=clamp01((u - 1.0) / 0.4))
        draw_meringue(d, W / 2, 1550 - abs(math.sin(u * 5)) * 30, 200, blink=blink_at(u, [1.8]), mood='smile', look=(0, -0.3))
        tie(d, W / 2, 1550 - abs(math.sin(u * 5)) * 30, 200)
        text(d, 'Back to you in the studio!', 1610, 54, 'serif-i', GOLDN, 600, alpha=clamp01((u - 1.6) / 0.4))
    out = im.resize((W, H), Image.LANCZOS)
    if t < 0.2: out = Image.blend(Image.new('RGB', (W, H), NAVY), out, t / 0.2)
    return out

def render(path):
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, 'm.wav'); vid = os.path.join(tmp, 'v.mp4')
    subprocess.run([sys.executable, os.path.join(HERE, 'news_music.py'), wav], check=True)
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', vid], stdin=subprocess.PIPE)
    X = 0.12   # quick news-style cuts
    for i in range(int(DUR * FPS)):
        t = i / FPS; f = frame(t)
        for c in CUTS:
            if c - X < t < c:
                f = Image.blend(f, frame(c + 0.001 + (t - (c - X))), (t - (c - X)) / X)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', path], check=True)

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        ts = [0.5, 1.6, 3.5, 5.5, 7.0, 9.0, 12.5]
        ims = [frame(t).resize((300, 533)) for t in ts]
        c = Image.new('RGB', (310 * len(ims), 533), 'white')
        for i, im in enumerate(ims): c.paste(im, (i * 310, 0))
        c.save(sys.argv[2])
    else:
        render(sys.argv[1])
