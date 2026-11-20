// Speisekarte: Suche/Filter + Original-Karte im Vollbild zum Zoomen
(function () {
  var f = document.getElementById('skFilter'), leer = document.getElementById('skLeer');
  if (f) f.addEventListener('input', function () {
    var q = f.value.trim().toLowerCase().replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ä/g, 'ae');
    var treffer = 0;
    document.querySelectorAll('.sk-gruppe').forEach(function (g) {
      var n = 0;
      g.querySelectorAll('.sk-liste li').forEach(function (li) {
        var t = (g.querySelector('h2').textContent + ' ' + li.textContent).toLowerCase().replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ä/g, 'ae');
        if (/vegetar|veggie/.test(q) && !/Getränke/.test(g.querySelector('h2').textContent) && !/fleisch|schinken|salami|thunfisch|sucuk|hähnchen|peperoniwurst|meeres|hack|nuggets|schnitzel|lahmacun|drehspieß|döner|kebab|ketchup|sauce$/i.test(li.textContent)) t += ' vegetarisch veggie';
        var ok = !q || q.split(/\s+/).every(function (w) { return t.indexOf(w) >= 0; });
        li.hidden = !ok; if (ok) n++;
      });
      g.hidden = !n; treffer += n;
    });
    if (leer) leer.hidden = treffer > 0;
  });
  var z = document.querySelector('.sk-zoom'); if (!z) return;
  z.addEventListener('click', function () {
    var o = document.createElement('div'); o.className = 'sk-voll';
    o.innerHTML = '<img src="' + z.querySelector('img').getAttribute('src') + '" alt="Speisekarte groß">';
    var b = document.createElement('button'); b.type = 'button'; b.className = 'sk-voll-zu'; b.textContent = '✕ Schließen';
    function zu() { o.remove(); b.remove(); document.documentElement.style.overflow = ''; }
    b.addEventListener('click', zu);
    document.addEventListener('keydown', function k(ev) { if (ev.key === 'Escape') { zu(); document.removeEventListener('keydown', k); } });
    document.body.appendChild(o); document.body.appendChild(b); document.documentElement.style.overflow = 'hidden';
  });
})();
