self.addEventListener('install',function(){self.skipWaiting()});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim())});
self.addEventListener('fetch',function(e){if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).catch(function(){return new Response('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><body style="font-family:sans-serif;padding:24px"><h1>BDKNG</h1><p>Du bist gerade offline. Bitte versuche es mit Internet noch einmal.</p>',{headers:{'Content-Type':'text/html; charset=utf-8'}})}))});
