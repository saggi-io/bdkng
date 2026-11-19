"""BDKNG Abend-Video (9:16): Hook-Intro (Top-Meldung groß ab dem ersten Bild), "Der Tag in Bad König" (bis 6 Meldungen, 2 Seiten),
"Morgen in Bad König" (Wetter, Müll, Termine, Tanken), "Mach mit", Abspann.
Rendert jede data/videos/<id>.json ohne fertiges Video nach assets/social/videos/<id>.mp4 und behält nur die letzten Videos."""
import sys, os, math, json, subprocess, glob
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import karte2 as K
W, H, FPS = 1080, 1920, 30
B = K.BASE; DK = (16, 32, 22); GOLD = (232, 184, 74)
hd = Image.open(os.path.join(B, 'assets', 'bdkng-header-jens.png')).convert('RGB')
q = hd.crop((1150, 40, 2172, 704))
logo = Image.open(os.path.join(B, 'assets', 'bdkng-logo-jens.png')).convert('RGBA'); logo.thumbnail((300, 190))
STIL = 'fb'  # 'fb' = bisheriger Look (Facebook), 'c' = moderner Stil C (Instagram Reels, TikTok)
KRONE = Image.open(os.path.join(B, 'assets', 'logos', 'bdkng-krone-gold.png')).convert('RGBA'); KRONE = KRONE.crop(KRONE.getbbox())
VERLAUF = None
def verlauf_c():
    global VERLAUF
    if VERLAUF is None:
        im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
        for y in range(H):
            t = y / H; d.line((0, y, W, y), fill=(int(255 - 40 * t), int(122 + 40 * t), int(89 + 120 * t)))
        VERLAUF = im
    return VERLAUF.copy()
def basis_c(t):
    im = verlauf_c(); l = KRONE.copy(); p = 1 + 0.03 * math.sin(t * 2 * math.pi * 0.8); l.thumbnail((int(330 * p), int(330 * p)), Image.LANCZOS)
    im.paste(l, ((W - l.width) // 2, 70 + (330 - l.height) // 2), l)
    return im, ImageDraw.Draw(im), 400
ICONS_C = None
def fuss(im, quelle):
    """Fußzeile: bisher grüner Balken; Stil C: bdkng.de groß + Kanal-Symbole."""
    global ICONS_C
    d = ImageDraw.Draw(im)
    if STIL != 'c':
        FU = 420; d.rectangle([0, H - FU, W, H], fill=K.GRUEN_D)
        d.text((W // 2 - 50, H - FU + 90), 'Alles auf bdkng.de', font=K.f('InterDisplay-Black.otf', 64), fill=K.WEISS, anchor='mm')
        d.text((W // 2 - 50, H - FU + 165), quelle[:60], font=K.f('Inter-Medium.otf', 30), fill=(205, 225, 210), anchor='mm')
        return
    if ICONS_C is None:
        ICONS_C = [Image.open(os.path.join(B, 'assets', 'social', 'icons', n + '.png')).convert('RGBA').resize((96, 96), Image.LANCZOS) for n in ('whatsapp', 'facebook', 'instagram', 'tiktok')]
    y = H - 400
    d.text((W // 2, y), 'bdkng.de', font=K.f('InterDisplay-Black.otf', 80), fill=K.WEISS, anchor='mt')
    x = (W - (4 * 96 + 3 * 28)) // 2
    for ic in ICONS_C: im.paste(ic, (x, y + 120), ic); x += 124
    d.text((W // 2, y + 240), 'WhatsApp-Kanal · Facebook · Instagram · TikTok: BDKNG', font=K.f('Inter-Bold.otf', 30), fill=K.WEISS, anchor='mt')
    d.text((W // 2, y + 300), quelle[:70], font=K.f('Inter-Medium.otf', 26), fill=(255, 240, 235), anchor='mt')
def UEB(): return (255, 255, 255) if STIL == 'c' else K.GOLD
def TIT(): return (255, 255, 255) if STIL == 'c' else K.GRUEN_D
def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def kopfbild(t, h):
    z = 1.0 + 0.04 * t  # langsamer Zoom
    r = max(W / q.width, h / q.height) * z
    im = q.resize((int(q.width * r), int(q.height * r)), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - h) // 3
    return im.crop((x, y, x + W, y + h))
def basis(t):
    if STIL == 'c': return basis_c(t)
    im = Image.new('RGB', (W, H), K.CREME); d = ImageDraw.Draw(im)
    TOP = 440; im.paste(kopfbild(t, TOP + 40), (0, 0))
    welle = [(0, TOP - 4)] + [(x, TOP - 18 + int(22 * ((x / W) - 0.5) ** 2 * 4) - int(14 * (x / W))) for x in range(0, W + 1, 20)] + [(W, TOP + 60), (0, TOP + 60)]
    d.polygon([(x, y - 10) for x, y in welle], fill=(140, 190, 90)); d.polygon(welle, fill=K.CREME)
    pad = Image.new('RGBA', (logo.width + 40, logo.height + 30), (255, 255, 255, 245)); pad.paste(logo, (20, 15), logo)
    im.paste(pad, ((W - pad.width) // 2, 120), K.maske(pad.size, 26))
    return im, d, TOP
def text_alpha(im, xy, txt, font, fill, a):
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).text(xy, txt, font=font, fill=fill + (int(255 * a),))
    im.paste(lay, (0, 0), lay)
def frame(t, n_items, auftritt):
    im, d, TOP = basis(t)
    fu = K.f('Inter-Bold.otf', 40)
    ts = 92
    while ts > 50 and ImageDraw.Draw(im).textlength(data['titel'], font=K.f('InterDisplay-Black.otf', ts)) > W - 190: ts -= 4
    ft = K.f('InterDisplay-Black.otf', ts)
    a = ease(t / 0.6); dy = int(40 * (1 - a))
    text_alpha(im, (60, TOP + 50 + dy), data['ueber'].upper(), fu, UEB(), a)
    text_alpha(im, (60, TOP + 105 + dy), data['titel'], ft, TIT(), a)
    y = TOP + 250; fk = K.f('Inter-Bold.otf', 32); fz = K.f('Inter-Bold.otf', 46); KS = 140
    for i, z in enumerate(data['zeilen'][:n_items]):
        p = ease(auftritt[i]) if i < len(auftritt) else 1
        x0 = int(60 - 120 * (1 - p))
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ls = K.wrap(ld, z['t'], fz, W - 190 - (x0 + KS + 34))[:3]; h = max(KS, 44 + len(ls) * 56) + 36
        ld.rounded_rectangle([x0 - 16, y - 12, W - 150, y + h - 22], 30, fill=(255, 255, 255, int(235 * p)))
        ld.rounded_rectangle([x0, y, x0 + KS, y + KS], 28, fill=K.HELL + (int(255 * p),))
        ld.text((x0 + KS + 34, y + 2), z.get('k', '').upper(), font=fk, fill=K.GOLD + (int(255 * p),))
        ty = y + 46
        for l in ls: ld.text((x0 + KS + 34, ty), l, font=fz, fill=K.TEXT + (int(255 * p),)); ty += 56
        im.paste(lay, (0, 0), lay)
        if p > 0.05:
            pic = K.quadrat(K.RUBRIK.get(z.get('r', 'aktuell'), K.RUBRIK['aktuell'])[1], KS - 20)
            m = K.maske(pic.size, 22).point(lambda v: int(v * p)); im.paste(pic, (x0 + 10, y + 10), m)
        y += h
    fuss(im, 'Quelle: ' + data['quelle'][:52])
    return im
def ende(t):
    if STIL == 'c':
        im = verlauf_c(); d = ImageDraw.Draw(im); a = ease(t / 0.5)
        l = KRONE.copy(); l.thumbnail((520, 520), Image.LANCZOS); im.paste(l, ((W - l.width) // 2, 300), l)
        text_alpha(im, (W // 2 - d.textlength('Dein Info-Kanal', font=K.f('InterDisplay-Black.otf', 84)) // 2, 880), 'Dein Info-Kanal', K.f('InterDisplay-Black.otf', 84), K.WEISS, a)
        text_alpha(im, (W // 2 - d.textlength('rund um Bad König', font=K.f('InterDisplay-Black.otf', 84)) // 2, 980), 'rund um Bad König', K.f('InterDisplay-Black.otf', 84), K.WEISS, a)
        fuss(im, 'Folgen für mehr News aus Bad König')
        return im
    im = Image.new('RGB', (W, H), K.GRUEN_D); d = ImageDraw.Draw(im)
    a = ease(t / 0.5)
    pad = Image.new('RGBA', (logo.width + 60, logo.height + 44), (255, 255, 255, 255)); pad.paste(logo, (30, 22), logo)
    im.paste(pad, ((W - pad.width) // 2, 520), K.maske(pad.size, 30))
    text_alpha(im, (W // 2 - d.textlength('Dein Info-Kanal', font=K.f('InterDisplay-Black.otf', 84)) // 2, 860), 'Dein Info-Kanal', K.f('InterDisplay-Black.otf', 84), K.WEISS, a)
    text_alpha(im, (W // 2 - d.textlength('rund um Bad König', font=K.f('InterDisplay-Black.otf', 84)) // 2, 960), 'rund um Bad König', K.f('InterDisplay-Black.otf', 84), K.WEISS, a)
    for i, s in enumerate(['🔎 KI-Suche auf bdkng.de', '💬 WhatsApp-Kanal: BDKNG', '👉 Folgen für mehr News']):
        b = ease((t - 0.4 - i * 0.3) / 0.4); txt = s[2:]
        fz = K.f('Inter-Bold.otf', 50); w = d.textlength(txt, font=fz)
        em = K.emoji(s[:1], 56)
        x = (W - w - 70) // 2; yy = 1200 + i * 110
        if em and b > 0: im.paste(em, (int(x), yy - 4), em.split()[3].point(lambda v: int(v * b)))
        text_alpha(im, (x + 70, yy), txt, fz, (226, 239, 214), b)
    return im
def szene(name, dauer, fn):
    tmp = name + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(int(dauer * FPS)): p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0; os.replace(tmp, name)

LG = [Image.open(B + '/assets/logos/bdkng-krone-gold.png').convert('RGBA'), Image.open(B + '/assets/logos/bdkng-krone-weiss.png').convert('RGBA')]
LG = [l.crop(l.getbbox()) for l in LG]
HP = Image.open(B + '/assets/bdkng-logo-jens.png').convert('RGBA'); HP = HP.crop(HP.getbbox())
_pad = Image.new('RGBA', (HP.width + 160, HP.height + 120), (0, 0, 0, 0)); ImageDraw.Draw(_pad).rounded_rectangle([0, 0, _pad.width - 1, _pad.height - 1], 90, fill=(255, 255, 255, 255)); _pad.alpha_composite(HP, (80, 60)); HP = _pad
def ease(x): x = max(0, min(1, x)); return 1 - (1 - x) ** 3
def setz(im, l, cx, cy, size, a=1.0):
    if size < 8: return
    l = l.copy(); l.thumbnail((int(size), int(size)))
    if a < 1: l.putalpha(l.getchannel('A').point(lambda v: int(v * a)))
    im.alpha_composite(l, (int(cx - l.width / 2), int(cy - l.height / 2)))
def intro(t):  # 2,4 s: Kronen-Logo gold/weiß im Wechsel pulsierend, dann HP-Logo, dann ausblenden
    im = (verlauf_c().convert('RGBA') if STIL == 'c' else Image.new('RGBA', (W, H), DK + (255,))); d = ImageDraw.Draw(im)
    p = 1 + 0.06 * math.sin(t * 2 * math.pi * 1.4); aus = 1 - ease((t - 1.3) / 0.3)
    if STIL == 'c': setz(im, LG[0 if (t % 0.4) < 0.2 else 1], W / 2, H / 2 - 80, 760 * p, aus)
    elif t < 0.8: setz(im, LG[0 if (t % 0.4) < 0.2 else 1], W / 2, H / 2 - 80, 700 * p, aus)
    else: setz(im, HP, W / 2, H / 2 - 80, 820 * p, aus)
    # Unter dem Logo: "BDKNG kompakt" und das Datum
    try:
        import datetime as _dt
        uv = str(data.get('ueber', '')).split(' · ')[0]
        tg = {'Mo.': 'Montag', 'Di.': 'Dienstag', 'Mi.': 'Mittwoch', 'Do.': 'Donnerstag', 'Fr.': 'Freitag', 'Sa.': 'Samstag', 'So.': 'Sonntag'}
        teile = uv.split(' '); MON = ['', 'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
        tag, mon = teile[1].strip('.').split('.')[:2] if len(teile) > 1 else ('', '')
        datum = tg.get(teile[0], teile[0]) + ', ' + str(int(tag)) + '. ' + MON[int(mon)] if tag else uv
    except Exception:
        datum = ''
    ta = ease(t / 0.3) * aus
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((W // 2, H // 2 + 330), 'BDKNG kompakt', font=K.f('InterDisplay-Black.otf', 96), fill=(255, 255, 255, int(255 * ta)), anchor='mm')
    if datum: ld.text((W // 2, H // 2 + 440), datum, font=K.f('Inter-Bold.otf', 60), fill=((255, 255, 255) if STIL == 'c' else GOLD) + (int(255 * ta),), anchor='mm')
    im.alpha_composite(lay)
    return im.convert('RGB')
def intro_hook(t):  # 2,2 s: ab dem ERSTEN Bild sichtbar – die wichtigste Meldung des Tages groß, Logo klein oben (Hook für Reels)
    im = (verlauf_c().convert('RGBA') if STIL == 'c' else Image.new('RGBA', (W, H), DK + (255,))); d = ImageDraw.Draw(im)
    z0 = data.get('zeilen') or []
    # Hook = die griffigste Meldung: Wichtiges/Verkehr zuerst, allgemeine Sammeltitel („Ergebnisse“, „Termine“) nur zur Not
    allg = lambda x: any(w in x['t'] for w in ('Ergebnisse', 'Termine dieser Woche', 'Termine am Wochenende', 'Rückblick'))
    rang = {'wichtig': 0, 'verkehr': 1, 'polizei': 1, 'aktuell': 2, 'sport': 3, 'termine': 4}
    z = sorted(z0, key=lambda x: (allg(x), rang.get(x.get('r', 'aktuell'), 5)))
    hook = str(data.get('hook') or (z[0]['t'] if z else '') or ('Morgen: ' + data['morgen'][0][2] if data.get('morgen') else 'Der Tag in Bad König'))
    rub = (z[0].get('k') if z else '') or ''
    p = 1 + 0.025 * math.sin(t * 2 * math.pi * 0.9)
    setz(im, LG[0], W / 2, 250, 300 * p)
    uv = str(data.get('ueber', '')).split(' · ')[0]
    d.text((W // 2, 470), ('Heute in Bad König' + (' · ' + uv if uv else '')).upper(), font=K.f('Inter-Bold.otf', 44), fill=(255, 255, 255) if STIL == 'c' else GOLD, anchor='mm')
    s = 1 + 0.06 * (1 - ease(t / 0.35))  # kleiner „Punch“ am Anfang, Text ist trotzdem sofort lesbar
    gr = int(104 * s)
    while gr > 64:
        ls = K.wrap(d, hook, K.f('InterDisplay-Black.otf', gr), W - 140)
        if len(ls) <= 4: break
        gr -= 6
    ft = K.f('InterDisplay-Black.otf', gr); ls = K.wrap(d, hook, ft, W - 140)[:4]
    zh = int(gr * 1.12); y0 = 980 - len(ls) * zh // 2
    if rub:
        fk = K.f('Inter-Bold.otf', 40); bw = d.textlength(rub.upper(), font=fk) + 60
        d.rounded_rectangle([W / 2 - bw / 2, y0 - 110, W / 2 + bw / 2, y0 - 40], 35, fill=(255, 255, 255) if STIL == 'c' else GOLD)
        d.text((W // 2, y0 - 75), rub.upper(), font=fk, fill=(214, 84, 60) if STIL == 'c' else DK, anchor='mm')
    for i, l in enumerate(ls):
        d.text((W // 2, y0 + i * zh + zh // 2), l, font=ft, fill=(255, 255, 255), anchor='mm')
    rest = max(0, len(z) - 1)
    unten = ('+ ' + str(rest) + ' weitere Meldung' + ('en' if rest != 1 else '') + ' · ' if rest else '') + 'Wetter & Müll morgen'
    a = ease((t - 0.5) / 0.4)
    if a > 0: text_alpha(im, (W // 2 - d.textlength(unten, font=K.f('Inter-Bold.otf', 46)) // 2, 1450), unten, K.f('Inter-Bold.otf', 46), (255, 255, 255) if STIL == 'c' else (226, 239, 214), a)
    return im.convert('RGB')
def vorschau(t):
    im, d, TOP = basis(t)
    a = ease(t / 0.5)
    text_alpha(im, (60, TOP + 50), D['morgen_ueber'].upper(), K.f('Inter-Bold.otf', 40), K.GOLD, a)
    text_alpha(im, (60, TOP + 105), 'Morgen in Bad König', K.f('InterDisplay-Black.otf', 84), K.GRUEN_D, a)
    y = TOP + 250
    for i, (em, kk, txt) in enumerate(D['morgen']):
        p = ease((t - 0.4 - i * 0.45) / 0.35)
        if p <= 0: continue
        x0 = int(60 - 120 * (1 - p)); lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        fz = K.f('Inter-Bold.otf', 54 if gross else 46); zh = 64 if gross else 56; ls = K.wrap(ld, txt, fz, W - 170 - (x0 + 140 + 34))[:3]; h = max(140, 50 + len(ls) * zh) + 30
        ld.rounded_rectangle([x0 - 16, y - 12, W - 130, y + h - 22], 30, fill=(255, 255, 255, int(235 * p)))
        ld.rounded_rectangle([x0, y, x0 + 140, y + 140], 28, fill=K.HELL + (int(255 * p),))
        ld.text((x0 + 174, y + 2), kk.upper(), font=K.f('Inter-Bold.otf', 38 if gross else 32), fill=K.GOLD + (int(255 * p),))
        ty = y + (52 if gross else 46)
        for l in ls: ld.text((x0 + 174, ty), l, font=fz, fill=K.TEXT + (int(255 * p),)); ty += zh
        im.paste(lay, (0, 0), lay)
        e = K.emoji(em, 84)
        if e: im.paste(e, (x0 + 70 - e.width // 2, y + 70 - e.height // 2), e.split()[3].point(lambda v: int(v * p)))
        y += h
    FU = 420; d = ImageDraw.Draw(im); d.rectangle([0, H - FU, W, H], fill=K.GRUEN_D)
    d.text((W // 2 - 50, H - FU + 90), 'Alles auf bdkng.de', font=K.f('InterDisplay-Black.otf', 64), fill=K.WEISS, anchor='mm')
    d.text((W // 2 - 50, H - FU + 165), 'Quelle: DWD, RESO, Stadt Bad König', font=K.f('Inter-Medium.otf', 30), fill=(205, 225, 210), anchor='mm')
    return im

def render(D, OUT, tmp):
    global data
    data = D
    STEP = 1.4
    def seite(zeilen, titel):
        n = len(zeilen)
        def f(t):
            D2 = dict(D); D2['zeilen'] = zeilen; D2['titel'] = titel
            globals()['data'] = D2
            auft = [(t - 0.7 - i * STEP) / 0.4 for i in range(n)]
            return frame(t, sum(1 for x in auft if x > 0), auft)
        return f, 0.7 + n * STEP + 2.2
    def mitmachen(t):
        D2 = dict(D); D2['morgen_ueber'] = 'Mach mit bei BDKNG'; D2['morgen'] = D['mitmachen']; D2['fussquelle'] = 'bdkng.de · WhatsApp-Kanal: BDKNG'
        return vorschau_x(t, D2, 'Dein Bad König', True)
    def vorschau_x(t, DD, titel, gross=False):
        im, d, TOP = basis(t)
        a = ease(t / 0.5)
        text_alpha(im, (60, TOP + 50), DD['morgen_ueber'].upper(), K.f('Inter-Bold.otf', 40), UEB(), a)
        text_alpha(im, (60, TOP + 105), titel, K.f('InterDisplay-Black.otf', 84), TIT(), a)
        y = TOP + 250
        for i, (em, kk, txt) in enumerate(DD['morgen']):
            p = ease((t - 0.4 - i * 0.45) / 0.35)
            if p <= 0: continue
            x0 = int(60 - 120 * (1 - p)); lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            fz = K.f('Inter-Bold.otf', 54 if gross else 46); zh = 64 if gross else 56; ls = K.wrap(ld, txt, fz, W - 170 - (x0 + 140 + 34))[:3]; h = max(140, 50 + len(ls) * zh) + 30
            ld.rounded_rectangle([x0 - 16, y - 12, W - 130, y + h - 22], 30, fill=(255, 255, 255, int(235 * p)))
            ld.rounded_rectangle([x0, y, x0 + 140, y + 140], 28, fill=K.HELL + (int(255 * p),))
            ld.text((x0 + 174, y + 2), kk.upper(), font=K.f('Inter-Bold.otf', 38 if gross else 32), fill=K.GOLD + (int(255 * p),))
            ty = y + (52 if gross else 46)
            for l in ls: ld.text((x0 + 174, ty), l, font=fz, fill=K.TEXT + (int(255 * p),)); ty += zh
            im.paste(lay, (0, 0), lay)
            e = K.emoji(em, 84)
            if e: im.paste(e, (x0 + 70 - e.width // 2, y + 70 - e.height // 2), e.split()[3].point(lambda v: int(v * p)))
            y += h
        fuss(im, DD.get('fussquelle', 'Quelle: DWD, RESO, Stadt Bad König'))
        return im
    def vorschau2(t): return vorschau_x(t, D, 'Morgen in Bad König')
    Z = D['zeilen'][:6]; teile = [Z[i:i + 3] for i in range(0, len(Z), 3)]
    szenen = [('b0.mp4', 2.2, intro_hook)]  # früher: 1,6 s Logo-Intro (zu schwacher Einstieg, 18.11. nur 55 Aufrufe)
    for k, tl in enumerate(teile):
        fn, dau = seite(tl, D['titel'] + (' (%d/%d)' % (k + 1, len(teile)) if len(teile) > 1 else ''))
        szenen.append(('b%d.mp4' % (k + 1), dau, fn))
    szenen.append(('bv.mp4', 0.4 + len(D['morgen']) * 0.45 + 2.6, vorschau2))
    szenen.append(('bm.mp4', 0.4 + len(D['mitmachen']) * 0.45 + 2.6, mitmachen))
    szenen.append(('be.mp4', 2.2, ende))
    for n_, d_, f_ in szenen: szene(os.path.join(tmp, n_), d_, f_)
    open(os.path.join(tmp, 'liste.txt'), 'w').write(''.join("file '%s'\n" % x[0] for x in szenen))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', os.path.join(tmp, 'liste.txt'), '-c', 'copy', OUT], check=True)
    print('Länge', round(sum(x[1] for x in szenen), 1))

if __name__ == '__main__':
    ziel = os.path.join(B, 'assets', 'social', 'videos'); os.makedirs(ziel, exist_ok=True)
    tmp = '/tmp/bdkng-video'; os.makedirs(tmp, exist_ok=True)
    auftraege = []
    for f in sorted(glob.glob(os.path.join(B, 'data', 'videos', '*.json')))[-2:]:
        vid = os.path.splitext(os.path.basename(f))[0]
        auftraege += [(f, vid, 'fb', os.path.join(ziel, vid + '.mp4')), (f, vid, 'c', os.path.join(ziel, vid + '-ig.mp4'))]
    for f, vid, stil, out in auftraege:
        if os.path.exists(out): continue
        STIL = stil; VERLAUF = None
        stumm = out + '.stumm.mp4'
        render(json.load(open(f, encoding='utf-8')), stumm, tmp)
        # Musik (lizenzfrei, Pixabay) im täglichen Wechsel, leise ausgeblendet; Ton bleibt auch ohne Musik möglich
        titel = sorted(glob.glob(os.path.join(B, 'assets', 'musik', '*.mp3')))
        if titel:
            lang = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', stumm], capture_output=True, text=True).stdout.strip() or 20)
            m = titel[sum(map(ord, vid)) % len(titel)]
            subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', stumm, '-i', m, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k',
                            '-af', 'volume=0.7,afade=t=in:d=0.5,afade=t=out:st=%.2f:d=1.5' % max(0, lang - 1.5), '-shortest', out + '.tmp.mp4'], check=True)
            os.remove(stumm)
        else:
            os.replace(stumm, out + '.tmp.mp4')
        os.replace(out + '.tmp.mp4', out)
    # nur die letzten 4 Videos aufheben (Speicherplatz)
    for alt in sorted(glob.glob(os.path.join(ziel, '*[0-9].mp4')))[:-4]: os.remove(alt)
    for alt in sorted(glob.glob(os.path.join(ziel, '*-ig.mp4')))[:-4]: os.remove(alt)
