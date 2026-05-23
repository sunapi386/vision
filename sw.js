var CACHE = 'trust-at-scale-v13';
var AUDIO_FILES = [
  'audio/part01-world-changed.mp3',
  'audio/part02-the-void.mp3',
  'audio/part03-the-pattern.mp3',
  'audio/part04-the-stack.mp3',
  'audio/part05-transitions.mp3',
  'audio/part06-what-comes-next.mp3'
];

self.addEventListener('install', function(e) {
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(caches.keys().then(function(names) {
    return Promise.all(names.filter(function(n) { return n !== CACHE; }).map(function(n) { return caches.delete(n); }));
  }));
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  var url = e.request.url;
  var isAudio = AUDIO_FILES.some(function(f) { return url.indexOf(f) !== -1; });

  if (e.request.mode === 'navigate' || url.indexOf('.html') !== -1) {
    e.respondWith(
      caches.open(CACHE).then(function(cache) {
        return cache.match(e.request).then(function(cached) {
          var net = fetch(e.request).then(function(resp) {
            if (resp.ok) {
              cache.put(e.request, resp.clone());
              if (cached) {
                var oldEtag = cached.headers.get('etag');
                var newEtag = resp.headers.get('etag');
                if (oldEtag && newEtag && oldEtag !== newEtag) {
                  self.clients.matchAll().then(function(clients) {
                    clients.forEach(function(c) { c.postMessage({ type: 'updated' }); });
                  });
                }
              }
            }
            return resp;
          }).catch(function() { return cached; });
          return cached || net;
        });
      })
    );
  } else if (isAudio) {
    e.respondWith(
      caches.match(e.request).then(function(cached) {
        if (cached) return cached;
        return fetch(e.request).then(function(resp) {
          if (resp.ok) {
            var clone = resp.clone();
            caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
          }
          return resp;
        });
      })
    );
  }
});
