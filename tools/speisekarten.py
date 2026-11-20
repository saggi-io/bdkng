#!/usr/bin/env python3
"""Speisekarten aller Wirtschaften rendern (idempotent).

Quelle: data/speisekarten/<slug>.json  (kommt per Mail über n8n oder von Hand)
Erzeugt:
  speisekarte-<slug>.html          eigene Seite je Wirtschaft (Karte, Mittagstisch, Bilder/PDF)
  data/speisekarten/index.json     Kurzliste für die KI-Suche (Mittagstisch, Links)
  data/speisekarte-kebab.json      Kopie für die bestehenden Such-Buttons
  genuss.html                      Knopf „Speisekarte ansehen“ beim passenden Eintrag
  data/wissen-badkoenig.json       je Wirtschaft ein Eintrag „Speisekarte …“ (KI-Wissen)
"""
import json, re, html, datetime
from pathlib import Path

R = Path(__file__).resolve().parent.parent
e = lambda s: html.escape(str(s), quote=True)
HEUTE = datetime.date.today().isoformat()
CSS = (R / 'tools/speisekarte.css').read_text()


def de(iso):
    try: return datetime.date.fromisoformat(iso).strftime('%d.%m.%Y')
    except Exception: return iso or ''


def mittag_gueltig(m):
    return bool(m) and (not m.get('gueltig_bis') or m['gueltig_bis'] >= HEUTE)


def kopf_fuss(titel, desc, url):
    g = (R / 'genuss.html').read_text()
    kopf = g.split('<main', 1)[0]
    fuss = '<footer' + g.split('<footer', 1)[1]
    kopf = re.sub(r'<title>.*?</title>', '<title>' + e(titel) + '</title>', kopf)
    for k in ('name="description"', 'property="og:description"'):
        kopf = re.sub(r'(<meta ' + k + r' content=")[^"]*', lambda m: m.group(1) + e(desc), kopf)
    kopf = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + e(titel), kopf)
    kopf = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, kopf)
    kopf = re.sub(r'(<meta property="og:url" content=")[^"]*', lambda m: m.group(1) + url, kopf)
    kopf = re.sub(r'<style>\.wi-karte[^<]*</style>', '', kopf)
    kopf = kopf.replace(' aria-current="page"', '').replace('</head>', '<script src="/assets/bdkng-speisekarte.js?v=20261120a" defer></script><style>' + CSS + '</style></head>', 1)
    return kopf, fuss


def liste_html(gr):
    sp = gr.get('spalten') or ['Preis']
    h = ['<ul class="sk-liste">']
    for z in gr.get('liste', []):
        z = list(z) + ['', '', '', '']
        nr, name, zus, preise = z[0], z[1], z[2], [p for p in z[3:5] if p]
        neu = str(name).startswith('NEU ')
        name = name[4:] if neu else name
        pr = ''.join('<span class="sk-p">' + ('<small>' + e(sp[k]) + '</small> ' if len(sp) > 1 and len(preise) > 1 and k < len(sp) else '') + e(p) + (' €' if re.search(r'\d$', str(p)) else '') + '</span>' for k, p in enumerate(preise))
        h.append('<li><span class="sk-nr">' + e(nr) + '</span><div class="sk-t"><b>' + e(name) + (' <em class="sk-neu">NEU</em>' if neu else '') + '</b>' + ('<span>' + e(zus) + '</span>' if zus else '') + '</div><div class="sk-pr">' + pr + '</div></li>')
    h.append('</ul>')
    return ''.join(h)


def seite(slug, d):
    url = 'https://bdkng.de/speisekarte-' + slug + '.html'
    titel = 'Speisekarte ' + d['name'] + ' | BDKNG'
    desc = ('Speisekarte vom ' + d['name'] + (': ' + d['untertitel'] if d.get('untertitel') else '') + ' – mit Preisen, Öffnungszeiten' + (' und Mittagstisch' if d.get('mittagstisch') else '') + '.')[:300]
    kopf, fuss = kopf_fuss(titel, desc, url)
    em = d.get('emoji', '🍽️')
    tel = re.sub(r'[^\d+]', '', d.get('telefon', ''))
    telhref = ('tel:+49' + tel[1:]) if tel.startswith('0') else ('tel:' + tel)
    maps = 'https://www.google.com/maps/search/?api=1&amp;query=' + re.sub(r'\s+', '%20', e(d['name'] + ' ' + d.get('adresse', 'Bad König')))
    h = ['<main class="wrap subpage sk"><p class="eyebrow"><a href="/genuss.html#wirtschaften">Genuss &amp; Gewerbe</a> / Speisekarte</p>',
         '<section class="sk-hero"><p class="sk-kicker">' + em + ' Speisekarte</p><h1>' + e(d['name']) + '</h1>' + ('<p class="sk-sub">' + e(d['untertitel']) + '</p>' if d.get('untertitel') else '')]
    if d.get('aktion'): h.append('<div class="sk-aktion">🔥 ' + e(re.sub(r'^Aktion:\s*', '', d['aktion'])) + '</div>')
    h.append('<div class="sk-knoepfe">' + ('<a class="btn sk-tel" href="' + telhref + '">📞 ' + ('Bestellen: ' if d.get('liefer') else 'Anrufen: ') + e(d['telefon']) + '</a>' if tel else '')
             + ('<a class="btn sk-sek" href="#mittag">🍲 Mittagstisch</a>' if mittag_gueltig(d.get('mittagstisch')) else '')
             + ('<a class="btn sk-sek" href="#karte">🖼️ Original-Karte</a>' if d.get('bilder') or d.get('pdf') else '')
             + ('<a class="btn sk-sek" href="' + maps + '" target="_blank" rel="noopener">📍 ' + e(d['adresse'].split(',')[0]) + '</a>' if d.get('adresse') else '') + '</div>')
    info = [x for x in [('🕘 ' + d['zeiten']) if d.get('zeiten') else '', ('🛵 ' + d['liefer']) if d.get('liefer') else '', ('🚫 ' + d['ruhetage']) if d.get('ruhetage') else ''] if x]
    if info: h.append('<ul class="sk-info">' + ''.join('<li>' + e(x) + '</li>' for x in info) + '</ul>')
    h.append('</section>')
    m = d.get('mittagstisch')
    if mittag_gueltig(m):
        zeit = ('vom ' + de(m['gueltig_von']) + ' ' if m.get('gueltig_von') else '') + ('bis ' + de(m['gueltig_bis']) if m.get('gueltig_bis') else '')
        h.append('<section class="subpanel sk-gruppe sk-mittag" id="mittag"><h2>🍲 ' + e(m.get('titel') or 'Mittagstisch') + '</h2>' + ('<p class="sk-hin">Gültig ' + e(zeit.strip()) + '</p>' if zeit.strip() else ''))
        for t in m.get('tage', []):
            h.append('<h3 class="sk-tag">' + e(t.get('tag', '')) + '</h3>' + liste_html({'liste': t.get('gerichte', [])}))
        if m.get('text'): h.append('<p>' + e(m['text']) + '</p>')
        h.append('</section>')
    gruppen = d.get('gruppen') or []
    if gruppen:
        h.append('<section class="subpanel sk-such"><label class="sk-filter"><span aria-hidden="true">🔍</span><input type="search" id="skFilter" placeholder="Was hast du Hunger drauf?" aria-label="Speisekarte durchsuchen" autocomplete="off"></label>'
                 '<div class="sk-sprung" role="navigation" aria-label="Kategorien">' + ''.join('<a href="#k' + str(i) + '">' + e(gr['titel']) + '</a>' for i, gr in enumerate(gruppen)) + '</div></section>')
        for i, gr in enumerate(gruppen):
            sp = gr.get('spalten') or ['Preis']
            h.append('<section class="subpanel sk-gruppe" id="k' + str(i) + '"><h2>' + e(gr['titel']) + '</h2>' + ('<p class="sk-hin">' + e(gr['hinweis']) + '</p>' if gr.get('hinweis') else '')
                     + ('<p class="sk-spalten">' + ' · '.join(e(x) for x in sp) + '</p>' if len(sp) > 1 else '') + liste_html(gr) + '<a class="nach-oben" href="#" aria-label="Nach oben">↑ nach oben</a></section>')
        h.append('<p class="sk-leer" id="skLeer" hidden>Dazu steht nichts auf der Karte. Probier ein anderes Wort – oder ruf kurz an.</p>')
    if d.get('bilder') or d.get('pdf'):
        h.append('<section class="subpanel sk-bild" id="karte"><h2>🖼️ Original-Speisekarte</h2><p class="form-note">Tippe auf die Karte zum Vergrößern.</p>')
        for b in d.get('bilder', []):
            h.append('<button type="button" class="sk-zoom" aria-label="Speisekarte vergrößern"><img src="' + e(b) + '" alt="Speisekarte ' + e(d['name']) + '" loading="lazy"></button>')
        for p in d.get('pdf', []):
            h.append('<p><a class="btn sk-sek" href="' + e(p) + '" target="_blank" rel="noopener">📄 Speisekarte als PDF öffnen</a></p>')
        if d.get('download'): h.append('<p><a class="btn sk-sek" href="' + e(d['download']) + '" download>⬇️ Speisekarte speichern</a></p>')
        h.append('</section>')
    h.append('<p class="editorial-note">' + e(d.get('stand', '')) + ' ' + e(d.get('hinweis', '')) + ' Angaben ohne Gewähr. Fehler entdeckt? <a href="/kontakt.html?thema=hinweis">Sag’s uns</a>.<br>Betreibst du ein Lokal in Bad König und willst deine Karte oder deinen Mittagstisch auch hier? Schick sie einfach an <a href="mailto:info@bdkng.de">info@bdkng.de</a>.</p></main>')
    (R / ('speisekarte-' + slug + '.html')).write_text(kopf + ''.join(h) + fuss)


def wissen_text(d):
    t = [d['name'] + (', ' + d['adresse'] if d.get('adresse') else '') + (', Telefon ' + d['telefon'] if d.get('telefon') else '') + '.']
    for k in ('zeiten', 'ruhetage', 'liefer', 'aktion', 'hinweis'):
        if d.get(k): t.append(('Öffnungszeiten: ' if k == 'zeiten' else 'Ruhetage: ' if k == 'ruhetage' else '') + d[k].rstrip('.') + '.')
    m = d.get('mittagstisch')
    if mittag_gueltig(m):
        z = [(x.get('tag', '') + ': ' + '; '.join(' '.join(str(y) for y in g[1:2]) + (' (' + g[2] + ')' if len(g) > 2 and g[2] else '') + (' ' + g[3] + ' €' if len(g) > 3 and g[3] else '') for g in x.get('gerichte', []))) for x in m.get('tage', [])]
        t.append((m.get('titel') or 'Mittagstisch') + (' (gültig bis ' + de(m['gueltig_bis']) + ')' if m.get('gueltig_bis') else '') + ': ' + ' | '.join(z) + ((' ' + m['text']) if m.get('text') else '') + '.')
    for g in d.get('gruppen') or []:
        sp = g.get('spalten') or ['Preis']; it = []
        for z in g.get('liste', []):
            z = list(z) + ['', '', '', '']; p = [x for x in z[3:5] if x]
            it.append(('Nr. ' + z[0] + ' ' if z[0] else '') + str(z[1]).replace('NEU ', 'neu: ') + (' (' + z[2] + ')' if z[2] else '') + ': ' + ' / '.join(str(x) + ' €' + (' (' + sp[i] + ')' if len(sp) > 1 and len(p) > 1 and i < len(sp) else '') for i, x in enumerate(p)))
        t.append(re.sub(r'^\W+\s*', '', g['titel']) + (' (' + g['hinweis'] + ')' if g.get('hinweis') else '') + ': ' + '; '.join(it) + '.')
    if d.get('stand'): t.append(d['stand'])
    return ' '.join(t)


def uebersicht(karten):
    """speisekarten.html: alle Wirtschaften (aus genuss.html), Speisekarten und Mittagstische auf einen Blick."""
    url = 'https://bdkng.de/speisekarten.html'
    titel = 'Speisekarten in Bad König – Restaurants, Mittagstisch & Preise | BDKNG'
    desc = 'Alle Speisekarten in Bad König auf einen Blick: Restaurants, Döner, Pizza, Cafés und Biergärten mit Preisen, Mittagstisch und Öffnungszeiten – kostenlos auf BDKNG.'
    kopf, fuss = kopf_fuss(titel, desc, url)
    g = (R / 'genuss.html').read_text()
    nach_name = {e(d.get('genuss_name') or d['name']): (slug, d) for slug, d in karten.items()}
    h = ['<main class="wrap subpage sk"><p class="eyebrow"><a href="/genuss.html">Genuss &amp; Gewerbe</a> / Speisekarten</p>',
         '<section class="sk-hero"><p class="sk-kicker">🍽️ Essen gehen in Bad König</p><h1>Speisekarten in Bad König</h1><p class="sk-sub">Was gibt’s wo – mit Preisen, Mittagstisch und Öffnungszeiten. Tippe auf eine Wirtschaft.</p></section>']
    mittag = [(slug, d) for slug, d in karten.items() if mittag_gueltig(d.get('mittagstisch'))]
    h.append('<section class="subpanel sk-gruppe sk-mittag" id="mittag"><h2>🍲 Mittagstisch diese Woche</h2>')
    if mittag:
        h.append('<ul class="sk-liste">' + ''.join('<li><span class="sk-nr">' + d.get('emoji', '🍲') + '</span><div class="sk-t"><b><a href="/speisekarte-' + slug + '.html#mittag">' + e(d['name']) + '</a></b><span>' + e((d['mittagstisch'].get('titel') or 'Mittagstisch') + (' · bis ' + de(d['mittagstisch']['gueltig_bis']) if d['mittagstisch'].get('gueltig_bis') else '')) + '</span></div><div class="sk-pr"></div></li>' for slug, d in mittag) + '</ul>')
    else:
        h.append('<p>Gerade hat uns noch keine Wirtschaft einen aktuellen Mittagstisch geschickt.</p>')
    h.append('</section>')
    h.append('<section class="subpanel sk-gruppe"><h2>📋 Mit Speisekarte auf BDKNG</h2><div class="sk-kacheln">' + ''.join(
        '<a class="sk-kachel" href="/speisekarte-' + slug + '.html"><span class="sk-k-em">' + d.get('emoji', '🍽️') + '</span><b>' + e(d['name']) + '</b><small>' + e(d.get('untertitel', '')) + '</small></a>' for slug, d in karten.items()) + '</div></section>')
    for gm in re.finditer(r'<div class="wi-gruppe"><h3>(.*?)</h3><ul>(.*?)</ul></div>', g, re.S):
        items = re.findall(r'<li><a href="([^"]*)"[^>]*><b>(.*?)</b></a><span>(.*?)</span>', gm.group(2))
        if not items: continue
        h.append('<section class="subpanel sk-gruppe"><h2>' + gm.group(1) + '</h2><ul class="sk-liste">')
        for href, nm, info in items:
            k = nach_name.get(nm)
            knopf = ('<a class="wi-karte" href="/speisekarte-' + k[0] + '.html">' + k[1].get('emoji', '🍽️') + ' Speisekarte</a>') if k else '<small class="sk-fehlt">Karte folgt</small>'
            h.append('<li><span class="sk-nr">📍</span><div class="sk-t"><b><a href="' + href + '" target="_blank" rel="noopener">' + nm + '</a></b><span>' + info + '</span></div><div class="sk-pr">' + knopf + '</div></li>')
        h.append('</ul></section>')
    h.append('<p class="editorial-note">Du betreibst eine Wirtschaft in Bad König? Schick deine Speisekarte oder deinen Mittagstisch als JPG oder PDF an <a href="mailto:info@bdkng.de">info@bdkng.de</a> – kurz darauf ist sie hier online und die BDKNG KI kennt sie. Kostenlos. Angaben ohne Gewähr.</p></main>')
    kopf = kopf.replace('</head>', '<style>.sk-kacheln{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}.sk-kachel{display:flex;flex-direction:column;gap:2px;padding:14px;border-radius:16px;background:#141414;color:#fff!important;text-decoration:none}.sk-kachel:hover{background:#2a1d10}.sk-k-em{font-size:1.8rem}.sk-kachel small{color:#d4d4d4}.sk-fehlt{color:#999}.wi-karte{display:inline-block;background:#141414;color:#fff!important;border-radius:999px;padding:6px 12px;font-weight:700;font-size:.85rem;text-decoration:none;white-space:nowrap}</style></head>', 1)
    (R / 'speisekarten.html').write_text(kopf + ''.join(h) + fuss)


def main():
    karten = {}
    for f in sorted((R / 'data/speisekarten').glob('*.json')):
        if f.name == 'index.json': continue
        karten[f.stem] = json.loads(f.read_text())
    idx = []
    for slug, d in karten.items():
        seite(slug, d)
        m = d.get('mittagstisch')
        idx.append({'slug': slug, 'name': d['name'], 'url': '/speisekarte-' + slug + '.html', 'emoji': d.get('emoji', '🍽️'), 'telefon': d.get('telefon', ''),
                    'mittagstisch': m if mittag_gueltig(m) else None, 'stand': d.get('stand', '')})
    uebersicht(karten)
    (R / 'data/speisekarten/index.json').write_text(json.dumps({'stand': HEUTE, 'karten': idx}, ensure_ascii=False, indent=1))
    if 'kebab' in karten:  # bestehende Such-Buttons
        (R / 'data/speisekarte-kebab.json').write_text(json.dumps(karten['kebab'], ensure_ascii=False, indent=2))
    # Genuss: Knopf beim passenden Eintrag
    g = (R / 'genuss.html').read_text()
    g = re.sub(r'<a class="wi-karte" href="[^"]*">[^<]*</a>', '', g)
    for slug, d in karten.items():
        nm = e(d.get('genuss_name') or d['name'])
        pat = re.compile(r'(<b>' + re.escape(nm) + r'</b></a><span>[^<]*</span>)')
        g, n = pat.subn(lambda m: m.group(1) + '<a class="wi-karte" href="/speisekarte-' + slug + '.html">' + d.get('emoji', '🍽️') + ' Speisekarte' + (' & Mittagstisch' if mittag_gueltig(d.get('mittagstisch')) else ' ansehen') + '</a>', g, count=1)
        if not n: print('Hinweis: kein Genuss-Eintrag gefunden für', d['name'])
    if '.wi-karte{' not in g:
        g = g.replace('</head>', '<style>.wi-karte{display:inline-block;margin:6px 0 2px;background:#141414;color:#fff!important;border-radius:999px;padding:6px 12px;font-weight:700;font-size:.88rem;text-decoration:none}.wi-karte:hover{background:#b45309}</style></head>', 1)
    (R / 'genuss.html').write_text(g)
    # KI-Wissen
    wp = R / 'data/wissen-badkoenig.json'; w = json.loads(wp.read_text())
    w['eintraege'] = [x for x in w['eintraege'] if not x.get('titel', '').startswith('Speisekarte ')]
    for slug, d in karten.items():
        w['eintraege'].append({'titel': 'Speisekarte ' + d['name'] + (' mit Mittagstisch' if mittag_gueltig(d.get('mittagstisch')) else '') + ' (Gerichte, Preise, Öffnungszeiten)',
                               'text': wissen_text(d), 'url': 'https://bdkng.de/speisekarte-' + slug + '.html', 'fest': True})
    wp.write_text(json.dumps(w, ensure_ascii=False, indent=1))
    print('Speisekarten:', ', '.join(karten))


if __name__ == '__main__':
    main()
