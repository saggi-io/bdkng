"""Kalenderdateien (.ics) zum Herunterladen/Abonnieren aus den BDKNG-Daten erzeugen (ohne Netzwerk).

Erzeugt:
  kalender/termine.ics          – Veranstaltungskalender der Stadt Bad König (data/termine-kalender.json)
  kalender/sport.ics            – Fußball SG Bad König/Zell + Handball (data/sport-termine.json)
  kalender/muell-<ortsteil>.ics – Abfuhrtermine je Ortsteil mit Erinnerung am Vorabend (data/muell.json)
"""
from pathlib import Path
from datetime import datetime, date, timedelta, timezone
import json, re, hashlib

root = Path(__file__).resolve().parents[1]
out = root / 'kalender'
out.mkdir(exist_ok=True)
STAMP = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

VTZ = ['BEGIN:VTIMEZONE', 'TZID:Europe/Berlin',
       'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST', 'DTSTART:19700329T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
       'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET', 'DTSTART:19701025T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
       'END:VTIMEZONE']


def esc(s):
    return str(s or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\r', '').replace('\n', '\\n')


def fold(line):
    b = line.encode('utf-8')
    if len(b) <= 75:
        return line
    parts, cur = [], b''
    for ch in line:
        c = ch.encode('utf-8')
        if len(cur) + len(c) > (75 if not parts else 74):
            parts.append(cur.decode('utf-8'))
            cur = b''
        cur += c
    parts.append(cur.decode('utf-8'))
    return '\r\n '.join(parts)


def uid(*teile):
    return hashlib.sha1('|'.join(teile).encode('utf-8')).hexdigest()[:20] + '@bdkng.de'


def kalender(name, beschreibung, events):
    z = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//BDKNG//Bad Koenig kompakt//DE', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:' + esc(name), 'X-WR-CALDESC:' + esc(beschreibung), 'X-WR-TIMEZONE:Europe/Berlin',
         'REFRESH-INTERVAL;VALUE=DURATION:PT12H', 'X-PUBLISHED-TTL:PT12H'] + VTZ
    for e in events:
        z += ['BEGIN:VEVENT', 'UID:' + e['uid'], 'DTSTAMP:' + STAMP] + e['zeilen'] + ['END:VEVENT']
    z.append('END:VCALENDAR')
    return '\r\n'.join(fold(l) for l in z) + '\r\n'


def dt_lokal(d, t):
    return d.replace('-', '') + 'T' + t.replace(':', '') + '00'


def ganztags(d, bis=None):
    end = date.fromisoformat(bis or d) + timedelta(days=1)
    return ['DTSTART;VALUE=DATE:' + d.replace('-', ''), 'DTEND;VALUE=DATE:' + end.strftime('%Y%m%d')]


def zeitlich(d, t, stunden=2):
    start = datetime.fromisoformat(d + 'T' + t)
    ende = start + timedelta(hours=stunden)
    return ['DTSTART;TZID=Europe/Berlin:' + dt_lokal(d, t), 'DTEND;TZID=Europe/Berlin:' + ende.strftime('%Y%m%dT%H%M00')]


def schreiben(datei, text):
    p = out / datei
    alt = p.read_text(encoding='utf-8') if p.exists() else ''
    # DTSTAMP ignorieren, damit nur echte Änderungen einen Commit auslösen
    if re.sub(r'DTSTAMP:\S+', '', alt) == re.sub(r'DTSTAMP:\S+', '', text):
        return False
    p.write_bytes(text.encode('utf-8'))
    return True


geaendert = []

# --- Veranstaltungen ---
k = json.loads((root / 'data/termine-kalender.json').read_text(encoding='utf-8'))
ev = []
for t in k.get('termine', []):
    if t.get('bis') or not t.get('uhrzeit'):
        zeit = ganztags(t['datum'], t.get('bis') or None)
    else:
        zeit = zeitlich(t['datum'], t['uhrzeit'])
    desc = ' – '.join(x for x in [t.get('info', ''), ('Veranstalter: ' + t['veranstalter']) if t.get('veranstalter') else '',
                                    'Quelle: ' + k.get('quelle', '') + ' ' + k.get('url', '')] if x)
    z = zeit + ['SUMMARY:' + esc(t['titel'])]
    if t.get('ort'):
        z.append('LOCATION:' + esc(t['ort'] + ('' if 'Bad K' in t['ort'] else ', Bad König')))
    z += ['DESCRIPTION:' + esc(desc), 'URL:' + k.get('url', 'https://bdkng.de/termine.html')]
    ev.append({'uid': uid('termin', t['datum'], t.get('uhrzeit', ''), t['titel']), 'zeilen': z})
if schreiben('termine.ics', kalender('BDKNG Termine Bad König', 'Veranstaltungen in Bad König (Quelle: Veranstaltungskalender der Stadt Bad König). Privates Angebot von bdkng.de, ohne Gewähr.', ev)):
    geaendert.append('termine.ics')

# --- Sport ---
s = json.loads((root / 'data/sport-termine.json').read_text(encoding='utf-8'))
ev = []
heute = date.today().isoformat()
for x in s.get('spiele', []):
    if x.get('date', '') < heute or not x.get('time'):
        continue
    liga = 'Kreisliga A' if x.get('team') == 'm1' else 'Kreisliga B'
    ev.append({'uid': uid('fb', x['date'], x['home'], x['away']), 'zeilen': zeitlich(x['date'], x['time']) + [
        'SUMMARY:' + esc('⚽ ' + x['home'] + ' – ' + x['away']),
        'DESCRIPTION:' + esc('Fußball ' + liga + '. Quelle: FuPa https://www.fupa.net/club/tsg-bad-koenig – Änderungen möglich.'),
        'URL:https://bdkng.de/sport.html']})
for x in s.get('handball', []):
    if x.get('date', '') < heute or not x.get('time'):
        continue
    ev.append({'uid': uid('hb', x['date'], x['home'], x['away']), 'zeilen': zeitlich(x['date'], x['time']) + [
        'SUMMARY:' + esc('🤾 ' + x['home'] + ' – ' + x['away']),
        'DESCRIPTION:' + esc('Handball (' + str(x.get('team', '')) + '). Quelle: nuLiga – Änderungen möglich.'),
        'URL:https://bdkng.de/sport.html']})
if schreiben('sport.ics', kalender('BDKNG Sport Bad König', 'Spiele der SG Bad König/Zell (Fußball) und der HSG Odenwald (Handball). Privates Angebot von bdkng.de, ohne Gewähr.', ev)):
    geaendert.append('sport.ics')

# --- Müll je Ortsteil ---
m = json.loads((root / 'data/muell.json').read_text(encoding='utf-8'))
IC = {'Rest': '⚫', 'Bio': '🟤', 'Papier': '🔵', 'Gelber-Sack': '🟡', 'SA': '⚠️'}
slug = lambda o: re.sub(r'[^a-z0-9]+', '-', o.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')).strip('-')
index = {}
for ot, arten in m['ortsteile'].items():
    tage = {}
    for art, daten in arten.items():
        for d in daten:
            tage.setdefault(d, []).append(art)
    ev = []
    for d in sorted(tage):
        namen = [IC.get(a, '') + ' ' + m['arten'].get(a, a) for a in tage[d]]
        ev.append({'uid': uid('muell', ot, d), 'zeilen': ganztags(d) + [
            'SUMMARY:' + esc('Müll ' + ot + ': ' + ', '.join(n.strip() for n in namen)),
            'DESCRIPTION:' + esc(m.get('hinweis', '') + (' ' + m['arten']['SA'] if 'SA' in tage[d] else '') + ' Quelle: ' + m['quelle'] + ' ' + m['url']),
            'TRANSP:TRANSPARENT',
            'BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + esc('Morgen Müll: ' + ', '.join(n.strip() for n in namen)), 'TRIGGER:-PT6H', 'END:VALARM']})
    datei = 'muell-' + slug(ot) + '.ics'
    index[ot] = datei
    if schreiben(datei, kalender('BDKNG Müll ' + ot, 'Abfuhrtermine ' + ot + ' (Quelle: ' + m['quelle'] + '), mit Erinnerung am Vorabend um 18 Uhr. Privates Angebot von bdkng.de, ohne Gewähr.', ev)):
        geaendert.append(datei)
(out / 'muell-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('Kalender aktualisiert:', ', '.join(geaendert) or 'nichts geändert')
