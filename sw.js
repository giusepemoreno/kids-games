// Offline service worker.
// Pages and files come from the network when it answers (so updates show up
// on the next launch) and from the cache when offline.
// Bump CACHE_VERSION when you change the list below.
const CACHE_VERSION = 'kids-games-v9';
const NETWORK_TIMEOUT_MS = 4000;
const CORE_ASSETS = [
  './',
  './index.html',
  './styles.css',
  './kit.js',
  './manifest.webmanifest',
  './games/memory.html',
  './games/target.html',
  './games/sequence.html',
  './games/trivoca.html',
  './games/imposter.html',
  './games/pelea.html',
  './games/pelea/fighters.js',
  './games/pelea/fighters/mikati/brazo_adelante.png',
  './games/pelea/fighters/mikati/brazo_atras.png',
  './games/pelea/fighters/mikati/cabeza.png',
  './games/pelea/fighters/mikati/cuerpo.png',
  './games/pelea/fighters/mikati/mano_adelante.png',
  './games/pelea/fighters/mikati/mano_atras.png',
  './games/pelea/fighters/mikati/pie_adelante.png',
  './games/pelea/fighters/mikati/pie_atras.png',
  './games/pelea/fighters/mikati/pierna_adelante.png',
  './games/pelea/fighters/mikati/pierna_atras.png',
  './games/pelea/fighters/romboman/cabeza.png',
  './games/pelea/fighters/romboman/cuerpo.png',
  './games/pelea/fighters/romboman/mano_adelante.png',
  './games/pelea/fighters/romboman/mano_atras.png',
  './games/pelea/fighters/romboman/pie_adelante.png',
  './games/pelea/fighters/romboman/pie_atras.png',
  './games/pelea/fighters/sword-men/brazo_adelante.png',
  './games/pelea/fighters/sword-men/brazo_atras.png',
  './games/pelea/fighters/sword-men/cabeza.png',
  './games/pelea/fighters/sword-men/cuerpo.png',
  './games/pelea/fighters/sword-men/pie_adelante.png',
  './games/pelea/fighters/sword-men/pie_atras.png',
  './games/pelea/fighters/sword-men/pierna_adelante.png',
  './games/pelea/fighters/sword-men/pierna_atras.png',
  './games/pelea/fonts/bowlby-one.woff2',
  './games/pelea/fonts/patrick-hand.woff2',
  './games/pelea/fonts/rubik.woff2',
  './icons/launcher-180.png',
  './icons/launcher-192.png',
  './icons/launcher-512.png',
  './icons/memory-180.png',
  './icons/target-180.png',
  './icons/sequence-180.png',
  './icons/trivoca-180.png',
  './icons/imposter-180.png',
  './icons/pelea-180.png'
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

function fromNetwork(request) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(reject, NETWORK_TIMEOUT_MS);
    fetch(request).then(
      (response) => { clearTimeout(timer); resolve(response); },
      (error) => { clearTimeout(timer); reject(error); }
    );
  });
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  // Only our own files; other sites (e.g. web fonts) go straight to the browser.
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
  event.respondWith(
    fromNetwork(request)
      .then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
        }
        return response;
      })
      .catch(() =>
        caches.match(request, { ignoreSearch: true }).then((cached) =>
          cached || (request.mode === 'navigate' ? caches.match('./index.html') : Response.error())
        )
      )
  );
});
