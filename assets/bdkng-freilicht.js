(function(){
var box=document.getElementById('freilicht');if(!box)return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var wt=['So','Mo','Di','Mi','Do','Fr','Sa'];
fetch('/data/termine-kalender.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var n=new Date(),h=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
 var L=(d.termine||[]).filter(function(t){return (t.quelle==='freilicht'||/Freilichtb(ü|ue)hne/i.test(t.ort||''))&&t.datum>=h});
 if(!L.length)return;
 box.innerHTML='<h2>🎭 Freilichtbühne Bad König</h2><p>Das Programm auf der Freilichtbühne am Schlossplatz:</p><ul class="sp-list">'+L.map(function(t){
  var p=t.datum.split('-'),dt=new Date(+p[0],+p[1]-1,+p[2]),m=(t.info||'').match(/https:\/\/\S+/),inf=(t.info||'').replace(/Tickets und Infos:\s*https:\/\/\S+/,'').trim();
  return '<li><span class="sp-d">'+wt[dt.getDay()]+', '+p[2]+'.'+p[1]+'.'+p[0]+(t.uhrzeit?'<br>'+esc(t.uhrzeit)+' Uhr':'')+'</span><span class="sp-m"><strong>'+esc(t.titel)+'</strong>'+(inf?'<br><small>'+esc(inf)+'</small>':'')+(m?'<br><a class="text-link" href="'+esc(m[0])+'" target="_blank" rel="noopener">Infos &amp; Tickets ↗</a>':'')+'</span></li>';
 }).join('')+'</ul><p class="form-note">Quelle: <a href="https://freilichtbuehne-bad-koenig.de/programm/" target="_blank" rel="noopener">Förderkreis Freilichtbühne Bad König e.V.</a> · täglich automatisch abgeglichen. Änderungen bitte beim Veranstalter prüfen.</p>';
 box.hidden=false;
}).catch(function(){});
})();
