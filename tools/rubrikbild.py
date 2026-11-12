"""Rubrikbilder der Startseite im Stil der Social-Karten: Header-Hintergrund, Rubrikmotiv eckig mit Rahmen, Logo oben rechts."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from karte import BASE, RUBRIK, rund, WEISS
W, H = 1200, 720
def bild(key, ziel):
    name, farbe, motiv = RUBRIK[key]
    hd = Image.open(os.path.join(BASE, 'assets', 'bdkng-header-jens.png')).convert('RGB')
    q = hd.crop((1150, 40, 2172, 704)); r = max(W / q.width, H / q.height)
    q = q.resize((int(q.width * r) + 1, int(q.height * r) + 1)); x0 = (q.width - W) // 2
    im = q.crop((x0, 0, x0 + W, H))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for y in range(H): od.line([(0, y), (W, y)], fill=(0, 0, 0, int(130 * max(0, (y - H * 0.35) / (H * 0.65)))))
    im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
    S = 400; ic = Image.open(os.path.join(BASE, 'assets', motiv)).convert('RGB'); m = min(ic.size)
    ic = ic.crop(((ic.width - m) // 2, (ic.height - m) // 2, (ic.width - m) // 2 + m, (ic.height - m) // 2 + m)).resize((S, S))
    px, py = 60, H - S - 60
    d.rounded_rectangle([px - 12, py - 12, px + S + 12, py + S + 12], 34, fill=WEISS)
    im.paste(ic, (px, py), rund(ic, 24))
    d.rounded_rectangle([px + S + 40, H - 92, px + S + 340, H - 72], 10, fill=farbe)
    lg = Image.open(os.path.join(BASE, 'assets', 'bdkng-logo-jens.png')).convert('RGBA'); lg.thumbnail((170, 100))
    pad = Image.new('RGBA', (lg.width + 28, lg.height + 18), (255, 255, 255, 235)); pad.paste(lg, (14, 9), lg)
    im.paste(pad, (W - pad.width - 40, 40), rund(pad, 16))
    im.save(ziel, 'WEBP', quality=82)
if __name__ == '__main__':
    out = os.path.join(BASE, 'assets', 'rubrik'); os.makedirs(out, exist_ok=True)
    for k in ['aktuell', 'verkehr', 'termine', 'sport', 'wetter', 'muell', 'wichtig', 'genuss']:
        bild(k, os.path.join(out, k + '.webp')); print(k)
