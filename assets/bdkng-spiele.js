(function(){
var box=document.getElementById('sportTermine');if(!box)return;
var limit=parseInt(box.getAttribute('data-limit')||'6',10);
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
fetch('/data/sport-termine.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var n=new Date(),h=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
 var L=(d.spiele||[]).filter(function(x){return x.date>=h}).slice(0,limit);
 if(!L.length)return;
 var wt=['So','Mo','Di','Mi','Do','Fr','Sa'];
 var html=L.map(function(x){var p=x.date.split('-'),dt=new Date(+p[0],+p[1]-1,+p[2]);
  var wir=/Bad König\/Zell/;var heim=wir.test(x.home);
  return '<li><span class="sp-d">'+wt[dt.getDay()]+', '+p[2]+'.'+p[1]+'.<br>'+esc(x.time)+' Uhr</span><span class="sp-m"><strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>Fußball · Kreisliga '+(x.team==='m1'?'A':'B')+(heim?' · Heimspiel':' · Auswärts')+'</small></span></li>';}).join('');
 box.innerHTML='<h2>⚽ Anstehende Fußballspiele</h2><ul class="sp-list">'+html+'</ul><p class="form-note">Quelle: FuPa, SG Bad König/Zell I und II. Spielverlegungen und Absagen bitte beim Verein prüfen.'+(box.getAttribute('data-link')?' <a href="/sport.html">Alle Sport-Termine</a>':'')+'</p>';
 box.hidden=false;
}).catch(function(){});
})();
