# -*- coding: utf-8 -*-
"""Adres arama + en yakin otopark + uygulama ici yol tarifi regresyon testi.

DIS SERVIS KULLANIR: Nominatim (adres) ve OSRM demo (rota). Yani bu dosya
internet olmadan gecmez ve servis yavassa uzun surer - bu yuzden test_uret.py
icinde degil, ayri. test_uret.py yalniz "kod o servisi cagiriyor mu" bakar;
burasi "cagri gercekten sonuc donuyor mu" bakar.

Calistir: python kontrol_adres.py   (hata varsa exit 1)
"""
import threading, http.server, socketserver, functools, sys
from playwright.sync_api import sync_playwright

PORT = 8746
BEKLENEN_404 = ("/_vercel/",)     # yerel sunucu Vercel Analytics betigini sunmaz

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
        p = t.new_context(viewport={"width": 375, "height": 812}, locale="tr-TR").new_page()
        kotu = []
        p.on("response", lambda r: kotu.append(f"{r.status} {r.url}")
             if r.status >= 400 and not any(x in r.url for x in BEKLENEN_404) else None)

        p.goto(f"{T}/harita/", wait_until="networkidle")
        es("baslangicta yakin kutusu gizli",
           p.locator("#adres-yakin-kutu").is_visible(), False)
        es("baslangicta yol kutusu gizli", p.locator("#yol").is_visible(), False)

        p.fill("#adres", "Kadikoy Istanbul")
        p.click("#adres-form button[type=submit]")
        p.wait_for_selector("#adres-yakin li", timeout=40000)

        n = p.locator("#adres-yakin li").count()
        es("yakin otopark listelendi", 0 < n <= 8, True)
        es("baslikta adres geciyor",
           "Kadıköy" in p.inner_text("#adres-yakin-baslik"), True)
        ilk = p.locator("#adres-yakin li").first.inner_text()
        es("kartta mesafe yazili", ("m uzakta" in ilk or "km uzakta" in ilk), True)
        k = p.locator("#adres-yakin .yol-dug").first.bounding_box()
        es("yol dugmesi 44px+", k["height"] >= 44, True)

        # Yol tarifi UYGULAMA ICINDE: adimlar sayfada cikmali, disariya atmamali.
        p.locator("#adres-yakin .yol-dug").first.click()
        p.wait_for_function("document.querySelectorAll('#yol-adim li').length>0",
                            timeout=45000)
        ozet = p.inner_text("#yol-ozet")
        es("ozette mesafe+sure var", ("·" in ozet and "yaklaşık" in ozet), True)
        es("ozet hata metni degil", "alınamadı" in ozet, False)
        es("ilk adim yola cikisla basliyor",
           p.locator("#yol-adim li").first.inner_text().startswith("Yola çık"), True)
        es("adim metni buyuk harfle basliyor",
           all(s[:1].isupper() for s in
               p.locator("#yol-adim li").all_inner_texts() if s.strip()), True)
        es("rota cizgisi haritaya dusuldu",
           p.evaluate("!!document.querySelector('#harita .leaflet-overlay-pane path')"), True)

        es("mobilde yatay tasma yok", p.evaluate(
            "document.documentElement.scrollWidth - document.documentElement.clientWidth"), 0)
        es("beklenmeyen 4xx/5xx yok", kotu, [])
        t.close()
    srv.shutdown()

if __name__ == "__main__":
    main()
    print("\nADRES + YOL TARIFI: " + (", ".join(hata) if hata else "hepsi gecti"))
    sys.exit(1 if hata else 0)
