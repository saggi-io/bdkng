'use strict';
(function () {
  var PP = 'https://paypal.me/saggi';
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
    var R = [['/aktuell.html','📰','Aktuelles'],['/verkehr.html','🚧','Verkehr'],['/termine.html','📅','Termine & Veranstaltungen'],['/sport.html','⚽','Sport & Vereine'],['/genuss.html','🍽️','Genuss & Gewerbe'],['/wichtig.html','⚠️','Wichtige Meldungen'],['/wetter.html','⛅','Wetter'],['/muell.html','🗑️','Müllabfuhr'],['/kontakt.html','✉️','Kontakt']];
    var b = document.createElement('button'); b.type = 'button'; b.className = 'menunav'; b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-label', 'Menü mit allen Rubriken');
    b.innerHTML = '<span aria-hidden="true">☰</span> Menü';
    var logo = nav.querySelector('.brand'); nav.insertBefore(b, logo ? logo.nextSibling : nav.firstChild);
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
