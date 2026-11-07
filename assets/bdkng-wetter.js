"use strict";
(function(){
  var box=document.getElementById('wetterleiste');if(!box)return;
  var IC={'clear-day':'☀️','clear-night':'🌙','partly-cloudy-day':'⛅','partly-cloudy-night':'☁️','cloudy':'☁️','fog':'🌫️','wind':'💨','rain':'🌧️','sleet':'🌨️','snow':'❄️','hail':'🌨️','thunderstorm':'⛈️'};
  var TX={'clear-day':'Sonnig','clear-night':'Klar','partly-cloudy-day':'Wolkig','partly-cloudy-night':'Wolkig','cloudy':'Bedeckt','fog':'Nebel','wind':'Windig','rain':'Regen','sleet':'Schneeregen','snow':'Schnee','hail':'Hagel','thunderstorm':'Gewitter'};
  var WT=['So','Mo','Di','Mi','Do','Fr','Sa'];
  fetch('/data/wetter-aktuell.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
    var h=new Date(d.aktualisiert);var heute=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Berlin'}).format(new Date());
    var alt=(Date.now()-h.getTime())>8*3600*1000;
    var j=d.jetzt,ic=IC[j.icon]||'🌡️';
    var tage=d.tage.filter(function(t){return t.datum>heute}).slice(0,3).map(function(t){var wd=WT[new Date(t.datum+'T12:00:00Z').getUTCDay()];
      return '<li><span class="wl-d">'+wd+'</span><span class="wl-i" aria-hidden="true">'+(IC[t.icon]||'')+'</span><span class="wl-t"><strong>'+t.tmax+'°</strong> '+t.tmin+'°</span></li>'}).join('');
    var st=d.aktualisiert.slice(11,16);
    box.innerHTML='<a class="wl-now" href="/wetter.html" aria-label="Wetter in Bad König, Details"><span class="wl-big" aria-hidden="true">'+ic+'</span><span><span class="wl-temp">'+j.temp+'°C</span><span class="wl-cond">'+(TX[j.icon]||'')+' · Wind '+j.wind+' km/h</span><span class="wl-ort">Bad König jetzt</span></span></a><ul class="wl-days">'+tage+'</ul><p class="wl-src">'+(alt?'Stand nicht aktuell · ':'')+'Quelle: <a href="'+d.quelle_url+'" target="_blank" rel="noopener">'+d.quelle+'</a> · Stand '+st+' Uhr</p>';
    box.hidden=false;
  }).catch(function(){});
})();
