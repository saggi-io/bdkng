(function(){
var box=document.getElementById('verkehrStatus');if(!box)return;
var n=new Date(),p=function(x){return('0'+x).slice(-2)},h=n.getFullYear()+'-'+p(n.getMonth()+1)+'-'+p(n.getDate());
var g=new Date(n.getTime()-2*864e5),gr=g.getFullYear()+'-'+p(g.getMonth()+1)+'-'+p(g.getDate());
var stand=p(n.getDate())+'.'+p(n.getMonth()+1)+'., '+p(n.getHours())+':'+p(n.getMinutes())+' Uhr';
fetch('/data/news.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(L){
 var live=L.filter(function(x){return (x.categories||[]).indexOf('verkehr')>=0&&/^verkehr-live/.test(x.id)&&x.checked>=gr&&(!x.valid_until||x.valid_until>=h)&&!/bis Ende|202[7-9]/.test(x.title+' '+(x.paragraphs||[]).join(' '))});
 box.innerHTML=live.length?'<p><strong>⚠️ Aktuelle Behinderungen:</strong> '+live.map(function(x){return '<a href="#'+x.id+'">'+x.title.replace(/[<>&]/g,'')+'</a>'}).join(' · ')+'</p>'
  :'<p><strong>✅ Derzeit sind keine aktuellen Behinderungen bekannt</strong> (keine Staus oder Unfälle gemeldet, Stand '+stand+').</p><p class="form-note">Länger laufende Baustellen und Sperrungen stehen weiter unten.</p>';
 box.hidden=false;
}).catch(function(){});
})();
