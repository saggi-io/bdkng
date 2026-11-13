(function(){
var box=document.getElementById('muellWoche');if(!box)return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function iso(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}
var WT=['So','Mo','Di','Mi','Do','Fr','Sa'],IC={Rest:'⚫',Bio:'🟤',Papier:'🔵','Gelber-Sack':'🟡',SA:'⚠️'};
fetch('/data/muell.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var ots=Object.keys(d.ortsteil||d.ortsteile),O=d.ortsteile||d.ortsteil,cur='Kernstadt';
 try{cur=localStorage.getItem('bdkng-ot')||cur}catch(e){}
 if(!O[cur])cur=ots[0];
 var sel='<label class="mw-sel"><span>Ortsteil</span><select id="mwOt">'+ots.map(function(o){return '<option'+(o===cur?' selected':'')+'>'+esc(o)+'</option>'}).join('')+'</select></label>';
 function woche(o,start){var out=[];for(var i=0;i<7;i++){var dt=new Date(start.getTime()+i*864e5),k=iso(dt),arts=[];
   Object.keys(O[o]).forEach(function(a){if((O[o][a]||[]).indexOf(k)>=0)arts.push((IC[a]||'•')+' '+esc(d.arten[a]||a))});
   if(arts.length)out.push('<li><strong>'+WT[dt.getDay()]+', '+('0'+dt.getDate()).slice(-2)+'.'+('0'+(dt.getMonth()+1)).slice(-2)+'.</strong> '+arts.join(', ')+'</li>')}
  return out.length?'<ul class="mw-list">'+out.join('')+'</ul>':'<p class="mw-none">Keine Abholung.</p>'}
 function draw(){var n=new Date();n.setHours(12,0,0,0);var wd=(n.getDay()+6)%7,mo=new Date(n.getTime()-wd*864e5),mo2=new Date(mo.getTime()+7*864e5);
  function bis(s){var e=new Date(s.getTime()+6*864e5);return ('0'+s.getDate()).slice(-2)+'.'+('0'+(s.getMonth()+1)).slice(-2)+'.–'+('0'+e.getDate()).slice(-2)+'.'+('0'+(e.getMonth()+1)).slice(-2)+'.'}
  var sl=cur.toLowerCase().replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue').replace(/ß/g,'ss').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''),kal='/kalender/muell-'+sl+'.ics';
  box.innerHTML='<h2>🗓️ Abfuhr in dieser und der nächsten Woche</h2>'+sel+'<h3>Diese Woche ('+bis(mo)+')</h3>'+woche(cur,mo)+'<h3>Nächste Woche ('+bis(mo2)+')</h3>'+woche(cur,mo2)+'<div class="kal-dl"><p><strong>📥 Müllkalender '+esc(cur)+' in deinen Kalender</strong><br>Alle Abfuhrtermine, mit Erinnerung am Vorabend um 18 Uhr.</p><a class="btn" href="webcal://bdkng.de'+kal+'">Kalender abonnieren</a> <a class="text-link" href="'+kal+'" download>Als Datei herunterladen (.ics)</a></div>'+'<p class="form-note">'+esc(d.hinweis||'')+' Quelle: <a href="'+esc(d.url)+'" target="_blank" rel="noopener">'+esc(d.quelle)+'</a>, Stand '+esc(d.stand.slice(8)+'.'+d.stand.slice(5,7)+'.'+d.stand.slice(0,4))+'.</p>';
  box.hidden=false;document.getElementById('mwOt').addEventListener('change',function(e){cur=e.target.value;try{localStorage.setItem('bdkng-ot',cur)}catch(x){}draw()})}
 draw();
}).catch(function(){});
})();
