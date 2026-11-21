"""Werbefilm Neuerungen (Nov 2026): Speisekarte, Wetter & Sprit oben, Wirtschaften, KI, Melder, App.
Aufruf: python3 tools/promofilm2.py jung|alt|probe  -> /tmp/film/"""
import sys, os, math, subprocess
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from promofilm import *  # noqa: F401,F403  (F, BLACK, W, H, FPS, Farben, Szenen-Bausteine, render)

KARTE = Image.open(B + '/assets/speisekarte/kebab-pizzahaus-bad-koenig.jpg').convert('RGB')
ORANGE = (245, 158, 11); LIME = (132, 204, 22); SCHW = (20, 20, 20)

def karte_szene(t, dur, alt=False):
    """Speisekarte: Karte fährt durchs Bild, darüber Überschrift."""
    im = Image.new('RGB', (W, H), SCHW); d = ImageDraw.Draw(im)
    a = ease(t / 0.4)
    d.text((W // 2, 150 - int((1 - a) * 80)), 'NEU', font=F(BLACK, 90), fill=ORANGE, anchor='ma')
    d.text((W // 2, 255), 'Speisekarte', font=F(BLACK, 150 if not alt else 160), fill=WH, anchor='ma')
    d.text((W // 2, 430), 'Kebab & Pizzahaus Bad König', font=F('Inter-Bold.otf', 58 if not alt else 62), fill=CR, anchor='ma')
    # Kartenausschnitt: von links oben (Drehspieß) nach rechts (Pizza), dann runter (Falafel/Getränke)
    bw, bh = 820, 840; p = min(1, t / max(0.1, dur - 0.3))
    pts = [(0, 0), (780, 0), (780, 827), (0, 827)]
    seg = p * (len(pts) - 1); i = min(int(seg), len(pts) - 2); f = ease(seg - i)
    x = int(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f); y = int(pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
    ab = KARTE.crop((x, y, x + bw, y + bh)).resize((960, int(960 * bh / bw)))
    m = Image.new('L', ab.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, ab.width, ab.height], 40, fill=255)
    k = back_out(t / 0.45); yy = 540 + int((1 - min(1, k)) * 500)
    im.paste(ab, (60, yy), m)
    d = ImageDraw.Draw(im); y2 = yy + ab.height + 50
    if t > 0.8:
        for j, (txt, bg, fg) in enumerate([('Döner · Pizza · Pide', ORANGE, SCHW), ('Mit Preisen – direkt anrufen', LIME, SCHW)]):
            if t > 0.8 + j * 0.35:
                fo = F(BLACK, 60 if not alt else 64); w = d.textlength(txt, font=fo) + 90
                d.rounded_rectangle([W // 2 - w // 2, y2, W // 2 + w // 2, y2 + 105], 52, fill=bg)
                d.text((W // 2, y2 + 52), txt, font=fo, fill=fg, anchor='mm'); y2 += 135
    return im

def leiste_szene(t, alt=False):
    """Handy-Kopf mit fester Leiste: Wetter + Tanken bleiben oben, Inhalt scrollt drunter weg."""
    im = Image.new('RGB', (W, H), CR); d = ImageDraw.Draw(im)
    # scrollender Inhalt
    off = int(ease(max(0, t - 0.6) / 1.6) * 700)
    for i in range(9):
        y = 560 + i * 260 - off
        if -260 < y < H:
            d.rounded_rectangle([70, y, W - 70, y + 220], 36, fill=WH, outline=(225, 218, 205), width=3)
            d.rounded_rectangle([110, y + 45, 520, y + 85], 20, fill=(210, 222, 212))
            d.rounded_rectangle([110, y + 115, W - 160, y + 145], 15, fill=(232, 228, 220))
    # Kopf
    d.rectangle([0, 0, W, 440], fill=(251, 250, 246)); d.line([0, 440, W, 440], fill=(231, 225, 213), width=3)
    d.rectangle([0, 0, W, 130], fill=GR)
    k = back_out(t / 0.35)
    fo = F(BLACK, 58)
    for j, txt in enumerate(['⛅ 7 °C', '⛽ E10 · Diesel']):
        pass
    # Pillen (Emoji ohne Emoji-Font: als Kreis-Icons gezeichnet)
    x = 70
    for j, (lab, col) in enumerate([('7 °C', (255, 213, 79)), ('E10 · Diesel', (120, 200, 255))]):
        kk = back_out((t - j * 0.15) / 0.35)
        if kk <= 0: continue
        w = int(d.textlength(lab, font=fo)) + 140; yy = 22 + int((1 - min(1, kk)) * -120)
        d.rounded_rectangle([x, yy, x + w, yy + 88], 44, fill=(60, 110, 78))
        d.ellipse([x + 22, yy + 20, x + 70, yy + 68], fill=col)
        d.text((x + 90, yy + 44), lab, font=fo, fill=WH, anchor='lm'); x += w + 30
    l = LG[0].copy(); l.thumbnail((230, 150)); im.paste(l, (70, 175), l)
    for j, r in enumerate(['Kompakt', 'Verkehr', 'Termine']):
        f2 = F('Inter-Bold.otf', 44); w = d.textlength(r, font=f2) + 60; xx = 70 + j * 300
        d.rounded_rectangle([xx, 345, xx + w, 415], 35, fill=WH, outline=(220, 214, 200), width=3); d.text((xx + w / 2, 380), r, font=f2, fill=DK, anchor='mm')
    # Text unten
    if t > 0.9:
        a = ease((t - 0.9) / 0.4)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([60, H - 560, W - 60, H - 120], 50, fill=GR + (int(240 * a),))
        L = ['Wetter & Sprit', 'immer oben', 'im Blick'] if alt else ['Wetter & Sprit', 'bleiben oben.']
        fs = F(BLACK, 108 if alt else 118)
        for i, s in enumerate(L): ld.text((W // 2, H - 520 + i * 125), s, font=fs, fill=(GOLD if i == 0 else WH) + (int(255 * a),), anchor='ma')
        im = im.convert('RGBA'); im.alpha_composite(lay); im = im.convert('RGB')
    return im

def wirtschaften(t, alt=False):
    im = Image.new('RGB', (W, H), GR); d = ImageDraw.Draw(im)
    d.text((W // 2, 230), 'Wo gehen wir hin?', font=F(BLACK, 100), fill=GOLD, anchor='ma')
    items = [('Kneipen & Bars', (255, 90, 60)), ('Biergärten', LIME), ('Restaurants', WH), ('Döner & Pizza', ORANGE), ('Cafés & Eis', (120, 200, 255))]
    for i, (s, c) in enumerate(items):
        k = back_out((t - 0.2 - i * 0.18) / 0.3)
        if k <= 0: continue
        fo = F(BLACK, 92); w = d.textlength(s, font=fo) + 120; y = 470 + i * 200
        x = W // 2 - w // 2 + int((1 - min(1, k)) * (W if i % 2 else -W))
        d.rounded_rectangle([x, y, x + w, y + 150], 75, fill=c); d.text((x + w / 2, y + 75), s, font=fo, fill=DK, anchor='mm')
    if t > 1.4:
        d.text((W // 2, H - 330), 'Alle Wirtschaften', font=F(BLACK, 84), fill=WH, anchor='ma')
        d.text((W // 2, H - 230), 'in Bad König', font=F(BLACK, 84), fill=WH, anchor='ma')
    return im

def ki_chat(t, alt=False):
    im = Image.new('RGB', (W, H), DK if not alt else GR); d = ImageDraw.Draw(im)
    d.text((W // 2, 230), 'Frag die BDKNG-KI', font=F(BLACK, 100), fill=GOLD, anchor='ma')
    f = F('Inter-Bold.otf', 58 if alt else 54); y = 470
    q = 'Was kostet ein Dürüm?'; n = int(len(q) * min(1, t / 0.8))
    y = bubble(d, (0, y), q[:n] or ' ', f, GOLD, DK, True)
    if 0.9 < t < 1.4:
        for i in range(3): d.ellipse([90 + i * 50, y + 20, 120 + i * 50, y + 50], fill=CR)
    if t >= 1.4:
        for i, a in enumerate(['Dürüm: 8,00 €', 'mit Käse: 8,50 €', 'Falafel-Dürüm: 8,00 €']):
            if t >= 1.4 + i * 0.35: y = bubble(d, (0, y), a, f, WH, DK, False)
    if t > 2.5:
        d.text((W // 2, H - 330), 'Auch Müll, Termine,', font=F(BLACK, 76), fill=WH, anchor='ma')
        d.text((W // 2, H - 230), 'Rathaus und Wetter.', font=F(BLACK, 76), fill=WH, anchor='ma')
    if not alt:
        im = im.convert('RGBA'); logo_on(im, 1, W - 150, 110, 180, t); im = im.convert('RGB')
    return im

def app_szene(t, alt=False):
    im = Image.new('RGB', (W, H), GOLD if not alt else GR); d = ImageDraw.Draw(im)
    k = back_out(t / 0.4)
    # Handy
    pw, ph = 470, 880; x0 = W // 2 - pw // 2; y0 = 330 + int((1 - min(1, k)) * 600)
    d.rounded_rectangle([x0, y0, x0 + pw, y0 + ph], 70, fill=DK)
    d.rounded_rectangle([x0 + 25, y0 + 25, x0 + pw - 25, y0 + ph - 25], 52, fill=(40, 70, 52))
    for r in range(3):
        for c in range(3):
            xx = x0 + 70 + c * 120; yy = y0 + 120 + r * 140
            if (r, c) == (1, 1):
                ic = Image.new('RGBA', (100, 100), (0, 0, 0, 0)); ImageDraw.Draw(ic).rounded_rectangle([0, 0, 99, 99], 24, fill=GR + (255,))
                l = LG[1].copy(); l.thumbnail((86, 80)); ic.alpha_composite(l, ((100 - l.width) // 2, (100 - l.height) // 2))
                s = 1 + 0.12 * math.sin(t * 7) if t > 0.6 else 1; ic = ic.resize((int(100 * s), int(100 * s)))
                im.paste(ic, (xx + 50 - ic.width // 2, yy + 50 - ic.height // 2), ic)
            else:
                d.rounded_rectangle([xx, yy, xx + 100, yy + 100], 24, fill=(70, 100, 82))
    d = ImageDraw.Draw(im); col = DK if not alt else WH
    d.text((W // 2, 1300), 'BDKNG als App', font=F(BLACK, 110), fill=col, anchor='ma')
    d.text((W // 2, 1440), 'Ein Klick – aufs Handy.', font=F(BLACK, 76), fill=col, anchor='ma')
    d.text((W // 2, 1540), 'Kostenlos.', font=F(BLACK, 76), fill=col, anchor='ma')
    return im

JUNG2 = [(1.2, cover), (0.7, intro),
         (1.2, lambda t: slam(['NEU', 'AUF', 'BDKNG'], t, GOLD, DK, 270, 0.18)),
         (0.6, lambda t: pop('Hunger?', t, (255, 90, 60), WH, 250)),
         (3.0, lambda t: karte_szene(t, 3.0)),
         (0.55, lambda t: pop('Tanken?', t, DK, GOLD, 250)), (0.55, lambda t: pop('Wetter?', t, GR, WH, 250)),
         (2.4, leiste_szene),
         (2.2, wirtschaften),
         (3.2, ki_chat),
         (0.55, lambda t: pop('Blitzer?', t, RED, WH, 230)), (2.2, melder),
         (2.0, app_szene),
         (2.0, folg), (2.4, endcard)]


# ---------- Drei zusätzliche Seiten (21.11.2026): Wirte, Vereine, Alt bewährt ----------
SEITEN = {
  'wirte': ('Für Wirtinnen & Wirte', 'Schickt uns eure Karte!',
            [('🍽️', 'Alle Wirtschaften', 'Kneipe, Café, Restaurant, Imbiss'), ('📸', 'Einfach schicken', 'Speisekarte als Foto oder PDF an info@bdkng.de'), ('🥗', 'Mittagstisch', 'Wochenkarte schicken – wir stellen sie online')],
            'Kostenlos · info@bdkng.de'),
  'vereine': ('Für Vereine & Veranstalter', 'Keine Terminkollision',
              [('🔍', 'Wunschtermin prüfen', 'Ist an eurem Tag schon was los in Bad König?'), ('📅', 'Termin melden', 'Euer Fest, Konzert oder Basar – nach Prüfung online'), ('🤝', 'Alle sehen es', 'Andere Vereine planen drumherum')],
              'bdkng.de/termine.html'),
  'bewaehrt': ('Alt bewährt', 'Jeden Tag für dich',
               [('⛽', 'Tankpreise', 'Günstigste Tankstelle rund um Bad König'), ('📅', 'Termine', 'Was ist los – heute, diese Woche, am Wochenende'), ('🚨', 'Blitzer & Stau', 'Warnen und selbst melden')],
               'Alles auf bdkng.de'),
}

def alt_tafel(key):
    import abendvideo as AV
    ueber, titel, items, fuss = SEITEN[key]
    def f(t):
        im = Image.new('RGB', (W, H), GR); d = ImageDraw.Draw(im)
        im.paste(headimg(), (0, 70)); d.rectangle([0, 70 + HH, W, 70 + HH + 12], fill=GOLD)
        top = 70 + HH + 70; a = ease(t / 0.4)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.text((W // 2, top), ueber, font=F('Inter-Bold.otf', 56), fill=CR + (int(255 * a),), anchor='ma')
        ft, L, sz = fit2(ld, titel, 104, W - 100)
        for i, l in enumerate(L): ld.text((W // 2, top + 90 + i * int(sz * 1.1)), l, font=ft, fill=GOLD + (int(255 * a),), anchor='ma')
        im = im.convert('RGBA'); im.alpha_composite(lay)
        y = top + 110 + len(L) * int(sz * 1.1) + 20
        for i, (em, kk, txt) in enumerate(items):
            p = ease((t - 0.5 - i * 0.55) / 0.4)
            if p <= 0: continue
            x0 = 60 + int((1 - p) * -200); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            fz = F('Inter-Bold.otf', 54); ls = wrap(ld, txt, fz, W - 120 - (x0 + 190))[:2]; h = 120 + len(ls) * 66
            ld.rounded_rectangle([x0, y, W - 60, y + h], 34, fill=CR + (int(250 * p),))
            ld.rounded_rectangle([x0 + 24, y + 24, x0 + 164, y + 164 if h > 180 else y + h - 24], 28, fill=WH + (int(255 * p),))
            ld.text((x0 + 190, y + 22), kk, font=F(BLACK, 64), fill=GR + (int(255 * p),))
            for j, l in enumerate(ls): ld.text((x0 + 190, y + 100 + j * 66), l, font=fz, fill=DK + (int(255 * p),))
            im.alpha_composite(lay)
            e = AV.K.emoji(em, 96)
            if e: im.paste(e, (x0 + 94 - e.width // 2, y + min(h, 188) // 2 - e.height // 2), e.split()[3].point(lambda v: int(v * p)))
            y += h + 30
        if t > 0.5 + 3 * 0.55:
            ld = ImageDraw.Draw(im); fo = F(BLACK, 66); w = ld.textlength(fuss, font=fo) + 100
            ld.rounded_rectangle([W // 2 - w // 2, H - 250, W // 2 + w // 2, H - 140], 55, fill=GOLD)
            ld.text((W // 2, H - 195), fuss, font=fo, fill=DK, anchor='mm')
        return im.convert('RGB')
    return f

def alt_szenen():
    sc = [(1.4, cover),
          (2.2, lambda t: alt_frame('Neu auf\nbdkng.de', t, 2.2)),
          (4.0, lambda t: karte_szene(t, 4.0, True)),
          (3.4, lambda t: leiste_szene(t, True)),
          (3.0, lambda t: wirtschaften(t, True)),
          (4.4, alt_tafel('wirte')),
          (4.4, alt_tafel('vereine')),
          (4.2, lambda t: ki_chat(t, True)),
          (4.4, alt_tafel('bewaehrt')),
          (2.8, lambda t: app_szene(t, True)),
          (2.6, lambda t: alt_social(t, 2.6)),
          (2.6, lambda t: alt_frame('bdkng.de', t, 2.6, True))]
    return sc

def mit_musik(video, musik, out):
    dauer = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', video]).decode())
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', video, '-i', musik, '-filter_complex',
                           f'[1:a]atrim=0:{dauer},afade=t=in:d=0.3,afade=t=out:st={dauer - 1.2}:d=1.2,volume=0.8[a]',
                           '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out])

if __name__ == '__main__':
    os.makedirs('/tmp/film', exist_ok=True); w = sys.argv[1]
    if w == 'probe':
        fr = [karte_szene(2.0, 3.0), leiste_szene(2.0), wirtschaften(2.0), ki_chat(3.0), app_szene(1.5), karte_szene(3, 4, True), leiste_szene(3, True), ki_chat(3.5, True)]
        c = Image.new('RGB', (270 * len(fr), 480)); [c.paste(x.resize((270, 480)), (i * 270, 0)) for i, x in enumerate(fr)]; c.save('/tmp/film/probe-neu.jpg')
    elif w == 'probe3':
        fr = [alt_tafel(k)(4.0) for k in ('wirte', 'vereine', 'bewaehrt')]
        c = Image.new('RGB', (360 * 3, 640)); [c.paste(x.resize((360, 640)), (i * 360, 0)) for i, x in enumerate(fr)]; c.save('/tmp/film/probe-alt3.jpg')
    elif w == 'jungc': pass
    elif w == 'jung':
        render(JUNG2, '/tmp/film/neu-jung-stumm.mp4'); mit_musik('/tmp/film/neu-jung-stumm.mp4', B + '/assets/musik/delosound-upbeat-summer-pop-368301.mp3', '/tmp/film/bdkng-neuerungen-jung.mp4')
    else:
        render(alt_szenen(), '/tmp/film/neu-alt-stumm.mp4'); mit_musik('/tmp/film/neu-alt-stumm.mp4', B + '/assets/musik/sonican-uplifting-ukulele-334612.mp3', '/tmp/film/bdkng-neuerungen-alt.mp4')

# ---------- JUNG im Stil C (wie die Instagram/TikTok-Reels seit 20.11.2026) ----------
def jung_c():
    import abendvideo as A
    A.STIL = 'c'; A.VERLAUF = None
    WEI = (255, 255, 255)
    def hook(t):
        im = A.verlauf_c().convert('RGBA'); d = ImageDraw.Draw(im)
        A.setz(im, A.LG[0], W / 2, 250, 300 * (1 + 0.025 * math.sin(t * 2 * math.pi * 0.9)))
        d.text((W // 2, 470), 'NEU AUF BDKNG.DE', font=A.K.f('Inter-Bold.otf', 44), fill=WEI, anchor='mm')
        fk = A.K.f('Inter-Bold.otf', 40); bw = d.textlength('FÜR DICH', font=fk) + 60
        d.rounded_rectangle([W / 2 - bw / 2, 650, W / 2 + bw / 2, 720], 35, fill=WEI); d.text((W // 2, 685), 'FÜR DICH', font=fk, fill=(214, 84, 60), anchor='mm')
        s = 1 + 0.06 * (1 - A.ease(t / 0.35)); ft = A.K.f('InterDisplay-Black.otf', int(112 * s))
        for i, l in enumerate(['Döner-Karte,', 'Sprit & Wetter', 'immer dabei']):
            d.text((W // 2, 840 + i * 130), l, font=ft, fill=WEI, anchor='mm')
        a = A.ease((t - 0.5) / 0.4)
        u = 'Speisekarte · Sprit · Wetter · KI · Melder'
        if a > 0: A.text_alpha(im, (W // 2 - d.textlength(u, font=A.K.f('Inter-Bold.otf', 44)) // 2, 1300), u, A.K.f('Inter-Bold.otf', 44), WEI, a)
        return im.convert('RGB')
    def karten(ueber, titel, liste, quelle):
        def f(t):
            im, d, TOP = A.basis(t); a = A.ease(t / 0.5)
            A.text_alpha(im, (60, TOP + 50), ueber.upper(), A.K.f('Inter-Bold.otf', 40), A.UEB(), a)
            A.text_alpha(im, (60, TOP + 105), titel, A.K.f('InterDisplay-Black.otf', 84), A.TIT(), a)
            y = TOP + 250
            for i, (em, kk, txt) in enumerate(liste):
                p = A.ease((t - 0.4 - i * 0.45) / 0.35)
                if p <= 0: continue
                x0 = int(60 - 120 * (1 - p)); lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
                fz = A.K.f('Inter-Bold.otf', 52); zh = 62; ls = A.K.wrap(ld, txt, fz, W - 170 - (x0 + 174))[:3]; h = max(140, 50 + len(ls) * zh) + 30
                ld.rounded_rectangle([x0 - 16, y - 12, W - 130, y + h - 22], 30, fill=(255, 255, 255, int(235 * p)))
                ld.rounded_rectangle([x0, y, x0 + 140, y + 140], 28, fill=A.K.HELL + (int(255 * p),))
                ld.text((x0 + 174, y + 2), kk.upper(), font=A.K.f('Inter-Bold.otf', 36), fill=A.K.GOLD + (int(255 * p),))
                ty = y + 50
                for l in ls: ld.text((x0 + 174, ty), l, font=fz, fill=A.K.TEXT + (int(255 * p),)); ty += zh
                im.paste(lay, (0, 0), lay)
                e = A.K.emoji(em, 84)
                if e: im.paste(e, (x0 + 70 - e.width // 2, y + 70 - e.height // 2), e.split()[3].point(lambda v: int(v * p)))
                y += h
            A.fuss(im, quelle); return im
        return f
    def karte_c(t, dur=3.2):
        im, d, TOP = A.basis(t); a = A.ease(t / 0.5)
        A.text_alpha(im, (60, TOP + 50), 'NEU · GENUSS'.upper(), A.K.f('Inter-Bold.otf', 40), WEI, a)
        A.text_alpha(im, (60, TOP + 105), 'Speisekarte', A.K.f('InterDisplay-Black.otf', 84), WEI, a)
        bw, bh = 820, 520; p = min(1, t / max(0.1, dur - 0.3))
        pts = [(0, 0), (780, 0), (780, 1126), (0, 1126)]
        seg = p * (len(pts) - 1); i = min(int(seg), len(pts) - 2); f = A.ease(seg - i)
        x = int(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f); y = int(pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)
        ab = KARTE.crop((x, y, x + bw, y + bh)).resize((960, int(960 * bh / bw)))
        k = back_out(t / 0.45); yy = TOP + 240 + int((1 - min(1, k)) * 400)
        fr = Image.new('RGB', (ab.width + 24, ab.height + 24), WEI); fr.paste(ab, (12, 12))
        im.paste(fr, (48, yy), A.K.maske(fr.size, 36))
        d = ImageDraw.Draw(im); y2 = yy + fr.height + 30
        if t > 0.8: d.text((W // 2, y2), 'Kebab & Pizzahaus Bad König', font=A.K.f('InterDisplay-Black.otf', 56), fill=WEI, anchor='mt')
        if t > 1.2: d.text((W // 2, y2 + 80), 'Mit Preisen – direkt anrufen', font=A.K.f('Inter-Bold.otf', 46), fill=WEI, anchor='mt')
        A.fuss(im, 'Speisekarte: Kebab & Pizzahaus Bad König'); return im
    def chat_c(t):
        im, d, TOP = A.basis(t); a = A.ease(t / 0.5)
        A.text_alpha(im, (60, TOP + 50), 'FRAG DIE BDKNG-KI', A.K.f('Inter-Bold.otf', 40), WEI, a)
        A.text_alpha(im, (60, TOP + 105), 'Einfach fragen', A.K.f('InterDisplay-Black.otf', 84), WEI, a)
        d = ImageDraw.Draw(im); f = A.K.f('Inter-Bold.otf', 54); y = TOP + 260
        q = 'Was kostet ein Dürüm?'; n = int(len(q) * min(1, t / 0.8))
        y = bubble(d, (0, y), q[:n] or ' ', f, (255, 255, 255), (214, 84, 60), True)
        if 0.9 < t < 1.4:
            for i in range(3): d.ellipse([90 + i * 50, y + 20, 120 + i * 50, y + 50], fill=WEI)
        if t >= 1.4:
            for i, s in enumerate(['Dürüm: 8,00 €', 'mit Käse: 8,50 €', 'Falafel-Dürüm: 8,00 €']):
                if t >= 1.4 + i * 0.35: y = bubble(d, (0, y), s, f, (255, 255, 255), A.K.TEXT, False)
        A.fuss(im, 'Auch Müll, Termine, Rathaus und Wetter'); return im
    neu1 = [('🥙', 'Speisekarte', 'Döner, Pizza, Pide – mit Preisen'), ('⛽', 'Wetter & Sprit', 'Immer oben im Blick'), ('🍻', 'Wirtschaften', 'Kneipen, Biergärten, Restaurants')]
    neu2 = [('🤖', 'BDKNG-KI', 'Frag: Was kostet ein Dürüm?'), ('📣', 'Blitzer & Stau', 'Gesehen? Auf bdkng.de melden'), ('📲', 'Als App', 'Mit einem Klick aufs Handy')]
    return [(2.4, hook),
            (0.4 + 3 * 0.45 + 2.2, karten('Neu auf bdkng.de', 'Was ist neu? (1/2)', neu1, 'Alles kostenlos auf bdkng.de')),
            (3.4, karte_c),
            (3.4, chat_c),
            (0.4 + 3 * 0.45 + 2.2, karten('Neu auf bdkng.de', 'Was ist neu? (2/2)', neu2, 'Alles kostenlos auf bdkng.de')),
            *[(0.4 + 3 * 0.45 + 2.4, karten(SEITEN[k][0], SEITEN[k][1], SEITEN[k][2], SEITEN[k][3])) for k in ('wirte', 'vereine', 'bewaehrt')],
            (2.4, A.ende)]

if __name__ == '__main__' and sys.argv[1] == 'jungc':
    render(jung_c(), '/tmp/film/neu-jungc-stumm.mp4'); mit_musik('/tmp/film/neu-jungc-stumm.mp4', B + '/assets/musik/delosound-upbeat-summer-pop-368301.mp3', '/tmp/film/bdkng-neuerungen-jung.mp4')
