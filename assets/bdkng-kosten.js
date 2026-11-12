'use strict';
(function () {
  var box = document.getElementById('bdkng-kosten'); if (!box) return;
  fetch('/data/kosten.json').then(function (r) { return r.json(); }).then(function (k) {
    var eur = function (n) { return n.toFixed(2).replace('.', ',') + ' €'; };
    var summe = k.posten.reduce(function (s, p) { return s + p.monat; }, 0), sp = k.spenden_monat || 0, pz = Math.min(100, Math.round(sp / summe * 100));
    box.querySelector('.ks-summe').textContent = eur(summe);
    box.querySelector('.kosten-balken i').style.width = pz + '%';
    box.querySelector('.ks-sp').textContent = 'gespendet: ' + eur(sp);
    box.title = 'Server, Domains und KI. BDKNG ist werbefrei – dein Kaffee hilft beim Betrieb und beim Ziel einer eigenen BDKNG-App.';
    box.hidden = false;
  }).catch(function () {});
})();
