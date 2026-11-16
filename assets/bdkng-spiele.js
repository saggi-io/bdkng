(function(){
var box=document.getElementById('sportTermine');if(!box)return;
var limit=parseInt(box.getAttribute('data-limit')||'4',10);if(limit<4)limit=4;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function vn(s){return esc(String(s).replace(/^Spvgg /,'SpVgg '))}
var wt=['So','Mo','Di','Mi','Do','Fr','Sa'];
function dat(x){var p=x.date.split('-'),dt=new Date(+p[0],+p[1]-1,+p[2]);return wt[dt.getDay()]+', '+p[2]+'.'+p[1]+'.'+(x.time?'<br>'+esc(x.time)+' Uhr':'');}
function liste(L,zeile){return '<ul class="sp-list">'+L.map(function(x){return '<li><span class="sp-d">'+dat(x)+'</span><span class="sp-m">'+zeile(x)+'</span></li>';}).join('')+'</ul>';}
function sym(eig,geg){return eig>geg?' ✅':eig<geg?' ❌':' 🤝'}
// Ein Abschnitt je Sportart: erst letzte Ergebnisse, dann nächste Termine
function teil(titel,erg,ergZ,kom,komZ){
 var h='';if(titel)h+='<h4 class="sp-t">'+titel+'</h4>';
 if(erg&&erg.length)h+='<p class="sp-k">Letzte Ergebnisse</p>'+liste(erg,ergZ);
 if(kom&&kom.length)h+='<p class="sp-k">Nächste Termine</p>'+liste(kom,komZ);
 if(!(erg&&erg.length)&&!(kom&&kom.length))h+='<p class="sp-leer">Derzeit keine Infos.</p>';
 return h;}
function sek(id,titel,inhalt,quelle){return '<div class="sp-sek" id="'+id+'"><h3 class="sp-h">'+titel+'</h3>'+inhalt+(quelle?'<p class="form-note">Quelle: '+quelle+'</p>':'')+'</div>';}
fetch('/data/sport-termine.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var n=new Date(),h=n.getFullYear()+'-'+('0'+(n.getMonth()+1)).slice(-2)+'-'+('0'+n.getDate()).slice(-2);
 var g=new Date(n.getTime()-8*864e5),gs=g.getFullYear()+'-'+('0'+(g.getMonth()+1)).slice(-2)+'-'+('0'+g.getDate()).slice(-2);
 var ab=function(a){return (a||[]).filter(function(x){return x.date>=h}).slice(0,limit)};
 var neu=function(a){return (a||[]).filter(function(x){return x.date>=gs&&x.date<=h}).sort(function(a,b){return b.date.localeCompare(a.date)}).slice(0,8)};
 var klub=function(a,k){return (a||[]).filter(function(x){return String(x.team||'').charAt(0)===k})};
 var fbErg=function(re,namen){return function(x){var w=re.test(x.home);return vn(x.home)+' – '+vn(x.away)+' <strong>'+x.hg+':'+x.ag+'</strong>'+sym(w?x.hg:x.ag,w?x.ag:x.hg)+'<br><small>'+namen[x.team]+'</small>'}};
 var fbKom=function(re,namen){return function(x){var heim=re.test(x.home);return '<strong>'+vn(x.home)+'</strong> – <strong>'+vn(x.away)+'</strong><br><small>'+namen[x.team]+(heim?' · Heimspiel':' · Auswärts')+'</small>'}};
 var nSG={m1:'1. Mannschaft · Kreisliga A',m2:'2. Mannschaft · Kreisliga B'},nKi={k1:'1. Mannschaft',k2:'2. Mannschaft'};
 var html='';
 html+=sek('sp-fussball','⚽ Fußball',
  teil('SG Bad König/Zell',neu(klub(d.ergebnisse,'m')),fbErg(/Bad König/,nSG),ab(klub(d.spiele,'m')),fbKom(/Bad König/,nSG))+
  teil('SpVgg Kinzigtal',neu(klub(d.ergebnisse,'k')),fbErg(/Kinzigtal/,nKi),ab(klub(d.spiele,'k')),fbKom(/Kinzigtal/,nKi)),'FuPa');
 html+=sek('sp-handball','🤾 Handball',teil('HSG Odenwald',
  neu((d.handball_ergebnisse||[]).filter(function(x){return x.hg+x.ag>0})),function(x){var w=/Odenwald/.test(x.home);return esc(x.home)+' – '+esc(x.away)+' <strong>'+x.hg+':'+x.ag+'</strong>'+sym(w?x.hg:x.ag,w?x.ag:x.hg)+'<br><small>'+esc(x.team)+' ('+esc(x.liga)+')</small>'},
  ab(d.handball),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>'+esc(x.team)+' ('+esc(x.liga)+')</small>'}),'nuLiga (HHV) · Ergebnisse am Spieltag können Zwischenstände sein');
 html+=sek('sp-tt','🏓 Tischtennis',teil('TSG Bad König · TTC Kimbach · RV-TTC Fürstengrund',
  neu((d.tischtennis||[]).filter(function(x){return x.erg})),function(x){var w=/Bad K|Kimbach|Fürstengrund/.test(x.home),p=x.erg.split(':').map(Number);return esc(x.home)+' – '+esc(x.away)+' <strong>'+esc(x.erg)+'</strong>'+sym(w?p[0]:p[1],w?p[1]:p[0])+'<br><small>'+esc(x.liga)+'</small>'},
  ab((d.tischtennis||[]).filter(function(x){return !x.erg})),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong><br><small>'+esc(x.liga)+'</small>'}),'click-TT (HeTTV)');
 html+=sek('sp-tennis','🎾 Tennis',teil('TC Bad König',[],null,ab(d.tennis),function(x){return '<strong>'+esc(x.home)+'</strong> – <strong>'+esc(x.away)+'</strong>'}),'nuLiga Tennis (HTV) · Punktspiele laufen vor allem im Sommer');
 html+=sek('sp-la','🏃 Leichtathletik',teil('',[],null,ab(d.leichtathletik),function(x){return '<strong>'+esc(x.titel)+'</strong>'+(x.ort?'<br><small>'+esc(x.ort)+'</small>':'')}),'HLV Kreis Odenwald');
 box.innerHTML='<h2>🏆 Ergebnisse &amp; Termine</h2>'+html+'<p class="form-note">Verlegungen und Absagen bitte beim Verein prüfen.</p>';box.hidden=false;
 if(location.hash&&document.getElementById(location.hash.slice(1)))document.getElementById(location.hash.slice(1)).scrollIntoView();
}).catch(function(){});
})();
