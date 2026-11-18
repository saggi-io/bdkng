"""BDKNG Social-Karten, Stil C (modern, für Instagram und TikTok).
Gleiche Eingabe wie karte2 (data/karten/<id>.json). Ausgabe: <id>-ig.jpg (4:5) und <id>-ig-9x16.jpg.
Facebook nutzt weiter karte2 (<id>.jpg)."""
import os
from PIL import Image, ImageDraw, ImageFont
from karte2 import emoji, wrap, zeile
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(BASE, 'tools', 'fonts')
def F(n, s): return ImageFont.truetype(os.path.join(FD, n), int(s))
BLACK, BOLD, MED = 'InterDisplay-Black.otf', 'Inter-Bold.otf', 'Inter-Medium.otf'
RUB = {'aktuell': ('AKTUELLES', '📰', '#FF7A59'), 'verkehr': ('VERKEHR', '🚧', '#F08A24'), 'bahn': ('BAHN', '🚆', '#3B82F6'),
       'termine': ('TERMINE', '📅', '#8B5CF6'), 'sport': ('SPORT', '⚽', '#10B981'), 'wetter': ('WETTER', '🌦️', '#0EA5E9'),
       'muell': ('MÜLLABFUHR', '🗑️', '#64748B'), 'polizei': ('POLIZEI', '🚓', '#2563EB'), 'wichtig': ('WICHTIG', '⚠️', '#E11D48'),
       'genuss': ('GENUSS', '🍽️', '#D97706')}
ICONS = [('whatsapp', 'WhatsApp'), ('facebook', 'Facebook'), ('instagram', 'Instagram'), ('tiktok', 'TikTok')]

def verlauf(W, H):
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=(int(255 - 40 * t), int(122 + 40 * t), int(89 + 120 * t)))
    return im.convert('RGBA')

def inhalt(img, d, k, W, x0, x1, y, s, zeichnen=True):
    """Zeichnet (oder misst) den Karteninhalt ab y mit Schriftfaktor s. Gibt das Ende zurück."""
    rub = k.get('rubrik', 'aktuell'); name, emo, farbe = RUB.get(rub, RUB['aktuell'])
    zl = [zeile(z, rub) for z in k.get('zeilen', [])][:8]
    liste = k.get('art', 'liste') == 'liste'
    mx = (x0 + x1) // 2; bw = x1 - x0
    e = emoji(emo, int(130 * s))
    if e:
        if zeichnen: img.alpha_composite(e, (mx - e.width // 2, y))
        y += e.height + int(18 * s)
    fr = F(BLACK, 32 * s); tw = d.textlength(name, font=fr)
    if zeichnen:
        d.rounded_rectangle((mx - tw / 2 - 22 * s, y, mx + tw / 2 + 22 * s, y + fr.size + 20 * s), radius=999, fill=farbe)
        d.text((mx, y + 8 * s), name, font=fr, fill='#FFFFFF', anchor='ma')
    y += fr.size + int(36 * s)
    if k.get('ueber'):
        fu = F(BOLD, 28 * s)
        if zeichnen: d.text((mx, y), str(k['ueber']), font=fu, fill='#9A9A9A', anchor='ma')
        y += fu.size + int(14 * s)
    ft = F(BLACK, 66 * s)
    for ln in wrap(d, k.get('titel', ''), ft, bw):
        if zeichnen: d.text((mx, y), ln, font=ft, fill='#1B1B1B', anchor='ma')
        y += int(ft.size * 1.08)
    y += int(24 * s)
    if liste:
        fz = F(BOLD, 36 * s); fk = F(BOLD, 22 * s); ES = int(52 * s)
        for i, (t, r, em, kk) in enumerate(zl):
            if i:
                if zeichnen: d.line((x0, y, x1, y), fill='#EEE6E3', width=2)
                y += int(16 * s)
            ich = em or RUB.get(r, RUB['aktuell'])[1]
            ie = emoji(ich, ES)
            tx = x0 + ES + int(20 * s)
            yy = y
            if kk:
                if zeichnen: d.text((tx, yy), kk.upper()[:40], font=fk, fill=RUB.get(r, RUB['aktuell'])[2])
                yy += fk.size + int(6 * s)
            lines = wrap(d, t, fz, x1 - tx)
            hoehe = (yy - y) + len(lines) * int(fz.size * 1.18)
            if zeichnen and ie: img.alpha_composite(ie, (x0, y + max(0, (hoehe - ie.height) // 2)))
            for ln in lines:
                if zeichnen: d.text((tx, yy), ln, font=fz, fill='#2A2A2A')
                yy += int(fz.size * 1.18)
            y = max(yy, y + ES) + int(16 * s)
    else:
        fz = F(MED, 38 * s)
        for t, r, em, kk in zl:
            for ln in wrap(d, t, fz, bw):
                if zeichnen: d.text((mx, y), ln, font=fz, fill='#444444', anchor='ma')
                y += int(fz.size * 1.3)
            y += int(14 * s)
    return y

def karte(k, W, H, ziel):
    tik = H > 1500
    img = verlauf(W, H); d = ImageDraw.Draw(img)
    lg = Image.open(os.path.join(BASE, 'assets', 'bdkng-logo.png')).convert('RGBA'); lg.thumbnail((10000, 190 if tik else 150))
    lx = (W - lg.width) // 2; ly = 70 if tik else 34
    d.rounded_rectangle((lx - 30, ly - 14, lx + lg.width + 30, ly + lg.height + 14), radius=40, fill='#FFFFFF')
    img.alpha_composite(lg, (lx, ly))
    top = ly + lg.height + 40; fuss = 360 if tik else 275
    kx0, kx1, ky1 = 50, W - 50, H - fuss
    d.rounded_rectangle((kx0, top, kx1, ky1), radius=60, fill='#FFFFFF')
    x0, x1 = kx0 + 60, kx1 - 60; platz = (ky1 - 80) - (top + 40)
    probe = Image.new('RGBA', (W, H)); pd = ImageDraw.Draw(probe)
    s = 1.25 if tik else 1.1
    while s > 0.55:
        h = inhalt(probe, pd, k, W, x0, x1, 0, s, False)
        if h <= platz: break
        s -= 0.05
    if h > platz:  # Zeilen kürzen, bis es passt
        k = dict(k); zz = list(k.get('zeilen', []))
        while zz and inhalt(probe, pd, dict(k, zeilen=zz), W, x0, x1, 0, s, False) > platz: zz = zz[:-1]
        k['zeilen'] = zz; h = inhalt(probe, pd, k, W, x0, x1, 0, s, False)
    inhalt(img, d, k, W, x0, x1, top + 40 + max(0, (platz - h) // 2), s)
    d.text((W // 2, ky1 - 56), ('Quelle: ' + str(k.get('quelle', 'BDKNG')))[:80], font=F(MED, 24), fill='#9A9A9A', anchor='ma')
    # Werbung unten: Homepage + Kanäle
    fy = ky1 + (50 if tik else 34)
    d.text((W // 2, fy), 'bdkng.de', font=F(BLACK, 72 if tik else 64), fill='#FFFFFF', anchor='ma')
    sz = 96 if tik else 76; gap = 26; tw = len(ICONS) * sz + (len(ICONS) - 1) * gap; x = (W - tw) // 2; iy = fy + (112 if tik else 92)
    for n, _ in ICONS:
        ic = Image.open(os.path.join(BASE, 'assets', 'social', 'icons', n + '.png')).convert('RGBA').resize((sz, sz), Image.LANCZOS)
        img.alpha_composite(ic, (x, iy)); x += sz + gap
    d.text((W // 2, iy + sz + 16), 'WhatsApp-Kanal · Facebook · Instagram · TikTok: BDKNG', font=F(BOLD, 30 if tik else 26), fill='#FFFFFF', anchor='ma')
    img.convert('RGB').save(ziel, quality=90)

if __name__ == '__main__':
    import json, sys
    for p in sys.argv[1:]:
        k = json.load(open(p, encoding='utf-8')); b = os.path.splitext(os.path.basename(p))[0]
        karte(k, 1080, 1350, '/tmp/' + b + '-ig.jpg'); karte(k, 1080, 1920, '/tmp/' + b + '-ig-9x16.jpg'); print(b)
