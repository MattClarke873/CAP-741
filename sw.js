// Offline cache for the CAP 741 Log app.
// Bump VERSION whenever you upload changed files so phones pick up the new copy.
const VERSION = 'cap741-v26';
const FILES = [
  './',
  './index.html',
  './pdf-lib.min.js',
  './xlsx.mini.min.js',
  './cap741-template.pdf',
  './manifest.webmanifest',
  './icon-180.png',
  './icon-512.png',
  './data/part66-types.json',
  './data/part145-orgs.json'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return; // Dropbox etc. go straight to network
  // Network first (so updates arrive), fall back to cache when offline.
  e.respondWith(
    fetch(e.request)
      .then(res => {
        const copy = res.clone();
        caches.open(VERSION).then(c => c.put(e.request, copy));
        return res;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true }))
  );
});
