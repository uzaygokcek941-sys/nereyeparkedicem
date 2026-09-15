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

    NP.ayarOku().then(async a => {
      if (!a) {
        // Yapilandirma yoksa YALAN SOYLEME: dugmeyi devre disi birak ve sebebi yaz.
        form.querySelectorAll("input,button").forEach(x => { x.disabled = true; });
        if (google) google.disabled = true;
        durum.textContent = "Giriş henüz açık değil — hesap sunucusu yapılandırılmadı. " +
          "Favorilerin bu cihazda kayıtlı, giriş olmadan da çalışıyor.";
        return;
      }
      // Supabase panelinde Google kapaliysa dugmeyi HIC gosterme: basinca
      // "Unsupported provider" hatasi veriyor, kullanici sebebini anlamiyor.
      const s = await NP.saglayicilar();
      if (google && s.google !== true) {
        google.hidden = true;
        const ay = document.querySelector(".ayirac");
        if (ay) ay.hidden = true;
      }
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
      // Sayaci BOS birak: bos-durum kutusu zaten "Henuz favori yok" diyor,
      // ikisi birden yazinca ekranda ayni cumle iki kez cikiyordu.
      const s = $("#favori-sayi"); if (s) s.textContent = "";
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
        const h = NP.senkronHatasi();
        // Tablo yoksa veya RLS engelliyorsa "esitleniyor" demek YANLIS olur.
        durum.innerHTML = h
          ? `<strong>${k.email || "Hesabın"}</strong> ile giriş yapıldı, ama eşitleme ` +
            `çalışmıyor: <code>${h.replace(/</g, "&lt;")}</code>. Favorilerin yine de ` +
            "bu cihazda güvende."
          : `<strong>${k.email || "Hesabın"}</strong> ile giriş yapıldı — ` +
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
    document.addEventListener("np:senkron-hata", ciz);
    if (cikis) cikis.addEventListener("click", async () => {
      cikis.disabled = true;
      await NP.cikis();
      cikis.disabled = false;
      ciz();
    });
  }

  /* ---------- /hesap-sil/ ---------- */
  /* Play User Data politikasi hem uygulama ici hem WEB uzerinden hesap silme
     istiyor. Site zaten uygulamanin kendisi oldugu icin tek akis ikisini de
     karsiliyor: kullanici giris yapar, dugmeye basar, kayit silinir. */
  function silKur() {
    const dug = $("#hesap-sil"); if (!dug) return;
    const durum = $("#sil-durum"), giris = $("#sil-giris");

    const ciz = async () => {
      const a = await NP.ayarOku(), k = NP.kullanici();
      if (!a) {
        durum.textContent = "Hesap sistemi bu kurulumda kapalı — silinecek bir " +
          "hesabın yok. Favorilerin yalnız bu cihazda.";
        dug.hidden = true; if (giris) giris.hidden = true;
        return;
      }
      if (k) {
        durum.innerHTML = `<strong>${(k.email || "Hesabın").replace(/</g, "&lt;")}</strong> ` +
          "ile giriş yapıldı. Aşağıdaki düğme hesabını ve sunucudaki favori " +
          "listeni kalıcı olarak siler.";
        dug.hidden = false; dug.disabled = false;
        if (giris) giris.hidden = true;
      } else {
        durum.textContent = "Silme işlemi için önce giriş yapman gerekiyor — " +
          "aksi halde kimin hesabını sileceğimizi bilemeyiz.";
        dug.hidden = true; if (giris) giris.hidden = false;
      }
    };
    ciz();
    document.addEventListener("np:oturum", ciz);

    dug.addEventListener("click", async () => {
      if (!window.confirm("Hesabın ve sunucudaki favori listen kalıcı olarak " +
        "silinecek. Bu işlem geri alınamaz. Devam edilsin mi?")) return;
      dug.disabled = true; durum.textContent = "Siliniyor…";
      try {
        const c = await NP.istemciAl();
        if (!c) throw new Error("hesap sunucusu yapılandırılmadı");
        // Silmeyi sunucudaki security-definer fonksiyon yapiyor: anon anahtar
        // auth.users'a yazamaz - yazabilseydi zaten guvenlik acigi olurdu.
        const { error } = await c.rpc("hesabimi_sil");
        if (error) throw error;
        await NP.cikis();
        dug.hidden = true;
        durum.textContent = "Hesabın silindi. Bu cihazdaki favori listen " +
          "duruyor ve uygulama giriş yapmadan çalışmaya devam ediyor.";
      } catch (h) {
        durum.textContent = "Silinemedi: " + (h.message || h) + " — tekrar dene.";
        dug.disabled = false;
      }
    });
  }

  /* /favoriler/ sayfasindaki "Hesabımı sil" baglantisi yalniz giris varken */
  function silBaglantisi() {
    const b = $("#sil-baglanti"); if (!b) return;
    const ciz = () => { b.hidden = !NP.kullanici(); };
    ciz();
    document.addEventListener("np:oturum", ciz);
  }

  const basla = () => { girisKur(); favoriKur(); silKur(); silBaglantisi(); };
  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", basla);
  else basla();
})();
