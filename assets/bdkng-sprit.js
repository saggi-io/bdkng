// Spritpreise auf der Verkehrsseite: die drei günstigsten offenen Tankstellen je Sorte im Umkreis von 15 km
(function () {
  var URL = 'https://n8n.sagmeister.io/webhook/bdkng-sprit';
  function e(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function preis(p) { var s = p.toFixed(3).replace('.', ','); return s.slice(0, -1) + '<sup>' + s.slice(-1) + '</sup> €'; }
  function gross(s) { return /^[^a-zäöü]*$/.test(s) ? s.toLowerCase().replace(/(^|[\s\-\/])(\S)/g, function (m, a, b) { return a + b.toUpperCase(); }) : s; }
  function spalte(t, l) {
    if (!l || !l.length) return '';
    return '<div class="sp-sorte"><h3>' + t + '</h3><ol>' + l.map(function (x) {
      var q = encodeURIComponent([x.name, gross(x.strasse), x.ort].join(' '));
      return '<li><span class="sp-preis">' + preis(x.preis) + '</span><span class="sp-ort"><b>' + e(gross(x.name)) + '</b> · ' + e(x.ort) + ' (' + String(x.km).replace('.', ',') + ' km)<br><a href="https://www.google.com/maps/search/?api=1&query=' + q + '" target="_blank" rel="noopener">' + e(gross(x.strasse)) + '</a></span></li>';
    }).join('') + '</ol></div>';
  }
  function zeigen(d) {
    var hero = document.querySelector('main .subhero'); if (!hero || !d || !d.e10) return;
    var sec = document.getElementById('sprit');
    if (!sec) { sec = document.createElement('section'); sec.className = 'subpanel sprit-box'; sec.id = 'sprit'; var vs = document.getElementById('verkehrStatus'); (vs || hero).insertAdjacentElement('afterend', sec); }
    sec.innerHTML = '<h2>⛽ Günstig tanken rund um Bad König</h2><p class="sp-unter">Die drei günstigsten <b>geöffneten</b> Tankstellen je Sorte im Umkreis von 15 km. Stand: ' + e(d.standText) + '</p>' +
      '<div class="sp-grid">' + spalte('Super E10', d.e10) + spalte('Super E5', d.e5) + spalte('Diesel', d.diesel) + '</div>' +
      '<p class="sp-quelle">Preise ändern sich laufend – alle Angaben ohne Gewähr. Quelle: Markttransparenzstelle für Kraftstoffe (MTS-K) über <a href="https://creativecommons.tankerkoenig.de" target="_blank" rel="noopener">Tankerkönig</a>, Lizenz <a href="https://creativecommons.org/licenses/by/4.0/deed.de" target="_blank" rel="noopener">CC BY 4.0</a>.</p>';
    if (location.hash === '#sprit') setTimeout(function () { sec.scrollIntoView(); }, 50);
  }
  fetch(URL, { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(zeigen).catch(function () {});
})();
