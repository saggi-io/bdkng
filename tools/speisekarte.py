#!/usr/bin/env python3
"""Erzeugt speisekarte-kebab.html aus data/speisekarte-kebab.json (Kopf/Fuß von genuss.html)."""
import json, re, html
from pathlib import Path

R = Path(__file__).resolve().parent.parent
d = json.loads((R / 'data/speisekarte-kebab.json').read_text())
g = (R / 'genuss.html').read_text()
e = lambda s: html.escape(str(s), quote=True)

URL = 'https://bdkng.de/speisekarte-kebab.html'
TITEL = 'Speisekarte Kebab & Pizzahaus Bad König | BDKNG'
DESC = 'Speisekarte vom Kebab & Pizzahaus Bad König: Döner, Dürüm, Pizza, Pide, Lahmacun, Falafel, Salate und Getränke mit Preisen, Öffnungszeiten und Lieferservice.'

kopf = g.split('<main', 1)[0]
fuss = '<footer' + g.split('<footer', 1)[1]
kopf = re.sub(r'<title>.*?</title>', '<title>' + e(TITEL) + '</title>', kopf)
kopf = re.sub(r'(<meta name="description" content=")[^"]*', r'\g<1>' + e(DESC), kopf)
kopf = re.sub(r'(<meta property="og:description" content=")[^"]*', r'\g<1>' + e(DESC), kopf)
kopf = re.sub(r'(<meta property="og:title" content=")[^"]*', r'\g<1>' + e(TITEL), kopf)
kopf = kopf.replace('https://bdkng.de/genuss.html"', URL + '"')
kopf = re.sub(r'<script type="application/ld\+json">.*?</script>', '<script type="application/ld+json">' + json.dumps({
    "@context": "https://schema.org", "@type": "Restaurant", "name": d['name'], "servesCuisine": ["Türkisch", "Döner", "Pizza"],
    "address": {"@type": "PostalAddress", "streetAddress": "Bahnhofstraße 5", "postalCode": "64732", "addressLocality": "Bad König", "addressCountry": "DE"},
    "telephone": "+496063913533", "hasMenu": URL, "openingHours": ["Tu-Sa 11:00-22:00", "Su 12:00-22:00"]}, ensure_ascii=False) + '</script>', kopf, flags=re.S)
kopf = kopf.replace(' aria-current="page"', '').replace('</head>', '<script src="/assets/bdkng-speisekarte.js?v=20261120a" defer></script><style>' + (R / 'tools/speisekarte.css').read_text() + '</style></head>')

tel = d['telefon'].replace(' ', '')
h = ['<main class="wrap subpage sk"><p class="eyebrow"><a href="/genuss.html#wirtschaften">Genuss &amp; Gewerbe</a> / Speisekarte</p>',
     '<section class="sk-hero"><p class="sk-kicker">🥙 Speisekarte</p><h1>' + e(d['name']) + '</h1><p class="sk-sub">' + e(d['untertitel']) + '</p>',
     '<div class="sk-aktion">🔥 ' + e(d['aktion'].replace('Aktion: ', '')) + '</div>',
     '<div class="sk-knoepfe"><a class="btn sk-tel" href="tel:+49' + tel[1:] + '">📞 Bestellen: ' + e(d['telefon']) + '</a><a class="btn sk-sek" href="#karte">🖼️ Original-Karte</a><a class="btn sk-sek" href="https://www.google.com/maps/search/?api=1&amp;query=' + 'Kebab%20%26%20Pizzahaus%20Bahnhofstra%C3%9Fe%205%20Bad%20K%C3%B6nig" target="_blank" rel="noopener">📍 Bahnhofstraße 5</a></div>',
     '<ul class="sk-info"><li>🕘 ' + e(d['zeiten']) + '</li><li>🛵 ' + e(d['liefer']) + '</li></ul></section>',
     '<section class="subpanel sk-such"><label class="sk-filter"><span aria-hidden="true">🔍</span><input type="search" id="skFilter" placeholder="Was hast du Hunger drauf? z. B. Dürüm, Hawaii, vegetarisch" aria-label="Speisekarte durchsuchen" autocomplete="off"></label>',
     '<div class="sk-sprung" role="navigation" aria-label="Kategorien">' + ''.join('<a href="#k' + str(i) + '">' + e(gr['titel']) + '</a>' for i, gr in enumerate(d['gruppen'])) + '</div></section>']
for i, gr in enumerate(d['gruppen']):
    sp = gr['spalten']
    h.append('<section class="subpanel sk-gruppe" id="k' + str(i) + '"><h2>' + e(gr['titel']) + '</h2>' + ('<p class="sk-hin">' + e(gr['hinweis']) + '</p>' if gr.get('hinweis') else ''))
    if len(sp) > 1:
        h.append('<p class="sk-spalten">' + ' · '.join(e(x) for x in sp) + '</p>')
    h.append('<ul class="sk-liste">')
    for z in gr['liste']:
        nr, name, zus, preise = z[0], z[1], z[2], [p for p in z[3:] if p]
        neu = name.startswith('NEU ')
        name = name[4:] if neu else name
        pr = ''.join('<span class="sk-p">' + ('<small>' + e(sp[k]) + '</small> ' if len(sp) > 1 and len(preise) > 1 else '') + e(p) + ' €</span>' for k, p in enumerate(preise))
        h.append('<li><span class="sk-nr">' + e(nr) + '</span><div class="sk-t"><b>' + e(name) + (' <em class="sk-neu">NEU</em>' if neu else '') + '</b>' + ('<span>' + e(zus) + '</span>' if zus else '') + '</div><div class="sk-pr">' + pr + '</div></li>')
    h.append('</ul><a class="nach-oben" href="#" aria-label="Nach oben">↑ nach oben</a></section>')
h.append('<p class="sk-leer" id="skLeer" hidden>Dazu steht nichts auf der Karte. Probier ein anderes Wort – oder ruf kurz an.</p>')
h.append('<section class="subpanel sk-bild" id="karte"><h2>🖼️ Original-Speisekarte</h2><p class="form-note">Tippe auf die Karte zum Vergrößern – mit Zusatzstoffen und Allergenen.</p>'
         '<button type="button" class="sk-zoom" aria-label="Speisekarte vergrößern"><img src="/assets/speisekarte/kebab-pizzahaus-bad-koenig.webp" alt="Speisekarte Kebab &amp; Pizzahaus Bad König mit Drehspieß, Pizza, Lahmacun, Pide, Falafel, Salaten, Snacks und Getränken" width="1600" height="1646" loading="lazy"></button>'
         '<p><a class="btn sk-sek" href="/assets/speisekarte/kebab-pizzahaus-bad-koenig.jpg" download>⬇️ Speisekarte speichern</a></p></section>')
h.append('<p class="editorial-note">' + e(d['stand']) + ' ' + e(d['hinweis']) + ' Fehler entdeckt? <a href="/kontakt.html?thema=hinweis">Sag’s uns</a>. <br>Betreibst du ein Lokal in Bad König und willst deine Karte auch hier? <a href="/kontakt.html?thema=sonstiges">Melde dich</a>.</p></main>')
(R / 'speisekarte-kebab.html').write_text(kopf + ''.join(h) + fuss)
print('ok', len(kopf + ''.join(h) + fuss))
