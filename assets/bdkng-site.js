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
})();
