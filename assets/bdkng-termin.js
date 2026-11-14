/* BDKNG: Termin melden (Vereine, Gastronomie, Veranstalter) – Meldung geht zur Prüfung an BDKNG */
(function () {
  var URL_MELDEN = 'https://n8n.sagmeister.io/webhook/bdkng-termin-melden';
  function el(t, a, h) { var e = document.createElement(t); for (var k in (a || {})) e.setAttribute(k, a[k]); if (h != null) e.innerHTML = h; return e; }
  function init() {
    var box = document.getElementById('terminMelden');
    if (!box) return;
    var vorwahl = box.getAttribute('data-art') || 'veranstaltung';
    var btn = box.querySelector('.tm-open');
    var heute = new Date(); var iso = heute.getFullYear() + '-' + String(heute.getMonth() + 1).padStart(2, '0') + '-' + String(heute.getDate()).padStart(2, '0');
    var form = el('form', { id: 'tmForm', hidden: '', novalidate: '' });
    form.innerHTML =
      '<label class="field"><span>Was findet statt? *</span><input name="titel" maxlength="120" required placeholder="z. B. Schlachtfest, Konzert, Jahreshauptversammlung"></label>' +
      '<div class="form-row"><label class="field"><span>Datum *</span><input name="datum" type="date" min="' + iso + '" required></label>' +
      '<label class="field"><span>Uhrzeit</span><input name="uhrzeit" type="time"></label></div>' +
      '<div class="form-row"><label class="field"><span>Bis (bei mehrtägigen Terminen)</span><input name="bis" type="date" min="' + iso + '"></label>' +
      '<label class="field"><span>Art</span><select name="art">' +
      '<option value="veranstaltung">Veranstaltung / Fest / Markt</option><option value="verein">Verein</option><option value="gastro">Kneipe / Restaurant / Café</option><option value="sport">Sport</option><option value="kultur">Kultur / Konzert / Lesung</option><option value="sonstiges">Sonstiges</option></select></label></div>' +
      '<div class="form-row"><label class="field"><span>Ort *</span><input name="ort" maxlength="120" required placeholder="z. B. Rentmeisterei, Schlossplatz 2"></label>' +
      '<label class="field"><span>Veranstalter *</span><input name="veranstalter" maxlength="100" required placeholder="Verein, Lokal oder Name"></label></div>' +
      '<label class="field"><span>Kurzbeschreibung</span><textarea name="text" maxlength="500" placeholder="Worum geht es? Eintritt, Anmeldung, Programm – kurz und knapp."></textarea></label>' +
      '<label class="field"><span>Link (optional)</span><input name="link" type="url" maxlength="300" placeholder="https://…"></label>' +
      '<label class="field"><span>Kontakt für Rückfragen (optional, wird nicht veröffentlicht)</span><input name="kontakt" maxlength="120" placeholder="E-Mail oder Telefon"></label>' +
      '<label class="tm-hp" aria-hidden="true">Bitte leer lassen <input name="website" tabindex="-1" autocomplete="off"></label>' +
      '<label class="field tm-check"><input type="checkbox" name="ok" required> <span>Ich darf diesen Termin veröffentlichen lassen und habe die <a href="/datenschutz.html#termine" target="_blank">Datenschutzhinweise</a> gelesen.</span></label>' +
      '<button class="btn" type="submit">Termin senden</button> <button class="tm-abbr text-link" type="button">Abbrechen</button>' +
      '<p class="form-result" hidden></p>';
    box.appendChild(form);
    form.querySelector('[name=art]').value = vorwahl;
    var res = form.querySelector('.form-result');
    btn.addEventListener('click', function () { form.hidden = false; btn.style.display = 'none'; form.querySelector('[name=titel]').focus(); });
    form.querySelector('.tm-abbr').addEventListener('click', function () { form.hidden = true; btn.style.display = ''; });
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!form.reportValidity()) return;
      var f = new FormData(form), d = {};
      f.forEach(function (v, k) { d[k] = String(v).trim(); });
      if (d.bis && d.bis < d.datum) { res.hidden = false; res.textContent = 'Das Enddatum liegt vor dem Startdatum.'; return; }
      var sb = form.querySelector('button[type=submit]'); sb.disabled = true; sb.textContent = 'Wird gesendet …';
      fetch(URL_MELDEN, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(d) })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          res.hidden = false; res.textContent = j.antwort || 'Danke! Dein Termin ist angekommen.';
          if (j.ok) { form.querySelectorAll('input,textarea,select,button[type=submit]').forEach(function (x) { if (x.type !== 'button') x.disabled = true; }); }
          else { sb.disabled = false; sb.textContent = 'Termin senden'; }
        })
        .catch(function () { res.hidden = false; res.textContent = 'Das hat leider nicht geklappt. Bitte versuch es später noch einmal oder schreib an info@bdkng.de.'; sb.disabled = false; sb.textContent = 'Termin senden'; });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
