# -*- coding: utf-8 -*-
"""Statik site ureticisi. veri/ispark.json -> site/
Canli doluluk tarayicida IBB API'sinden cekilir (CORS: *), sunucu yok."""
import json, os, re, shutil, html
from datetime import datetime, timezone, timedelta

TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
CIKTI = "site"
URL = "https://nereyeparkedicem.vercel.app"

def iller():
    """site/veri/iller.json - harita_veri.py uretir. Yoksa bos liste doner,
    site harita katmani olmadan da uretilebilsin."""
    try:
        return json.load(open(f"{CIKTI}/veri/iller.json", encoding="utf-8"))
    except (OSError, ValueError):
        return {"toplam": 0, "iller": []}

def tr_baslik(s):
    """Turkce baslik harfi. Python .title() I/i ayrimini bilmez:
    'KADIKOY'.title() -> 'Kadikoy' (yanlis), dogrusu 'Kadikoy' degil 'Kadıköy'."""
    if not s: return ""
    kucuk = s.replace("I", "ı").replace("İ", "i").lower()
    return " ".join((k[0].replace("i", "İ").upper() + k[1:]) if k else k for k in kucuk.split())

def slug(s):
    s = (s or "").translate(TR).lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")

def tl(x):
    return f"{x:,.0f}".replace(",", ".") if isinstance(x, (int, float)) else "—"

def kayitlar():
    d = json.load(open("veri/ispark.json", encoding="utf-8"))
    for k in d:
        k["slug"] = slug(k["ilce"])
        k["ad_tr"] = k["ad"].strip()
    return d

def ilce_grupla(d):
    g = {}
    for k in d: g.setdefault(k["slug"], {"ad": tr_baslik(k["ilce"]), "kayit": []})["kayit"].append(k)
    for v in g.values():
        v["kayit"].sort(key=lambda x: -(x["kapasite"] or 0))
        f = [x["ilk_saat_tl"] for x in v["kayit"] if x["ilk_saat_tl"]]
        f.sort()
        v["medyan"] = f[len(f)//2] if f else None
        v["kapasite"] = sum(x["kapasite"] or 0 for x in v["kayit"])
    return dict(sorted(g.items(), key=lambda kv: -len(kv[1]["kayit"])))

def kart(k):
    tarife = "".join(
        f'<li><span>{html.escape(t["aralik"])}</span><b>{tl(t["tl"])} ₺</b></li>'
        for t in k["tarife"][:6])
    return f'''<article class="otopark" data-id="{k['id']}" data-lat="{k['lat']}" data-lng="{k['lng']}"
 data-ad="{html.escape(k['ad_tr'], quote=True)}" data-ilce="{html.escape(tr_baslik(k['ilce']), quote=True)}">
 <header>
  <h3>{html.escape(k['ad_tr'])}</h3>
  <p class="adres">{html.escape(tr_baslik(k['adres'] or ''))}</p>
 </header>
 <dl class="ozet">
  <div><dt>Kapasite</dt><dd>{k['kapasite'] or '—'}</dd></div>
  <div><dt>Boş</dt><dd class="bos" data-bos>{k['bos'] if k['bos'] is not None else '—'}</dd></div>
  <div><dt>İlk saat</dt><dd>{tl(k['ilk_saat_tl'])} ₺</dd></div>
  <div><dt>Ücretsiz</dt><dd>{k['ucretsiz_dk'] or 0} dk</dd></div>
 </dl>
 <p class="dolu-cubuk" hidden><i></i></p>
 <p class="saat">{html.escape(k['saat'] or '')} · {html.escape(tr_baslik(k['tip'] or ''))}</p>
 <details><summary>Tam tarife{f" · aylık {tl(k['aylik_tl'])} ₺" if k['aylik_tl'] else ""}</summary>
  <ul class="tarife">{tarife}</ul></details>
 <div class="git">
  <a href="https://www.google.com/maps/dir/?api=1&destination={k['lat']},{k['lng']}" target="_blank" rel="noopener">Google Maps</a>
  <a href="https://yandex.com.tr/harita/?rtext=~{k['lat']},{k['lng']}&rtt=auto" target="_blank" rel="noopener">Yandex</a>
 </div>
</article>'''

SIMGE_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" '
             'aria-hidden="true">')

# Alt sekme cubugu. Tek yerde durur: her sayfa ayni isareti kullansin.
SEKMELER = [
    ("ana", "/", "Ana",
     '<path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/>'),
    ("harita", "/harita/", "Harita",
     '<path d="M9 3 3 5.5v15L9 18l6 3 6-2.5v-15L15 6 9 3z"/><path d="M9 3v15"/>'
     '<path d="M15 6v15"/>'),
    # Etiket ikonu, para isareti DEGIL: "$" ucretsiz sekmesinde tersini
    # cagristiriyordu (ekran goruntusunde olculdu).
    ("bedava", "/ucretsiz-otopark/", "Ücretsiz",
     '<path d="M3.5 12.4V4.5a1 1 0 0 1 1-1h7.9a1 1 0 0 1 .71.29l7.1 7.1a1 1 0 0 1 '
     '0 1.42l-7.9 7.9a1 1 0 0 1-1.42 0l-7.1-7.1a1 1 0 0 1-.29-.71z"/>'
     '<circle cx="7.75" cy="7.75" r="1.15"/>'),
    ("hesap", "/favoriler/", "Favoriler",
     '<path d="M12 3.5l2.6 5.3 5.9.85-4.25 4.15 1 5.85L12 16.9l-5.25 2.75 '
     '1-5.85L3.5 9.65l5.9-.85L12 3.5z"/>'),
]

def alt_sekme(aktif):
    """Mobil alt sekme cubugu. Yollar MUTLAK: Vercel cleanUrls sayfayi bir
    dizin asagida servis ettigi icin goreli yol kayiyor (olculdu: /gizlilik/
    altinda menu oluyordu)."""
    p = []
    for k, yol, ad, d in SEKMELER:
        simdiki = ' aria-current="page"' if k == aktif else ""
        p.append(f'<a href="{yol}"{simdiki}>{SIMGE_SVG}{d}</svg><span>{ad}</span></a>')
    return '<nav class="alt-sekme" aria-label="Alt gezinme">' + "".join(p) + "</nav>"

def sayfa(baslik, aciklama, govde, kok="", canonical="", kaynak_html=None, js=True,
          ek_head="", ek_js="", sekme=""):
    simdi = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M")
    js_etiket = f'<script src="{kok}uygulama.js" defer></script>' if js else ""
    if kaynak_html is None:
        kaynak_html = (
            '<p>Veri: <a href="https://data.ibb.gov.tr/" target="_blank" rel="noopener">İBB Açık Veri Portalı</a> — '
            'İSPARK otopark servisi, lisans <a href="https://creativecommons.org/licenses/by/4.0/deed.tr" '
            'target="_blank" rel="noopener">CC BY 4.0</a>.</p>'
            '<p><strong>Bağımsız uygulamadır.</strong> İstanbul Büyükşehir Belediyesi, İSPARK A.Ş. veya İSTMOP ile '
            "resmî bağlantısı yoktur. Doluluk verisi İBB'nin güncelleme aralığına bağlıdır; "
            'aksama olursa birkaç dakika geride kalabilir.</p>')
    return f'''<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(baslik)}</title>
<meta name="description" content="{html.escape(aciklama)}">
{f'<link rel="canonical" href="{canonical}">' if canonical else ''}
<meta property="og:title" content="{html.escape(baslik)}">
<meta property="og:description" content="{html.escape(aciklama)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://nereyeparkedicem.vercel.app/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="tr_TR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b3d2e">
<link rel="icon" href="/simge.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/simge-180.png">
<link rel="manifest" href="/manifest.json">
<link rel="stylesheet" href="{kok}stil.css">
{ek_head}
</head><body>
<!-- Vercel Web Analytics: ayni kokenden servis edilir, CSP 'self' yeterli.
     Cerez yok; engellenirse sayfa aynen calisir. -->
<script defer src="/_vercel/insights/script.js"></script>
<a class="atla" href="#icerik">İçeriğe atla</a>
<header class="ust">
 <div class="ust-ic">
  <a class="marka" href="/">{SIMGE_SVG}<path d="M12 21s7-5.7 7-11a7 7 0 1 0-14 0c0 5.3 7 11 7 11z"/><path d="M10 14V8h2.4a2.3 2.3 0 0 1 0 4.6H10"/></svg>nereye<b>parkedicem</b></a>
  <nav aria-label="Ana">
   <a href="/harita/"{' aria-current="page"' if sekme == "harita" else ""}>Harita</a>
   <a href="/il/">81 il</a>
   <a href="/ucretsiz-otopark/"{' aria-current="page"' if sekme == "bedava" else ""}>Ücretsiz</a>
   <a href="/fiyat-endeksi/">Fiyat</a>
  </nav>
  <a class="hesap-dug" data-hesap href="/giris/"><span>Giriş</span></a>
 </div>
</header>
<main id="icerik">{govde}</main>
{alt_sekme(sekme)}
<footer class="alt">
 {kaynak_html}
 <p><a href="{kok}gizlilik/">Gizlilik ve KVKK</a></p>
 <p class="uretim">Sayfa üretimi: {simdi}</p>
</footer>
<script src="/sw-kur.js" defer></script>
<script src="/oturum.js" defer></script>
{js_etiket}{ek_js}
</body></html>'''

def sss_schema(ilce, n, medyan):
    sorular = [
        (f"{ilce}'da kaç İSPARK otoparkı var?",
         f"İBB Açık Veri Portalı'na göre {ilce} ilçesinde {n} İSPARK otoparkı kayıtlı."),
        (f"{ilce}'da otopark ne kadar?",
         f"İlk saat ücretinin medyanı {tl(medyan)} TL. Her otoparkın tam tarifesi sayfada listelidir." if medyan
         else "Tarife bilgisi otopark kartlarında listelidir."),
        ("Doluluk bilgisi canlı mı?",
         "Evet. Boş kapasite sayfa açıldığında İBB Açık Veri Portalı'ndan doğrudan çekilir."),
    ]
    d = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": s, "acceptedAnswer": {"@type": "Answer", "text": c}}
        for s, c in sorular]}
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'

def olcum_zamani(d):
    """ISPARK kayitlarindaki en yeni guncelleme damgasi. Bos yer sayilari
    HTML'e DERLEME ANINDA gomuluyor; tarih yazilmazsa kullanici onlari canli
    sanar - denetimde 2 gun eski olduklari olculdu."""
    en = None
    for k in d:
        g = k.get("guncelleme")
        if not g: continue
        for bicim in ("%d.%m.%Y %H:%M:%S", "%d.%m.%Y %H:%M"):
            try:
                t = datetime.strptime(g[:len("13.09.2026 12:20:17")
                                        if bicim.endswith("%S") else 16], bicim)
                break
            except ValueError:
                t = None
        if t and (en is None or t > en): en = t
    if en is None: return "bilinmiyor", ""
    return en.strftime("%d.%m.%Y %H:%M"), en.strftime("%Y-%m-%dT%H:%M:00+03:00")

def ana_schema(il_s, il_n):
    """Denetimde olculdu: ana sayfada hic ld+json yoktu. WebSite + Organization
    + SearchAction; arama hedefi harita sayfasi (il sorgusu ?il= ile)."""
    d = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": "nereyeparkedicem",
         "url": f"{URL}/", "inLanguage": "tr-TR",
         "description": f"{il_s} ilde {il_n} otopark haritada.",
         "potentialAction": {"@type": "SearchAction",
                             "target": {"@type": "EntryPoint",
                                        "urlTemplate": f"{URL}/harita/?q={{search_term_string}}"},
                             "query-input": "required name=search_term_string"}},
        {"@context": "https://schema.org", "@type": "Organization",
         "name": "nereyeparkedicem", "url": f"{URL}/", "logo": f"{URL}/simge-512.png"},
    ]
    return "".join(f'<script type="application/ld+json">'
                   f'{json.dumps(x, ensure_ascii=False)}</script>' for x in d)

def uret():
    d = kayitlar(); g = ilce_grupla(d)
    os.makedirs(CIKTI, exist_ok=True)
    import sehir                                   # dongusel import: fonksiyon icinde
    sg = sehir.uret_hepsi()
    izd = sehir.yukle(sehir.SEHIR["izmir"]["dosya"])
    andd = sehir.yukle(sehir.SEHIR["ankara"]["dosya"])
    iz_n, iz_i = len(izd), len(sg["izmir"])
    iz_t = sum(1 for k in izd if k["tarife"])
    an_n, an_i = len(andd), len(sg["ankara"])
    olcum, olcum_iso = olcum_zamani(d)
    toplam_kap = sum(k["kapasite"] or 0 for k in d)
    fiyat = sorted(k["ilk_saat_tl"] for k in d if k["ilk_saat_tl"])
    medyan = fiyat[len(fiyat)//2]

    ilce_kart = "".join(
        f'<a class="ilce" href="ilce/{s}/"><b>{v["ad"]}</b>'
        f'<span>{len(v["kayit"])} otopark · {v["kapasite"]:,} yer</span>'.replace(",", ".") +
        f'<span class="fiyat">ilk saat medyan {tl(v["medyan"])} ₺</span></a>'
        for s, v in g.items())

    o = iller()
    il_n, il_s = o["toplam"], len(o["iller"])
    uc_n = sum(x.get("uc", 0) for x in o["iller"])
    # harita rozetleri: ana sayfada ilk 12, tamami /il/ dizininde
    il_kart = "".join(
        f'<a class="ilce" href="il/{slug(x["ad"])}/"><b>{x["ad"]}</b>'
        f'<span>{tl(x["n"])} otopark</span>'
        f'<span class="fiyat">{tl(x["uc"])} ücretsiz</span></a>'
        for x in o["iller"][:12])

    govde = f'''<section class="kahraman">
 <p><span class="rozet canli">Canlı doluluk</span></p>
 <h1>En yakın otoparkı <em>saniyede</em> bul</h1>
 <p class="alt-baslik">{il_s} ilde {tl(il_n)} otopark haritada. İstanbul&#8217;da canlı doluluk
 ve tam tarife, İzmir&#8217;de tarife. Uygulama indirmene gerek yok.</p>
 <div class="rakamlar">
  <div><b>{il_s}</b><span>il</span></div>
  <div><b>{tl(il_n)}</b><span>otopark</span></div>
  <div><b>{tl(uc_n)}</b><span>ücretsiz</span></div>
  <div><b data-doluluk>—</b><span>İstanbul doluluk</span></div>
 </div>
 <div class="dugmeler">
  <button id="yakin" class="birincil">En yakın otoparkları göster</button>
  <a class="ikincil" href="harita/">Haritayı aç</a>
 </div>
 <p id="konum-durum" class="durum" role="status"></p>
</section>
<section id="sonuc" hidden><h2>Sana en yakın otoparklar</h2><div class="liste" id="yakin-liste"></div></section>
<section id="turkiye"><h2>Türkiye haritası — {il_s} il</h2>
 <p class="alt-baslik">Otoparkların tamamı tek haritada. İl balonuna dokun, yakınlaş.</p>
 <div class="dugmeler">
  <a class="birincil" href="harita/">Haritayı aç</a>
  <a class="ikincil" href="ucretsiz-otopark/">Ücretsiz otoparklar ({tl(uc_n)})</a>
  <a class="ikincil" href="favoriler/">Favorilerim</a>
 </div>
 <div class="ilce-izgara">{il_kart}</div>
 <p><a href="il/">{il_s} ilin tamamı →</a></p>
</section>
<section id="sehirler"><h2>Tarife yayınlanan şehirler</h2>
 <div class="ilce-izgara">
  <a class="ilce" href="index.html#ilceler"><b>İstanbul</b><span>{len(d)} İSPARK · {len(g)} ilçe</span>
   <span class="fiyat">canlı doluluk + tam tarife</span></a>
  <a class="ilce" href="izmir/"><b>İzmir</b><span>{iz_n} İZELMAN otoparkı · {iz_i} ilçe</span>
   <span class="fiyat">{iz_t} otoparkın tarifesi</span></a>
  <a class="ilce" href="ankara/"><b>Ankara</b><span>{an_n} ANPARK otoparkı · {an_i} ilçe</span>
   <span class="fiyat">tarife yayınlanmıyor</span></a>
 </div></section>
<section id="ilceler"><h2>İstanbul&#8217;da ilçeye göre</h2>
 <p class="alt-baslik">{len(d)} İSPARK noktası · {tl(toplam_kap)} yer · ilk saat medyan {tl(medyan)} ₺
 · doluluk İBB Açık Veri Portalı&#8217;ndan canlı</p>
 <div class="ilce-izgara">{ilce_kart}</div></section>'''

    open(f"{CIKTI}/index.html", "w", encoding="utf-8").write(sayfa(
        "Türkiye Otopark Haritası — 81 İlde En Yakın Otopark",
        f"{il_s} ilde {tl(il_n)} otopark, {tl(uc_n)} tanesi ücretsiz. İstanbul'da {len(d)} İSPARK "
        f"otoparkının canlı doluluğu ve tam tarifesi. En yakınını bul, yol tarifi al.",
        govde, canonical=f"{URL}/", ek_head=ana_schema(il_s, il_n), sekme="ana"))

    for s, v in g.items():
        os.makedirs(f"{CIKTI}/ilce/{s}", exist_ok=True)
        kartlar = "".join(kart(k) for k in v["kayit"])
        gv = f'''<nav class="iz"><a href="../../index.html">Ana sayfa</a> › <span>{v["ad"]}</span></nav>
<section class="kahraman dar">
 <h1>{v["ad"]} otoparkları — canlı doluluk ve fiyat</h1>
 <p class="alt-baslik">{len(v["kayit"])} İSPARK noktası · {v["kapasite"]:,} yer ·
 ilk saat medyan {tl(v["medyan"])} ₺</p>
 <p class="durum" data-ilce-doluluk>Doluluk yükleniyor…</p>
</section>
<section class="liste-bolum">
 <h2>{v["ad"]} otopark listesi</h2>
 <p class="alt-baslik">Boş yer sayısı sayfa açılınca canlı güncellenir;
 aşağıdaki değerler <time datetime="{olcum_iso}">{olcum}</time> ölçümüdür.</p>
 <div class="liste">{kartlar}</div>
</section>
{sss_schema(v["ad"], len(v["kayit"]), v["medyan"])}'''.replace(f'{v["kapasite"]:,}', f'{v["kapasite"]:,}'.replace(",", "."))
        open(f"{CIKTI}/ilce/{s}/index.html", "w", encoding="utf-8").write(sayfa(
            f"{v['ad']} Otopark — Canlı Doluluk ve Fiyat",
            f"{v['ad']} ilçesindeki {len(v['kayit'])} İSPARK otoparkının canlı doluluk oranı, "
            f"tam tarifesi ve yol tarifi. İlk saat medyan {tl(v['medyan'])} TL.",
            gv, kok="../../", canonical=f"{URL}/ilce/{s}/"))

    import ikon_uret; ikon_uret.yaz()
    # auth.json ONCE: yaz_gizlilik() metni hesap ozelliginin acik olup
    # olmamasina gore degistirdigi icin dosyanin var olmasi gerekiyor.
    yaz_auth_ayar()
    yaz_gizlilik(); yaz_404(); yaz_cevrimdisi(); yaz_endeks(d, g)
    yaz_giris(); yaz_favoriler()
    harita_var = os.path.exists(f"{CIKTI}/veri/iller.json")
    il_sluglari = {}
    if harita_var:
        import harita_sayfa; harita_sayfa.yaz()
        import il_sayfa; il_sluglari = il_sayfa.yaz()
    else:
        print("harita atlandi: site/veri/iller.json yok (once koord_cek.py + harita_veri.py)")

    # sitemap + robots
    url = "https://nereyeparkedicem.vercel.app"
    sm = "".join(f"<url><loc>{url}/ilce/{s}/</loc><changefreq>daily</changefreq></url>" for s in g)
    for kod, gg in sg.items():
        sm += f"<url><loc>{url}/{kod}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>"
        sm += "".join(f"<url><loc>{url}/{kod}/ilce/{x}/</loc><changefreq>weekly</changefreq></url>" for x in gg)
    if harita_var:
        sm += f"<url><loc>{url}/harita/</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>"
        sm += f"<url><loc>{url}/il/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>"
        sm += f"<url><loc>{url}/ucretsiz-otopark/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>"
        sm += "".join(f"<url><loc>{url}/il/{sl}/</loc><changefreq>weekly</changefreq>"
                      f"<priority>0.7</priority></url>" for sl in il_sluglari.values())
    open(f"{CIKTI}/sitemap.xml","w",encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{url}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>'
        f'{sm}<url><loc>{url}/fiyat-endeksi/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>'
        f'<url><loc>{url}/gizlilik/</loc><changefreq>yearly</changefreq><priority>0.1</priority></url></urlset>')
    open(f"{CIKTI}/robots.txt","w",encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {url}/sitemap.xml\n")
    json.dump([{k: r[k] for k in ("id","ad","lat","lng","ilce","kapasite","ilk_saat_tl","saat","tip")} for r in d],
              open(f"{CIKTI}/otoparklar.json","w",encoding="utf-8"), ensure_ascii=False)
    ss = sum(len(x) for x in sg.values())
    print(f"uretildi: {CIKTI}/ · 1 ana sayfa + {len(g)} ilce + {len(sg)} sehir + "
          f"{ss} sehir-ilce + {len(il_sluglari)} il sayfasi + sitemap")


GIZLILIK_BAS = """<section class="kahraman dar">
<h1>Gizlilik ve KVKK</h1>
<p class="alt-baslik">{ozet}</p>
</section>
<section class="metin">
<h2>Hangi veriyi topluyoruz</h2>
{giris_blok}
<p>Site statik dosyalardan oluşur; sayfaları üreten bir sunucu kodumuz ve
otoparkları tutan bir veritabanımız yoktur.</p>
<p><strong>Vercel Web Analytics</strong>: kaç kez hangi sayfanın açıldığını
sayar. <strong>Çerez kullanmaz, parmak izi çıkarmaz, ziyaretçiyi sayfalar arasında
takip etmez;</strong> IP adresi kimliğe dönüştürülmeden anonim bir sayfa görüntüleme
sayısına indirgenir. Betik sitemizin kendi alan adından servis edilir
(<code>/_vercel/insights/</code>), ölçüm de oraya gider — reklam ağına veri gitmez.
Tarayıcınızın izleme engelleyicisi bu betiği kapatırsa site aynen çalışır.</p>

<h2>Favoriler</h2>
<p>Bir otopark kartındaki yıldıza dokunduğunuzda o otoparkın adı, ilçesi ve koordinatı
<strong>tarayıcınızın kendi deposuna</strong> (<code>localStorage</code>) yazılır.
Giriş yapmadıysanız bu liste <strong>cihazınızdan hiç çıkmaz</strong>; tarayıcı verisini
temizlediğinizde silinir.</p>
{favori_blok}
<h2>Konum bilgisi</h2>
<p>&quot;En yakın otoparkları göster&quot; düğmesine bastığınızda tarayıcınız konum izni ister.
Verilen konum <strong>yalnızca cihazınızın içinde</strong> kullanılır: mesafe hesabı tarayıcıda
yapılır, sonuç ekranda gösterilir. Konum <strong>bize gönderilmez, kaydedilmez.</strong>
Sayfayı kapattığınızda kaybolur. İzin vermek zorunda değilsiniz; ilçe listesinden de
gezebilirsiniz.</p>
<p><strong>Tek istisna, sizin başlattığınız yol tarifi:</strong> haritada &quot;Yol
tarifi&quot; düğmesine bastığınızda başlangıç ve varış <em>koordinatları</em> rotayı
hesaplayan OSRM sunucusuna gider — başka türlü rota çizilemez. Düğmeye basmazsanız bu
istek hiç olmaz, ve giderken kimliğinizle ilgili hiçbir şey taşınmaz.</p>

<h2>Dışarıya giden istekler</h2>
<p>Dördü de kimliğinizi taşımaz; ikisi yalnız siz isteyince olur:</p>
<ul>
<li><strong>Canlı doluluk</strong> için tarayıcınız doğrudan İstanbul Büyükşehir
Belediyesi Açık Veri Portalı'na (<code>api.ibb.gov.tr</code>) istek atar; yalnızca
otopark listesi çekilir.</li>
<li><strong>Harita fayansları</strong> OpenStreetMap sunucusundan
(<code>tile.openstreetmap.org</code>) iner. Bu istek hangi bölgeye baktığınızı o
sunucuya gösterir — OSM'nin kendi gizlilik politikası geçerlidir. Harita sayfasını
açmazsanız bu istek hiç olmaz.</li>
<li><strong>Adres arama</strong> için yazdığınız adres metni OpenStreetMap'in
Nominatim servisine (<code>nominatim.openstreetmap.org</code>) gider ve koordinata
çevrilir. Yalnız <strong>siz &quot;Ara&quot; düğmesine bastığınızda</strong> gönderilir;
yazarken harf harf sorgu atılmaz.</li>
<li><strong>Yol tarifi</strong> için başlangıç ve varış koordinatı OSRM demo
sunucusuna (<code>router.project-osrm.org</code>) gider. Yalnız &quot;Yol tarifi&quot;
düğmesine bastığınızda olur. İkisi de OpenStreetMap ekosisteminde çalışır; kendi
gizlilik politikaları geçerlidir.</li>
{supabase_madde}</ul>
<p>İçerik Güvenliği Politikamız (CSP) bunların dışında hiçbir dış adrese bağlantı
kurulmasına izin vermez. Otopark koordinatları ve tarifeler kendi alan adımızdan iner.</p>

<h2>Barındırma kayıtları</h2>
<p>Site Vercel üzerinde barındırılır. Her web sunucusu gibi Vercel de teknik erişim kaydı
(IP, tarayıcı bilgisi, istenen adres) tutabilir. Bu kayıtlar barındırma sağlayıcısına aittir
ve tarafımızca okunmaz veya işlenmez.</p>

<h2>KVKK</h2>
{kvkk_blok}

<h2>Verinin kaynağı ve doğruluğu</h2>
<p>Otopark, doluluk ve tarife verisi İBB Açık Veri Portalı'ndan CC BY 4.0 lisansıyla gelir.
Güncellik İBB'nin yenileme aralığına bağlıdır; aksama olursa veri birkaç dakika geride
kalabilir. <strong>Bu site bağımsızdır</strong>; İBB, İSPARK A.Ş. veya İSTMOP ile resmî
bağlantısı yoktur. Gösterilen fiyatlar bilgilendirme amaçlıdır, bağlayıcı değildir.</p>
</section>"""

DORTYUZDORT = """<section class="kahraman dar">
<h1>Bu sayfa yok</h1>
<p class="alt-baslik">Aradığın ilçe sayfası taşınmış veya hiç olmamış olabilir.</p>
<p><a class="git-geri" href="/">Ana sayfaya dön ve ilçe seç</a></p>
</section>"""

# kok="/" ZORUNLU: Vercel cleanUrls gizlilik.html'i /gizlilik/ altinda servis
# ediyor, 404.html'i de her derinlikte. Goreli yol bir dizin kayiyor ve
# OLCULDU: /gizlilik/stil.css 404, /gizlilik/harita/ 404 - sayfa stilsiz,
# menusu olu kaliyordu.
def auth_acik():
    """site/veri/auth.json doldurulmus mu. Gizlilik metni buna gore degisir:
    hesap ozelligi KAPALIYKEN 'e-postanizi isliyoruz' demek de yanlis olur,
    ACIKKEN 'hicbir kisisel veri yok' demek de. Iki hâli de dogru yazilir."""
    try:
        a = json.load(open(f"{CIKTI}/veri/auth.json", encoding="utf-8"))
        return bool(a.get("url")) and "YAPILANDIRILMADI" not in f"{a.get('url')}{a.get('anonKey')}"
    except (OSError, ValueError, AttributeError):
        return False

def yaz_gizlilik():
    acik = auth_acik()
    if acik:
        ozet = ("Kısa versiyon: konumunuz bize hiç gelmiyor. Hesap açmak isteğe bağlı; "
                "açarsanız yalnız e-posta adresiniz ve favori listeniz saklanır.")
        giris_blok = (
            "<p><strong>Hesap açmazsanız kişisel veri toplamıyoruz.</strong> "
            "Sitenin tamamı — harita, arama, favoriler, yol tarifi — giriş yapmadan "
            "çalışır.</p>"
            "<p>Giriş yapmayı seçerseniz işlenen veri şudur: <strong>e-posta adresiniz</strong> "
            "(Google ile girdiyseniz Google'ın paylaştığı e-posta ve hesap kimliği) ve "
            "<strong>favori otopark listeniz</strong>. Parola tutmuyoruz — giriş e-posta "
            "bağlantısı veya Google ile yapılır.</p>")
        favori_blok = (
            "<p>Giriş yaparsanız aynı liste hesabınıza bağlı olarak <strong>Supabase</strong> "
            "üzerinde de tutulur ki diğer cihazlarınızda görünsün. Veritabanı satır düzeyi "
            "güvenlik (RLS) ile korunur: <strong>bir kullanıcı yalnız kendi satırını "
            "okuyabilir ve yazabilir.</strong> Favori listesi kimseyle paylaşılmaz, "
            "reklam amacıyla kullanılmaz.</p>")
        supabase_madde = (
            "<li><strong>Hesap ve favori eşitlemesi</strong> için giriş yaptıysanız "
            "tarayıcınız <code>*.supabase.co</code> adresine istek atar. Bu istek "
            "yalnız hesap oturumunuzu ve favori listenizi taşır; konumunuzu taşımaz. "
            "Giriş yapmazsanız bu istek hiç olmaz.</li>")
        kvkk_blok = (
            "<p>6698 sayılı Kanun anlamında veri sorumlusu bu sitenin işletmecisidir. "
            "<strong>Hukuki sebep:</strong> talebiniz üzerine hesap hizmetinin sunulması "
            "(açık rızanız ve sözleşmenin ifası). <strong>Amaç:</strong> yalnızca favori "
            "listenizi cihazlarınız arasında eşitlemek. <strong>Saklama süresi:</strong> "
            "hesabınız açık kaldığı sürece.</p>"
            "<p><strong>Yurt dışına aktarım:</strong> Supabase ve Vercel yurt dışında "
            "barındırma yapar; hesap açtığınızda e-postanız ve favori listeniz bu "
            "sunucularda saklanır. Bunu kabul etmek istemiyorsanız hesap açmayın — "
            "site giriş yapmadan tam olarak çalışır.</p>"
            "<p><strong>Haklarınız</strong> (m.11): verilerinizin silinmesini, düzeltilmesini "
            "veya bir kopyasını isteyebilirsiniz. Talebinizi GitHub deposundan issue açarak "
            "iletebilirsiniz; hesap silme talebinde e-posta adresiniz ve favori kaydınız "
            "tamamen kaldırılır.</p>")
    else:
        ozet = ("Kısa versiyon: sunucumuz yok, hesabınız yok, konumunuz bize gelmiyor.")
        giris_blok = (
            "<p><strong>Kişisel veri toplamıyoruz.</strong> Hesap özelliği bu sürümde "
            "<strong>kapalıdır</strong>: giriş sayfası açılsa da kayıt oluşturulamaz, "
            "hiçbir e-posta adresi tarafımıza ulaşmaz.</p>")
        favori_blok = (
            "<p>Hesap özelliği kapalı olduğu için favori listeniz <strong>hiçbir sunucuya "
            "gönderilmez</strong>; yalnız bu cihazda kalır.</p>")
        supabase_madde = ""
        kvkk_blok = (
            "<p>6698 sayılı Kişisel Verilerin Korunması Kanunu anlamında tarafımızca "
            "<strong>işlenen kişisel veri yoktur</strong>; bu nedenle veri sorumlusu "
            "sıfatıyla tutulan bir kayıt ortamı bulunmamaktadır. Yine de sorunuz olursa "
            "GitHub deposundan issue açabilirsiniz.</p>")
    govde = GIZLILIK_BAS.format(ozet=ozet, giris_blok=giris_blok, favori_blok=favori_blok,
                                supabase_madde=supabase_madde, kvkk_blok=kvkk_blok)
    open(f"{CIKTI}/gizlilik.html", "w", encoding="utf-8").write(sayfa(
        "Gizlilik ve KVKK | nereyeparkedicem",
        ("Konumunuz cihazınızdan çıkmıyor. Hesap isteğe bağlı; açarsanız yalnız "
         "e-posta ve favori listesi saklanır." if acik else
         "Sunucumuz yok, hesabınız yok, konumunuz cihazınızdan çıkmıyor. "
         "Toplanan kişisel veri bulunmuyor."),
        govde, kok="/", canonical=f"{URL}/gizlilik/"))

GIRIS = """<section class="giris-sar">
<div class="giris">
 <h1>Giriş yap</h1>
 <p class="alt-baslik">Favori otoparkların bütün cihazlarında görünsün.
 Parola yok — e-postana gelen bağlantıya dokunman yeterli.</p>

 <form id="giris-form" novalidate>
  <label class="etiket" for="eposta">E-posta adresin</label>
  <input class="alan" type="email" id="eposta" name="eposta" required
         autocomplete="email" inputmode="email" placeholder="ornek@eposta.com">
  <button class="birincil" id="giris-dug" type="submit">Giriş bağlantısı gönder</button>
 </form>

 <div class="ayirac">veya</div>
 <button class="ikincil" id="google-giris" type="button">Google ile devam et</button>

 <p class="durum" id="giris-durum" role="status"></p>
 <p class="giris-not">Hesap açmak <strong>zorunlu değil</strong>. Favorilerin giriş
 yapmadan da bu cihazda saklanır; hesap yalnızca cihazlar arasında eşitleme içindir.
 Ne topladığımız <a href="/gizlilik/">Gizlilik ve KVKK</a> sayfasında yazılı.</p>
</div>
</section>"""

FAVORILER = """<section class="kahraman dar">
<h1>Favori otoparkların</h1>
<p class="durum" id="hesap-durum" role="status"></p>
<p class="dugmeler"><button class="ikincil" id="cikis" type="button" hidden>Çıkış yap</button></p>
</section>
<section class="liste-bolum">
 <p class="alt-baslik" id="favori-sayi"></p>
 <div class="liste" id="favori-liste"></div>
 <div class="bos-durum" id="favori-bos" hidden>
  <svg viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round"
   stroke-linejoin="round" d="M12 3.5l2.6 5.3 5.9.85-4.25 4.15 1 5.85L12
   16.9l-5.25 2.75 1-5.85L3.5 9.65l5.9-.85L12 3.5z"/></svg>
  <p>Henüz favori yok. Herhangi bir otopark kartındaki yıldıza dokun,
  burada birikirler.</p>
  <a class="birincil" href="/harita/">Haritayı aç</a>
 </div>
</section>"""

def yaz_giris():
    os.makedirs(f"{CIKTI}/giris", exist_ok=True)
    open(f"{CIKTI}/giris/index.html", "w", encoding="utf-8").write(sayfa(
        "Giriş yap — nereyeparkedicem",
        "Favori otoparklarını bütün cihazlarında görmek için giriş yap. "
        "Parola yok, e-posta bağlantısı yeterli.", GIRIS, kok="/",
        canonical=f"{URL}/giris/", js=False, sekme="hesap",
        ek_head='<meta name="robots" content="noindex">',
        ek_js='<script src="/hesap.js" defer></script>'))

def yaz_favoriler():
    os.makedirs(f"{CIKTI}/favoriler", exist_ok=True)
    open(f"{CIKTI}/favoriler/index.html", "w", encoding="utf-8").write(sayfa(
        "Favori otoparkların — nereyeparkedicem",
        "Yıldızladığın otoparklar. Giriş yaparsan bütün cihazlarında görünür.",
        FAVORILER, kok="/", canonical=f"{URL}/favoriler/", js=False, sekme="hesap",
        ek_head='<meta name="robots" content="noindex">',
        ek_js='<script src="/hesap.js" defer></script>'))

def yaz_auth_ayar():
    """Supabase yapilandirmasi. anon anahtar TASARIM GEREGI acik metindir
    (istemcide calisir, korumayi RLS saglar) - o yuzden depoda durabilir.
    Dosya YOKSA ustune yazma: kullanicinin girdigi degerleri silmeyelim."""
    yol = f"{CIKTI}/veri/auth.json"
    os.makedirs(f"{CIKTI}/veri", exist_ok=True)
    if os.path.exists(yol):
        return
    json.dump({"url": "YAPILANDIRILMADI", "anonKey": "YAPILANDIRILMADI"},
              open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

CEVRIMDISI = """<section class="kahraman dar">
<h1>Bağlantı yok</h1>
<p class="alt-baslik">İnternete erişilemiyor. Daha önce açtığın sayfalar
çalışmaya devam eder; yeni veri gelemez.</p>
</section>
<section class="metin">
<h2>Şu an ne çalışıyor</h2>
<ul>
<li><strong>Daha önce açtığın sayfalar</strong> cihazda saklı, açılır.</li>
<li><strong>Yol tarifi bağlantıları</strong> çalışır — harita uygulaması kendi
verisini kullanır.</li>
<li><strong>Adres arama ve uygulama içi yol tarifi çalışmaz:</strong> ikisi de
OpenStreetMap sunucularına bağlanmak zorunda. Kayıtlı favorilerin ve daha önce
açtığın il sayfaları yerinde duruyor.</li>
<li><strong>Canlı doluluk çalışmaz:</strong> İBB Açık Veri Portalı'na bağlanmak
gerekiyor. Ekranda gördüğün boş yer sayıları son ölçümdür, şu anki değil.</li>
<li><strong>Harita fayansları</strong> yalnız daha önce görüntülediğin bölgelerde
görünür.</li>
</ul>
<h2>Ne yapmalı</h2>
<p>Bağlantı gelince sayfayı yenile; veriler kendiliğinden tazelenir.</p>
<p><a class="birincil" href="/">Ana sayfaya dön</a></p>
</section>"""

def yaz_cevrimdisi():
    os.makedirs(f"{CIKTI}/cevrimdisi", exist_ok=True)
    open(f"{CIKTI}/cevrimdisi/index.html", "w", encoding="utf-8").write(sayfa(
        "Bağlantı yok — nereyeparkedicem",
        "İnternet bağlantısı olmadığında gösterilen sayfa.", CEVRIMDISI, kok="/",
        ek_head='<meta name="robots" content="noindex">', js=False))

def yaz_404():
    open(f"{CIKTI}/404.html", "w", encoding="utf-8").write(sayfa(
        "Sayfa bulunamadı | nereyeparkedicem",
        "Aradığınız sayfa bulunamadı.", DORTYUZDORT, kok="/",
        ek_head='<meta name="robots" content="noindex">'))


def yaz_endeks(d, g):
    """Ilce bazinda otopark fiyat endeksi. Turkiye'de baska yerde yayinlanmiyor."""
    import statistics as st
    osm_p = ""
    try:
        o = json.load(open("veri/osm_ispark.json", encoding="utf-8"))
        osm_p = (
            f'<p>Bu tarifeler OpenStreetMap’te yok. 150 m yarıçapla yapılan '
            f'eşleştirmede {o["ispark_toplam"]} İSPARK otoparkının '
            f'{o["osm_yok"]}’ü OSM’de hiç kayıtlı değil; '
            f'eşleşen {o["osm_var"]} otoparktan yalnız '
            f'<strong>{o["eslesen_tarifeli"]}’ünde</strong> fiyat etiketi var. '
            f'Bu sayfadaki {len(d)} otoparkın tamamında tarife bulunur.</p>')
    except (OSError, ValueError, KeyError):
        pass
    ilk = sorted(k["ilk_saat_tl"] for k in d if k["ilk_saat_tl"])
    gun = sorted(t["tl"] for k in d for t in k["tarife"] if "Tam" in t["aralik"])
    ay  = sorted(k["aylik_tl"] for k in d if k["aylik_tl"])

    satir = []
    for s_, v in sorted(g.items(), key=lambda kv: -(kv[1]["medyan"] or 0)):
        kk = v["kayit"]
        tg = sorted(t["tl"] for k in kk for t in k["tarife"] if "Tam" in t["aralik"])
        aa = sorted(k["aylik_tl"] for k in kk if k["aylik_tl"])
        satir.append(
            f'<tr><th scope="row"><a href="../ilce/{s_}/">{v["ad"]}</a></th>'
            f'<td>{len(kk)}</td><td>{tl(v["medyan"])}</td>'
            f'<td>{tl(st.median(tg)) if tg else "—"}</td>'
            f'<td>{tl(st.median(aa)) if aa else "—"}</td></tr>')

    en = sorted(g.items(), key=lambda kv: -(kv[1]["medyan"] or 0))
    pahali, ucuz = en[0][1], en[-1][1]
    kat = pahali["medyan"] / ucuz["medyan"] if ucuz["medyan"] else 0

    veri_ld = {"@context": "https://schema.org", "@type": "Dataset",
      "name": "İstanbul İlçe Bazında Otopark Fiyat Endeksi",
      "description": f"{len(d)} İSPARK otoparkının ilçe bazında saatlik, günlük ve aylık tarife medyanları.",
      "license": "https://creativecommons.org/licenses/by/4.0/",
      "isBasedOn": "https://data.ibb.gov.tr/", "temporalCoverage": datetime.now().strftime("%Y-%m-%d"),
      "creator": {"@type": "Organization", "name": "nereyeparkedicem"}}

    gv = f"""<nav class="iz"><a href="../index.html">Ana sayfa</a> › <span>Fiyat endeksi</span></nav>
<section class="kahraman dar">
 <h1>İstanbul otopark fiyat endeksi</h1>
 <p class="alt-baslik">{len(d)} İSPARK otoparkının ilçe bazında tarife medyanı.
 Kaynak İBB Açık Veri Portalı; hesaplama tarafımızca yapıldı.</p>
</section>
<section>
 <div class="rakamlar">
  <div><b>{tl(st.median(ilk))} ₺</b><span>ilk saat medyanı</span></div>
  <div><b>{tl(st.median(gun))} ₺</b><span>tam gün medyanı</span></div>
  <div><b>{tl(st.median(ay))} ₺</b><span>aylık abonelik medyanı</span></div>
  <div><b>{kat:.1f}×</b><span>en pahalı / en ucuz ilçe</span></div>
 </div>
 <p class="alt-baslik">En pahalı <strong>{pahali["ad"]}</strong> ({tl(pahali["medyan"])} ₺) ·
 en ucuz <strong>{ucuz["ad"]}</strong> ({tl(ucuz["medyan"])} ₺) ·
 aralık {tl(ilk[0])}–{tl(ilk[-1])} ₺.</p>
</section>
<section class="tablo-sar">
 <table class="endeks">
  <caption>İlçelere göre tarife medyanları (₺)</caption>
  <thead><tr><th scope="col">İlçe</th><th scope="col">Otopark</th><th scope="col">İlk saat</th>
   <th scope="col">Tam gün</th><th scope="col">Aylık</th></tr></thead>
  <tbody>{"".join(satir)}</tbody>
 </table>
</section>
<section class="metin">
 <h2>Yöntem</h2>
 <p>Her ilçe için o ilçedeki İSPARK otoparklarının tarifelerinin <strong>medyanı</strong>
 alınmıştır — ortalama değil, çünkü tek bir yüksek tarifeli otopark ortalamayı bozar.
 Tam gün sütunu tarifesinde &quot;Tam Gün&quot; kalemi bulunan otoparklardan, aylık sütunu
 abonelik ücreti tanımlı otoparklardan hesaplanır; tanımsızsa hücre boştur.</p>
 <p>Veri İBB Açık Veri Portalı'ndan CC BY 4.0 ile alınır. Sayfa üretildiği anki tarifeyi
 gösterir; İSPARK zam yaptığında sayfa yeniden üretilene kadar eski değer görünür.
 <strong>Bağlayıcı değildir</strong>, bilgilendirme amaçlıdır.</p>
 <p>Yalnız İSPARK otoparkları kapsanır. Özel otoparklar, AVM otoparkları ve sokak üstü
 park bu endekste yoktur.</p>
 {osm_p}
</section>
<script type="application/ld+json">{json.dumps(veri_ld, ensure_ascii=False)}</script>"""

    os.makedirs(f"{CIKTI}/fiyat-endeksi", exist_ok=True)
    open(f"{CIKTI}/fiyat-endeksi/index.html", "w", encoding="utf-8").write(sayfa(
        "İstanbul Otopark Fiyat Endeksi — İlçe İlçe Tarife",
        f"İstanbul'da {len(d)} İSPARK otoparkının ilçe bazında tarife medyanı. "
        f"İlk saat {tl(st.median(ilk))} ₺, tam gün {tl(st.median(gun))} ₺. "
        f"En pahalı {pahali['ad']}, en ucuz {ucuz['ad']} — {kat:.1f} kat fark.",
        gv, kok="../", canonical=f"{URL}/fiyat-endeksi/"))

if __name__ == "__main__": uret()
