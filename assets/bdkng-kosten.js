'use strict';
(function () {
  var box = document.getElementById('bdkng-kosten'); if (!box) return;
  fetch('/data/kosten.json').then(function (r) { return r.json(); }).then(function (k) {
    var e = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var eur = function (n) { return n.toFixed(2).replace('.', ',') + ' €'; };
    var summe = k.posten.reduce(function (s, p) { return s + p.monat; }, 0), sp = k.spenden_monat || 0, pz = Math.min(100, Math.round(sp / summe * 100));
    box.querySelector('.kosten-liste').innerHTML = k.posten.map(function (p) { return '<li><span>' + e(p.name) + '</span><b>' + eur(p.monat) + '</b></li>'; }).join('') + '<li class="summe"><span>Zusammen pro Monat</span><b>' + eur(summe) + '</b></li>';
    box.querySelector('.kosten-balken i').style.width = pz + '%';
    box.querySelector('.kosten-text').textContent = 'Diesen Monat gespendet: ' + eur(sp) + ' von ' + eur(summe) + ' (' + pz + ' %)';
    box.hidden = false;
  }).catch(function () {});
})();
