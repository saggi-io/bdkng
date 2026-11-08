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
      fetch('/data/sport-termine.json').then(function (r) { return r.json(); }).catch(function () { return null; })]).then(function (a) { data.muell = a[0]; data.news = a[1] || []; data.spiele = a[2] && a[2].spiele || []; });
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
    else if (/wochenende/.test(l)) { var wd = new Date(t + 'T12:00:00Z').getUTCDay(); var sa = plus(t, (6 - wd + 7) % 7); tage = [plus(sa, -1), sa, plus(sa, 1)]; }
    tage = tage.filter(function (d) { return d >= t; });
    var dm = l.match(/(\d{1,2})\.(\d{1,2})\./); if (dm) { tage = [t.slice(0, 4) + '-' + ('0' + dm[2]).slice(-2) + '-' + ('0' + dm[1]).slice(-2)]; }
    if (!tage.length) return /wochenende|heute|morgen/.test(l) ? '<p>Dafür habe ich keine kommenden Termine gefunden.</p>' : null;
    var treffer = [];
    data.news.forEach(function (n) {
      if (n.categories.indexOf('termine') < 0) return;
      n.paragraphs.forEach(function (p) { tage.forEach(function (d) { if (p.indexOf(d.slice(8) + '.' + d.slice(5, 7) + '.') >= 0 && p.length < 400) treffer.push({ p: p, n: n }); }); });
    });
    var sp = (data.spiele || []).filter(function (x) { return tage.indexOf(x.date) >= 0; });
    if (sp.length) {
      var hs = '<ul>';
      sp.forEach(function (x) { hs += '<li>' + esc(deDatum(x.date)) + ', ' + esc(x.time) + ' Uhr: Fußball – ' + esc(x.home) + ' – ' + esc(x.away) + '<br><small>Quelle: <a href="https://www.fupa.net/club/tsg-bad-koenig" target="_blank" rel="noopener">FuPa</a></small></li>'; });
      var seen0 = {}; treffer.forEach(function (x) { if (seen0[x.p]) return; seen0[x.p] = 1; hs += '<li>' + esc(x.p) + '<br><small>Quelle: <a href="' + esc(x.n.url) + '" target="_blank" rel="noopener">' + esc(x.n.source) + '</a></small></li>'; });
      return hs + '</ul>';
    }
    if (!treffer.length) return '<p>Dafür habe ich keine Termine gefunden. Schau in <a href="/termine.html">Termine &amp; Veranstaltungen</a>.</p>';
    var seen = {}, h = '<ul>';
    treffer.forEach(function (x) { if (seen[x.p]) return; seen[x.p] = 1; h += '<li>' + esc(x.p) + '<br><small>Quelle: <a href="' + esc(x.n.url) + '" target="_blank" rel="noopener">' + esc(x.n.source) + '</a></small></li>'; });
    return h + '</ul>';
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
      if (/müll|muell|abfall|abfuhr|tonne|sack|säcke|saecke|papier|biotonne|restmüll|sperrmüll|schadstoff|sonderabfall/i.test(q)) h = muellAntwort(q);
      if (!h) h = spieleAntwort(q);
      if (!h) h = terminAntwort(q);
      if (!h) h = news(q);
      if (!h) return ki(q);
      zeige(h);
    });
  }
  var KAFFEE = 'https://paypal.me/saggi';
  function zeige(h) {
    out.innerHTML = h + '<div class="bs-tools"><button type="button" class="bs-speak">🔊 Vorlesen</button></div>';
      var sp = out.querySelector('.bs-speak');
      if (!window.speechSynthesis) sp.hidden = true; else sp.addEventListener('click', function () {
        window.speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance(out.innerText.replace('🔊 Vorlesen', '')); u.lang = 'de-DE'; window.speechSynthesis.speak(u);
      });
  }
  function ki(q) {
    out.innerHTML = '<p class="bs-load">Ich schaue genauer nach …</p>';
    var c = new AbortController(), t = setTimeout(function () { c.abort(); }, 40000);
    fetch('https://n8n.sagmeister.io/webhook/bdkng-frage', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q: q }), signal: c.signal })
      .then(function (r) { return r.json(); }).then(function (j) {
        clearTimeout(t);
        if (j.limit) return zeige('<div class="bs-kaffee"><p><strong>Für heute ist das Limit der KI-Suche erreicht.</strong> ☕</p><p>BDKNG ist ein privates Angebot ohne Werbung und ohne Paywall. Die KI-Suche kostet pro Frage ein paar Cent. Wenn du magst, gib mir einen Kaffee aus – freiwillig, danke dir! 🙏</p><p><a class="bs-kaffee-btn" href="' + KAFFEE + '" target="_blank" rel="noopener">☕ Kaffee ausgeben</a></p><p class="bs-note">Müll, Termine und Stichworte kannst du weiterhin suchen. Morgen geht die KI-Suche wieder.</p></div>');
        zeige('<p>' + esc(j.antwort || 'Dazu habe ich nichts gefunden.').replace(/\n+/g, '<br>') + '</p><p class="bs-note">KI-Antwort aus den Infos dieser Seite – bitte bei Wichtigem die genannte Quelle prüfen.</p>');
      }).catch(function () { clearTimeout(t); zeige('<p>Dazu habe ich auf dieser Seite nichts gefunden. Du kannst uns einen Hinweis über das <a href="/kontakt.html?thema=hinweis">Kontaktformular</a> schicken.</p>'); });
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
    d.innerHTML = '<span class="bs-cup" aria-hidden="true">☕</span><span class="bs-txt"><strong>BDKNG ist privat – ohne Werbung, ohne Paywall.</strong> Wenn dir die Infos helfen, freue ich mich über einen Kaffee. Freiwillig, danke dir!</span><a class="bs-gift" href="https://paypal.me/saggi" target="_blank" rel="noopener">Kaffee ausgeben</a><button type="button" aria-label="Hinweis schließen">×</button>';
    d.querySelector('button').addEventListener('click', function () { try { localStorage.setItem(K, Date.now()); } catch (e) {} d.remove(); });
    box.insertAdjacentElement('afterend', d);
  })();
})();
