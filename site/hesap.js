/* Yalniz /giris/ ve /favoriler/ sayfalarina yuklenir. oturum.js'teki
 * window.NP yuzeyini kullanir; supabase istemcisini kendisi kurmaz. */
(() => {
  "use strict";
  const $ = (s, k = document) => k.querySelector(s);
  const DONUS = () => location.origin + "/favoriler/";

  /* ---------- /giris/ ---------- */
  function girisKur() {
    const form = $("#giris-form"); if (!form) return;
    const durum = $("#giris-durum"), google = $("#google-giris");

    NP.ayarOku().then(a => {
      if (a) return;
      // Yapilandirma yoksa YALAN SOYLEME: dugmeyi devre disi birak ve sebebi yaz.
      form.querySelectorAll("input,button").forEach(x => { x.disabled = true; });
      if (google) google.disabled = true;
      durum.textContent = "Giriş henüz açık değil — hesap sunucusu yapılandırılmadı. " +
        "Favorilerin bu cihazda kayıtlı, giriş olmadan da çalışıyor.";
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const posta = $("#eposta").value.trim();
      if (!posta) return;
      const dug = $("#giris-dug");
      dug.disabled = true; durum.textContent = "Bağlantı gönderiliyor…";
      try {
        const c = await NP.istemciAl();
        if (!c) throw new Error("hesap sunucusu yapılandırılmadı");
        const { error } = await c.auth.signInWithOtp({
          email: posta, options: { emailRedirectTo: DONUS() } });
        if (error) throw error;
        durum.textContent = `${posta} adresine giriş bağlantısı gönderildi. ` +
          "Postayı aç ve bağlantıya dokun — parola yok.";
        form.reset();
      } catch (h) {
        durum.textContent = "Gönderilemedi: " + (h.message || h);
      } finally { dug.disabled = false; }
    });

    if (google) google.addEventListener("click", async () => {
      google.disabled = true; durum.textContent = "Google'a yönlendiriliyor…";
      try {
        const c = await NP.istemciAl();
        if (!c) throw new Error("hesap sunucusu yapılandırılmadı");
        const { error } = await c.auth.signInWithOAuth({
          provider: "google", options: { redirectTo: DONUS() } });
        if (error) throw error;
      } catch (h) {
        google.disabled = false;
        durum.textContent = "Google girişi başarısız: " + (h.message || h);
      }
    });
  }

  /* ---------- /favoriler/ ---------- */
  function kart(f) {
    const ad = String(f.ad || "Otopark");
    const yer = String(f.ilce || "");
    return `<article class="otopark" data-id="${f.id || ""}" data-lat="${f.lat}"
      data-lng="${f.lng}" data-ad="${ad.replace(/"/g, "&quot;")}"
      data-ilce="${yer.replace(/"/g, "&quot;")}">
      <header><h3></h3><p class="adres"></p></header>
      <div class="git">
       <a href="https://www.google.com/maps/dir/?api=1&destination=${f.lat},${f.lng}"
          target="_blank" rel="noopener">Google Maps</a>
       <a href="https://yandex.com.tr/harita/?rtext=~${f.lat},${f.lng}&rtt=auto"
          target="_blank" rel="noopener">Yandex</a>
      </div></article>`;
  }

  function listeCiz() {
    const kutu = $("#favori-liste"); if (!kutu) return;
    const l = NP.favoriler();
    const bos = $("#favori-bos");
    if (!l.length) {
      kutu.innerHTML = ""; if (bos) bos.hidden = false;
      const s = $("#favori-sayi"); if (s) s.textContent = "Henüz favori yok.";
      return;
    }
    if (bos) bos.hidden = true;
    kutu.innerHTML = l.map(kart).join("");
    // Ad ve ilce metin olarak yazilir (innerHTML degil): favori adi kullanici
    // girdisi degil ama OSM'den geliyor, kaynakta < > olabilir.
    [...kutu.querySelectorAll(".otopark")].forEach((el, i) => {
      el.querySelector("h3").textContent = l[i].ad || "Otopark";
      el.querySelector(".adres").textContent = l[i].ilce || "";
    });
    NP.yildizlariBas(kutu);
    const s = $("#favori-sayi");
    if (s) s.textContent = `${l.length} kayıtlı otopark.`;
  }

  function favoriKur() {
    if (!$("#favori-liste")) return;
    listeCiz();
    document.addEventListener("np:favori", listeCiz);

    const durum = $("#hesap-durum"), cikis = $("#cikis");
    const ciz = async () => {
      const a = await NP.ayarOku(), k = NP.kullanici();
      if (!a) {
        durum.textContent = "Favoriler bu cihazda saklı. Cihazlar arası eşitleme " +
          "için hesap sunucusu henüz yapılandırılmadı.";
        if (cikis) cikis.hidden = true;
        return;
      }
      if (k) {
        durum.innerHTML = `<strong>${k.email || "Hesabın"}</strong> ile giriş yapıldı — ` +
          "favoriler cihazlar arasında eşitleniyor.";
        if (cikis) cikis.hidden = false;
      } else {
        durum.innerHTML = 'Favoriler yalnız bu cihazda saklı. ' +
          '<a href="/giris/">Giriş yap</a> ve tüm cihazlarında görünsün.';
        if (cikis) cikis.hidden = true;
      }
    };
    ciz();
    document.addEventListener("np:oturum", ciz);
    if (cikis) cikis.addEventListener("click", async () => {
      cikis.disabled = true;
      await NP.cikis();
      cikis.disabled = false;
      ciz();
    });
  }

  const basla = () => { girisKur(); favoriKur(); };
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", basla);
  else basla();
})();
