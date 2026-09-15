/* 81 il otopark haritasi. Kume eklentisi yok: Leaflet'in kendi canvas renderer'i
   binlerce daireyi tasiyor, ek bagimlilik gerekmiyor.
   Il verisi ancak gorunen alana girince indiriliyor - 81 ilin tamami ~1 MB. */
(function () {
  var KOK = location.pathname.indexOf("/harita") === 0 ? "../" : "";
  var AC_ZOOM = 8;                       // bu zoom'dan itibaren nokta gosterilir
  var harita, tuval, ilKat = {}, yukleniyor = {}, ozet = null, balonKat;

  function $(s) { return document.querySelector(s); }
  function durum(m) { var e = $("#harita-durum"); if (e) e.textContent = m || ""; }

  function kesisiyor(bb, s) {   // bb = [minLat,minLng,maxLat,maxLng]
    return bb[0] <= s.getNorth() && bb[2] >= s.getSouth() &&
           bb[1] <= s.getEast()  && bb[3] >= s.getWest();
  }

  function metin(b) {
    var p = [];
    if (b.t) p.push(b.t);
    if (b.u === 1) p.push("ücretli"); else if (b.u === 0) p.push("ücretsiz");
    if (b.k) p.push(b.k + " kapasite");
    if (b.s) p.push(b.s);
    return p.join(" · ");
  }

  function balon(lat, lng, b, ilAd) {
    var ad = (b && b.a) ? b.a : "Otopark";
    var alt = b ? metin(b) : "";
    var op = (b && b.o) ? '<div class="op">' + b.o + "</div>" : "";
    return '<div class="balon"><strong>' + ad + "</strong>" +
      (alt ? '<div class="alt">' + alt + "</div>" : "") + op +
      '<div class="il">' + ilAd + "</div>" +
      '<div class="git">' +
      '<a target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination=' +
      lat + "," + lng + '">Google Maps</a>' +
      '<a target="_blank" rel="noopener" href="https://yandex.com.tr/harita/?rtext=~' +
      lat + "," + lng + '&rtt=auto">Yandex</a></div>' +
      '<div class="kaynak">Kaynak: OpenStreetMap</div></div>';
  }

  // ?ucretsiz=1 -> yalniz fee=no isaretli noktalar. OSM'de noktalarin %88'inde
  // ucret bilgisi YOK; filtre "ucretsiz oldugu yazan" demek, "ucretsiz olan" degil.
  var SORGU = new URLSearchParams(location.search);
  var SADECE_UCRETSIZ = SORGU.get("ucretsiz") === "1";

  function ilCiz(d) {
    var g = L.layerGroup(), k = d.k, b = d.b;
    for (var i = 0; i < k.length; i += 2) {
      var idx = i / 2, bi = b[idx];
      if (SADECE_UCRETSIZ && !(bi && bi.u === 0)) continue;
      var m = L.circleMarker([k[i], k[i + 1]], {
        renderer: tuval, radius: 5, weight: 1,
        color: "#0b3d2e", fillColor: bi && bi.u === 1 ? "#f0a500" : "#17a673",
        fillOpacity: 0.85
      });
      m.bindPopup(balon(k[i], k[i + 1], bi, d.ad));
      g.addLayer(m);
    }
    g.nokta = g.getLayers().length;   // filtre sonrasi GERCEK sayi
    return g;
  }

  function ilYukle(p) {
    if (ilKat[p] || yukleniyor[p]) return;
    yukleniyor[p] = true;
    var ad = ("0" + p).slice(-2);
    fetch(KOK + "veri/il-" + ad + ".json")
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        ilKat[p] = ilCiz(d);
        if (harita.getZoom() >= AC_ZOOM) harita.addLayer(ilKat[p]);
        yenile();
      })
      .catch(function (e) { durum("İl verisi alınamadı (" + ad + "): " + e.message); })
      .then(function () { delete yukleniyor[p]; });
  }

  function yenile() {
    var z = harita.getZoom(), s = harita.getBounds();
    if (z < AC_ZOOM) {
      if (!harita.hasLayer(balonKat)) harita.addLayer(balonKat);
      for (var p in ilKat) if (harita.hasLayer(ilKat[p])) harita.removeLayer(ilKat[p]);
      durum("Yakınlaştır: il seçtiğinde o ilin otoparkları yüklenir.");
      return;
    }
    if (harita.hasLayer(balonKat)) harita.removeLayer(balonKat);
    var gorunen = 0, bekleyen = 0;
    ozet.iller.forEach(function (il) {
      if (!kesisiyor(il.bb, s)) {
        if (ilKat[il.p] && harita.hasLayer(ilKat[il.p])) harita.removeLayer(ilKat[il.p]);
        return;
      }
      if (ilKat[il.p]) {
        if (!harita.hasLayer(ilKat[il.p])) harita.addLayer(ilKat[il.p]);
        gorunen += ilKat[il.p].nokta != null ? ilKat[il.p].nokta : il.n;
      } else { bekleyen++; ilYukle(il.p); }
    });
    durum(bekleyen ? "Yükleniyor…"
                   : gorunen.toLocaleString("tr") +
                     (SADECE_UCRETSIZ ? " ücretsiz otopark" : " otopark") + " gösteriliyor");
  }

  function balonlar() {
    var g = L.layerGroup();
    ozet.iller.forEach(function (il) {
      var r = Math.max(7, Math.min(26, Math.sqrt(il.n) * 0.55));
      var m = L.circleMarker(il.c, {
        renderer: tuval, radius: r, weight: 1.5, color: "#0b3d2e",
        fillColor: "#17a673", fillOpacity: 0.55
      });
      m.bindTooltip(il.ad + " · " + il.n.toLocaleString("tr"), { direction: "top" });
      m.on("click", function () { harita.setView(il.c, 11); });
      g.addLayer(m);
    });
    return g;
  }

  function konumBul() {
    var b = $("#harita-konum");
    if (!navigator.geolocation) { durum("Tarayıcı konum desteklemiyor."); return; }
    b.disabled = true; durum("Konum alınıyor…");
    navigator.geolocation.getCurrentPosition(function (k) {
      b.disabled = false;
      var ll = [k.coords.latitude, k.coords.longitude];
      harita.setView(ll, 14);
      L.circleMarker(ll, { renderer: tuval, radius: 8, weight: 3,
        color: "#1d4ed8", fillColor: "#60a5fa", fillOpacity: 0.9 })
        .addTo(harita).bindPopup("Buradasın").openPopup();
    }, function (e) {
      b.disabled = false;
      durum(e.code === 1 ? "Konum izni verilmedi." : "Konum alınamadı.");
    }, { enableHighAccuracy: true, timeout: 10000 });
  }

  /** ?il=<plaka> ile gelindiginde o ile yakinlastir (il sayfalarindaki
   *  "haritada ac" baglantisi bunu kullanir). */
  function ilAc(kod) {
    if (!kod || !ozet) return;
    // "?il=06" -> 6: string karsilastirma "06"!=="6" yuzunden eslesmiyordu
    var n = parseInt(kod, 10);
    var il = ozet.iller.filter(function (x) { return x.p === n; })[0];
    if (!il) return;
    harita.setView(il.c, 11);
  }

  /** 81 rozet mobilde uzun liste; arama kutusu daraltir. */
  function aramaKur() {
    var i = $("#il-ara");
    if (!i) return;
    var rozet = [].slice.call(document.querySelectorAll(".il-rozet"));
    var sayac = $("#il-ara-sayac");
    i.addEventListener("input", function () {
      var q = i.value.trim().toLocaleLowerCase("tr");
      var n = 0;
      rozet.forEach(function (b) {
        var uy = !q || b.textContent.toLocaleLowerCase("tr").indexOf(q) > -1;
        b.hidden = !uy;
        if (uy) n++;
      });
      if (sayac) sayac.textContent = q ? n + " il" : "";
    });

    // ?q= ile gelen arama. Ana sayfadaki schema.org SearchAction bu adresi
    // ILAN EDIYOR; karsiligi olmadan birakmak beyan edilip yapilmayan bir
    // yetenek olurdu (Google sitelinks arama kutusu bos donerdi).
    var q0 = (SORGU.get("q") || "").trim();
    if (q0) {
      i.value = q0;
      i.dispatchEvent(new Event("input"));
      // Tek il kaldiysa dogrudan ona git; birden coksa liste filtreli kalir.
      var kalan = rozet.filter(function (b) { return !b.hidden; });
      if (kalan.length === 1) kalan[0].click();
      else if (sayac && !kalan.length) sayac.textContent = "eşleşme yok";
    }
  }

  function kur() {
    harita = L.map("harita", { zoomControl: true, preferCanvas: true })
      .setView([39.1, 35.2], 6);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: "&copy; OpenStreetMap katkıcıları"
    }).addTo(harita);
    tuval = L.canvas({ padding: 0.5 });

    fetch(KOK + "veri/iller.json")
      .then(function (r) { return r.json(); })
      .then(function (d) {
        ozet = d;
        balonKat = balonlar().addTo(harita);
        var t = $("#harita-toplam");
        if (t) t.textContent = d.toplam.toLocaleString("tr");
        harita.on("moveend zoomend", yenile);
        yenile();
        ilAc(SORGU.get("il"));
      })
      .catch(function (e) { durum("Harita verisi alınamadı: " + e.message); });

    var kb = $("#harita-konum");
    if (kb) kb.addEventListener("click", konumBul);
    if (SADECE_UCRETSIZ) {
      var u = $("#harita-filtre");
      if (u) u.hidden = false;
    }

    Array.prototype.forEach.call(document.querySelectorAll(".il-rozet"), function (b) {
      b.addEventListener("click", function () {
        harita.setView([parseFloat(b.dataset.lat), parseFloat(b.dataset.lng)], 11);
        document.getElementById("harita").scrollIntoView({ behavior: "smooth", block: "center" });
      });
    });
    // SIRA ONEMLI: aramaKur() ?q= icin rozete click() atiyor, dinleyici
    // bagli olmadan cagirilirsa hicbir sey olmuyordu.
    aramaKur();
  }

  if (document.getElementById("harita")) {
    document.readyState === "loading"
      ? document.addEventListener("DOMContentLoaded", kur) : kur();
  }
})();
