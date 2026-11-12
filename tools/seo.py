"""SEO: Beschreibungen, Open Graph, strukturierte Daten und sitemap.xml (idempotent)."""
import re, json, datetime, html
from pathlib import Path
root = Path(__file__).resolve().parents[1]
BASE = 'https://bdkng.de'
OG = BASE + '/assets/og-bdkng.jpg'
SEITEN = {
 'index.html': ('', 'BDKNG – Bad König kompakt: Nachrichten, Verkehr, Termine, Müllabfuhr, Wetter und Sport aus Bad König im Odenwald. Mit KI-Suche und WhatsApp-Kanal.', 'daily', '1.0'),
 'aktuell.html': ('Aktuelles', 'Aktuelle Nachrichten aus Bad König und den Stadtteilen Zell, Kimbach, Etzen-Gesäß, Momart, Nieder- und Ober-Kinzig – kurz zusammengefasst, mit Quelle.', 'hourly', '0.9'),
 'verkehr.html': ('Verkehr', 'Verkehr in Bad König: Staus, Unfälle, Sperrungen und Baustellen auf der B45, Zeller Brücke und Odenwaldbahn – live und mit Quelle.', 'hourly', '0.9'),
 'termine.html': ('Termine & Veranstaltungen', 'Veranstaltungen und Termine in Bad König: Was ist heute und am Wochenende los? Konzerte, Märkte, Vereinsfeste und mehr.', 'daily', '0.9'),
 'sport.html': ('Sport & Vereine', 'Sport in Bad König: Spielpläne und Ergebnisse von Fußball (SG Bad König/Zell), Handball (HSG Odenwald), Leichtathletik, Tischtennis und Tennis.', 'daily', '0.8'),
 'muell.html': ('Müllabfuhr', 'Müllabfuhr Bad König: Abfuhrtermine für Restmüll, Bio, Papier und Gelbe Tonne in allen Stadtteilen, dazu Grünschnitt und Hotline.', 'weekly', '0.8'),
 'wetter.html': ('Wetter', 'Wetter in Bad König: Vorhersage für die nächsten Tage, Live-Werte der Wetterstation und Regenradar für den Odenwald.', 'hourly', '0.8'),
 'wichtig.html': ('Wichtige Meldungen', 'Wichtige Meldungen für Bad König: Warnungen, Polizei, Feuerwehr und Bevölkerungsschutz.', 'daily', '0.8'),
 'genuss.html': ('Genuss & Gewerbe', 'Genuss und Gewerbe in Bad König: Gastronomie, Geschäfte, Handwerk und Neuigkeiten aus der lokalen Wirtschaft.', 'weekly', '0.6'),
 'kontakt.html': ('Kontakt', 'Kontakt zu BDKNG: Hinweise, Veranstaltungstipps und Anregungen für Bad König per E-Mail an info@bdkng.de.', 'monthly', '0.4'),
 'impressum.html': ('Impressum', 'Impressum von BDKNG – Bad König kompakt.', 'yearly', '0.2'),
 'datenschutz.html': ('Datenschutz', 'Datenschutzerklärung von BDKNG – Bad König kompakt.', 'yearly', '0.2'),
 'bildnachweise.html': ('Bildnachweise & Quellen', 'Woher die Meldungen von BDKNG stammen: Quellen, Bildnachweise und Hinweise zur Zusammenfassung.', 'monthly', '0.3'),
}
NOINDEX = ['werbung.html', 'suche-test.html']
ORG = {"@type": "NewsMediaOrganization", "@id": BASE + "/#org", "name": "BDKNG – Bad König kompakt", "alternateName": "BDKNG", "url": BASE + "/", "logo": BASE + "/assets/bdkng-logo-jens.png", "email": "info@bdkng.de", "areaServed": {"@type": "City", "name": "Bad König"}, "sameAs": ["https://www.facebook.com/bdkng.de/", "https://www.instagram.com/bd1kng/", "https://www.tiktok.com/@bdkng4", "https://whatsapp.com/channel/0029VaQq65RCxoAv42xpsi0M"]}
def setmeta(s, attr, key, val):
    e = html.escape(val, quote=True)
    pat = re.compile(r'<meta %s="%s" content="[^"]*">' % (attr, re.escape(key)))
    tag = '<meta %s="%s" content="%s">' % (attr, key, e)
    if pat.search(s): return pat.sub(lambda m: tag, s, count=1)
    return s.replace('</head>', tag + '</head>', 1)
heute = datetime.date.today().isoformat()
for f, (name, desc, freq, prio) in SEITEN.items():
    p = root / f; s = p.read_text(encoding='utf-8')
    url = BASE + '/' + ('' if f == 'index.html' else f)
    titel = re.search(r'<title>([^<]*)</title>', s).group(1)
    s = setmeta(s, 'name', 'description', desc)
    for k, v in [('og:type', 'website'), ('og:locale', 'de_DE'), ('og:site_name', 'BDKNG – Bad König kompakt'), ('og:title', html.unescape(titel)), ('og:description', desc), ('og:url', url), ('og:image', OG), ('og:image:width', '1200'), ('og:image:height', '630'), ('og:image:alt', 'BDKNG – Bad König kompakt')]:
        s = setmeta(s, 'property', k, v)
    s = setmeta(s, 'name', 'twitter:card', 'summary_large_image')
    s = setmeta(s, 'name', 'robots', 'index, follow, max-image-preview:large')
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', s, flags=re.S)
    if f == 'index.html':
        ld = {"@context": "https://schema.org", "@graph": [ORG, {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "BDKNG – Bad König kompakt", "inLanguage": "de-DE", "publisher": {"@id": BASE + "/#org"}}, {"@type": "WebPage", "@id": BASE + "/#webpage", "url": BASE + "/", "name": html.unescape(titel), "description": desc, "isPartOf": {"@id": BASE + "/#website"}, "inLanguage": "de-DE", "primaryImageOfPage": {"@type": "ImageObject", "url": OG}}]}
    else:
        ld = {"@context": "https://schema.org", "@graph": [{"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": html.unescape(titel), "description": desc, "inLanguage": "de-DE", "isPartOf": {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "BDKNG – Bad König kompakt"}, "publisher": {"@type": "NewsMediaOrganization", "@id": BASE + "/#org", "name": "BDKNG – Bad König kompakt", "url": BASE + "/"}}, {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Startseite", "item": BASE + "/"}, {"@type": "ListItem", "position": 2, "name": name, "item": url}]}]}
    s = s.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script></head>', 1)
    p.write_text(s, encoding='utf-8', newline='\n')
for f in NOINDEX:
    p = root / f
    if p.exists():
        s = p.read_text(encoding='utf-8'); s = setmeta(s, 'name', 'robots', 'noindex, follow'); p.write_text(s, encoding='utf-8', newline='\n')
urls = ''.join('<url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>' % (BASE + '/' + ('' if f == 'index.html' else f), heute if freq in ('hourly', 'daily') else '2026-11-12', freq, prio) for f, (_, _, freq, prio) in SEITEN.items())
(root / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n', encoding='utf-8')
print('SEO aktualisiert')
