/* nereyeparkedicem — hesap + favori katmani.
 *
 * Tasarim karari: FAVORI HER ZAMAN CALISIR. localStorage birincil depodur,
 * Supabase yalnizca istege bagli bir SENKRON katmanidir. Boylece:
 *  - auth yapilandirilmamisken (veri/auth.json yer tutucu) site tam calisir,
 *  - kullanici giris yapmadan favori ekleyebilir,
 *  - giris yapinca yerel liste uzaktakiyle BIRLESTIRILIR (silme degil, birlesim).
 *
 * supabase.js 218 KB. Her sayfaya koymuyoruz: yalniz auth yapilandirilmissa VE
 * (giris sayfasindaysak | daha once giris yapilmissa | donus adresindeysek)
 * <script> etiketi olarak enjekte edilir. CSP script-src 'self' — kendi
 * kokenimizden yuklendigi icin gecerli.
 */
(() => {
  "use strict";
  const ANAHTAR = "np.favori";
  const GIRDI_IZI = "np.girisyapildi";   // supabase'i tembel yuklemek icin ipucu
  const $ = (s, k = document) => k.querySelector(s);
  const $$ = (s, k = document) => [...k.querySelectorAll(s)];

  /* ---------- yerel depo ---------- */
  // localStorage gizli sekmede/kapaliyken firlatir; favori ozelligi sessizce
  // devre disi kalmali, sayfa patlamamali.
  const oku = () => {
    try { return JSON.parse(localStorage.getItem(ANAHTAR) || "[]"); }
    catch { return []; }
  };
  const yaz = (l) => {
    try { localStorage.setItem(ANAHTAR, JSON.stringify(l)); } catch { /* yok say */ }
  };
  const anahtarla = (f) => f.id || `${(+f.lat).toFixed(5)},${(+f.lng).toFixed(5)}`;

  function degistir(f) {
    const l = oku(), a = anahtarla(f);
    const i = l.findIndex(x => anahtarla(x) === a);
    if (i >= 0) l.splice(i, 1); else l.push({ ...f, t: Date.now() });
    yaz(l);
    uzagaYaz(l);
    document.dispatchEvent(new CustomEvent("np:favori"));
    return i < 0;                       // true = eklendi
  }
  const favoriMi = (f) => {
    const a = anahtarla(f);
    return oku().some(x => anahtarla(x) === a);
  };

  /* ---------- yildiz dugmesi ---------- */
  const YILDIZ_SVG =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" ' +
    'stroke-linejoin="round" d="M12 3.5l2.6 5.3 5.9.85-4.25 4.15 1 5.85L12 ' +
    '16.9l-5.25 2.75 1-5.85L3.5 9.65l5.9-.85L12 3.5z"/></svg>';

  function kartVeri(el) {
    const d = el.dataset;
    if (!d.lat || !d.lng) return null;
    return { id: d.id || "", ad: d.ad || "Otopark", ilce: d.ilce || "",
             lat: +d.lat, lng: +d.lng };
  }

  /** Yildizlari Python ve JS kartlarina TEK yerden basar: iki ayri kart
   *  uretici (uret.py kart() ve uygulama.js kartHTML/kartOSM) ayni SVG'yi
   *  kopyalamak zorunda kalmasin. */
  function yildizlariBas(kok = document) {
    $$(".otopark[data-lat]", kok).forEach(el => {
      if ($(".yildiz", el)) return;
      const f = kartVeri(el); if (!f) return;
      const b = document.createElement("button");
      b.className = "yildiz";
      b.type = "button";
      b.innerHTML = YILDIZ_SVG;
      const tazele = (v) => {
        b.setAttribute("aria-pressed", String(v));
        b.setAttribute("aria-label", (v ? "Favorilerden çıkar: " : "Favorilere ekle: ") + f.ad);
        b.title = v ? "Favorilerden çıkar" : "Favorilere ekle";
      };
      tazele(favoriMi(f));
      b.addEventListener("click", (e) => {
        e.preventDefault(); e.stopPropagation();
        tazele(degistir(f));
      });
      el.appendChild(b);
    });
  }

  /* ---------- doluluk cubugu ---------- */
  /** uygulama.js bos/kapasite yaziyor ama gorsel oran yoktu. Cubuk yalniz
   *  gercek sayi varken gorunur; veri yoksa gizli kalir ("0 bos" gibi
   *  yanlis bir izlenim vermesin). */
  function cubukYaz(el, bos, kap) {
    const c = $(".dolu-cubuk", el); if (!c) return;
    if (bos == null || !kap) { c.hidden = true; return; }
    const oran = Math.max(0, Math.min(100, Math.round((1 - bos / kap) * 100)));
    c.hidden = false;
    c.style.setProperty("--oran", oran);
    c.dataset.durum = bos / kap > 0.1 ? "bos" : "dolu";
    c.setAttribute("aria-label", `%${oran} dolu`);
  }

  /* ---------- Supabase (istege bagli) ---------- */
  let istemci = null, ayar = null, kullanici = null;

  async function ayarOku() {
    if (ayar !== null) return ayar;
    try {
      const a = await fetch("/veri/auth.json", { cache: "no-cache" }).then(r => r.json());
      // yer tutucu doldurulmadiysa auth KAPALI sayilir
      ayar = (a && a.url && a.anonKey && !/YAPILANDIR/i.test(a.url + a.anonKey)) ? a : false;
    } catch { ayar = false; }
    return ayar;
  }

  const betikYukle = (src) => new Promise((ok, hata) => {
    if ($(`script[src="${src}"]`)) return ok();
    const s = document.createElement("script");
    s.src = src; s.onload = () => ok(); s.onerror = () => hata(new Error(src + " yüklenemedi"));
    document.head.appendChild(s);
  });

  async function istemciAl() {
    if (istemci) return istemci;
    const a = await ayarOku(); if (!a) return null;
    await betikYukle("/vendor/supabase.js");
    istemci = window.supabase.createClient(a.url, a.anonKey, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
    });
    return istemci;
  }

  /** Supabase'de acik olan giris saglayicilari. Google panelde kapaliysa
   *  dugmeyi hic gostermemeliyiz - basinca "provider is not enabled" hatasi
   *  veriyor ve kullanici sebebini anlamiyor. */
  let saglayici = null;
  async function saglayicilar() {
    if (saglayici) return saglayici;
    const a = await ayarOku(); if (!a) return {};
    try {
      const d = await fetch(`${a.url}/auth/v1/settings`, { headers: { apikey: a.anonKey } })
        .then(r => r.json());
      saglayici = d.external || {};
    } catch { saglayici = {}; }
    return saglayici;
  }

  // Tablo yoksa/RLS engelliyorsa senkron sessizce dusuyordu. Sebebi tasiyalim.
  let senkronHata = "";

  async function uzagaYaz(liste) {
    if (!kullanici || !istemci) return;
    try {
      const { error } = await istemci.from("favoriler")
        .upsert({ kullanici: kullanici.id, veri: liste, guncelleme: new Date().toISOString() },
                { onConflict: "kullanici" });
      if (error) throw error;
      senkronHata = "";
    } catch (h) {
      // cevrimdisi olabilir; yerel liste zaten yazildi
      senkronHata = h && h.message ? h.message : String(h);
      document.dispatchEvent(new CustomEvent("np:senkron-hata"));
    }
  }

  /** Yerel ve uzak listeyi BIRLESTIRIR. Kesisim degil birlesim: kullanici
   *  ikinci cihazda favori eklediyse ilk cihaz onu silmemeli. */
  async function senkron() {
    if (!kullanici || !istemci) return;
    let uzak = [];
    try {
      const { data, error } = await istemci.from("favoriler").select("veri")
        .eq("kullanici", kullanici.id).maybeSingle();
      if (error) throw error;
      uzak = (data && Array.isArray(data.veri)) ? data.veri : [];
      senkronHata = "";
    } catch (h) {
      senkronHata = h && h.message ? h.message : String(h);
      document.dispatchEvent(new CustomEvent("np:senkron-hata"));
      return;
    }
    const harita = new Map();
    [...uzak, ...oku()].forEach(f => { if (f && f.lat != null) harita.set(anahtarla(f), f); });
    const birlesik = [...harita.values()];
    yaz(birlesik);
    await uzagaYaz(birlesik);
    yildizTazele();
    document.dispatchEvent(new CustomEvent("np:favori"));
  }

  function yildizTazele() {
    $$(".otopark[data-lat]").forEach(el => {
      const b = $(".yildiz", el), f = kartVeri(el);
      if (b && f) b.setAttribute("aria-pressed", String(favoriMi(f)));
    });
  }

  /* ---------- ust bar hesap dugmesi ---------- */
  function hesapCiz() {
    const d = $("[data-hesap]"); if (!d) return;
    if (kullanici) {
      const e = kullanici.email || "";
      d.innerHTML = `<span class="avatar">${(e[0] || "?").toUpperCase()}</span><span>Hesabım</span>`;
      d.setAttribute("href", "/favoriler/");
    } else {
      d.innerHTML = "<span>Giriş</span>";
      d.setAttribute("href", "/giris/");
    }
  }

  async function oturumKur() {
    const a = await ayarOku();
    const d = $("[data-hesap]");
    if (!a) { if (d) d.hidden = true; return null; }   // auth kapali: dugmeyi hic gosterme
    let girisIzi = false;
    try { girisIzi = localStorage.getItem(GIRDI_IZI) === "1"; } catch { /* yok say */ }
    // supabase.js'i yalniz gerekince yukle: giris/favori sayfasi, OAuth donus
    // adresi veya daha once giris yapilmis olmasi.
    const gerek = girisIzi || location.pathname.startsWith("/giris") ||
      location.pathname.startsWith("/favoriler") ||
      location.hash.includes("access_token") || location.search.includes("code=");
    if (!gerek) { hesapCiz(); return null; }
    const c = await istemciAl(); if (!c) return null;
    const { data } = await c.auth.getSession();
    kullanici = data && data.session ? data.session.user : null;
    try { localStorage.setItem(GIRDI_IZI, kullanici ? "1" : "0"); } catch { /* yok say */ }
    hesapCiz();
    c.auth.onAuthStateChange((_olay, oturum) => {
      kullanici = oturum ? oturum.user : null;
      try { localStorage.setItem(GIRDI_IZI, kullanici ? "1" : "0"); } catch { /* yok say */ }
      hesapCiz();
      if (kullanici) senkron();
      document.dispatchEvent(new CustomEvent("np:oturum"));
    });
    if (kullanici) senkron();
    document.dispatchEvent(new CustomEvent("np:oturum"));
    return c;
  }

  /* ---------- disari acilan yuzey ---------- */
  window.NP = {
    favoriler: oku, favoriMi, degistir, yildizlariBas, cubukYaz, yildizTazele,
    istemciAl, ayarOku, senkron, saglayicilar,
    kullanici: () => kullanici,
    senkronHatasi: () => senkronHata,
    cikis: async () => {
      const c = await istemciAl(); if (c) await c.auth.signOut();
      try { localStorage.setItem(GIRDI_IZI, "0"); } catch { /* yok say */ }
      kullanici = null; hesapCiz();
    },
  };

  const basla = () => { yildizlariBas(); oturumKur(); };
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", basla);
  else basla();
})();
