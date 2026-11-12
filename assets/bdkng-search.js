'use strict';
(function () {
  var box = document.getElementById('bdkng-search');
  if (!box) return;
  var form = box.querySelector('form'), input = box.querySelector('input[type=search]');
  var out = box.querySelector('.bs-out'), mic = box.querySelector('.bs-mic');
  var Z = 'Europe/Berlin', data = {}, loading = null;
  var WT = ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'];
  var ARTEN = [
    { key: 'Rest', re: /rest|grau|schwarz/i, name: 'Restmüll' },
    { key: 'Bio', re: /bio|braun/i, name: 'Biotonne' },
    { key: 'Papier', re: /papier|blau|karton|pappe/i, name: 'Papier' },
    { key: 'Gelber-Sack', re: /gelb|sack|säcke|saecke|verpackung|plastik/i, name: 'Gelbe Säcke' },
    { key: 'SA', re: /sonderabfall|schadstoff|sondermüll|sondermuell|kleinmengen/i, name: 'Sonderabfall-Kleinmengensammlung' }
  ];
  function heute() { return new Intl.DateTimeFormat('sv-SE', { timeZone: Z }).format(new Date()); }
  function plus(iso, n) { var d = new Date(iso + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
  function deDatum(iso) { var d = new Date(iso + 'T12:00:00Z'); return WT[d.getUTCDay()] + ', ' + iso.slice(8) + '.' + iso.slice(5, 7) + '.' + iso.slice(0, 4); }
  function tageBis(iso) { var n = Math.round((new Date(iso + 'T12:00:00Z') - new Date(heute() + 'T12:00:00Z')) / 864e5); return n === 0 ? 'heute' : n === 1 ? 'morgen' : n === 2 ? 'übermorgen' : 'in ' + n + ' Tagen'; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function laden() {
    if (loading) return loading;
    loading = Promise.all([fetch('/data/muell.json').then(function (r) { return r.json(); }).catch(function () { return null; }),
      fetch('/data/news.json').then(function (r) { return r.json(); }).catch(function () { return []; }),
      fetch('/data/sport-termine.json').then(function (r) { return r.json(); }).catch(function () { return null; }),
      fetch('/data/wetter-aktuell.json').then(function (r) { return r.json(); }).catch(function () { return null; }),
      fetch('/data/wissen-badkoenig.json').then(function (r) { return r.json(); }).catch(function () { return null; })]).then(function (a) { data.muell = a[0]; data.news = a[1] || []; data.spiele = a[2] && a[2].spiele || []; data.handball = a[2] && a[2].handball || []; data.la = a[2] && a[2].leichtathletik || []; data.wetter = a[3]; data.wissen = a[4] && a[4].eintraege || []; });
    return loading;
  }
  function ortsteil(q, muell) {
    var map = { 'kernstadt': 'Kernstadt', 'bad könig': 'Kernstadt', 'bad koenig': 'Kernstadt', 'etzen': 'Etzen-Gesäß', 'gesäß': 'Etzen-Gesäß', 'fürstengrund': 'Fürstengrund', 'fuerstengrund': 'Fürstengrund', 'gumpersberg': 'Gumpersberg', 'kimbach': 'Kimbach', 'momart': 'Momart', 'nieder-kinzig': 'Nieder-Kinzig', 'nieder kinzig': 'Nieder-Kinzig', 'niederkinzig': 'Nieder-Kinzig', 'ober-kinzig': 'Ober-Kinzig', 'ober kinzig': 'Ober-Kinzig', 'oberkinzig': 'Ober-Kinzig', 'zell': 'Zell' };
    var l = q.toLowerCase();
    for (var k in map) if (l.indexOf(k) >= 0 && muell.ortsteile[map[k]]) return map[k];
    return null;
  }
  function naechster(ot, art, m) { var t = heute(), l = (m.ortsteile[ot][art] || []).filter(function (d) { return d >= t; }); return l; }
  function quelleMuell(m) { return '<p class="bs-src">Quelle: <a href="' + esc(m.url) + '" target="_blank" rel="noopener">' + esc(m.quelle) + '</a> · Stand ' + esc(m.stand.slice(8) + '.' + m.stand.slice(5, 7) + '.' + m.stand.slice(0, 4)) + '</p>'; }
  function muellAntwort(q) {
    var m = data.muell; if (!m) return null;
    var ot = ortsteil(q, m);
    var arten = ARTEN.filter(function (a) { return a.re.test(q); });
    if (!ot) {
      var b = Object.keys(m.ortsteile).map(function (o) { return '<button type="button" class="bs-chip" data-q="' + esc(q + ' ' + o) + '">' + esc(o) + '</button>'; }).join('');
      return '<p>Für welchen Ortsteil?</p><div class="bs-chips">' + b + '</div>';
    }
    if (!arten.length) arten = ARTEN.slice(0, 4);
    var h = '<p><strong>Abfuhr in ' + esc(ot) + '</strong></p><ul>';
    arten.forEach(function (a) {
      var l = naechster(ot, a.key, m);
      h += l.length ? '<li><strong>' + esc(a.name) + ':</strong> ' + esc(deDatum(l[0])) + ' (' + tageBis(l[0]) + ')' + (l[1] ? ', danach ' + esc(l[1].slice(8) + '.' + l[1].slice(5, 7) + '.') : '') + (a.key === 'SA' ? '<br><small>' + esc(m.arten.SA) + '</small>' : '') + '</li>' : '<li>' + esc(a.name) + ': kein weiterer Termin im Kalender.</li>';
    });
    return h + '</ul><p class="bs-note">' + esc(m.hinweis) + '</p>' + quelleMuell(m);
  }
  function terminAntwort(q) {
    var l = q.toLowerCase(), t = heute(), tage = [];
    if (/übermorgen|uebermorgen/.test(l)) tage = [plus(t, 2)]; else if (/morgen/.test(l)) tage = [plus(t, 1)]; else if (/heute/.test(l)) tage = [t];
    else if (/wochenende|\bwe\b/.test(l)) { var wd = new Date(t + 'T12:00:00Z').getUTCDay(); var sa = plus(t, (6 - wd + 7) % 7); tage = [plus(sa, -1), sa, plus(sa, 1)]; }
    tage = tage.filter(function (d) { return d >= t; });
    var dm = l.match(/(\d{1,2})\.(\d{1,2})\./); if (dm) { tage = [t.slice(0, 4) + '-' + ('0' + dm[2]).slice(-2) + '-' + ('0' + dm[1]).slice(-2)]; }
    if (!tage.length) return /wochenende|\bwe\b|heute|morgen/.test(l) ? '<p>Dafür habe ich keine kommenden Termine gefunden.</p>' : null;
    var treffer = [];
    data.news.forEach(function (n) {
      if (n.categories.indexOf('termine') < 0) return;
      n.paragraphs.forEach(function (p) { if (/^\s*(Änderungen|Quellen?:|Stand:)/.test(p) || /Stand: \d/.test(p)) return; if ((data.spiele || []).length && /Fußball/.test(p)) return; tage.forEach(function (d) { if (p.indexOf(d.slice(8) + '.' + d.slice(5, 7) + '.') >= 0 && p.length < 400) treffer.push({ p: p.replace(/^•\s*/, ''), n: n }); }); });
    });
    var fb = (data.spiele || []).filter(function (x) { return tage.indexOf(x.date) >= 0; });
    var hb = (data.handball || []).filter(function (x) { return tage.indexOf(x.date) >= 0; });
    var la = (data.la || []).filter(function (x) { return tage.indexOf(x.date) >= 0; });
    var ev = [], seen = {};
    treffer.forEach(function (x) { if (seen[x.p] || /Handball|Fußball/.test(x.p)) return; seen[x.p] = 1; ev.push(x); });
    if (!ev.length && !fb.length && !hb.length && !la.length) return '<p>' + (/heute/.test(l) ? 'Für heute habe ich keine Termine gefunden.' : 'Dafür habe ich keine Termine gefunden.') + ' Alle kommenden Termine findest du unter <a href="/termine.html">Termine &amp; Veranstaltungen</a>.</p>';
    var h = '<p><strong>📅 Veranstaltungen</strong></p>';
    h += ev.length ? '<ul>' + ev.map(function (x) { return '<li>' + esc(x.p) + '</li>'; }).join('') + '</ul><p class="bs-src">Quelle: <a href="/termine.html">Termine &amp; Veranstaltungen</a> (Stadt Bad König, Stadtnachrichten)</p>' : '<p>Keine Veranstaltungen eingetragen.</p>';
    if (fb.length || hb.length || la.length) {
      h += '<p><strong>🏆 Sport</strong></p><ul>';
      fb.forEach(function (x) { h += '<li>' + esc(deDatum(x.date)) + ', ' + esc(x.time) + ' Uhr: ⚽ ' + esc(x.home) + ' – ' + esc(x.away) + '</li>'; });
      hb.forEach(function (x) { h += '<li>' + esc(deDatum(x.date)) + ', ' + esc(x.time) + ' Uhr: 🤾 ' + esc(x.home) + ' – ' + esc(x.away) + ' (' + esc(x.team) + ')</li>'; });
      la.forEach(function (x) { h += '<li>' + esc(deDatum(x.date)) + (x.time ? ', ' + esc(x.time) + ' Uhr' : '') + ': 🏃 ' + esc(x.titel) + (x.ort ? ' (' + esc(x.ort) + ')' : '') + '</li>'; });
      h += '</ul><p class="bs-src">Quellen: FuPa, nuLiga, HLV Kreis Odenwald</p>';
    }
    return h;
  }
  function stichwort(q) {
    var w = q.toLowerCase().split(/[^a-zäöüß0-9-]+/).filter(function (x) { return x.length > 2 && !/^(kann|ich|von|nach|wann|die|der|das|wie|was|ist|und|für|mit|gibt|es|bad|könig|koenig|fahren|fahrenn|wird|wer|wo|zum|zur|den|dem|ein|eine|noch|auch|nicht|heute|morgen)$/.test(x); });
    if (!w.length) return null;
    var t = heute(), res = [];
    data.news.forEach(function (n) {
      var txt = (n.title + ' ' + n.paragraphs.join(' ')).toLowerCase(), s = 0;
      w.forEach(function (x) { if (txt.indexOf(x) >= 0) s += n.title.toLowerCase().indexOf(x) >= 0 ? 3 : 1; });
      if (s && n.valid_until && n.valid_until < t) s -= 2;
      if (s >= (w.length > 1 ? 2 : 1)) res.push({ n: n, s: s });
    });
    res.sort(function (a, b) { return b.s - a.s || (b.n.checked > a.n.checked ? 1 : -1); });
    return res.slice(0, 3);
  }
  var RUB = { aktuell: 'Aktuelles', verkehr: 'Verkehr', termine: 'Termine', sport: 'Sport', genuss: 'Genuss', wichtig: 'Wichtig', wetter: 'Wetter', muell: 'Müll' };
  function news(q) {
    var r = stichwort(q); if (!r) return '<p>Bitte stelle eine Frage oder gib ein Stichwort ein.</p>';
    if (!r.length) return null;
    return r.map(function (x) {
      var n = x.n, c = n.categories[0];
      return '<div class="bs-hit"><h3><a href="/' + esc(c) + '.html#' + esc(n.id) + '">' + esc(n.title) + '</a></h3><p>' + esc(n.paragraphs[0] || '') + '</p><p class="bs-src">' + esc(RUB[c] || c) + ' · Quelle: <a href="' + esc(n.url) + '" target="_blank" rel="noopener">' + esc(n.source) + '</a> · Stand ' + esc(n.checked.slice(8) + '.' + n.checked.slice(5, 7) + '.' + n.checked.slice(0, 4)) + '</p></div>';
    }).join('');
  }
  function spieleAntwort(q) {
    var ql = q.toLowerCase();
    var absicht = /\b(spiel|spiele|spielt|spielen|spielplan|fußballspiel|fussballspiel|fußballspiele|fussballspiele|heimspiel|heimspiele|auswärtsspiel|anpfiff|anstoß|derby|kreisliga|ergebnis(se)?)\b/.test(ql);
    var gegner = /\b(gegen|wann|spielt|nächste|nächsten)\b/.test(ql) && (data.spiele || []).some(function (x) { return (x.home + ' ' + x.away).toLowerCase().split(/[^a-zäöüß-]+/).some(function (t) { return t.length > 5 && !/könig|zell|michelstadt/.test(t) && ql.indexOf(t) >= 0; }); });
    if (/gehfu|walking|training|trainier/.test(ql)) return null;
    if (!absicht && !gegner) return null;
    var t = heute(), l = (data.spiele || []).filter(function (x) { return x.date >= t; });
    if (!l.length) return null;
    var w = q.toLowerCase().split(/[^a-zäöüß0-9-]+/).filter(function (x) { return x.length > 4 && !/fußball|fussball|spiel|spiele|kreisliga|heimspiel|auswärts|nächste|nächsten|anstehende|wann|wieder|nächstes|wochenende/.test(x); });
    var f = w.length ? l.filter(function (x) { var s = (x.home + ' ' + x.away).toLowerCase(); return w.some(function (y) { return s.indexOf(y) >= 0; }); }) : l;
    if (!f.length) f = l;
    var h = '<p>Die nächsten Fußballspiele der SG Bad König/Zell:</p><ul>';
    f.slice(0, 6).forEach(function (x) { h += '<li>' + esc(deDatum(x.date)) + ', ' + esc(x.time) + ' Uhr (' + tageBis(x.date) + '): <strong>' + esc(x.home) + ' – ' + esc(x.away) + '</strong> <small>(Kreisliga ' + (x.team === 'm1' ? 'A, 1. Mannschaft' : 'B, 2. Mannschaft') + ')</small></li>'; });
    return h + '</ul><p class="bs-src">Quelle: <a href="https://www.fupa.net/club/tsg-bad-koenig" target="_blank" rel="noopener">FuPa</a> · Änderungen bitte beim Verein prüfen.</p>';
  }
  function antworten(q) {
    q = q.trim(); if (!q) return;
    out.innerHTML = '<p class="bs-load">Ich suche …</p>'; out.hidden = false;
    laden().then(function () {
      var h = null;
      if (!/grünschnitt|gruenschnitt|bauhof/i.test(q) && /müll|muell|abfall|abfuhr|tonne|sack|säcke|saecke|papier|biotonne|restmüll|sperrmüll|schadstoff|sonderabfall/i.test(q)) h = muellAntwort(q);
      if (!h && !/handball/i.test(q) && !/gespielt|ergebnis|ausgang|gewonnen|verloren|letzte|vergangen|tabelle|torsch/i.test(q)) h = spieleAntwort(q);
      if (!h) h = serviceAntwort(q) || rathausAntwort(q) || sportAntwort(q) || wetterAntwort(q) || schnellAntwort(q);
      if (h) return zeige(h);
      var ta = terminAntwort(q);
      if (ta && /heute|morgen|wochenende|\bwe\b/i.test(q) && !/wetter|regen|müll|muell/i.test(q)) return zeige(ta);
      var fb = ta || news(q);
      ki(q, fb);
    });
  }
  var WI = { 'clear-day': 'sonnig', 'clear-night': 'klar', 'partly-cloudy-day': 'teils bewölkt', 'partly-cloudy-night': 'teils bewölkt', cloudy: 'bewölkt', fog: 'neblig', wind: 'windig', rain: 'Regen', sleet: 'Schneeregen', snow: 'Schnee', hail: 'Hagel', thunderstorm: 'Gewitter' };
  function wetterAntwort(q) {
    if (!/wetter|regen|temperatur|frost|grad|sonne|schnee|kalt|warm/i.test(q)) return null;
    var w = data.wetter; if (!w || !w.tage) return null;
    var t = heute(), tage = w.tage.filter(function (d) { return d.datum >= t; }).slice(0, 3);
    var h = '<div class="bs-hit"><h3>Wetter in Bad König</h3>';
    if (w.jetzt) h += '<p>Jetzt: ' + esc(w.jetzt.temp) + ' °C, ' + esc(WI[w.jetzt.icon] || w.jetzt.icon) + ', Wind ' + esc(w.jetzt.wind) + ' km/h</p>';
    h += '<ul>' + tage.map(function (d) { return '<li>' + esc(deDatum(d.datum)) + ': ' + esc(WI[d.icon] || d.icon) + ', ' + esc(d.tmin) + ' bis ' + esc(d.tmax) + ' °C' + (d.regen >= 0.5 ? ', Regen ca. ' + esc(Math.round(d.regen)) + ' mm' : '') + (d.tmin <= 0 ? ', Frost möglich' : '') + '</li>'; }).join('') + '</ul>';
    return h + '<p class="bs-src">Quelle: <a href="' + esc(w.quelle_url || 'https://brightsky.dev/') + '" target="_blank" rel="noopener">' + esc(w.quelle || 'Deutscher Wetterdienst') + '</a> · <a href="/wetter.html">Mehr auf der Wetterseite</a></p></div>';
  }
  function liste(kat, titel, n) {
    var t = heute();
    var r = (data.news || []).filter(function (x) { return (x.categories || []).indexOf(kat) >= 0 && (!x.valid_until || x.valid_until >= t); })
      .sort(function (a, b) { return a.checked < b.checked ? 1 : -1; }).slice(0, n);
    if (!r.length) return '<p>' + esc(titel) + ': Gerade liegt dazu nichts Aktuelles vor.</p>';
    return '<p><strong>' + esc(titel) + '</strong></p>' + r.map(function (x) { return '<div class="bs-hit"><h3><a href="/' + esc(kat) + '.html#' + esc(x.id) + '">' + esc(x.title) + '</a></h3><p>' + esc(x.paragraphs[0] || '') + '</p><p class="bs-src">Quelle: <a href="' + esc(x.url) + '" target="_blank" rel="noopener">' + esc(x.source) + '</a> · Stand ' + esc(x.checked.slice(8) + '.' + x.checked.slice(5, 7) + '.') + '</p></div>'; }).join('');
  }
  function standJetzt() { var d = new Date(); return d.toLocaleString('de-DE', { timeZone: Z, day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }) + ' Uhr'; }
  function aktuell(kat, re, tage) {
    var t = heute(), grenze = plus(t, -tage);
    return (data.news || []).filter(function (x) { return (x.categories || []).indexOf(kat) >= 0 && x.checked >= grenze && (!x.valid_until || x.valid_until >= t) && (!re || re.test(x.title + ' ' + (x.paragraphs || []).join(' '))); })
      .sort(function (a, b) { return a.checked < b.checked ? 1 : -1; });
  }
  function treffer(r, kat) { return r.map(function (x) { return '<div class="bs-hit"><h3><a href="/' + esc(kat) + '.html#' + esc(x.id) + '">' + esc(x.title) + '</a></h3><p>' + esc(x.paragraphs[0] || '') + '</p><p class="bs-src">Quelle: <a href="' + esc(x.url) + '" target="_blank" rel="noopener">' + esc(x.source) + '</a> · Stand ' + esc(x.checked.slice(8) + '.' + x.checked.slice(5, 7) + '.') + '</p></div>'; }).join(''); }
  function schnellAntwort(q) {
    if (/odenwaldbahn|\bzug\b|züge|zuege|bahn\b|vias|rb ?82/i.test(q)) {
      var st = aktuell('verkehr', /(bahn|zug|vias|rmv|schiene)/i, 3).filter(function (x) { var tx = x.title + ' ' + (x.paragraphs || []).join(' '); return /(störung|ausfall|fällt aus|ersatzverkehr|verspät|sperr|gesperrt|bauarbeit)/i.test(tx) && !/(fährt wieder|wieder frei|endet|beendet|freigabe)/i.test(tx); });
      var h = st.length ? '<p><strong>🚆 Aktuelle Meldungen zur Odenwaldbahn</strong></p>' + treffer(st.slice(0, 3), 'verkehr')
        : '<div class="bs-hit"><h3>🚆 Odenwaldbahn</h3><p>✅ Derzeit liegen uns keine Infos über Störungen vor (Stand ' + esc(standJetzt()) + ').</p></div>';
      return h + '<p class="bs-src">Live-Fahrplan und kurzfristige Ausfälle: <a href="https://www.vias-online.de/" target="_blank" rel="noopener">VIAS</a> · <a href="https://www.rmv.de/" target="_blank" rel="noopener">RMV</a></p>';
    }
    if (/sperrung|gesperrt|stau|verkehr|baustelle|umleitung|b ?45|unfall/i.test(q)) {
      var live = aktuell('verkehr', null, 2).filter(function (x) { return /^verkehr-live/.test(x.id) && !/bis Ende|202[7-9]/.test(x.title + (x.paragraphs || []).join(' ')); });
      var dauer = aktuell('verkehr', /(sperrung|gesperrt|baustelle|umleitung|b ?45)/i, 14).filter(function (x) { return live.indexOf(x) < 0; }).slice(0, 3);
      var h = live.length ? '<p><strong>🚧 Aktuell (Stau, Unfall, Sperrung)</strong></p>' + treffer(live.slice(0, 4), 'verkehr')
        : '<div class="bs-hit"><h3>🚧 Verkehr rund um Bad König</h3><p>✅ Derzeit liegen uns keine Meldungen über Staus oder Unfälle vor (Stand ' + esc(standJetzt()) + ').</p></div>';
      if (dauer.length) h += '<p><strong>Baustellen und längere Sperrungen</strong></p>' + treffer(dauer, 'verkehr');
      return h + '<p class="bs-src">Live-Lage: <a href="https://www.hessenschau.de/verkehr/index.html" target="_blank" rel="noopener">hessenschau Verkehrsservice</a></p>';
    }
    if (/neues|neuigkeit|was gibt.?s|nachrichten|aktuell/i.test(q) && !/termin|wochenende|heute|morgen/i.test(q)) return liste('aktuell', 'Neues aus Bad König', 5);
    return null;
  }

  function wissen(re) { return (data.wissen || []).filter(function (e) { return re.test(e.titel); })[0]; }
  function wQuelle(e) { return '<p class="bs-src">Quelle: <a href="' + esc(e.url) + '" target="_blank" rel="noopener">' + esc(/wittich/.test(e.url) ? 'Bad Königer Stadtnachrichten' : 'Stadt Bad König') + '</a></p>'; }
  function sportAntwort(q) {
    if (!/handball|fußball und|fussball und|wann spielen|spiele am wochenende|hsg|leichtathlet/i.test(q)) return null;
    var t = heute(), fb = (data.spiele || []).filter(function (x) { return x.date >= t; }).slice(0, 4), hb = (data.handball || []).filter(function (x) { return x.date >= t; }).slice(0, 5), la = (data.la || []).filter(function (x) { return x.date >= t; }).slice(0, 3);
    if (/leichtathlet/i.test(q) && !/fu(ß|ss)ball|handball/i.test(q)) { fb = []; hb = []; }
    if (!fb.length && !hb.length && !la.length) return null;
    var h = '';
    if (fb.length) h += '<p><strong>⚽ Fußball – SG Bad König/Zell</strong></p><ul>' + fb.map(function (x) { return '<li>' + esc(deDatum(x.date)) + ', ' + esc(x.time) + ' Uhr: ' + esc(x.home) + ' – ' + esc(x.away) + '</li>'; }).join('') + '</ul>';
    if (hb.length) h += '<p><strong>🤾 Handball – HSG Odenwald</strong></p><ul>' + hb.map(function (x) { return '<li>' + esc(deDatum(x.date)) + ', ' + esc(x.time) + ' Uhr (' + esc(x.team) + '): ' + esc(x.home) + ' – ' + esc(x.away) + '</li>'; }).join('') + '</ul>';
    if (la.length) h += '<p><strong>🏃 Leichtathletik in Bad König</strong></p><ul>' + la.map(function (x) { return '<li>' + esc(deDatum(x.date)) + (x.time ? ', ' + esc(x.time) + ' Uhr' : '') + ': ' + esc(x.titel) + (x.ort ? ' (' + esc(x.ort) + ')' : '') + '</li>'; }).join('') + '</ul>';
    return h + '<p class="bs-src">Quellen: <a href="https://www.fupa.net/club/tsg-bad-koenig" target="_blank" rel="noopener">FuPa</a> · <a href="https://hhv-handball.liga.nu/" target="_blank" rel="noopener">nuLiga Handball</a> · <a href="https://odenwald.hlv.de/home/veranstaltungen/sportveranstaltungen" target="_blank" rel="noopener">HLV Kreis Odenwald</a></p>';
  }
  function rathausAntwort(q) {
    var l = q.toLowerCase();
    if (/öffnungszeit|oeffnungszeit|geöffnet|rathaus.*(offen|auf)|wann hat .*rathaus/.test(l)) {
      var o = wissen(/Öffnungszeiten der Stadtverwaltung/); if (!o) return null;
      return '<div class="bs-hit"><h3>Öffnungszeiten Rathaus Bad König</h3><p>' + esc(o.text).replace(/\. /g, '.<br>') + '</p></div>' + wQuelle(o);
    }
    if (/ansprechpartner|ansprechperson|zuständig|zustaendig|wie erreiche ich das rathaus|amt\b|verwaltung/.test(l)) {
      var a = wissen(/Ansprechpartner Stadtverwaltung/), b = wissen(/Bürgermeister/); if (!a) return null;
      var teile = a.text.split(/\.\s+(?=[A-ZÄÖÜ])/).filter(function (x) { return /\d{3}/.test(x); });
      var treffer = teile.filter(function (x) { var k = x.split(':')[0].toLowerCase(); return k.split(/[\s,\/&]+/).some(function (w) { return w.length > 4 && l.indexOf(w) >= 0; }); });
      if (treffer.length) return '<div class="bs-hit"><h3>Ansprechpartner im Rathaus</h3><ul>' + treffer.map(function (x) { return '<li>' + esc(x.replace(/\.$/, '')) + '</li>'; }).join('') + '</ul></div>' + wQuelle(a);
      var chips = teile.map(function (x) { var k = x.split(':')[0]; return '<button type="button" class="bs-chip" data-q="' + esc('Ansprechpartner ' + k) + '">' + esc(k.length > 40 ? k.slice(0, 38) + '…' : k) + '</button>'; }).join('');
      return '<p><strong>Wofür suchst du einen Ansprechpartner?</strong></p><div class="bs-chips">' + chips + '</div><p>Zentrale: 06063 5009-0 · <a href="mailto:stadtverwaltung@badkoenig.de">stadtverwaltung@badkoenig.de</a></p>' + (b ? '<p>' + esc(b.titel) + ': ' + esc(b.text.slice(0, 160)) + '</p>' : '') + wQuelle(a);
    }
    return null;
  }
  function serviceAntwort(q) {
    var l = q.toLowerCase();
    if (/grünschnitt|gruenschnitt|bauhof|grüngut/.test(l)) {
      var g = wissen(/Grünschnitt/); if (!g) return null;
      var satz = g.text.split(/(?<=\.)\s+/).filter(function (x) { return /Grünschnitt/.test(x); }).join(' ');
      return '<div class="bs-hit"><h3>Grünschnitt am Bauhof</h3><p>' + esc(satz) + '</p><p>Fragen zur Müllabfuhr: Hotline 0800 9600100 (kostenlos).</p></div>' + wQuelle(g);
    }
    if (/notfall,|notruf|apotheke|notdienst|bereitschaft|ärzte|arzt|116 ?117|zahnarzt|giftnotruf|störungsdienst/.test(l)) {
      var ap = wissen(/Apotheken-Notdienst/), nt = wissen(/Notruftafel/), hin = '';
      if (ap) { var m = ap.text.match(/(\d{1,2})\.(\d{1,2})\.(\d{4}) hat die ([^.(]+?)\s*\(([^)]*)\)/); if (m) { var iso = m[3] + '-' + ('0' + m[2]).slice(-2) + '-' + ('0' + m[1]).slice(-2); hin = iso >= heute() ? '<p>Laut Stadtnachrichten am ' + esc(deDatum(iso)) + ': <strong>' + esc(m[4]) + '</strong>, ' + esc(m[5]) + '.</p>' : '<p>Die aktuelle Ausgabe der Stadtnachrichten nennt für Bad König nur den ' + esc(deDatum(iso)) + ' (' + esc(m[4]) + '). Für heute und die nächsten Tage hilft die Notdienstsuche:</p>'; } }
      var tel = function (n, nr) { return '<li>' + n + ': <a href="tel:' + nr.replace(/[^\d+]/g, '') + '"><strong>' + nr + '</strong></a></li>'; };
      var h = '<div class="bs-hit"><h3>🚨 Notruf</h3><ul>' + tel('Feuerwehr, Notarzt, Rettungsdienst', '112') + tel('Polizei', '110') + '</ul></div>';
      h += '<div class="bs-hit"><h3>🩺 Ärzte</h3><ul>' + tel('Ärztlicher Bereitschaftsdienst', '116 117') + tel('Zahnärztlicher Notdienst', '01805 607011') + tel('Giftnotruf Mainz', '06131 19240') + '</ul><p><small>Bereitschaftsdienst-Zentrale im Gesundheitszentrum Erbach: Mo, Di, Do 19–22 Uhr, Mi und Fr 14–22 Uhr, Sa, So und Feiertage 8–22 Uhr.</small></p></div>';
      h += '<div class="bs-hit"><h3>💊 Apotheken-Notdienst</h3>' + hin + '<p><a class="bs-kaffee-btn bs-link-btn" href="https://www.aponet.de/apotheke/notdienstsuche" target="_blank" rel="noopener">Notdienst heute finden (aponet.de, PLZ 64732)</a></p></div>';
      h += '<div class="bs-hit"><h3>🔧 Störungen und weitere Nummern</h3><ul>' + tel('Strom (e-Netz)', '0800 7018040') + tel('Gas (e-Netz)', '0800 7018080') + tel('Wasser (Wasserwerk Bad König)', '0171 5517483') + tel('Klärwerk', '06163 912751') + tel('Polizeistation Erbach', '06062 9530') + tel('City-Streife', '06063 35196-0') + tel('Odenwälder Frauenhaus', '06062 5646') + '</ul></div>';
      return h + (nt ? wQuelle(nt) : '');
    }
    if (/bürgerbus|buergerbus/.test(l)) { var bb = wissen(/Bürgerbus/); if (bb) return '<div class="bs-hit"><h3>🚌 Bürgerbus Bad König</h3><p>' + esc(bb.text) + '</p></div>' + wQuelle(bb); }
    if (/parken|parkpl|parkhaus|brötchentaste|e-mobil|emobil|lades|laden.*auto|e-auto|elektroauto/.test(l)) {
      var pk = wissen(/Parken und E-Lade/);
      return '<div class="bs-hit"><h3>🅿️ Parken in Bad König</h3><ul><li><strong>Brunnengärten 1–3</strong> (Therme): 0,50 € je 30 Min., 7–20 Uhr</li><li><strong>Bachgasse</strong> (Altstadt): 0,50 € je 30 Min., Mo–Fr 8–19, Sa 8–12 Uhr</li><li><strong>Alte Schule, Bleichstraße</strong> (lang parken): 2 € für 4 Std., 7-Tage-Ticket 10 €</li><li><strong>Brötchentaste:</strong> Bachgasse, Alte Schule, Bleichstraße – 60 Min. kostenlos</li><li>Bezahlen mit Münzen oder per Handy am Automaten</li></ul><p><small>Behindertenparkplätze u. a. an den P+R-Plätzen Werkstraße und Bahnhofstraße, am Schlossplatz und auf allen städtischen Parkplätzen.</small></p></div><div class="bs-hit"><h3>⚡ E-Ladesäulen</h3><ul><li>Parkplatz Alte Schule</li><li>Ecke Berggartenstraße / Mainstraße</li><li>Am Bahndamm / Parkplatz Brunnengärten</li></ul></div>' + (pk ? wQuelle(pk) : '');
    }
    if (/katastroph|krisenfall|stromausfall|sirene|warntag|warnung|evakuier|bevölkerungsschutz|schweinepest/.test(l)) {
      var BS = 'https://www.badkoenig.de/leben-wohnen/schutz-hilfe/bevoelkerungsschutz/';
      return '<div class="bs-hit"><h3>⚠️ Was tun im Katastrophenfall?</h3><ul><li><strong>Notruf:</strong> Feuerwehr und Rettungsdienst <a href="tel:112">112</a>, Polizei <a href="tel:110">110</a>.</li><li><strong>Warnungen:</strong> Warn-App <a href="https://www.bbk.bund.de/DE/Warnung-Vorsorge/Warn-App-NINA/warn-app-nina_node.html" target="_blank" rel="noopener">NINA</a>, Radio (hr), Sirenen und Cell Broadcast. Aktuelle Warnungen auch unter <a href="/wichtig.html">Wichtige Meldungen</a>.</li><li><strong>Vorsorge:</strong> Vorrat für 10 Tage, Notgepäck, wichtige Dokumente griffbereit – Checklisten beim <a href="https://www.bbk.bund.de/DE/Warnung-Vorsorge/Vorsorge/vorsorge_node.html" target="_blank" rel="noopener">BBK</a>.</li></ul></div><div class="bs-hit"><h3>🏛️ Infos der Stadt Bad König</h3><p>Die Stadt arbeitet dabei eng mit Feuerwehr, Rettungsdienst, THW und Freiwilligen zusammen. Eigene Hinweise gibt es zu:</p><ul><li><a href="' + BS + 'stromausfall/" target="_blank" rel="noopener">Stromausfall</a></li><li><a href="' + BS + 'afrikanische-schweinepest/" target="_blank" rel="noopener">Afrikanische Schweinepest</a></li><li><a href="' + BS + 'bundesweiter-warntag/" target="_blank" rel="noopener">Warntag</a></li></ul><p><a class="bs-kaffee-btn bs-link-btn" href="' + BS + '" target="_blank" rel="noopener">Bevölkerungsschutz bei der Stadt</a></p></div><p class="bs-src">Quellen: <a href="' + BS + '" target="_blank" rel="noopener">Stadt Bad König</a>, BBK</p>';
    }
    return null;
  }
  var KAFFEE = 'https://bdkng.de/kaffee/';
  function zeige(h) {
    out.innerHTML = h + '<div class="bs-tools"><button type="button" class="bs-speak">🔊 Vorlesen</button></div>';
      var sp = out.querySelector('.bs-speak');
      if (!window.speechSynthesis) sp.hidden = true; else sp.addEventListener('click', function () {
        window.speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance(out.innerText.replace('🔊 Vorlesen', '')); u.lang = 'de-DE'; window.speechSynthesis.speak(u);
      });
  }
  function ki(q, fb) {
    out.innerHTML = '<p class="bs-load">Ich schaue genauer nach …</p>';
    var c = new AbortController(), t = setTimeout(function () { c.abort(); }, 40000);
    fetch('https://n8n.sagmeister.io/webhook/bdkng-frage', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q: q }), signal: c.signal })
      .then(function (r) { return r.json(); }).then(function (j) {
        clearTimeout(t);
        if (j.limit) return zeige('<div class="bs-kaffee"><p><strong>Für heute ist das Limit der KI-Suche erreicht.</strong> ☕</p><p>BDKNG ist ein privates Angebot ohne Werbung und ohne Paywall. Die KI-Suche kostet pro Frage ein paar Cent. Wenn du magst, gib mir einen Kaffee aus – das hilft auch beim Ziel, eine eigene BDKNG-App für iPhone und Android anzubieten. Freiwillig, danke dir! 🙏</p><p><a class="bs-kaffee-btn" href="' + KAFFEE + '" target="_blank" rel="noopener">☕ Kaffee ausgeben</a></p><p class="bs-note">Müll, Termine und Stichworte kannst du weiterhin suchen. Morgen geht die KI-Suche wieder.</p></div>');
        zeige('<p>' + esc(j.antwort || 'Dazu habe ich nichts gefunden.').replace(/\n+/g, '<br>') + '</p><p class="bs-note">KI-Antwort aus den Infos dieser Seite – bitte bei Wichtigem die genannte Quelle prüfen.</p>');
      }).catch(function () { clearTimeout(t); if (fb) return zeige(fb); zeige('<p>Dazu habe ich auf dieser Seite nichts gefunden. Du kannst uns einen Hinweis über das <a href="/kontakt.html?thema=hinweis">Kontaktformular</a> schicken.</p>'); });
  }
  (function () {
    var fld = input.closest('.bs-field'); if (!fld) return;
    var x = document.createElement('button'); x.type = 'button'; x.className = 'bs-clear'; x.hidden = true; x.setAttribute('aria-label', 'Eingabe löschen'); x.textContent = '✕';
    fld.appendChild(x);
    function sync() { x.hidden = !input.value; }
    input.addEventListener('input', sync);
    x.addEventListener('click', function () { input.value = ''; sync(); out.hidden = true; out.innerHTML = ''; input.focus(); });
    form.addEventListener('submit', function () { setTimeout(sync, 0); });
    out.addEventListener('click', function () { setTimeout(sync, 0); });
    setInterval(sync, 600);
  })();
  form.addEventListener('submit', function (e) { e.preventDefault(); antworten(input.value); });
  out.addEventListener('click', function (e) { var b = e.target.closest('.bs-chip'); if (b) { input.value = b.getAttribute('data-q'); antworten(input.value); } });
  box.querySelectorAll('.bs-example').forEach(function (b) { b.addEventListener('click', function () { input.value = b.textContent; antworten(input.value); }); });
  input.addEventListener('focus', laden, { once: true });
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { mic.hidden = true; } else {
    var rec = null;
    mic.addEventListener('click', function () {
      if (rec) { rec.stop(); return; }
      rec = new SR(); rec.lang = 'de-DE'; rec.interimResults = false; rec.maxAlternatives = 1;
      mic.classList.add('on'); mic.setAttribute('aria-pressed', 'true');
      rec.onresult = function (e) { input.value = e.results[0][0].transcript; antworten(input.value); };
      rec.onend = function () { rec = null; mic.classList.remove('on'); mic.setAttribute('aria-pressed', 'false'); };
      rec.onerror = function () { rec = null; mic.classList.remove('on'); };
      rec.start();
    });
  }

  (function () {
    var K = 'bdkng-kaffee-zu', zu = 0;
    try { zu = +localStorage.getItem(K) || 0; } catch (e) {}
    if (Date.now() - zu < 14 * 864e5) return;
    var d = document.createElement('div'); d.className = 'bs-hint';
    d.innerHTML = '<span class="bs-cup" aria-hidden="true">☕</span><span class="bs-txt"><strong>BDKNG ist privat – ohne Werbung, ohne Paywall.</strong> Wenn dir die Infos helfen, freue ich mich über einen Kaffee. Ziel ist eine eigene BDKNG-App für iPhone und Android – jede Spende hilft dabei. Freiwillig, danke dir!</span><a class="bs-gift" href="https://bdkng.de/kaffee/" target="_blank" rel="noopener">Kaffee ausgeben</a><button type="button" aria-label="Hinweis schließen">×</button>';
    d.querySelector('button').addEventListener('click', function () { try { localStorage.setItem(K, Date.now()); } catch (e) {} d.remove(); });
    box.insertAdjacentElement('afterend', d);
  })();
})();
