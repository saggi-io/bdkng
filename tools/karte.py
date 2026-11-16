"""BDKNG Social-Karten: data/karten/<id>.json -> assets/social/karten/<id>.png (4:5) und <id>-9x16.png"""
import json, sys, os, glob
from PIL import Image, ImageDraw, ImageFont
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = os.path.join(BASE, 'tools', 'fonts')
def f(n, s): return ImageFont.truetype(os.path.join(FD, n), s)
GRUEN = (27, 77, 46); WEISS = (255, 255, 255); CREME = (247, 243, 234); DUNKEL = (28, 33, 30)
RUBRIK = {
  'aktuell': ('AKTUELLES', GRUEN, 'bdkng-news.webp'), 'verkehr': ('VERKEHR', (214, 120, 30), 'bdkng-verkehr.webp'),
  'bahn': ('BAHN', (214, 120, 30), 'bdkng-verkehr.webp'), 'termine': ('TERMINE', (31, 94, 150), 'bdkng-termine.webp'),
  'sport': ('SPORT', GRUEN, 'bdkng-sport.webp'), 'wetter': ('WETTER', (31, 94, 150), 'bdkng-wetter.webp'),
  'muell': ('MÜLLABFUHR', GRUEN, 'bdkng-muell.webp'), 'polizei': ('POLIZEI', (176, 42, 42), 'bdkng-wichtig.webp'),
  'wichtig': ('WICHTIG', (176, 42, 42), 'bdkng-wichtig.webp'), 'genuss': ('GENUSS & GEWERBE', GRUEN, 'bdkng-genuss.webp')}
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
def rund(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255); return m
def plan(k, W, H):
    """Layout suchen: alles muss lesbar draufpassen. Erst Schrift leicht kleiner, dann Kopfbild flacher,
    dann Schrift bis zur Mindestgröße, zuletzt Titel kleiner. Nur wenn das nicht reicht, wird gekürzt."""
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    hoch = H > 1500; FB = 400 if hoch else 140
    G0, GMIN = (46, 38) if hoch else (38, 30)      # Fließtext: Start- und Mindestgröße
    T0, TMIN = (76, 60) if hoch else (62, 50)      # Titel
    zl = [str(z) for z in k.get('zeilen', [])][:12]
    def mess(top, tg, gr):
        ft = f('InterDisplay-Black.otf', tg); tl = wrap(d, k.get('titel', ''), ft, W - 110)[:4]
        fz = f('Inter-Medium.otf', gr); zh = int(gr * 1.32); ab = max(6, gr // 4)
        lay = [wrap(d, z, fz, W - 108) for z in zl]
        y = int(H * top) + 44 + len(tl) * int(tg * 1.19) + 16
        return y + sum(len(x) * zh + ab for x in lay), (top, tg, gr, tl, lay, zh, ab)
    grenze = H - FB - 30
    versuche = [(0.46, T0, g) for g in range(G0, G0 - 5, -2)]
    versuche += [(t / 100, T0, G0 - 4) for t in range(42, 27, -4)]
    versuche += [(0.30, T0, g) for g in range(G0 - 6, GMIN - 1, -2)]
    versuche += [(0.30, t, GMIN) for t in range(T0 - 6, TMIN - 1, -6)]
    for v in versuche:
        ende, lay = mess(*v)
        if ende <= grenze: return lay, grenze, False
    return lay, grenze, True
def karte(k, W, H, ziel):
    name, farbe, bild = RUBRIK.get(k.get('rubrik', 'aktuell'), RUBRIK['aktuell'])
    (top, tg, gr, tl, lay, zh, ab), grenze, zuviel = plan(k, W, H)
    TOP = int(H * top)
    im = Image.new('RGB', (W, H), CREME)
    hd = Image.open(os.path.join(BASE, 'assets', 'bdkng-header-jens.png')).convert('RGB')
    q = hd.crop((1150, 40, 2172, 704))  # ohne Logo-Reste links
    r = max(W / q.width, TOP / q.height); q = q.resize((int(q.width * r) + 1, int(q.height * r) + 1))
    x0 = (q.width - W) // 2; y0 = (q.height - TOP) // 2; im.paste(q.crop((x0, y0, x0 + W, y0 + TOP)), (0, 0))
    ov = Image.new('RGBA', (W, TOP), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(TOP): od.line([(0, y), (W, y)], fill=(0, 0, 0, int(120 * max(0, (y - TOP * 0.45) / (TOP * 0.55)))))
    im.paste(ov, (0, 0), ov)
    d = ImageDraw.Draw(im)
    # Rubrikbild links, eckig mit Rahmen (schrumpft mit, wenn das Kopfbild flacher wird)
    S = min(int(W * 0.40), TOP - 90); ic = Image.open(os.path.join(BASE, 'assets', bild)).convert('RGB')
    m = min(ic.width, ic.height); ic = ic.crop(((ic.width - m) // 2, (ic.height - m) // 2, (ic.width - m) // 2 + m, (ic.height - m) // 2 + m)).resize((S, S))
    px, py = 48, TOP - S - 40
    d.rounded_rectangle([px - 10, py - 10, px + S + 10, py + S + 10], 30, fill=WEISS)
    im.paste(ic, (px, py), rund(ic, 22))
    # Logo klein oben rechts
    lg = Image.open(os.path.join(BASE, 'assets', 'bdkng-logo-jens.png')).convert('RGBA'); lg.thumbnail((150, 90))
    pad = Image.new('RGBA', (lg.width + 24, lg.height + 16), (255, 255, 255, 235)); pad.paste(lg, (12, 8), lg)
    im.paste(pad, (W - pad.width - 36, 36), rund(pad, 14))
    # Rubrik-Label rechts unten im Bild
    fb = f('Inter-Bold.otf', 34); tw = d.textlength(name, font=fb)
    lx = px + S + 40; d.rounded_rectangle([lx, TOP - 100, lx + tw + 48, TOP - 40], 14, fill=farbe); d.text((lx + 24, TOP - 92), name, font=fb, fill=WEISS)
    hoch = H > 1500; FB = 400 if hoch else 140  # 9:16: Fußzeile höher (TikTok/Story-Bedienelemente)
    ft = f('InterDisplay-Black.otf', tg); y = TOP + 44
    for l in tl: d.text((54, y), l, font=ft, fill=DUNKEL); y += int(tg * 1.19)
    y += 16; fz = f('Inter-Medium.otf', gr)
    # Passt selbst in der Mindestgröße nicht alles: ganze Zeilen weglassen und klar darauf hinweisen (nie mitten im Wort abschneiden)
    platz = grenze - (zh + ab if zuviel else 0); fertig = False
    for ls in lay:
        if y + len(ls) * zh > platz + 8: fertig = True; break
        for l in ls: d.text((54, y), l, font=fz, fill=(55, 60, 58)); y += zh
        y += ab
    if zuviel and fertig: d.text((54, y), '… alles Weitere auf bdkng.de', font=f('Inter-Bold.otf', gr), fill=GRUEN)
    d.rectangle([0, H - FB, W, H], fill=GRUEN)
    d.text((54, H - FB + 22), 'bdkng.de · Dein Info-Kanal rund um Bad König', font=f('Inter-Bold.otf', 34), fill=WEISS)
    d.text((54, H - FB + 72), ('Quelle: ' + k.get('quelle', 'BDKNG'))[:80], font=f('Inter-Medium.otf', 26), fill=(200, 220, 205))
    im.save(ziel, quality=88)
def main(dateien):
    out = os.path.join(BASE, 'assets', 'social', 'karten'); os.makedirs(out, exist_ok=True)
    for p in dateien:
        k = json.load(open(p, encoding='utf-8')); i = os.path.splitext(os.path.basename(p))[0]
        if os.path.exists(os.path.join(out, i + '.jpg')): continue
        karte(k, 1080, 1350, os.path.join(out, i + '.jpg'))
        karte(k, 1080, 1920, os.path.join(out, i + '-9x16.jpg'))
        print('Karte', i)
if __name__ == '__main__':
    main(sys.argv[1:] or glob.glob(os.path.join(BASE, 'data', 'karten', '*.json')))
