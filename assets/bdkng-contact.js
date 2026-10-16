 'use strict';
(()=>{const form=document.getElementById('contact-form');if(!form)return;
const topic=form.elements.namedItem('thema'),q=new URLSearchParams(location.search).get('thema');
if([...topic.options].some(o=>o.value===q))topic.value=q;
form.addEventListener('submit',async e=>{e.preventDefault();if(!form.reportValidity())return;
const button=form.querySelector('button[type="submit"]'),result=document.getElementById('mail-result');
if(button.disabled)return;button.disabled=true;button.textContent='Wird gesendet …';result.hidden=true;result.classList.remove('error');
const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),20000);
try{const response=await fetch(form.action,{method:'POST',body:new URLSearchParams(new FormData(form)),credentials:'omit',signal:controller.signal});
const data=await response.json();if(!response.ok||data.accepted!==true)throw new Error(data.message||'Der Versand ist fehlgeschlagen.');
result.textContent='Danke! Deine Nachricht wurde an unseren Versanddienst übergeben. Wir melden uns über deine angegebene E-Mail-Adresse.';form.reset();
}catch(err){result.classList.add('error');result.textContent=err.name==='AbortError'?'Die Bestätigung dauert zu lange. Ob die Nachricht angekommen ist, ist unklar. Bitte sende nicht sofort doppelt; alternativ erreichst du uns unter info@bdkng.de.':(err.message==='Failed to fetch'?'Der Versand ist gerade nicht erreichbar. Bitte versuche es später oder schreibe an info@bdkng.de.':err.message);}
finally{clearTimeout(timeout);result.hidden=false;button.disabled=false;button.textContent='Nachricht senden →';}});})();
