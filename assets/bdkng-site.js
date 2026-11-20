// Look „Jung“ (Stil C): automatisch aus Instagram/TikTok, sonst gespeicherte Wahl; ?stil=c / ?stil=klassisch zum Testen
(function () {
  try {
    var KRONE = '/assets/bdkng-krone-klein.png', ALT = null;
    window.BDKNG_STIL = function (an) {
      document.documentElement.classList.toggle('stil-c', !!an);
      var img = document.querySelector('.brand-logo img');
      if (img) { if (!ALT) ALT = img.getAttribute('src'); img.setAttribute('src', an ? KRONE : ALT); }
      var hero = document.querySelector('.hero-final > img');
      if (hero) { if (!hero.dataset.alt) hero.dataset.alt = hero.getAttribute('src'); hero.setAttribute('src', an ? '/assets/bdkng-header-neu.jpg' : hero.dataset.alt); }
    };
    var q = new URLSearchParams(location.search).get('stil'), w = null;
    try { if (q === 'c' || q === 'klassisch') localStorage.setItem('bdkngStil', q); w = localStorage.getItem('bdkngStil'); } catch (e) {}
    var app = /Instagram|TikTok|musical_ly|BytedanceWebview|trill/i.test(navigator.userAgent) || /instagram|tiktok/i.test(document.referrer) || /^(ig|instagram|tiktok|tt)$/i.test(new URLSearchParams(location.search).get('utm_source') || '');
    var an = w ? w === 'c' : app;
    if (an) { document.documentElement.classList.add('stil-c'); var los = function () { window.BDKNG_STIL(true); }; if (document.readyState !== 'loading') los(); else document.addEventListener('DOMContentLoaded', los); }
  } catch (e) {}
})();
'use strict';
(function () {
  var PP = 'https://bdkng.de/kaffee/';
  function ready(f) { if (document.readyState !== 'loading') f(); else document.addEventListener('DOMContentLoaded', f); }
  ready(function () {
    var nav = document.querySelector('header nav');
    var dp = null;
    var standalone = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || window.navigator.standalone;
    var ios = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    if (nav && !nav.querySelector('.kaffeenav')) {
      var k = document.createElement('a'); k.className = 'kaffeenav'; k.href = PP; k.target = '_blank'; k.rel = 'noopener';
      k.innerHTML = '<span aria-hidden="true">☕</span> Kaffee'; k.title = 'Kaffee ausgeben – freiwillig, danke dir!';
      var wa = nav.querySelector('.channelnav'); nav.insertBefore(k, wa || null);
      var ib = document.createElement('button'); ib.type = 'button'; ib.className = 'installnav'; ib.hidden = true;
      ib.innerHTML = '<span aria-hidden="true">📲</span> App'; ib.title = 'BDKNG als App installieren';
      nav.insertBefore(ib, k);
      function zeigeInstall() { if (!standalone) ib.hidden = false; }
      if (ios) zeigeInstall();
      window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); dp = e; zeigeInstall(); });
      window.addEventListener('appinstalled', function () { ib.hidden = true; });
      ib.addEventListener('click', function () {
        if (dp) { dp.prompt(); dp.userChoice.then(function () { dp = null; ib.hidden = true; }); return; }
        var m = document.createElement('div'); m.className = 'bs-modal';
        m.innerHTML = '<div class="bs-sheet" role="dialog" aria-modal="true" aria-label="App installieren"><h3>📲 BDKNG als App</h3><ol><li>Tippe unten in Safari auf <strong>Teilen</strong> (Quadrat mit Pfeil).</li><li>Wähle <strong>„Zum Home-Bildschirm“</strong>.</li><li>Tippe auf <strong>Hinzufügen</strong>. Fertig!</li></ol><button type="button" class="bs-sheet-ok">Verstanden</button></div>';
        m.addEventListener('click', function (e) { if (e.target === m || e.target.className === 'bs-sheet-ok') m.remove(); });
        document.body.appendChild(m);
      });
    }
    var main = document.querySelector('main.subpage');
    if (main && !main.querySelector('.backbtn')) {
      var b = document.createElement('a'); b.className = 'backbtn'; b.href = '/#kompakt'; b.innerHTML = '<span aria-hidden="true">←</span> Zurück';
      b.addEventListener('click', function (e) {
        var same = false; try { same = document.referrer && new URL(document.referrer).origin === location.origin; } catch (x) {}
        if (same && history.length > 1) { e.preventDefault(); history.back(); }
      });
      main.insertBefore(b, main.firstChild);
    }
  });
  if ('serviceWorker' in navigator) window.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js').catch(function () {}); });

  ready(function () {
    var nav = document.querySelector('header nav'); if (!nav || nav.querySelector('.menunav')) return;
    var R = [['/aktuell.html','📰','Aktuelles'],['/verkehr.html','🚧','Verkehr'],['/termine.html','📅','Termine & Veranstaltungen'],['/sport.html','⚽','Sport & Vereine'],['/genuss.html','🍽️','Genuss & Gewerbe'],['/wichtig.html','⚠️','Wichtige Meldungen'],['/wetter.html','⛅','Wetter'],['/muell.html','🗑️','Müllabfuhr'],['/kompakt.html','🗞️','Kompakt – alle neuen Meldungen'],['/kontakt.html','✉️','Kontakt & Anregungen']];
    var b = document.createElement('button'); b.type = 'button'; b.className = 'menunav'; b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-label', 'Menü mit allen Rubriken');
    b.innerHTML = '<span aria-hidden="true">☰</span> Menü';
    // Look-Umschalter (Klassisch ↔ Jung), steht links neben dem Menü
    try {
      var sk = document.createElement('button'); sk.type = 'button'; sk.className = 'stil-knopf';
      var setz = function () { var c = document.documentElement.classList.contains('stil-c'); sk.innerHTML = c ? '🎨 <span class="sk-t">Klassisch</span>' : '✨ <span class="sk-t">Neuer Look</span>'; sk.setAttribute('aria-label', c ? 'Zum klassischen Look wechseln' : 'Zum neuen Look wechseln'); };
      sk.addEventListener('click', function () { var c = !document.documentElement.classList.contains('stil-c'); window.BDKNG_STIL(c); try { localStorage.setItem('bdkngStil', c ? 'c' : 'klassisch'); } catch (e) {} setz(); });
      setz(); nav.appendChild(sk);
    } catch (e) {}
    nav.appendChild(b); // Menü ganz rechts
    var p = document.createElement('div'); p.className = 'menupanel'; p.hidden = true;
    p.innerHTML = '<a class="mp-home" href="/">🏠 Startseite</a>' + R.map(function (r) { return '<a href="' + r[0] + '"><span aria-hidden="true">' + r[1] + '</span> ' + r[2].replace('&', '&amp;') + '</a>'; }).join('');
    document.body.appendChild(p);
    function zu() { p.hidden = true; b.setAttribute('aria-expanded', 'false'); }
    b.addEventListener('click', function (e) { e.stopPropagation(); if (!p.hidden) return zu(); p.style.top = document.querySelector('header').getBoundingClientRect().bottom + 'px'; p.hidden = false; b.setAttribute('aria-expanded', 'true'); });
    document.addEventListener('click', function (e) { if (!p.contains(e.target)) zu(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') zu(); });
    window.addEventListener('scroll', zu, { passive: true });
  });
})();

/* BDKNG weiterempfehlen (13.11.2026) */
(function () {
  var TEXT = 'Kennst du schon BDKNG? Dein Info-Kanal rund um Bad König: News, Termine, Müll, Verkehr, KI-Suche und der Blitzer- & Stau-Melder.';
  var URL = 'https://bdkng.de/';
  var menu = null;
  function schliessen() { if (menu) { menu.remove(); menu = null; document.removeEventListener('click', aussen, true); } }
  function aussen(ev) { if (menu && !menu.contains(ev.target)) schliessen(); }
  function teilen(e) {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    var mobil = window.matchMedia && matchMedia('(pointer: coarse)').matches;
    if (mobil && navigator.share) { navigator.share({ title: 'BDKNG – Bad König kompakt', text: TEXT, url: URL }).catch(function () {}); return; }
    if (menu) { schliessen(); return; }
    var t = encodeURIComponent(TEXT + ' ' + URL);
    menu = document.createElement('div');
    menu.setAttribute('role', 'dialog'); menu.setAttribute('aria-label', 'BDKNG weiterempfehlen');
    menu.style.cssText = 'position:fixed;z-index:9999;left:50%;top:50%;transform:translate(-50%,-50%);background:#fff;color:#10201a;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.35);padding:18px 18px 12px;width:min(320px,90vw);font:15px/1.4 Inter,system-ui,sans-serif';
    var b = 'display:block;padding:11px 14px;margin:0 0 8px;border-radius:12px;background:#edf5ec;color:#10201a;text-decoration:none;font-weight:700;border:0;width:100%;text-align:left;cursor:pointer;font:inherit;font-weight:700';
    menu.innerHTML = '<p style="margin:0 0 12px;font-weight:800">💚 BDKNG weiterempfehlen</p>' +
      '<a style="' + b + '" target="_blank" rel="noopener" href="https://wa.me/?text=' + t + '">WhatsApp</a>' +
      '<a style="' + b + '" target="_blank" rel="noopener" href="https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(URL) + '">Facebook</a>' +
      '<a style="' + b + '" href="mailto:?subject=' + encodeURIComponent('Tipp: BDKNG – Bad König kompakt') + '&body=' + t + '">E-Mail</a>' +
      '<button type="button" data-k style="' + b + '">Link kopieren</button>' +
      (navigator.share ? '<button type="button" data-s style="' + b + '">Weitere Apps …</button>' : '') +
      '<button type="button" data-x style="' + b + ';background:none;text-align:center;font-weight:600">Schließen</button>';
    document.body.appendChild(menu);
    menu.querySelector('[data-k]').addEventListener('click', function () { var k = this; (navigator.clipboard ? navigator.clipboard.writeText(TEXT + ' ' + URL) : Promise.reject()).then(function () { k.textContent = '✔ Kopiert'; }).catch(function () { prompt('Link kopieren:', URL); }); });
    var sb = menu.querySelector('[data-s]'); if (sb) sb.addEventListener('click', function () { navigator.share({ title: 'BDKNG', text: TEXT, url: URL }).catch(function () {}); schliessen(); });
    menu.querySelector('[data-x]').addEventListener('click', schliessen);
    menu.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', function () { setTimeout(schliessen, 100); }); });
    setTimeout(function () { document.addEventListener('click', aussen, true); }, 0);
  }
  function init() {
    document.querySelectorAll('[data-bdkng-share]').forEach(function (b) { b.addEventListener('click', teilen); });
    var h = Array.prototype.filter.call(document.querySelectorAll('footer h4'), function (x) { return /Folgen/.test(x.textContent); })[0];
    if (h && h.nextElementSibling && !document.getElementById('bdkngShareFoot')) {
      var a = document.createElement('a'); a.href = '#'; a.id = 'bdkngShareFoot'; a.textContent = '💚 BDKNG weiterempfehlen';
      a.addEventListener('click', teilen);
      h.nextElementSibling.appendChild(document.createElement('br')); h.nextElementSibling.appendChild(a);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* Datensparsamer Zugriffszähler: keine Cookies, keine IP-Speicherung, nicht sichtbar.
   Nichts wird im Browser gespeichert. Übertragen werden nur Seite, ob der Besuch von außen kommt, und die Herkunftsseite (nur Domain).
   Eigene Aufrufe ausschließen: bdkng.de/?ich=1 aufrufen (wieder zählen: ?ich=0). */
(function () {
  try {
    var q = location.search;
    if (/[?&]ich=1/.test(q)) localStorage.setItem('bdkng_ich', '1');
    if (/[?&]ich=0/.test(q)) localStorage.removeItem('bdkng_ich');
    if (localStorage.getItem('bdkng_ich') || navigator.doNotTrack === '1' || !/(^|\.)bdkng\.de$/.test(location.hostname)) return;
    var ref = document.referrer || '', intern = ref.indexOf('://' + location.hostname) > 0 || ref.indexOf('://www.' + location.hostname) > 0;
    var neu = !intern, r = neu && ref ? ref.split('/').slice(0, 3).join('/') : '';
    var d = JSON.stringify({ p: location.pathname, n: neu ? 1 : 0, r: r }), u = 'https://n8n.sagmeister.io/webhook/bdkng-zugriff';
    if (navigator.sendBeacon) navigator.sendBeacon(u, new Blob([d], { type: 'text/plain' }));
    else fetch(u, { method: 'POST', body: d, mode: 'no-cors', keepalive: true });
  } catch (e) {}
})();
// "Nach oben": unter jedem Kasten einer Rubrikseite und als schwebender Knopf beim Scrollen
(function () {
  try {
    function knopf() { var a = document.createElement('a'); a.className = 'nach-oben'; a.href = '#'; a.setAttribute('aria-label', 'Nach oben'); a.textContent = '↑ nach oben'; a.addEventListener('click', function (e) { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }); return a; }
    function setzen() { [].forEach.call(document.querySelectorAll('main .subpanel, .sp-sek'), function (s) { if (s.hidden || s.querySelector(':scope > .nach-oben')) return; if (s.offsetHeight < 260 && !/^(verkehrStatus|sprit)$/.test(s.id)) return; s.appendChild(knopf()); }); }
    [].forEach.call(document.querySelectorAll('.news-entry .nach-oben'), function (a) { a.addEventListener('click', function (e) { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }); });
    var f = document.createElement('button'); f.type = 'button'; f.className = 'nach-oben-fix'; f.setAttribute('aria-label', 'Nach oben'); f.textContent = '↑'; f.hidden = true;
    f.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
    document.addEventListener('DOMContentLoaded', function () { document.body.appendChild(f); setzen(); setTimeout(setzen, 2500); setTimeout(setzen, 6000); });
    if (document.readyState !== 'loading') { document.body.appendChild(f); setzen(); setTimeout(setzen, 2500); setTimeout(setzen, 6000); }
    window.addEventListener('scroll', function () { f.hidden = window.scrollY < 700; }, { passive: true });
  } catch (e) {}
})();

// Kopfzeile: Rubrik-Leiste – aktive Rubrik in den sichtbaren Bereich schieben
(function () { try { var a = document.querySelector('.kopf-rub a[aria-current="page"]'); if (a) { var n = a.closest('.kopf-rub'); n.scrollLeft = Math.max(0, a.offsetLeft - 16); } } catch (e) {} })();
// Sprung-Knöpfe zu den Abschnitten einer Seite (Termine, Verkehr) – wie bei Sport
(function () {
  try {
    var P = {
      '/termine.html': [['#terminMelden', 'terminMelden', '📣 Termin melden & prüfen'], ['#dieseWoche', 'dieseWoche', '📅 Diese Woche'], ['#kalender', 'kalender', '📆 Kalender 3 Monate', function () { var b = document.querySelector('.tk-f[data-f="alle"]'); if (b) b.click(); }], ['#kalender', 'kalender', '⛪ Kirche & Gedenken', function () { var b = document.querySelector('.tk-f[data-f="kirche"]'); if (b) b.click(); }], ['#kalender', 'kalender', '🗓️ Feiertage', function () { var b = document.querySelector('.tk-f[data-f="feiertag"]'); if (b) b.click(); }], ['#freilicht', 'freilicht', '🎭 Freilichtbühne'], [function () { return [].find.call(document.querySelectorAll('.news-entry'), function (a) { return !a.hidden && /Therme|Sauna/i.test((a.querySelector('h2') || {}).textContent || ''); }); }, 'therme', '♨️ Therme'], ['.news-list', 'meldungen', '📰 Meldungen']],
      '/verkehr.html': [['#verkehrStatus', 'verkehrStatus', '🚦 Aktuelle Behinderungen'], ['#sprit', 'sprit', '⛽ Tanken'], ['.news-list', 'meldungen', '🚧 Verkehrsmeldungen'], ['#blitzer', 'blitzer', '📸 Blitzer & Stau-Melder'], ['.verkehr-links', 'links', '🔗 Links']]
    }[location.pathname];
    if (!P) return;
    // Verkehr: Reihenfolge der Abschnitte = Reihenfolge der Knöpfe (Behinderungen, Tanken, Meldungen, Blitzer/Melder, Links)
    function ordnen() {
      if (location.pathname !== '/verkehr.html') return;
      var hero = document.querySelector('main .subhero'); if (!hero) return;
      var nach = hero;
      ['#verkehrStatus', '#sprit', '.news-list', '#blitzer', '.verkehr-links'].forEach(function (q) { var el = document.querySelector(q); if (el) { nach.insertAdjacentElement('afterend', el); nach = el; } });
    }
    function bauen() {
      ordnen();
      var alt = document.querySelector('.sprung-nav'); if (alt) alt.remove();
      var nav = document.createElement('nav'); nav.className = 'sprung-nav'; nav.setAttribute('aria-label', 'Abschnitte dieser Seite');
      P.forEach(function (x) {
        var el = typeof x[0] === 'function' ? x[0]() : document.querySelector(x[0]);
        if (!el || el.hidden) return;
        if (!el.id) el.id = x[1];
        var a = document.createElement('a'); a.href = '#' + el.id; a.textContent = x[2];
        a.addEventListener('click', function (e) { e.preventDefault(); if (x[3]) x[3](); var h = (document.querySelector('header') || {}).offsetHeight || 0; window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - h - 10, behavior: 'smooth' }); });
        nav.appendChild(a);
      });
      if (!nav.children.length) return;
      var hero = document.querySelector('main .subhero'); if (hero) hero.insertAdjacentElement('afterend', nav);
    }
    function los() { bauen(); setTimeout(bauen, 2500); setTimeout(bauen, 6000); }
    if (document.readyState !== 'loading') los(); else document.addEventListener('DOMContentLoaded', los);
  } catch (e) {}
})();
// Admin-Knopf (nur auf Geräten, die einmal bdkng.de/?admin=an aufgerufen haben): öffnet die Post-Liste im Cockpit (Teilen/Löschen)
(function () {
  try {
    var q = new URLSearchParams(location.search).get('admin');
    if (q === 'an') localStorage.setItem('bdkngAdmin', '1'); if (q === 'aus') localStorage.removeItem('bdkngAdmin');
    if (localStorage.getItem('bdkngAdmin') !== '1') return;
    var a = document.createElement('a'); a.className = 'admin-knopf'; a.href = 'https://n8n.sagmeister.io/webhook/cockpit?f=posts.html'; a.target = '_blank'; a.rel = 'noopener';
    a.innerHTML = '🛠️ <span>Posts teilen/löschen</span>';
    (document.body ? Promise.resolve() : new Promise(function (r) { document.addEventListener('DOMContentLoaded', r); })).then(function () { document.body.appendChild(a); });
  } catch (e) {}
})();
// Kopf-Leiste (bleibt oben stehen, alle Seiten): Wetter jetzt + günstigster Spritpreis
(function () {
  function ready(f) { if (document.readyState !== 'loading') f(); else document.addEventListener('DOMContentLoaded', f); }
  ready(function () {
    var hd = document.querySelector('body > header'); if (!hd || hd.querySelector('.kopf-info')) return;
    var ICON = { 'clear-day': '☀️', 'clear-night': '🌙', 'partly-cloudy-day': '⛅', 'partly-cloudy-night': '☁️', 'cloudy': '☁️', 'fog': '🌫️', 'wind': '💨', 'rain': '🌧️', 'sleet': '🌨️', 'snow': '❄️', 'hail': '🌨️', 'thunderstorm': '⛈️' };
    var bar = document.createElement('div'); bar.className = 'kopf-info'; bar.hidden = true;
    bar.innerHTML = '<div class="ki-in"><a class="ki-wetter" href="/wetter.html" hidden></a><a class="ki-sprit" href="/verkehr.html#sprit" hidden></a><a class="ki-karten" href="/speisekarten.html"><span aria-hidden="true">🍽️</span> Speisekarten</a></div>'; bar.hidden = false;
    hd.insertBefore(bar, hd.firstChild);
    function hoehe() { document.documentElement.style.setProperty('--kopf-h', hd.getBoundingClientRect().height + 'px'); }
    function zeig(a, h) { a.innerHTML = h; a.hidden = false; bar.hidden = false; hoehe(); }
    fetch('/data/wetter-aktuell.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
      var j = d.jetzt || {}, t = (d.tage || [])[0] || {}; if (j.temp == null) return;
      zeig(bar.querySelector('.ki-wetter'), '<span aria-hidden="true">' + (ICON[j.icon] || '🌦️') + '</span> <b>' + Math.round(j.temp) + ' °C</b>' + (t.tmin != null ? '<span class="ki-lang"> · heute ' + Math.round(t.tmin) + '–' + Math.round(t.tmax) + ' °C</span>' : '') + (t.regen >= 1 ? ' <span aria-label="Regen">☔</span>' : ''));
    }).catch(function () {});
    fetch('https://n8n.sagmeister.io/webhook/bdkng-sprit', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
      if (!d.leiste) return;
      zeig(bar.querySelector('.ki-sprit'), '<span aria-hidden="true">⛽</span> ' + String(d.leiste).replace(/ ab /g, ' ').replace(/ €/g, '€').replace(/ · (.*)$/, '<span class="ki-lang"> · $1</span>'));
    }).catch(function () {});
    hoehe(); window.addEventListener('resize', hoehe);
  });
})();
// „Überblick statt Zeitung“ in den Rubriken: nur angetextet, aufklappbar, beim Laden immer zu (Handy + PC)
(function () {
  function ready(f) { if (document.readyState !== 'loading') f(); else document.addEventListener('DOMContentLoaded', f); }
  ready(function () {
    document.querySelectorAll('.subhero-note').forEach(function (p, i) {
      if (p.dataset.klapp) return; p.dataset.klapp = '1';
      var id = 'snText' + i, inner = document.createElement('span'); inner.className = 'sn-text'; inner.id = id;
      while (p.firstChild) inner.appendChild(p.firstChild);
      var b = document.createElement('button'); b.type = 'button'; b.className = 'sn-mehr'; b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', id); b.textContent = 'mehr ▾';
      p.appendChild(inner); p.appendChild(b); p.classList.add('sn-zu');
      b.addEventListener('click', function () { var zu = p.classList.toggle('sn-zu'); b.setAttribute('aria-expanded', zu ? 'false' : 'true'); b.textContent = zu ? 'mehr ▾' : 'weniger ▴'; });
    });
  });
})();
