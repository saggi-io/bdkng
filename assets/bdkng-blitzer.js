(function () {
  var box = document.getElementById('blitzer'); if (!box) return;
  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function de(iso) { return iso.slice(8, 10) + '.' + iso.slice(5, 7) + '.' + iso.slice(0, 4); }
  fetch('/data/blitzer.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
    var h = '';
    var ms = d.messstellen || [];
    h += '<h3>👮 Von der Polizei angekündigte Messstellen</h3>';
    h += ms.length ? '<ul class="bz-list">' + ms.map(function (m) {
      return '<li><strong>' + esc(de(m.datum)) + ':</strong> ' + esc(m.titel) + (m.text ? '<br><small>' + esc(m.text) + '</small>' : '') + ' <a class="text-link" href="' + esc(m.link) + '" target="_blank" rel="noopener">Meldung lesen ↗</a></li>';
    }).join('') + '</ul>' : '<p class="form-note">Zurzeit hat die Polizei Südhessen keine Messstellen für den Odenwaldkreis veröffentlicht. Mobile Kontrollen sind trotzdem jederzeit möglich.</p>';
    var g = {}; (d.fest || []).forEach(function (x) { var k = x.ort + '|' + x.strasse + '|' + x.ref + '|' + x.tempo; if (g[k]) g[k].n++; else { g[k] = Object.assign({ n: 1 }, x); } });
    var f = Object.keys(g).map(function (k) { return g[k]; }).sort(function (a, b) { return ((a.ort === 'Bad König' ? '0' : '1') + a.ort + a.strasse).localeCompare((b.ort === 'Bad König' ? '0' : '1') + b.ort + b.strasse, 'de'); });
    h += '<h3>📷 Feste Blitzer rund um Bad König</h3>';
    h += f.length ? '<ul class="bz-list">' + f.map(function (x) {
      var rf = (x.ref || '').replace(/;/g, ' / '), wo = [x.strasse, rf && x.strasse.indexOf(x.ref) < 0 ? rf : ''].filter(Boolean).join(' / ') || 'Straße unbekannt';
      return '<li><strong>' + esc(x.ort || 'Umgebung') + ':</strong> ' + esc(wo) + (x.tempo ? ' · ' + esc(x.tempo) + ' km/h' : '') + (x.art !== 'Tempo' ? ' · ' + esc(x.art) : '') + (x.n > 1 ? ' · ' + x.n + ' Geräte' : '') + ' <a class="text-link" href="https://www.openstreetmap.org/?mlat=' + x.lat + '&amp;mlon=' + x.lon + '#map=17/' + x.lat + '/' + x.lon + '" target="_blank" rel="noopener">Karte ↗</a></li>';
    }).join('') + '</ul>' : '<p class="form-note">In OpenStreetMap ist im Umkreis zurzeit kein fester Blitzer eingetragen.</p>';
    h += '<p class="form-note">' + esc(d.hinweis) + ' Quellen: feste Blitzer ' + esc(d.fest_quelle.replace(/, https.*/, '')) + ' (<a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">Lizenz</a>); Messstellen: <a href="https://www.presseportal.de/blaulicht/nr/4969" target="_blank" rel="noopener">Polizeipräsidium Südhessen</a>. Stand: ' + esc(de(d.stand.slice(0, 10))) + '.</p>';
    document.getElementById('blitzerDaten').innerHTML = h;
  }).catch(function () { document.getElementById('blitzerDaten').innerHTML = '<p class="form-note">Blitzer-Daten gerade nicht verfügbar.</p>'; });
})();
