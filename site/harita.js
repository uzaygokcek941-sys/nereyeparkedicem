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
      '<button type="button" class="balon-yol" data-lat="' + lat + '" data-lng="' +
      lng + '">Yol tarifi (uygulama içinde)</button>' +
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

  // Ham il verisi onbellegi: hem katman cizimi hem "en yakin otopark" hesabi
  // ayni dosyayi istiyor, iki kez indirmesin.
  var ham = {};
  function ilHam(p) {
    if (ham[p]) return Promise.resolve(ham[p]);
    var ad = ("0" + p).slice(-2);
    return fetch(KOK + "veri/il-" + ad + ".json")
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { ham[p] = d; return d; });
  }

  function ilYukle(p) {
    if (ilKat[p] || yukleniyor[p]) return;
    yukleniyor[p] = true;
    ilHam(p)
      .then(function (d) {
        ilKat[p] = ilCiz(d);
        if (harita.getZoom() >= AC_ZOOM) harita.addLayer(ilKat[p]);
        yenile();
      })
      .catch(function (e) {
        durum("İl verisi alınamadı (" + ("0" + p).slice(-2) + "): " + e.message);
      })
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
      basla(k.coords.latitude, k.coords.longitude, "Bulunduğun yer");
    }, function (e) {
      b.disabled = false;
      durum(e.code === 1 ? "Konum izni verilmedi." : "Konum alınamadı.");
    }, { enableHighAccuracy: true, timeout: 10000 });
  }

  /* ---------- adres arama + en yakin otoparklar + yol tarifi ---------- */
  var BAS = null;                 // baslangic noktasi {lat,lng,ad}
  var basKat = null, yolKat = null;

  function mesafeKm(a1, n1, a2, n2) {          // haversine
    var R = 6371, t = Math.PI / 180;
    var dl = (a2 - a1) * t, dn = (n2 - n1) * t;
    var x = Math.sin(dl / 2) * Math.sin(dl / 2) + Math.cos(a1 * t) *
      Math.cos(a2 * t) * Math.sin(dn / 2) * Math.sin(dn / 2);
    return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
  }
  function uzunluk(m) {
    return m < 950 ? Math.round(m / 10) * 10 + " m"
                   : (m / 1000).toFixed(1).replace(".", ",") + " km";
  }
  function sure(sn) {
    var d = Math.round(sn / 60);
    return d < 60 ? d + " dk" : Math.floor(d / 60) + " sa " + (d % 60) + " dk";
  }
  // Kullanici girdisi ve OSM adlari HTML'e metin olarak girer, oznitelige degil.
  function yaz(el, s) { el.textContent = s == null ? "" : String(s); }

  /** Baslangic noktasini kurar: isaretci, gorunum, yakin otopark listesi. */
  function basla(lat, lng, ad) {
    BAS = { lat: lat, lng: lng, ad: ad };
    if (basKat) harita.removeLayer(basKat);
    basKat = L.circleMarker([lat, lng], { renderer: tuval, radius: 9, weight: 3,
      color: "#1d4ed8", fillColor: "#60a5fa", fillOpacity: 0.9 }).addTo(harita);
    // Nominatim'den gelen ad kullanici girdisine dayaniyor: metin dugumu olarak
    // bagla, HTML dizesi olarak DEGIL.
    var pe = document.createElement("div"); pe.textContent = ad;
    basKat.bindPopup(pe);
    harita.setView([lat, lng], 14);
    durum(ad + " — çevredeki otoparklar aranıyor…");
    yakinlariBul(lat, lng);
  }

  /** Noktaya en yakin otoparklar. Yalniz noktayi iceren/komsu illerin verisi
   *  indirilir; 81 ilin tamami ~1 MB, hepsini cekmek gereksiz. */
  function yakinlariBul(lat, lng) {
    var P = 0.45;                                // ~50 km'lik komsuluk payi
    var adaylar = ozet.iller.filter(function (il) {
      return il.bb[0] - P <= lat && il.bb[2] + P >= lat &&
             il.bb[1] - P <= lng && il.bb[3] + P >= lng;
    });
    Promise.all(adaylar.map(function (il) {
      return ilHam(il.p).catch(function () { return null; });
    })).then(function (liste) {
      var s = [];
      liste.forEach(function (d) {
        if (!d) return;
        for (var i = 0; i < d.k.length; i += 2) {
          var bi = d.b[i / 2];
          if (SADECE_UCRETSIZ && !(bi && bi.u === 0)) continue;
          var u = mesafeKm(lat, lng, d.k[i], d.k[i + 1]);
          if (u <= 25) s.push({ lat: d.k[i], lng: d.k[i + 1], b: bi, il: d.ad, u: u });
        }
      });
      s.sort(function (a, b) { return a.u - b.u; });
      yakinCiz(s.slice(0, 8));
    });
  }

  function yakinCiz(liste) {
    var kutu = $("#adres-yakin-kutu"), ul = $("#adres-yakin");
    if (!kutu || !ul) return;
    ul.innerHTML = "";
    if (!liste.length) {
      kutu.hidden = true;
      durum(BAS.ad + " bulundu, ama 25 km içinde kayıtlı otopark yok.");
      return;
    }
    var bas = $("#adres-yakin-baslik");
    if (bas) yaz(bas, BAS.ad + " çevresindeki otoparklar");
    liste.forEach(function (o) {
      var li = document.createElement("li");
      var ad = document.createElement("strong");
      yaz(ad, (o.b && o.b.a) ? o.b.a : "Otopark");
      var alt = document.createElement("span");
      alt.className = "yakin-alt";
      var p = [uzunluk(o.u * 1000) + " uzakta", o.il];
      if (o.b && o.b.u === 1) p.push("ücretli");
      else if (o.b && o.b.u === 0) p.push("ücretsiz");
      if (o.b && o.b.k) p.push(o.b.k + " kapasite");
      yaz(alt, p.join(" · "));
      var dug = document.createElement("button");
      dug.type = "button"; dug.className = "birincil yol-dug";
      dug.textContent = "Yol tarifi";
      dug.addEventListener("click", function () { yolCiz(o.lat, o.lng, ad.textContent); });
      var goster = document.createElement("button");
      goster.type = "button"; goster.className = "ikincil";
      goster.textContent = "Haritada";
      goster.addEventListener("click", function () { harita.setView([o.lat, o.lng], 17); });
      li.appendChild(ad); li.appendChild(alt);
      var dg = document.createElement("span"); dg.className = "yakin-dug";
      dg.appendChild(dug); dg.appendChild(goster); li.appendChild(dg);
      ul.appendChild(li);
    });
    kutu.hidden = false;
    durum(liste.length + " otopark bulundu — en yakını " +
          uzunluk(liste[0].u * 1000) + ".");
  }

  var YON = { left: "sola", right: "sağa", "slight left": "hafif sola",
    "slight right": "hafif sağa", "sharp left": "keskin sola",
    "sharp right": "keskin sağa", straight: "düz", uturn: "U dönüşü" };

  /** OSRM adimi Turkce cumleye. Sunucu yalniz tip+yon kodu doner, metni
   *  ureten taraf biziz (OSRM'in kendi metin eklentisi ingilizce). */
  function adimMetin(s) {
    var m = s.maneuver, y = YON[m.modifier] || "", ad = s.name || "", t;
    switch (m.type) {
      case "depart": t = "Yola çık"; break;
      case "arrive": t = "Varış"; break;
      case "roundabout": case "rotary":
        t = "Göbekte " + (m.exit ? m.exit + ". " : "") + "çıkışı al"; break;
      case "merge": t = y ? y + " katıl" : "Katıl"; break;
      case "fork": t = y ? "Ayrımda " + y + " devam et" : "Ayrımda devam et"; break;
      case "on ramp": t = "Bağlantı yoluna gir"; break;
      case "off ramp": t = "Bağlantı yolundan çık"; break;
      case "end of road": t = y ? "Yol sonunda " + y + " dön" : "Yol sonunda dön"; break;
      case "new name": case "continue":
        t = (y && y !== "düz") ? y + " devam et" : "Düz devam et"; break;
      default: t = y === "U dönüşü" ? "U dönüşü yap" : (y ? y + " dön" : "Devam et");
    }
    // "sola dön" cumle basinda kucuk kaliyordu; "i" -> "İ" icin tr yerel ayari.
    t = t.charAt(0).toLocaleUpperCase("tr") + t.slice(1);
    return t + (ad ? " — " + ad : "");
  }

  function yolCiz(hLat, hLng, hAd) {
    var kutu = $("#yol"), ozetEl = $("#yol-ozet"), ol = $("#yol-adim");
    if (!kutu) return;
    if (!BAS) { durum("Önce adres ara ya da “Konumum”a bas."); return; }
    kutu.hidden = false; ol.innerHTML = "";
    yaz(ozetEl, "Rota hesaplanıyor…");
    kutu.scrollIntoView({ behavior: "smooth", block: "start" });
    fetch("https://router.project-osrm.org/route/v1/driving/" +
          BAS.lng + "," + BAS.lat + ";" + hLng + "," + hLat +
          "?overview=full&geometries=geojson&steps=true")
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) {
        if (d.code !== "Ok" || !d.routes || !d.routes.length)
          throw new Error(d.code === "NoRoute" ? "araçla gidilebilir yol yok" : d.code);
        var r = d.routes[0];
        if (yolKat) harita.removeLayer(yolKat);
        // Noktalar canvas'ta (binlerce daire), rota TEK cizgi: SVG'de birakildi
        // - canvas'ta kenarlari tirtikli ciziliyor ve nokta katmanlarinin
        // altinda kaliyordu.
        yolKat = L.polyline(r.geometry.coordinates.map(function (c) {
          return [c[1], c[0]];
        }), { renderer: L.svg(), color: "#1d4ed8", weight: 5, opacity: 0.85 })
          .addTo(harita);
        harita.fitBounds(yolKat.getBounds(), { padding: [30, 30] });
        yaz(ozetEl, BAS.ad + " → " + hAd + " · " + uzunluk(r.distance) +
                    " · yaklaşık " + sure(r.duration));
        r.legs[0].steps.forEach(function (s) {
          var li = document.createElement("li");
          var t = document.createElement("span");
          yaz(t, adimMetin(s));
          li.appendChild(t);
          if (s.distance >= 20) {
            var u = document.createElement("b");
            yaz(u, uzunluk(s.distance));
            li.appendChild(u);
          }
          ol.appendChild(li);
        });
      })
      .catch(function (e) {
        yaz(ozetEl, "Yol tarifi alınamadı: " + e.message +
            ". Balondaki Google Maps / Yandex bağlantıları çalışmaya devam ediyor.");
      });
  }

  /** Adres -> koordinat (Nominatim). Kullanim kosulu geregi her tusa basista
   *  degil, YALNIZ gonderimde sorgulanir. */
  function adresAra(q) {
    var sec = $("#adres-secenek");
    sec.hidden = true; sec.innerHTML = "";
    durum("“" + q + "” aranıyor…");
    fetch("https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5" +
          "&countrycodes=tr&accept-language=tr&q=" + encodeURIComponent(q))
      .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
      .then(function (d) {
        if (!d.length) { durum("Bu adres bulunamadı. İl veya ilçe adı ekleyip dene."); return; }
        basla(+d[0].lat, +d[0].lon, d[0].display_name.split(",").slice(0, 3).join(","));
        if (d.length > 1) {
          var b = document.createElement("span");
          b.className = "adres-secenek-etiket";
          b.textContent = "Bunu mu demek istedin?";
          sec.appendChild(b);
          d.slice(1).forEach(function (x) {
            var dug = document.createElement("button");
            dug.type = "button";
            dug.textContent = x.display_name.split(",").slice(0, 3).join(",");
            dug.addEventListener("click", function () {
              sec.hidden = true;
              basla(+x.lat, +x.lon, dug.textContent);
            });
            sec.appendChild(dug);
          });
          sec.hidden = false;
        }
      })
      .catch(function (e) { durum("Adres araması başarısız: " + e.message); });
  }

  function adresKur() {
    var f = $("#adres-form"), i = $("#adres");
    if (!f || !i) return;
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var q = i.value.trim();
      if (q) adresAra(q);
    });
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
    adresKur();
    // Balonlar Leaflet tarafindan sonradan basiliyor: dinleyiciyi tek yerden,
    // harita kabina delege et.
    harita.getContainer().addEventListener("click", function (e) {
      var d = e.target.closest ? e.target.closest(".balon-yol") : null;
      if (!d) return;
      var kap = d.parentNode.querySelector("strong");
      yolCiz(+d.dataset.lat, +d.dataset.lng, kap ? kap.textContent : "Otopark");
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
