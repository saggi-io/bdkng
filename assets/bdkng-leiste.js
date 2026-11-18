// Info-Leiste Startseite: Wetter jetzt + (später) günstigster Spritpreis
(function () {
  var el = document.getElementById('infoLeiste'); if (!el) return;
  var ICON = { 'clear-day': '☀️', 'clear-night': '🌙', 'partly-cloudy-day': '⛅', 'partly-cloudy-night': '☁️', 'cloudy': '☁️', 'fog': '🌫️', 'wind': '💨', 'rain': '🌧️', 'sleet': '🌨️', 'snow': '❄️', 'hail': '🌨️', 'thunderstorm': '⛈️' };
  function z(n) { return String(n).replace('.', ','); }
  fetch('/data/wetter-aktuell.json', { cache: 'no-cache' }).then(function (r) { return r.json(); }).then(function (d) {
    var j = d.jetzt || {}, t = (d.tage || [])[0] || {};
    var s = (ICON[j.icon] || '🌦️') + ' <b>' + Math.round(j.temp) + ' °C</b> in Bad König';
    if (t.tmin != null) s += ' · heute ' + t.tmin + '–' + t.tmax + ' °C';
    if (t.regen >= 1) s += ', ' + z(Math.round(t.regen * 10) / 10) + ' mm Regen';
    if (j.boen >= 50) s += ' · Böen ' + j.boen + ' km/h';
    var a = el.querySelector('.il-wetter'); a.innerHTML = '<span>' + s + '</span><span class="il-mehr">→</span>'; el.hidden = false;
  }).catch(function () {});
  fetch('https://n8n.sagmeister.io/webhook/bdkng-sprit', { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
    var p = d.leiste; if (!p) return;
    var a = el.querySelector('.il-sprit'); a.innerHTML = '<span>⛽ ' + p + '</span><span class="il-mehr">→</span>'; a.hidden = false; el.hidden = false;
  }).catch(function () {});
})();
