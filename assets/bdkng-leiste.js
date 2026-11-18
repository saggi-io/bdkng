// Info-Leiste Startseite: Wetter jetzt · günstigster Spritpreis · Verkehrsampel
(function () {
  var el = document.getElementById('infoLeiste'); if (!el) return;
  var ICON = { 'clear-day': '☀️', 'clear-night': '🌙', 'partly-cloudy-day': '⛅', 'partly-cloudy-night': '☁️', 'cloudy': '☁️', 'fog': '🌫️', 'wind': '💨', 'rain': '🌧️', 'sleet': '🌨️', 'snow': '❄️', 'hail': '🌨️', 'thunderstorm': '⛈️' };
  function z(n) { return String(n).replace('.', ','); }
  function lab(t) { return '<span class="il-lab">' + t + '</span>'; }
  fetch('/data/wetter-aktuell.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
    var j = d.jetzt || {}, t = (d.tage || [])[0] || {};
    var s = (ICON[j.icon] || '🌦️') + ' <b>' + Math.round(j.temp) + ' °C</b>';
    if (t.tmin != null) s += ' · heute ' + t.tmin + '–' + t.tmax + ' °C';
    if (t.regen >= 1) s += ', ' + z(Math.round(t.regen * 10) / 10) + ' mm Regen';
    if (j.boen >= 50) s += ' · Böen ' + j.boen + ' km/h';
    var a = el.querySelector('.il-wetter'); a.innerHTML = lab('Wetter') + '<span>' + s + '</span><span class="il-mehr">→</span>'; el.hidden = false;
  }).catch(function () {});
  fetch('https://n8n.sagmeister.io/webhook/bdkng-sprit', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
    var p = d.leiste; if (!p) return;
    var a = el.querySelector('.il-sprit'); a.innerHTML = lab('Tanken') + '<span>⛽ ' + p + '</span><span class="il-mehr">→</span>'; a.hidden = false; el.hidden = false;
  }).catch(function () {});
  // Verkehrsampel: grün = frei, gelb = Unfall/Stau/Baustelle, rot = Sperrung oder mehrere Unfälle.
  // Die lange bekannten Baustellen (Zeller Brücke, B-45-Talbrücke, Unterführung Mümling/Behelfsumfahrung am Kurpark) zählen nicht.
  var amp = el.querySelector('.il-ampel'); if (!amp) return;
  var n = new Date(), p2 = function (x) { return ('0' + x).slice(-2); }, iso = function (d) { return d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate()); };
  var heute = iso(n), vor2 = iso(new Date(n.getTime() - 2 * 864e5));
  var jz = heute + 'T' + p2(n.getHours()) + ':' + p2(n.getMinutes());
  var DAUER = /Zeller Br(ü|ue)cke|Talbr(ü|ue)cke|Unterf(ü|ue)hrung M(ü|ue)mling|Behelfsumfahrung|Kurpark|Asselbrunn|kleinen Schwester|Ortsdurchfahrt.*(frei|wieder)|freigegeben|aufgehoben/i;
  Promise.all([
    fetch('/data/news.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).catch(function () { return []; }),
    fetch('/data/blitzer.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).catch(function () { return {}; })
  ]).then(function (res) {
    var L = Array.isArray(res[0]) ? res[0] : [], gem = (res[1].gemeldet || []).filter(function (x) { return x.bis > jz && !/Blitzer|Kontrolle|Messung/i.test(x.art); });
    var unfall = 0, sperr = 0, gelb = 0, gruende = [];
    L.forEach(function (x) {
      if ((x.categories || []).indexOf('verkehr') < 0 || /^bahn-/.test(x.id)) return;
      if (x.valid_until && x.valid_until < heute) return;
      var t = x.title + ' ' + (x.paragraphs || []).join(' ');
      var live = /^verkehr-live/.test(x.id);
      if (!live && x.checked < vor2) return;            // ältere Stadt-/Hessen-Mobil-Meldungen: nur die frischen zählen
      if (DAUER.test(t)) return;
      if (/\bab (dem )?\d{1,2}\./i.test(x.title + ' ' + (x.paragraphs || [])[0]) && !live) return; // angekündigt, noch nicht aktiv
      if (/Unfall/i.test(t)) { unfall++; gruende.push('Unfall'); }
      else if (/Vollsperrung|gesperrt|Sperrung/i.test(t)) { sperr++; gruende.push('Sperrung'); }
      else if (/Baustelle|Stau|Fahrbahn|Gefahr/i.test(t)) { gelb++; gruende.push(/Stau/i.test(t) ? 'Stau' : 'Baustelle'); }
    });
    gem.forEach(function (x) { if (/Unfall/i.test(x.art)) { unfall++; gruende.push('Unfall'); } else if (/Sperrung/i.test(x.art)) { sperr++; gruende.push('Sperrung'); } else { gelb++; gruende.push(x.art); } });
    var stufe = (sperr || unfall >= 2) ? 'rot' : (unfall || gelb) ? 'gelb' : 'gruen';
    var text = { gruen: 'frei', gelb: 'Behinderung', rot: 'Sperrung' }[stufe];
    if (stufe === 'rot' && !sperr) text = 'mehrere Unfälle';
    if (stufe === 'gelb' && gruende.length) text = gruende[0];
    amp.className = 'il-ampel amp-' + stufe;
    amp.setAttribute('aria-label', 'Verkehr: ' + text);
    amp.innerHTML = lab('Verkehr') + '<span class="amp-l" aria-hidden="true"><i class="g"></i><i class="y"></i><i class="r"></i></span><span>' + text + '</span><span class="il-mehr">→</span>';
    amp.hidden = false; el.hidden = false;
  });
})();
