// Daumen hoch für jede Meldung: anonym gezählt (keine IP, keine Cookies), Merken nur im eigenen Browser
(function () {
  var L = document.querySelectorAll('.news-list .news-entry[id]'); if (!L.length) return;
  var URL_G = 'https://n8n.sagmeister.io/webhook/bdkng-daumen', URL_L = 'https://n8n.sagmeister.io/webhook/bdkng-daumen-liste';
  var mein = {}; try { mein = JSON.parse(localStorage.getItem('bdkngDaumen') || '{}'); } catch (e) {}
  function merken() { try { localStorage.setItem('bdkngDaumen', JSON.stringify(mein)); } catch (e) {} }
  function txt(b, n) { b.querySelector('.dh-n').textContent = n > 0 ? n : ''; b.classList.toggle('an', !!mein[b.dataset.id]); b.setAttribute('aria-pressed', mein[b.dataset.id] ? 'true' : 'false'); }
  var knoepfe = [];
  [].forEach.call(L, function (a) {
    if (a.querySelector('.dh')) return;
    var b = document.createElement('button'); b.type = 'button'; b.className = 'dh'; b.dataset.id = a.id; b.dataset.n = '0';
    b.setAttribute('aria-label', 'Daumen hoch für diese Meldung');
    b.innerHTML = '<span aria-hidden="true">👍</span> <span class="dh-t">Gefällt mir</span> <span class="dh-n"></span>';
    b.addEventListener('click', function () {
      var weg = !!mein[a.id], n = +b.dataset.n + (weg ? -1 : 1);
      if (weg) delete mein[a.id]; else mein[a.id] = 1; merken();
      b.dataset.n = Math.max(0, n); txt(b, +b.dataset.n);
      try { fetch(URL_G, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ id: a.id, weg: weg ? 1 : 0 }) }).then(function (r) { return r.json(); }).then(function (d) { if (d && d.ok) { b.dataset.n = d.n; txt(b, d.n); } }).catch(function () {}); } catch (e) {}
    });
    var q = a.querySelector('.source'), oben = a.querySelector('.nach-oben');
    if (q) q.insertAdjacentElement('afterend', b); else if (oben) a.insertBefore(b, oben); else a.appendChild(b);
    knoepfe.push(b); txt(b, 0);
  });
  fetch(URL_L, { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (o) { knoepfe.forEach(function (b) { b.dataset.n = o[b.dataset.id] || 0; txt(b, +b.dataset.n); }); }).catch(function () {});
})();
