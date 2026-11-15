(function(){
var box=document.getElementById('sportTermine');if(!box)return;
var limit=parseInt(box.getAttribute('data-limit')||'6',10);if(limit<4)limit=4;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var wt=['So','Mo','Di','Mi','Do','Fr','Sa'];
function dat(x){var p=x.date.split('-'),dt=new Date(+p[0],+p[1]-1,+p[2]);return wt[dt.getDay()]+', '+p[2]+'.'+p[1]+'.'+(x.time?'<br>'+esc(x.time)+' Uhr':'');}
function block(t,L,zeile,quelle){
 var h='<h3 class="sp-h">'+t+'</h3>';
 if(!L.length)return h+'<p class="sp-leer">Derzeit keine Infos.</p>';
 return h+'<ul class="sp-list">'+L.map(function(x){return '<li><span class="sp-d">'+dat(x)+'</span><span class="sp-m">'+zeile(x)+'</span></li>';}).join('')+'</ul><p class="form-note">Quelle: '+quelle+'</p>';}
fetch('/data/sport-termine.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var n=new Date(),h=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
 var ab=function(a){return (a||[]).filter(function(x){return x.date>=h}).slice(0,limit)};
 var html='<h2>📅 Anstehende Termine</h2>';
 html+=block('⚽ Fußball',ab(d.spiele),function(x){var heim=/Bad König\/Zell/.test(x.home);return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>Kreisliga '+(x.team==='m1'?'A':'B')+(heim?' · Heimspiel':' · Auswärts')+'</small>'},'FuPa (SG Bad König/Zell)');
 html+=block('🤾 Handball',ab(d.handball),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>HSG Odenwald · '+esc(x.team)+'</small>'},'nuLiga (HSG Odenwald)');
 html+=block('🏃 Leichtathletik',ab(d.leichtathletik),function(x){return '<strong>'+esc(x.titel)+'</strong>'+(x.ort?'<br><small>'+esc(x.ort)+'</small>':'')},'HLV Kreis Odenwald');
 html+=block('🏓 Tischtennis',ab((d.tischtennis||[]).filter(function(x){return !x.erg})),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>'+esc(x.liga)+'</small>'},'click-TT (TSG Bad König, TTC Kimbach, RV-TTC Fürstengrund)');
 html+=block('🎾 Tennis',ab(d.tennis),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong>'},'nuLiga Tennis');
 // Letzte Ergebnisse (8 Tage)
 var g=new Date(n.getTime()-8*864e5),gs=g.getFullYear()+'-'+('0'+(g.getMonth()+1)).slice(-2)+'-'+('0'+g.getDate()).slice(-2);
 var neu=function(a){return (a||[]).filter(function(x){return x.date>=gs&&x.date<=h}).sort(function(a,b){return b.date.localeCompare(a.date)}).slice(0,8)};
 var sym=function(eig,geg){return eig>geg?' ✅':eig<geg?' ❌':' 🤝'};
 var e='<h2>🏆 Letzte Ergebnisse</h2>';
 e+=block('⚽ Fußball',neu(d.ergebnisse),function(x){var w=/Bad König/.test(x.home);return esc(x.home)+' – '+esc(x.away)+' <strong>'+x.hg+':'+x.ag+'</strong>'+sym(w?x.hg:x.ag,w?x.ag:x.hg)+'<br><small>'+(x.team==='m1'?'1. Mannschaft':'2. Mannschaft')+'</small>'},'FuPa');
 e+=block('🤾 Handball',neu((d.handball_ergebnisse||[]).filter(function(x){return x.hg+x.ag>0})),function(x){var w=/Odenwald/.test(x.home);return esc(x.home)+' – '+esc(x.away)+' <strong>'+x.hg+':'+x.ag+'</strong>'+sym(w?x.hg:x.ag,w?x.ag:x.hg)+'<br><small>HSG Odenwald · '+esc(x.team)+' ('+esc(x.liga)+')</small>'},'nuLiga');
 e+=block('🏓 Tischtennis',neu((d.tischtennis||[]).filter(function(x){return x.erg})),function(x){var w=/Bad K|Kimbach|Fürstengrund/.test(x.home),p=x.erg.split(':').map(Number);return esc(x.home)+' – '+esc(x.away)+' <strong>'+esc(x.erg)+'</strong>'+sym(w?p[0]:p[1],w?p[1]:p[0])+'<br><small>'+esc(x.liga)+'</small>'},'click-TT');
 box.innerHTML=e+html+'<p class="form-note">Verlegungen und Absagen bitte beim Verein prüfen. Handball-Ergebnisse am Spieltag können Zwischenstände sein.</p>';box.hidden=false;
}).catch(function(){});
})();
