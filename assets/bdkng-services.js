'use strict';
document.querySelectorAll('.external-embed').forEach(box=>{
 const load=box.querySelector('.load-radar'),unload=box.querySelector('.unload-radar'),host=box.querySelector('.radar-host'),consent=box.querySelector('.embed-consent');
 load.addEventListener('click',()=>{if(host.firstChild)return;const frame=document.createElement('iframe');frame.src=box.dataset.embedSrc;frame.title='Regenradar rund um Bad König – Windy';frame.referrerPolicy='no-referrer';frame.setAttribute('allow','fullscreen');host.append(frame);consent.hidden=true;unload.hidden=false;unload.focus();});
 unload.addEventListener('click',()=>{host.replaceChildren();unload.hidden=true;consent.hidden=false;load.focus();});
});
