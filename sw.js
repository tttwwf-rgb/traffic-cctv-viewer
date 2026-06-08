// Service Worker — CCTV 뷰어
const CACHE = 'cctv-v1';
const STATIC = ['/', '/index.html', '/manifest.json', '/icon-192.png', '/icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // API 요청은 캐시 안 함 (항상 최신 데이터)
  if (e.request.url.includes('openapi.its.go.kr') ||
      e.request.url.includes('cctvsec.ktict.co.kr')) return;

  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
