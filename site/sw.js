/* Service worker. TWA kalite kriteri (Chrome belgesi) uygulamanin sunlari
   ele almasini istiyor: cevrimdisi istekte HTTP 200 donmemesi, 404 ve 5xx.
   Olculdu: SW'siz cevrimdisi -> net::ERR_INTERNET_DISCONNECTED, sayfa hic acilmiyor.

   Tek strateji: stale-while-revalidate. Surum damgasi tutulmuyor cunku her
   yanit arka planda tazelenir; boylece deploy sonrasi eski CSS yapismaz.
   ISTISNA: IBB canli doluluk API'si ve olcum betigi ASLA onbellege girmez -
   eski doluluk sayisi canli sanilirsa kullaniciya yanlis bilgi verir. */
const ONBELLEK = "np-v4";
const CEVRIMDISI = "/cevrimdisi/";

const ONDEN = [
  "/", "/harita/", "/il/", "/ucretsiz-otopark/", CEVRIMDISI,
  "/stil.css", "/uygulama.js", "/harita.js", "/sw-kur.js", "/oturum.js",
  "/simge.svg", "/manifest.json",
  "/vendor/leaflet.js", "/vendor/leaflet.css",
  "/veri/iller.json", "/veri/auth.json",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(ONBELLEK)
      // tek tek: bir adres 404 olursa addAll hepsini birden dusuruyor
      .then((c) => Promise.all(ONDEN.map((u) => c.add(u).catch(() => null))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((k) => Promise.all(k.filter((x) => x !== ONBELLEK).map((x) => caches.delete(x))))
      .then(() => self.clients.claim())
  );
});

function onbelleklenmez(u) {
  return u.hostname !== self.location.hostname ||
         u.pathname.startsWith("/_vercel/");
}

self.addEventListener("fetch", (e) => {
  const r = e.request;
  if (r.method !== "GET") return;
  const u = new URL(r.url);
  if (onbelleklenmez(u)) return;   // API ve olcum: tarayiciya birak

  e.respondWith((async () => {
    const c = await caches.open(ONBELLEK);
    const eski = await c.match(r, { ignoreSearch: r.mode === "navigate" });

    const ag = fetch(r).then((y) => {
      // 404/5xx onbellege YAZILMAZ; bozuk yanit kalici hale gelmesin
      if (y && y.ok && y.type !== "opaque") c.put(r, y.clone()).catch(() => {});
      return y;
    });

    if (eski) { ag.catch(() => {}); return eski; }      // stale-while-revalidate

    try {
      const y = await ag;
      if (y && y.ok) return y;
      if (r.mode === "navigate") {
        // sunucunun kendi 404 sayfasi varsa onu goster, yoksa cevrimdisi sayfasi
        if (y && y.status === 404) return y;
        const f = await c.match(CEVRIMDISI);
        if (f) return f;
      }
      return y;
    } catch (_) {
      if (r.mode === "navigate") {
        const f = await c.match(CEVRIMDISI);
        if (f) return f;
      }
      return new Response("", { status: 504, statusText: "Cevrimdisi" });
    }
  })());
});
