# -*- coding: utf-8 -*-
"""TESLIM ONCESI ZORUNLU KONTROL. Markup degil HESAPLANAN deger olcer.
CLAUDE.md: 0px veya tarayici varsayilani -> CSS dusmus demektir."""
import subprocess, sys, threading, http.server, socketserver, functools, time
from playwright.sync_api import sync_playwright

PORT = 8731
GENISLIK = [(375, 812, "mobil"), (768, 1024, "tablet"), (1440, 900, "masaustu")]
SAYFA = ["/", "/ilce/fatih/", "/ilce/besiktas/", "/fiyat-endeksi/",
         "/izmir/", "/izmir/ilce/konak/", "/ankara/", "/ankara/ilce/cankaya/",
         "/harita/", "/il/", "/il/ankara/", "/il/bayburt/", "/ucretsiz-otopark/",
         "/gizlilik/", "/giris/", "/favoriler/", "/hesap-sil/", "/boyle-bir-sayfa-yok/"]
# Bu yollar Vercel cleanUrls / 404 yonlendirmesi gerektiriyor; yerel
# SimpleHTTPRequestHandler saglamaz, yalniz canli modda olculur.
CANLI_YOL = {"/gizlilik/", "/boyle-bir-sayfa-yok/"}
# 404 sayfasini olcmek icin bilerek var olmayan yol isteniyor; o istegin
# kendi 404'u BEKLENEN, konsol hatasi sayilmaz.
YOK_YOL = "/boyle-bir-sayfa-yok/"
TABANAD = ""

def sunucu():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory="site")
    socketserver.TCPServer.allow_reuse_address = True
    s = socketserver.TCPServer(("127.0.0.1", PORT), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s

OLCUM = """() => {
  const g = (s,p) => { const e=document.querySelector(s); return e?getComputedStyle(e)[p]:null; };
  const r = {};
  r.h1_font   = g('h1','fontSize');
  r.h1_mb     = g('h1','marginBottom');
  r.kahr_pt   = g('.kahraman','paddingTop');
  r.body_pl   = g('body','paddingLeft') ;
  r.main_pl   = getComputedStyle(document.querySelector('main')).paddingLeft;
  r.liste_gap = g('.liste','gap') || g('.ilce-izgara','gap');
  r.kart_p    = g('.otopark','padding') || g('.ilce','padding');
  r.tasma     = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  // WCAG 2.5.8 muafiyeti: akan metin icindeki satir ici linkler haric
  r.kucuk_dokunma = [...document.querySelectorAll('a,button')]
      .filter(e=>{const b=e.getBoundingClientRect();
        if(!(b.width>0 && b.height>0 && b.height<44)) return false;
        if(e.classList.contains('atla')) return false;
        // leaflet atif kutusu div ama icerigi akan metin ("Leaflet | (c) OSM
        // katkicilari"), satir ici muafiyeti oraya da gecer
        return !e.closest('p, li, .iz, .leaflet-control-attribution');})
      .map(e=>e.textContent.trim().slice(0,28));
  r.yer_tutucu = (document.body.innerText.match(/\{[a-z_]+\}/g)||[]).length;
  // ust uste binme: kahraman ile ilk bolum
  // gizli bolumler olculmez: rect sifir doner, sahte negatif uretir
  const gorunur = e => { const b=e.getBoundingClientRect(); return b.width>0 && b.height>0; };
  const a=document.querySelector('.kahraman');
  const b=[...document.querySelectorAll('.liste,.ilce-izgara')].find(gorunur);
  if(a&&b){const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect(); r.bosluk_px=Math.round(rb.top-ra.bottom);}
  // stil dosyasi GERCEKTEN geldi mi: cleanUrls goreli yolu kaydirinca
  // sayfa 200 doner ama CSS 404 olur, markup saglam gorunur
  r.css_kural = [...document.styleSheets].reduce((n,s)=>{
      try { return n + s.cssRules.length } catch(e) { return n }}, 0);
  r.css_adres = [...document.styleSheets].map(s=>s.href).filter(Boolean);
  return r;
}"""

# Ana sayfadaki "en yakin otoparklar" bir sure YALNIZ ISPARK (Istanbul)
# verisini kullaniyordu: Ankara'daki kullaniciya Tuzla'yi gosteriyordu ve
# sessizce yanlis cevap veriyordu. Bu senaryo o hatanin nobetcisi.
KONUM = [("Ankara Kızılay", 39.9208, 32.8541, "Ankara"),
         ("İzmir Konak",    38.4192, 27.1287, "İzmir"),
         ("İstanbul Kadıköy", 40.9903, 29.0270, "KADIKÖY")]

def konum_testi(tarayici, taban):
    sorun = []
    for ad, la, lo, beklenen in KONUM:
        ctx = tarayici.new_context(viewport={"width": 390, "height": 844},
              geolocation={"latitude": la, "longitude": lo},
              permissions=["geolocation"], locale="tr-TR")
        sf = ctx.new_page()
        sf.goto(f"{taban}/", wait_until="networkidle")
        sf.click("#yakin"); sf.wait_for_timeout(4000)
        n = sf.locator("#yakin-liste .otopark").count()
        adres = sf.inner_text("#yakin-liste .otopark .adres") if n else ""
        print(f"\n--- konum {ad}: {n} kart · ilk adres {adres!r}")
        if not n:
            sorun.append(f"konum {ad}: hic otopark listelenmedi")
        elif beklenen.lower() not in adres.lower():
            sorun.append(f"konum {ad}: en yakin otopark {adres!r} - "
                         f"{beklenen!r} bekleniyordu (yanlis il)")
        ctx.close()
    return sorun

def main():
    # argv[1] verilirse canli adres olculur. Yerel SimpleHTTPRequestHandler
    # cleanUrls yapmadigi icin /gizlilik/ gibi yollar ve goreli-yol kaymasi
    # YALNIZ canlida gorunur - o yuzden bu secenek sart.
    canli = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else None
    s = None if canli else sunucu()
    if not canli: time.sleep(0.6)
    global TABANAD
    TABANAD = canli or f"http://127.0.0.1:{PORT}"
    hata, uyari = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        for w, h, ad in GENISLIK:
            sf = b.new_page(viewport={"width": w, "height": h})
            konsol, dis = [], []
            # /_vercel/insights/ betigini Vercel calisma aninda servis eder; yerel
            # statik sunucuda 404 verir. Yerelde yanlis pozitif, canlida 200 olmali
            # (isit.py ve canli kontrol dogruluyor).
            vercel404 = []
            sf.on("response", lambda r: vercel404.append(r.url)
                  if "/_vercel/" in r.url and r.status == 404 else None)
            sf.on("console", lambda m: konsol.append(f"{m.type}: {m.text[:90]}") if m.type in ("error","warning") else None)
            sf.on("pageerror", lambda e: konsol.append(f"pageerror: {str(e)[:90]}"))
            # Dis servis arizasi bizim kusurumuz degil: ayri topla, HATA sayma.
            sf.on("response", lambda r: dis.append(f"{r.status} {r.url[:70]}")
                  if r.status >= 500 and "127.0.0.1" not in r.url and "localhost" not in r.url else None)
            for yol in SAYFA:
                if yol in CANLI_YOL and TABANAD.startswith("http://127."):
                    continue
                onceki = len(konsol)
                sf.goto(f"{TABANAD}{yol}", wait_until="networkidle")
                r = sf.evaluate(OLCUM)
                print(f"\n--- {ad} {w}x{h} · {yol}")
                for k, v in r.items(): print(f"    {k:<16} {v}")
                if r["tasma"] > 0: hata.append(f"{ad}{yol}: yatay tasma {r['tasma']}px")
                # None = sayfada .kahraman YOK (orn. /giris/ .giris-sar kullanir);
                # bu bir CSS dususu degil. Gercek dusus "0px" ile gelir. O sayfalar
                # zaten css_kural>0 ve h1 varsayilan-degil testleriyle korunuyor.
                if r["kahr_pt"] == "0px": hata.append(f"{ad}{yol}: .kahraman padding-top 0px -> CSS dusmus")
                if r["main_pl"] in ("0px", None): hata.append(f"{ad}{yol}: main yan bosluk 0px")
                if r["h1_font"] in ("32px", None): hata.append(f"{ad}{yol}: h1 {r['h1_font']} = tarayici varsayilani -> CSS dusmus")
                if r["css_kural"] == 0:
                    hata.append(f"{ad}{yol}: stil dosyasi HIC yuklenmedi "
                                f"(kural 0, adres {r['css_adres']}) -> goreli yol kaymasi")
                if r["yer_tutucu"]: hata.append(f"{ad}{yol}: {r['yer_tutucu']} doldurulmamis yer tutucu")
                if r.get("bosluk_px", 1) < 0: hata.append(f"{ad}{yol}: ust uste binme {r['bosluk_px']}px")
                if r["kucuk_dokunma"]: uyari.append(f"{ad}{yol}: <44px dokunma -> {r['kucuk_dokunma']}")
                if yol == YOK_YOL:
                    del konsol[onceki:]   # beklenen 404, kusur degil
            if dis:
                uyari.append(f"{ad}: DIS SERVIS 5xx (bizim kusurumuz degil) -> {sorted(set(dis))[:2]}")
                konsol = [k for k in konsol if "Failed to load resource" not in k]
            if vercel404:
                konsol = [k for k in konsol if "Failed to load resource" not in k]
                uyari.append(f"{ad}: /_vercel/ 404 (yerelde beklenen, canlida kontrol et)")
            if konsol: hata.append(f"{ad}: konsol -> {konsol[:3]}")
            sf.close()
        hata += konum_testi(b, TABANAD)
        b.close()
    if s: s.shutdown()
    print("\n" + "="*54)
    print("HATA :", len(hata)); [print("  x", x) for x in hata]
    print("UYARI:", len(uyari)); [print("  !", x) for x in uyari]
    sys.exit(1 if hata else 0)

if __name__ == "__main__": main()
