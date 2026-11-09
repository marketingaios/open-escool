// Estructura base de la app en caché para abrirla desde el icono aunque la red vaya lenta; los datos (/api) van siempre al servidor local.
const CACHE = "open-escool-v3";
const GUSCIO = ["/", "/app.js", "/stile.css", "/manifest.webmanifest", "/icone/icona.svg", "/icone/icona-192.png", "/marca/ismagit-bianco.png", "/marca/ismagit-nero.png"];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(CACHE).then((c) => c.addAll(GUSCIO))); self.skipWaiting(); });
self.addEventListener("activate", (e) => { e.waitUntil(caches.keys().then((k) => Promise.all(k.filter((x) => x !== CACHE).map((x) => caches.delete(x))))); self.clients.claim(); });
self.addEventListener("fetch", (e) => {
  const u = new URL(e.request.url);
  if (u.origin !== location.origin || u.pathname.startsWith("/api/") || e.request.method !== "GET") return;
  // los vídeos de las lecciones llegan por partes (Range, 206): sin caché, los sirve siempre el servidor
  if (e.request.headers.has("range") || /\.(mp4|webm|m4a)$/.test(u.pathname)) return;
  // primero la red (el servidor está en el ordenador), la caché solo si el servidor no responde
  e.respondWith(fetch(e.request).then((r) => { const c = r.clone(); caches.open(CACHE).then((x) => x.put(e.request, c)); return r; })
    .catch(() => caches.match(e.request).then((r) => r || caches.match("/"))));
});
