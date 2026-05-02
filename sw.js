// Simple offline-first service worker.
// Bump CACHE_VERSION when you change cached files so iPads pick up the update.
const CACHE_VERSION = 'kids-games-v4';
const CORE_ASSETS = [
  './',
  './index.html',
  './styles.css',
  './manifest.webmanifest',
  './games/memory.html',
  './games/target.html',
  './games/sequence.html',
  './games/wordle.html',
  './games/imposter.html',
  './icons/launcher-180.png',
  './icons/launcher-192.png',
  './icons/launcher-512.png',
  './icons/memory-180.png',
  './icons/target-180.png',
  './icons/sequence-180.png',
  './icons/wordle-180.png',
  './icons/imposter-180.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {
          // Cache same-origin successful GETs for offline replay.
          if (response.ok && new URL(event.request.url).origin === self.location.origin) {
            const copy = response.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(event.request, copy));
          }
          return response;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});
