(function(){
var box=document.getElementById('sportTermine');if(!box)return;
var limit=parseInt(box.getAttribute('data-limit')||'6',10);if(limit<4)limit=4;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var wt=['So','Mo','Di','Mi','Do','Fr','Sa'];
function dat(x){var p=x.date.split('-'),dt=new Date(+p[0],+p[1]-1,+p[2]);return wt[dt.getDay()]+', '+p[2]+'.'+p[1]+'.'+(x.time?'<br>'+esc(x.time)+' Uhr':'');}
function block(t,L,zeile,quelle){
 var h='<h3 class="sp-h">'+t+'</h3>';
 if(!L.length)return h+'<p class="sp-leer">Derzeit keine Infos über Termine.</p>';
 return h+'<ul class="sp-list">'+L.map(function(x){return '<li><span class="sp-d">'+dat(x)+'</span><span class="sp-m">'+zeile(x)+'</span></li>';}).join('')+'</ul><p class="form-note">Quelle: '+quelle+'</p>';}
fetch('/data/sport-termine.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var n=new Date(),h=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
 var ab=function(a){return (a||[]).filter(function(x){return x.date>=h}).slice(0,limit)};
 var html='<h2>📅 Anstehende Termine</h2>';
 html+=block('⚽ Fußball',ab(d.spiele),function(x){var heim=/Bad König\/Zell/.test(x.home);return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>Kreisliga '+(x.team==='m1'?'A':'B')+(heim?' · Heimspiel':' · Auswärts')+'</small>'},'FuPa (SG Bad König/Zell)');
 html+=block('🤾 Handball',ab(d.handball),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>HSG Odenwald · '+esc(x.team)+'</small>'},'nuLiga (HSG Odenwald)');
 html+=block('🏃 Leichtathletik',ab(d.leichtathletik),function(x){return '<strong>'+esc(x.titel)+'</strong>'+(x.ort?'<br><small>'+esc(x.ort)+'</small>':'')},'HLV Kreis Odenwald');
 html+=block('🏓 Tischtennis',ab(d.tischtennis),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong>'},'click-TT');
 html+=block('🎾 Tennis',ab(d.tennis),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong>'},'nuLiga Tennis');
 box.innerHTML=html+'<p class="form-note">Verlegungen und Absagen bitte beim Verein prüfen.</p>';box.hidden=false;
}).catch(function(){});
})();
