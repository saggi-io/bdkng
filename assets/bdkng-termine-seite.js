// Termine-Seite: Termin melden mit Kollisions-Check, „Diese Woche“, Kalender für 3 Monate (Spalten je Monat),
// Kirche & Gedenken, Feiertage, Freilichtbühne – alles aus /data/*.json zusammengeführt.
(function () {
  if (location.pathname !== '/termine.html') return;
  var WT = ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'], MON = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'];
  var STADT = 'https://www.badkoenig.de/kultur-freizeit/veranstaltungen/veranstaltungskalender/';
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function p2(n) { return ('0' + n).slice(-2); }
  function iso(d) { return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); }
  function dat(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function plus(d, n) { var x = new Date(d); x.setDate(x.getDate() + n); return x; }
  function kurz(s) { var d = dat(s); return WT[d.getDay()] + ' ' + p2(d.getDate()) + '.' + p2(d.getMonth() + 1) + '.'; }
  var heute = new Date(); heute.setHours(0, 0, 0, 0); var H = iso(heute);
  var ENDE = iso(new Date(heute.getFullYear(), heute.getMonth() + 3, 0)); // Ende des dritten Monats
  // Feiertage Hessen + kirchliche Gedenktage
  function ostern(j) { var a = j % 19, b = Math.floor(j / 100), c = j % 100, d = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451), mo = Math.floor((h + l - 7 * m + 114) / 31), t = ((h + l - 7 * m + 114) % 31) + 1; return new Date(j, mo - 1, t); }
  function feiertage(j) {
    var o = ostern(j), w = new Date(j, 11, 25), adv4 = plus(w, -((w.getDay() + 7) % 7 || 7));
    var L = [['01-01', 'Neujahr', 1], [iso(plus(o, -2)), 'Karfreitag', 1], [iso(o), 'Ostersonntag', 0], [iso(plus(o, 1)), 'Ostermontag', 1], ['05-01', 'Tag der Arbeit', 1], [iso(plus(o, 39)), 'Christi Himmelfahrt', 1], [iso(plus(o, 49)), 'Pfingstsonntag', 0], [iso(plus(o, 50)), 'Pfingstmontag', 1], [iso(plus(o, 60)), 'Fronleichnam', 1], ['10-03', 'Tag der Deutschen Einheit', 1], ['12-24', 'Heiligabend', 0], ['12-25', '1. Weihnachtstag', 1], ['12-26', '2. Weihnachtstag', 1], ['12-31', 'Silvester', 0],
      [iso(plus(adv4, -21)), '1. Advent', 0], [iso(plus(adv4, -14)), '2. Advent', 0], [iso(plus(adv4, -7)), '3. Advent', 0], [iso(adv4), '4. Advent', 0], [iso(plus(adv4, -28)), 'Totensonntag (Ewigkeitssonntag)', 0], [iso(plus(adv4, -35)), 'Volkstrauertag', 0], ['11-01', 'Allerheiligen', 0]];
    return L.map(function (x) { return { datum: x[0].length === 5 ? j + '-' + x[0] : x[0], titel: x[1], art: 'feiertag', gesetzlich: !!x[2] }; });
  }
  function holen(u) { return fetch(u, { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); }
  Promise.all([holen('/data/termine-kalender.json'), holen('/data/termine-kirche.json'), holen('/data/sport-termine.json')]).then(function (r) {
    var kal = (r[0] && r[0].termine) || [], ki = (r[1] && r[1].termine) || [], sp = (r[2] && r[2].spiele) || [];
    var A = [];
    kal.forEach(function (t) {
      var fl = t.quelle === 'freilicht' || /Freilichtb(ü|ue)hne/i.test(t.ort || '');
      var m = (t.info || '').match(/https:\/\/\S+/);
      A.push({ datum: t.datum, bis: t.bis || '', uhrzeit: t.uhrzeit || '', titel: t.titel, ort: t.ort || '', art: fl ? 'freilicht' : (/Gottesdienst|Messe|Andacht|Kirche/i.test(t.titel) ? 'kirche' : 'veranstaltung'), link: m ? m[0] : (fl ? '#freilicht' : STADT), quelle: fl ? 'Freilichtbühne' : 'Stadt Bad König' });
    });
    ki.forEach(function (t) { A.push({ datum: t.datum, uhrzeit: t.uhrzeit || '', titel: t.titel + (t.gemeinde === 'ev' ? ' (ev.)' : t.gemeinde === 'kath' ? ' (kath.)' : ''), ort: t.ort || '', info: t.info || '', art: 'kirche', link: (r[1] && r[1].url) || '', quelle: 'Stadtnachrichten' }); });
    sp.forEach(function (s) { if (!/Bad K(ö|oe)nig|Kinzigtal/i.test(s.home)) return; A.push({ datum: s.date, uhrzeit: s.time || '', titel: s.home + ' – ' + s.away, ort: /Kinzigtal/i.test(s.home) ? 'Sportplatz Kinzigtal' : 'Sportplatz Bad König/Zell', art: 'sport', link: '/sport.html', quelle: 'FuPa' }); });
    [heute.getFullYear(), heute.getFullYear() + 1].forEach(function (j) { feiertage(j).forEach(function (f) { A.push(f); }); });
    // Gedenk-Tag aus dem Kirchenkalender doppelt? Dann Feiertag-Zeile behalten, Gottesdienste trotzdem zeigen
    A = A.filter(function (t) { return (t.bis || t.datum) >= H; }).sort(function (a, b) { return (a.datum + (a.art === 'feiertag' ? '00' : a.uhrzeit || '99')).localeCompare(b.datum + (b.art === 'feiertag' ? '00' : b.uhrzeit || '99')); });
    window.BDKNG_TERMINE = A;
    bauen(A);
  });
  var ICON = { veranstaltung: '🎉', kirche: '⛪', sport: '⚽', freilicht: '🎭', feiertag: '🗓️' };
  function zeile(t, mitDatum) {
    var titel = esc(t.titel);
    if (t.link) titel = '<a href="' + esc(t.link) + '"' + (/^https?:/.test(t.link) ? ' target="_blank" rel="noopener"' : '') + '>' + titel + '</a>';
    var dz = mitDatum ? '<span class="tk-d">' + kurz(t.datum) + (t.bis && t.bis !== t.datum ? '–' + kurz(t.bis).slice(3) : '') + '</span>' : '';
    return '<li class="tk-' + t.art + (t.gesetzlich ? ' tk-gesetzlich' : '') + '" data-art="' + t.art + '">' + dz + '<span class="tk-z">' + (t.art === 'feiertag' ? (t.gesetzlich ? 'Feiertag' : '') : esc(t.uhrzeit ? t.uhrzeit + ' Uhr' : '')) + '</span><span class="tk-t">' + (ICON[t.art] || '') + ' ' + titel + (t.ort ? '<small>' + esc(t.ort) + '</small>' : '') + (t.info && t.art === 'kirche' ? '<small>' + esc(t.info) + '</small>' : '') + '</span></li>';
  }
  function bauen(A) {
    var main = document.querySelector('main'); if (!main) return;
    var melden = document.getElementById('terminMelden');
    // 1) Kollisions-Check im Abschnitt „Termin melden“
    if (melden && !document.getElementById('kollision')) {
      var k = document.createElement('div'); k.className = 'kollision'; k.id = 'kollision';
      k.innerHTML = '<p><strong>🔍 Wunschtermin prüfen – für Vereine und Veranstalter</strong><br>Bevor ihr plant: Gibt es an eurem Wunschtag schon etwas in Bad König? Datum wählen, wir zeigen alles, was wir kennen (Stadtkalender, Freilichtbühne, Kirchen, Heimspiele, Feiertage).</p><label class="field"><span>Wunschtermin</span><input type="date" min="' + H + '" id="kolDatum"></label><div id="kolErg" aria-live="polite"></div>';
      var ref = melden.querySelector('.tm-open'); (ref ? ref.parentNode.insertBefore(k, ref) : melden.appendChild(k));
      var pr = function (d) {
        var out = document.getElementById('kolErg'); if (!d) { out.innerHTML = ''; return; }
        var vor = iso(plus(dat(d), -1)), nach = iso(plus(dat(d), 1));
        var am = A.filter(function (t) { return t.datum <= d && (t.bis || t.datum) >= d; });
        var nah = A.filter(function (t) { return (t.datum === vor || t.datum === nach) && t.art !== 'feiertag'; });
        out.innerHTML = (am.length ? '<p class="kol-warn">⚠️ Am ' + kurz(d) + ' ist schon etwas los:</p><ul class="tk-liste">' + am.map(function (t) { return zeile(t, false); }).join('') + '</ul>' : '<p class="kol-ok">✅ Am ' + kurz(d) + ' kennen wir noch keinen Termin in Bad König.</p>') + (nah.length ? '<p class="form-note">Am Tag davor oder danach:</p><ul class="tk-liste">' + nah.map(function (t) { return zeile(t, true); }).join('') + '</ul>' : '') + '<p class="form-note">Nur Termine, die uns bekannt sind – ohne Gewähr. Meldet euren Termin unten, dann sehen ihn auch andere Vereine.</p>';
      };
      document.getElementById('kolDatum').addEventListener('change', function () { pr(this.value); });
      document.addEventListener('change', function (e) { if (e.target && e.target.name === 'datum' && e.target.closest('#tmForm')) { document.getElementById('kolDatum').value = e.target.value; pr(e.target.value); } });
    }
    // 2) Diese Woche (heute bis Sonntag)
    var so = plus(heute, (7 - heute.getDay()) % 7), SO = iso(so);
    var woche = A.filter(function (t) { return t.datum <= SO && (t.bis || t.datum) >= H; });
    var dw = document.getElementById('dieseWoche') || document.createElement('section');
    dw.id = 'dieseWoche'; dw.className = 'subpanel tk-woche';
    dw.innerHTML = '<h2>📅 Diese Woche in Bad König</h2>' + (woche.length ? '<ul class="tk-liste">' + woche.map(function (t) { return zeile(t, true); }).join('') + '</ul>' : '<p>Für diese Woche kennen wir noch keine Termine.</p>');
    if (melden) melden.insertAdjacentElement('afterend', dw);
    // 3) Kalender: die nächsten 3 Monate, Spalten je Monat
    var kal = document.getElementById('kalender') || document.createElement('section');
    kal.id = 'kalender'; kal.className = 'subpanel tk-kal';
    var spalten = [0, 1, 2].map(function (i) {
      var m0 = new Date(heute.getFullYear(), heute.getMonth() + i, 1), key = m0.getFullYear() + '-' + p2(m0.getMonth() + 1);
      var L = A.filter(function (t) { return t.datum.slice(0, 7) === key || ((t.bis || '').slice(0, 7) === key && t.datum.slice(0, 7) < key); });
      return '<div class="tk-monat"><h3>' + MON[m0.getMonth()] + ' ' + m0.getFullYear() + '</h3>' + (L.length ? '<ul class="tk-liste">' + L.map(function (t) { return zeile(t, true); }).join('') + '</ul>' : '<p class="form-note">Noch keine Termine bekannt.</p>') + '</div>';
    }).join('');
    var filter = [['alle', 'Alle'], ['veranstaltung', '🎉 Veranstaltungen'], ['kirche', '⛪ Kirche & Gedenken'], ['sport', '⚽ Heimspiele'], ['freilicht', '🎭 Freilichtbühne'], ['feiertag', '🗓️ Feiertage']].map(function (f, i) { return '<button type="button" class="tk-f' + (i ? '' : ' an') + '" data-f="' + f[0] + '">' + f[1] + '</button>'; }).join('');
    kal.innerHTML = '<h2>📆 Kalender – die nächsten drei Monate</h2><p class="form-note">Alle Termine, die wir kennen: Stadtkalender, Freilichtbühne, Gottesdienste und Gedenkfeiern aus den Stadtnachrichten, Heimspiele und Feiertage. Ein Klick auf den Titel führt zur Quelle.</p><div class="tk-filter">' + filter + '</div><div class="tk-spalten">' + spalten + '</div>' +
      '<div class="tk-knoepfe"><a class="btn" href="https://meinort.de/bad-koenig/neues/" target="_blank" rel="noopener">📰 Stadtnachrichten (meinOrt) ↗</a><a class="btn" href="' + STADT + '" target="_blank" rel="noopener">📅 Veranstaltungskalender der Stadt ↗</a><a class="btn" href="webcal://bdkng.de/kalender/termine.ics">📥 Kalender abonnieren</a></div>' +
      '<p class="form-note">Kalender abonnieren klappt direkt auf iPhone, iPad und Mac. Android/Google Kalender: <a href="/kalender/termine.ics" download>diesen Link</a> kopieren und im Google Kalender am PC unter „Weitere Kalender → Per URL“ einfügen. Alle Angaben ohne Gewähr – Absagen und Änderungen bitte beim Veranstalter prüfen.</p>';
    dw.insertAdjacentElement('afterend', kal);
    kal.querySelectorAll('.tk-f').forEach(function (b) { b.addEventListener('click', function () { var f = b.getAttribute('data-f'); kal.querySelectorAll('.tk-f').forEach(function (x) { x.classList.toggle('an', x === b); }); kal.querySelectorAll('.tk-spalten li').forEach(function (li) { li.hidden = f !== 'alle' && li.getAttribute('data-art') !== f; }); }); });
    // alter Kasten „Was ist los“ (Links und Abo stehen jetzt unter dem Kalender), Freilichtbühne danach
    var alt = main.querySelector('.service-panel'); if (alt) alt.hidden = true;
    var fl = document.getElementById('freilicht'); if (fl) kal.insertAdjacentElement('afterend', fl);
    // Wochen-Vorschau-Posts („Termine diese Woche/am Wochenende“) unten nicht doppelt zeigen
    document.querySelectorAll('.news-list .news-entry').forEach(function (a) { if (/-termine$|^termine-/.test(a.id) || /^\s*TERMINE?\b/i.test((a.querySelector('h2') || {}).textContent || '')) a.hidden = true; });
    if (location.hash && document.querySelector(location.hash)) setTimeout(function () { document.querySelector(location.hash).scrollIntoView(); }, 80);
  }
  // Kirche-Knopf in der Sprungleiste: Kalender auf „Kirche & Gedenken“ filtern
  window.BDKNG_KIRCHE = function () { var b = document.querySelector('.tk-f[data-f="kirche"]'); if (b) b.click(); return document.getElementById('kalender'); };
})();
