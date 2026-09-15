# -*- coding: utf-8 -*-
"""Favori + giris akisi regresyon testi. DAVRANIS olcer, markup degil.

kontrol.py hesaplanan CSS degerlerini olcer; bu dosya kullanicinin fiilen
yaptigi isi yapar: yildiza bas, sayfayi yenile, /favoriler/'e git, cikar.
Ayri dosya cunku kontrol.py sayfa-bazli donuyor, bu ise oturum tasiyor.

Calistir: python kontrol_favori.py   (hata varsa exit 1)
"""
import threading, http.server, socketserver, functools, sys
from playwright.sync_api import sync_playwright

PORT = 8744
# Yerel SimpleHTTPRequestHandler Vercel Analytics betigini sunmaz; o 404
# BEKLENEN, konsol hatasi sayilmaz.
BEKLENEN_404 = ("/_vercel/",)

hata = []
def es(ad, olan, bek):
    ok = olan == bek
    print(("  OK  " if ok else "  X   ") + f"{ad}: {olan!r}" +
          ("" if ok else f"   (beklenen {bek!r})"))
    if not ok:
        hata.append(ad)

def main():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory="site")
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    T = f"http://127.0.0.1:{PORT}"

    with sync_playwright() as pw:
        t = pw.chromium.launch()
        s = t.new_context(viewport={"width": 375, "height": 812}, locale="tr-TR")
        p = s.new_page()
        kotu = []
        p.on("response", lambda r: kotu.append(f"{r.status} {r.url}")
             if r.status >= 400 and not any(x in r.url for x in BEKLENEN_404) else None)

        # 1) yildizlar kartlara basiliyor mu
        p.goto(f"{T}/ilce/fatih/", wait_until="networkidle")
        es("kartlara yildiz basildi", p.locator(".otopark .yildiz").count() > 0, True)
        y = p.locator(".otopark .yildiz").first
        es("yildiz baslangicta bos", y.get_attribute("aria-pressed"), "false")
        k = y.bounding_box()
        es("yildiz dokunma alani 44px", round(min(k["width"], k["height"])), 44)

        ad = p.locator(".otopark").first.get_attribute("data-ad")
        y.click()
        es("tiklayinca basili", y.get_attribute("aria-pressed"), "true")
        l = p.evaluate("JSON.parse(localStorage.getItem('np.favori')||'[]')")
        es("localStorage 1 kayit", len(l), 1)
        es("kayit adi kart adiyla ayni", l[0]["ad"], ad)
        es("kayitta gercek koordinat", bool(l[0]["lat"]) and bool(l[0]["lng"]), True)

        # 2) yenilemeye dayaniyor mu
        p.reload(wait_until="networkidle")
        es("yenilemeden sonra dolu",
           p.locator(".otopark .yildiz").first.get_attribute("aria-pressed"), "true")

        # 3) /favoriler/ sayfasi
        p.goto(f"{T}/favoriler/", wait_until="networkidle")
        p.wait_for_timeout(400)
        es("favorilerde 1 kart", p.locator("#favori-liste .otopark").count(), 1)
        es("kart basligi dogru", p.locator("#favori-liste h3").first.inner_text().strip(), ad)
        es("bos durum gizli", p.locator("#favori-bos").is_visible(), False)

        # 4) auth YAPILANDIRILMAMISKEN durus: yalan soylememeli, kilitli olmali
        auth = p.evaluate("fetch('/veri/auth.json').then(r=>r.json())")
        acik = bool(auth.get("url")) and "YAPILANDIRILMADI" not in \
            f"{auth.get('url')}{auth.get('anonKey')}"
        if not acik:
            es("auth kapali: cikis dugmesi gizli", p.locator("#cikis").is_visible(), False)
        else:
            es("auth acik: cikis dugmesi var", p.locator("#cikis").count(), 1)

        # 5) favoriden cikarma
        p.locator("#favori-liste .yildiz").first.click()
        p.wait_for_timeout(300)
        es("cikarinca bos durum gorunur", p.locator("#favori-bos").is_visible(), True)
        es("localStorage bosaldi",
           p.evaluate("JSON.parse(localStorage.getItem('np.favori')||'[]').length"), 0)

        # 6) giris sayfasi
        p.goto(f"{T}/giris/", wait_until="networkidle")
        p.wait_for_timeout(500)
        if not acik:
            es("auth kapali: e-posta alani kilitli", p.locator("#eposta").is_disabled(), True)
            es("auth kapali: google kilitli", p.locator("#google-giris").is_disabled(), True)
            es("auth kapali: sebep yazili",
               "açık değil" in p.locator("#giris-durum").inner_text(), True)
            # 218 KB supabase.js gereksiz yere inmemeli
            es("auth kapali: supabase.js yuklenmedi", p.evaluate("!!window.supabase"), False)
        else:
            es("auth acik: e-posta alani kullanilabilir",
               p.locator("#eposta").is_disabled(), False)
            es("auth acik: supabase.js yuklendi", p.evaluate("!!window.supabase"), True)

        # 7) mobil kabuk
        es("alt sekme mobilde gorunur", p.locator(".alt-sekme").is_visible(), True)
        es("ust nav mobilde gizli", p.locator(".ust nav").is_visible(), False)
        es("yatay tasma yok", p.evaluate(
            "document.documentElement.scrollWidth - document.documentElement.clientWidth"), 0)
        es("sekme yuksekligi 44px+",
           p.locator(".alt-sekme a").first.bounding_box()["height"] >= 44, True)

        # 8) masaustu kabugu
        p.set_viewport_size({"width": 1440, "height": 900})
        p.wait_for_timeout(200)
        es("alt sekme masaustunde gizli", p.locator(".alt-sekme").is_visible(), False)
        es("ust nav masaustunde gorunur", p.locator(".ust nav").is_visible(), True)

        es("beklenmeyen 4xx/5xx yok", kotu, [])
        t.close()
    srv.shutdown()

if __name__ == "__main__":
    main()
    print("\nFAVORI AKISI: " + (", ".join(hata) if hata else "hepsi gecti"))
    sys.exit(1 if hata else 0)
