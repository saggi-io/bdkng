"""BDKNG Social-Karten, Stil 2 (Liste mit Rubrik-Kacheln).
Eingabe (data/karten/<id>.json):
  {"rubrik": "aktuell", "titel": "BDKNG News am Morgen", "quelle": "BDKNG",
   "art": "liste" | "text",
   "ueber": "Mi. 18.11. · 07:30 Uhr" (optional),
   "zeilen": ["Text", {"t": "Text", "r": "verkehr", "k": "Verkehr · B45"}, {"t": "Text", "e": "🌧️"}, ...]}
Ausgabe: <id>.jpg (4:5, Feed Facebook/Instagram) und <id>-9x16.jpg (Story/Status)."""
import os
from PIL import Image, ImageDraw, ImageFont
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(BASE, 'tools', 'fonts')
EMOJI_FONTS = [os.path.join(FD, 'NotoColorEmoji.ttf'), '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf']
def f(n, s): return ImageFont.truetype(os.path.join(FD, n), s)
GRUEN = (27, 77, 46); GRUEN_D = (20, 64, 37); HELL = (226, 239, 214); LINIE = (176, 210, 150)
CREME = (250, 248, 242); WEISS = (255, 255, 255); TEXT = (28, 33, 30)
RUBRIK = {
  'aktuell': ('AKTUELLES', 'bdkng-news.webp'), 'verkehr': ('VERKEHR', 'bdkng-verkehr.webp'),
  'bahn': ('BAHN', 'bdkng-verkehr.webp'), 'termine': ('TERMINE', 'bdkng-termine.webp'),
  'sport': ('SPORT', 'bdkng-sport.webp'), 'wetter': ('WETTER', 'bdkng-wetter.webp'),
  'muell': ('MÜLLABFUHR', 'bdkng-muell.webp'), 'polizei': ('POLIZEI', 'bdkng-wichtig.webp'),
  'wichtig': ('WICHTIG', 'bdkng-wichtig.webp'), 'genuss': ('GENUSS & GEWERBE', 'bdkng-genuss.webp')}

def wrap(d, text, font, maxw):
    out, line = [], ''
    for w in str(text).split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=font) <= maxw: line = t
        else:
            if line: out.append(line)
            line = w
    if line: out.append(line)
    return out
def maske(size, r):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=255); return m
def quadrat(datei, s):
    ic = Image.open(os.path.join(BASE, 'assets', datei)).convert('RGB')
    m = min(ic.width, ic.height); x, y = (ic.width - m) // 2, (ic.height - m) // 2
    return ic.crop((x, y, x + m, y + m)).resize((s, s), Image.LANCZOS)
def emoji(ch, s):
    for p in EMOJI_FONTS:
        if os.path.exists(p):
            fe = ImageFont.truetype(p, 109); im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((80, 80), ch, font=fe, embedded_color=True, anchor='mm')
            bb = im.getbbox()
            if bb: im = im.crop(bb)
            im.thumbnail((s, s), Image.LANCZOS); return im
    return None
def zeile(z, rub):
    if isinstance(z, dict): return str(z.get('t', '')), z.get('r') or rub, z.get('e'), str(z.get('k') or '')
    return str(z), rub, None, ''
GOLD = (176, 128, 30)

def plan(k, W, H, top):
    """Größte Schrift suchen, bei der alles draufpasst (Untergrenze bleibt gut lesbar)."""
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    hoch = H > 1500; FUSS = 330 if hoch else 132
    liste = k.get('art', 'liste') == 'liste'
    zl = [zeile(z, k.get('rubrik', 'aktuell')) for z in k.get('zeilen', [])][:8]
    TS = [88, 80, 72, 66, 60, 56] if hoch else [74, 68, 62, 58, 54, 50]
    GS = [50, 46, 43, 40, 37, 34] if hoch else [44, 41, 38, 36, 34, 32]
    for ts in TS:
        for gs in GS:
            ft = f('InterDisplay-Black.otf', ts); tl = wrap(d, k.get('titel', ''), ft, W - 100)[:3]
            fz = f('Inter-Bold.otf' if liste else 'Inter-Medium.otf', gs); zh = int(gs * 1.22)
            kach = int(gs * 2.9) if liste else 0
            tx = 60 + (kach + 44 if liste else 0)
            rows = []; kh = int(gs * 0.62) + 8
            for t, r, e, kk in zl:
                ls = wrap(d, t, fz, W - tx - 60)[:4 if liste else 14]
                rows.append((ls, r, e, max(kach, len(ls) * zh + (kh if kk else 0)) + (34 if liste else 18), kk))
            y = top + 40 + (int(ts * 0.5) + 14 if k.get('ueber') else 0) + len(tl) * int(ts * 1.08) + 26
            if y + sum(r[3] for r in rows) <= H - FUSS - 24:
                return dict(ts=ts, gs=gs, tl=tl, rows=rows, zh=zh, kach=kach, tx=tx, fuss=FUSS, liste=liste, voll=True)
    # passt nicht: Mindestgrößen, überzählige Einträge weglassen
    rest = []; y = top + 40 + (int(ts * 0.5) + 14 if k.get('ueber') else 0) + len(tl) * int(ts * 1.08) + 26
    for r in rows:
        if y + r[3] > H - FUSS - 90: break
        rest.append(r); y += r[3]
    return dict(ts=ts, gs=gs, tl=tl, rows=rest, zh=zh, kach=kach, tx=tx, fuss=FUSS, liste=liste, voll=False)

def karte(k, W, H, ziel):
    rub = k.get('rubrik', 'aktuell'); name, bild = RUBRIK.get(rub, RUBRIK['aktuell'])
    hoch = H > 1500; TOP = 470 if hoch else 330
    p = plan(k, W, H, TOP)
    im = Image.new('RGB', (W, H), CREME); d = ImageDraw.Draw(im)
    # Kopfbild (Bad König) mit grüner Welle
    hd = Image.open(os.path.join(BASE, 'assets', 'bdkng-header-jens.png')).convert('RGB')
    q = hd.crop((1150, 40, 2172, 704)); r = max(W / q.width, (TOP + 40) / q.height)
    q = q.resize((int(q.width * r) + 1, int(q.height * r) + 1), Image.LANCZOS)
    x0 = (q.width - W) // 2; y0 = max(0, (q.height - TOP - 40) // 3); im.paste(q.crop((x0, y0, x0 + W, y0 + TOP + 40)), (0, 0))
    welle = [(0, TOP - 4)] + [(x, TOP - 18 + int(22 * ((x / W) - 0.5) ** 2 * 4) - int(14 * (x / W))) for x in range(0, W + 1, 20)] + [(W, TOP + 60), (0, TOP + 60)]
    d.polygon([(x, y - 10) for x, y in welle], fill=(140, 190, 90)); d.polygon(welle, fill=CREME)
    # Rubrikbild links, Logo rechts, Rubrik-Etikett
    S = 300 if hoch else 250; ic = quadrat(bild, S); px, py = 50, 40 if not hoch else 70
    d.rounded_rectangle([px - 10, py - 10, px + S + 10, py + S + 10], 34, fill=WEISS); im.paste(ic, (px, py), maske(ic.size, 26))
    lg = Image.open(os.path.join(BASE, 'assets', 'bdkng-logo-jens.png')).convert('RGBA'); lg.thumbnail((190, 120) if hoch else (170, 105))
    pad = Image.new('RGBA', (lg.width + 34, lg.height + 26), (255, 255, 255, 245)); pad.paste(lg, (17, 13), lg)
    im.paste(pad, (W - pad.width - 40, py), maske(pad.size, 22))
    fb = f('Inter-Bold.otf', 38 if hoch else 34); tw = d.textlength(name, font=fb)
    lx = px + S + 40; ly = py + S - 62
    d.rounded_rectangle([lx, ly, lx + tw + 56, ly + 62], 31, fill=GRUEN); d.text((lx + 28, ly + 31), name, font=fb, fill=WEISS, anchor='lm')
    # Titel
    y = TOP + 40; ft = f('InterDisplay-Black.otf', p['ts'])
    if k.get('ueber'):  # kleine Zeile über der Überschrift (z. B. Datum und Uhrzeit)
        fu = f('Inter-Bold.otf', int(p['ts'] * 0.5)); d.text((52, y), str(k['ueber']).upper()[:60], font=fu, fill=GOLD); y += int(p['ts'] * 0.5) + 14
    for l in p['tl']: d.text((50, y), l, font=ft, fill=GRUEN_D); y += int(p['ts'] * 1.08)
    y += 26
    fz = f('Inter-Bold.otf' if p['liste'] else 'Inter-Medium.otf', p['gs']); K = p['kach']
    fk = f('Inter-Bold.otf', int(p['gs'] * 0.62)); KH = int(p['gs'] * 0.62) + 8
    for i, (ls, r, e, h, kk) in enumerate(p['rows']):
        if p['liste']:
            ky = y + (h - 34 - K) // 2
            d.rounded_rectangle([50, ky, 50 + K, ky + K], 26, fill=HELL)
            if e:
                em = emoji(e, int(K * 0.62))
                if em: im.paste(em, (50 + (K - em.width) // 2, ky + (K - em.height) // 2), em)
            else:
                pic = quadrat(RUBRIK.get(r, RUBRIK['aktuell'])[1], K - 18); im.paste(pic, (59, ky + 9), maske(pic.size, 20))
            bx = 50 + K + 22; d.line([(bx, y + 8), (bx, y + h - 42)], fill=(120, 180, 70), width=4)
            ty = y + (h - 34 - len(ls) * p['zh'] - (KH if kk else 0)) // 2
            if kk: d.text((p['tx'], ty), kk.upper()[:40], font=fk, fill=GOLD); ty += KH  # kleine Zeile über der Überschrift
            for l in ls: d.text((p['tx'], ty), l, font=fz, fill=TEXT); ty += p['zh']
            if i < len(p['rows']) - 1: d.line([(p['tx'], y + h - 17), (W - 50, y + h - 17)], fill=LINIE, width=2)
        else:
            ty = y
            if kk: d.text((54, ty), kk.upper()[:40], font=fk, fill=GOLD); ty += KH
            for l in ls: d.text((54, ty), l, font=fz, fill=TEXT); ty += p['zh']
        y += h
    if not p['voll']: d.text((p['tx'] if p['liste'] else 54, y + 6), '… alles Weitere auf bdkng.de', font=f('Inter-Bold.otf', p['gs']), fill=GRUEN)
    # Fußzeile
    FU = p['fuss']; d.rectangle([0, H - FU, W, H], fill=GRUEN_D)
    fy = H - FU + (70 if hoch else 44)
    f1 = f('Inter-Bold.otf', 36 if hoch else 33); f2 = f('Inter-Medium.otf', 28 if hoch else 25)
    d.text((44, fy), 'bdkng.de · Dein Info-Kanal rund um Bad König', font=f1, fill=WEISS, anchor='lm')
    d.text((44, fy + (56 if hoch else 46)), 'Quelle: ' + str(k.get('quelle', 'BDKNG'))[:70], font=f2, fill=(205, 225, 210), anchor='lm')
    if hoch: d.text((44, fy + 112), 'Wird laufend verbessert und weiterentwickelt.', font=f2, fill=(170, 205, 180), anchor='lm')
    im.save(ziel, quality=82, optimize=True, progressive=True)
