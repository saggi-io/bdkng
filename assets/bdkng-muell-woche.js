(function(){
var box=document.getElementById('muellWoche');if(!box)return;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function iso(d){return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}
var WT=['So','Mo','Di','Mi','Do','Fr','Sa'],IC={Rest:'⚫',Bio:'🟤',Papier:'🔵','Gelber-Sack':'🟡',SA:'⚠️'};
fetch('/data/muell.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var ots=Object.keys(d.ortsteil||d.ortsteile),O=d.ortsteile||d.ortsteil,cur='Kernstadt';
 try{cur=localStorage.getItem('bdkng-ot')||cur}catch(e){}
 if(!O[cur])cur=ots[0];
 function woche(o,start){var out=[];for(var i=0;i<7;i++){var dt=new Date(start.getTime()+i*864e5),k=iso(dt),arts=[];
   Object.keys(O[o]).forEach(function(a){if((O[o][a]||[]).indexOf(k)>=0)arts.push((IC[a]||'•')+' '+esc(d.arten[a]||a))});
   if(arts.length)out.push('<li><strong>'+WT[dt.getDay()]+', '+('0'+dt.getDate()).slice(-2)+'.'+('0'+(dt.getMonth()+1)).slice(-2)+'.</strong> '+arts.join(', ')+'</li>')}
  if(out.length)return '<ul class="mw-list">'+out.join('')+'</ul>';
  // nichts im gewählten Ortsteil: zeigen, was in den anderen Ortsteilen abgeholt wird
  var andere={};for(var j=0;j<7;j++){var dt2=new Date(start.getTime()+j*864e5),k2=iso(dt2);ots.forEach(function(x){if(x===o)return;Object.keys(O[x]).forEach(function(a){if((O[x][a]||[]).indexOf(k2)>=0){var key=k2+'|'+a;(andere[key]=andere[key]||{dt:dt2,a:a,o:[]}).o.push(x)}})})}
  var L=Object.keys(andere).sort().map(function(k){var z=andere[k];return '<li><strong>'+WT[z.dt.getDay()]+', '+('0'+z.dt.getDate()).slice(-2)+'.'+('0'+(z.dt.getMonth()+1)).slice(-2)+'.</strong> '+(IC[z.a]||'•')+' '+esc(d.arten[z.a]||z.a)+' – '+esc(z.o.join(', '))+'</li>'});
  return '<p class="mw-none">In '+esc(o)+' ist keine Abholung.</p>'+(L.length?'<p class="form-note">In anderen Ortsteilen:</p><ul class="mw-list">'+L.join('')+'</ul>':'<p class="form-note">Auch in den anderen Ortsteilen ist keine Abholung.</p>')}
 function draw(){var sel='<label class="mw-sel"><span>Ortsteil</span><select id="mwOt">'+ots.map(function(o){return '<option'+(o===cur?' selected':'')+'>'+esc(o)+'</option>'}).join('')+'</select></label>';var n=new Date();n.setHours(12,0,0,0);var wd=(n.getDay()+6)%7,mo=new Date(n.getTime()-wd*864e5),mo2=new Date(mo.getTime()+7*864e5);
  function bis(s){var e=new Date(s.getTime()+6*864e5);return ('0'+s.getDate()).slice(-2)+'.'+('0'+(s.getMonth()+1)).slice(-2)+'.–'+('0'+e.getDate()).slice(-2)+'.'+('0'+(e.getMonth()+1)).slice(-2)+'.'}
  var sl=cur.toLowerCase().replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue').replace(/ß/g,'ss').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''),kal='/kalender/muell-'+sl+'.ics';
  box.innerHTML='<h2>🗓️ Abfuhr in dieser und der nächsten Woche</h2>'+sel+'<h3>Diese Woche in '+esc(cur)+' ('+bis(mo)+')</h3>'+woche(cur,mo)+'<h3>Nächste Woche in '+esc(cur)+' ('+bis(mo2)+')</h3>'+woche(cur,mo2)+'<div class="kal-dl"><p><strong>📥 Müllkalender '+esc(cur)+' in deinen Kalender</strong><br>Alle Abfuhrtermine, mit Erinnerung am Vorabend um 18 Uhr.</p><a class="btn" href="webcal://bdkng.de'+kal+'">Kalender abonnieren</a> <a class="text-link" href="'+kal+'" download>Als Datei herunterladen (.ics)</a></div>'+'<p class="form-note">'+esc(d.hinweis||'')+' Quelle: <a href="'+esc(d.url)+'" target="_blank" rel="noopener">'+esc(d.quelle)+'</a>, Stand '+esc(d.stand.slice(8)+'.'+d.stand.slice(5,7)+'.'+d.stand.slice(0,4))+'.</p>';
  box.hidden=false;document.getElementById('mwOt').addEventListener('change',function(e){cur=e.target.value;try{localStorage.setItem('bdkng-ot',cur)}catch(x){}draw()})}
 draw();
}).catch(function(){});
})();
