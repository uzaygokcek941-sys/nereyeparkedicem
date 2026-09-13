// nereyeparkedicem — canli doluluk + en yakin otopark. Bagimlilik yok.
const API = "https://api.ibb.gov.tr/ispark/Park";
const $ = (s, k = document) => k.querySelector(s);
const $$ = (s, k = document) => [...k.querySelectorAll(s)];

async function canli() {
  const c = await fetch(API, { cache: "no-store" });
  if (!c.ok) throw new Error("API " + c.status);
  const d = await c.json();
  return new Map(d.map(p => [String(p.parkID), p]));
}

function bosBoya(el, bos, kap) {
  el.textContent = bos ?? "—";
  if (bos == null || !kap) return;
  el.dataset.durum = bos / kap > 0.1 ? "bos" : "dolu";
}

async function doluluguYaz() {
  let m;
  try { m = await canli(); } catch (e) {
    const s = $("[data-ilce-doluluk]");
    if (s) s.textContent = "Canlı doluluk şu an alınamadı — tarife ve konum bilgisi geçerli.";
    return;
  }
  let kap = 0, bos = 0;
  $$(".otopark").forEach(k => {
    const p = m.get(k.dataset.id); if (!p) return;
    bosBoya($("[data-bos]", k), p.emptyCapacity, p.capacity);
    kap += p.capacity || 0; bos += p.emptyCapacity || 0;
  });
  const oran = kap ? Math.round((1 - bos / kap) * 100) : null;
  const s = $("[data-ilce-doluluk]");
  if (s) s.textContent = oran == null ? "" : `Şu an ortalama %${oran} dolu · ${bos.toLocaleString("tr")} boş yer`;
  const g = $("[data-doluluk]");
  if (g) {
    let tk = 0, tb = 0;
    m.forEach(p => { tk += p.capacity || 0; tb += p.emptyCapacity || 0; });
    g.textContent = tk ? `%${Math.round((1 - tb / tk) * 100)}` : "—";
  }
}

const R = 6371;
const mesafe = (a, b, c, d) => {
  const r = x => x * Math.PI / 180, dl = r(c - a), dg = r(d - b);
  const h = Math.sin(dl / 2) ** 2 + Math.cos(r(a)) * Math.cos(r(c)) * Math.sin(dg / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
};

function kartHTML(p, km) {
  const t = p.ilk_saat_tl ? `${p.ilk_saat_tl.toLocaleString("tr")} ₺` : "—";
  return `<article class="otopark" data-id="${p.id}">
   <header><h3>${p.ad}</h3><p class="adres">${p.ilce} · ${km.toFixed(1)} km</p></header>
   <dl class="ozet">
    <div><dt>Kapasite</dt><dd>${p.kapasite ?? "—"}</dd></div>
    <div><dt>Boş</dt><dd class="bos" data-bos>—</dd></div>
    <div><dt>İlk saat</dt><dd>${t}</dd></div>
    <div><dt>Mesafe</dt><dd>${km.toFixed(1)}<small> km</small></dd></div>
   </dl>
   <p class="saat">${p.saat || ""} · ${(p.tip || "").toLowerCase()}</p>
   <div class="git">
    <a href="https://www.google.com/maps/dir/?api=1&destination=${p.lat},${p.lng}" target="_blank" rel="noopener">Google Maps</a>
    <a href="https://yandex.com.tr/harita/?rtext=~${p.lat},${p.lng}&rtt=auto" target="_blank" rel="noopener">Yandex</a>
   </div></article>`;
}

function yakinKur() {
  const btn = $("#yakin"); if (!btn) return;
  btn.addEventListener("click", async () => {
    const durum = $("#konum-durum");
    if (!navigator.geolocation) { durum.textContent = "Tarayıcı konum desteklemiyor."; return; }
    btn.disabled = true; durum.textContent = "Konum alınıyor…";
    navigator.geolocation.getCurrentPosition(async (k) => {
      try {
        durum.textContent = "Otoparklar sıralanıyor…";
        const [hepsi, m] = await Promise.all([
          fetch("otoparklar.json").then(r => r.json()),
          canli().catch(() => new Map()),
        ]);
        const { latitude: la, longitude: lo } = k.coords;
        const sirali = hepsi
          .map(p => ({ p, km: mesafe(la, lo, p.lat, p.lng) }))
          .sort((a, b) => a.km - b.km).slice(0, 10);
        $("#yakin-liste").innerHTML = sirali.map(x => kartHTML(x.p, x.km)).join("");
        $$("#yakin-liste .otopark").forEach(el => {
          const c = m.get(el.dataset.id); if (c) bosBoya($("[data-bos]", el), c.emptyCapacity, c.capacity);
        });
        $("#sonuc").hidden = false;
        durum.textContent = `${sirali.length} otopark bulundu · en yakını ${sirali[0].km.toFixed(1)} km`;
        $("#sonuc").scrollIntoView({ behavior: "smooth", block: "start" });
      } catch (e) {
        durum.textContent = "Liste alınamadı: " + e.message;
      } finally { btn.disabled = false; }
    }, (e) => {
      btn.disabled = false;
      durum.textContent = e.code === 1
        ? "Konum izni verilmedi. Aşağıdan ilçe seçebilirsin."
        : "Konum alınamadı. Aşağıdan ilçe seçebilirsin.";
    }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 });
  });
}

doluluguYaz(); yakinKur();
