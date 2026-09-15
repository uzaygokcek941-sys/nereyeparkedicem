# -*- coding: utf-8 -*-
"""Statik site ureticisi. veri/ispark.json -> site/
Canli doluluk tarayicida IBB API'sinden cekilir (CORS: *), sunucu yok."""
import json, os, re, shutil, html
from datetime import datetime, timezone, timedelta

TR = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
CIKTI = "site"

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
    return f'''<article class="otopark" data-id="{k['id']}" data-lat="{k['lat']}" data-lng="{k['lng']}">
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
 <p class="saat">{html.escape(k['saat'] or '')} · {html.escape(tr_baslik(k['tip'] or ''))}</p>
 <details><summary>Tam tarife{f" · aylık {tl(k['aylik_tl'])} ₺" if k['aylik_tl'] else ""}</summary>
  <ul class="tarife">{tarife}</ul></details>
 <div class="git">
  <a href="https://www.google.com/maps/dir/?api=1&destination={k['lat']},{k['lng']}" target="_blank" rel="noopener">Google Maps</a>
  <a href="https://yandex.com.tr/harita/?rtext=~{k['lat']},{k['lng']}&rtt=auto" target="_blank" rel="noopener">Yandex</a>
 </div>
</article>'''

def sayfa(baslik, aciklama, govde, kok="", canonical="", kaynak_html=None, js=True,
          ek_head="", ek_js=""):
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
<link rel="stylesheet" href="{kok}stil.css">
{ek_head}
</head><body>
<a class="atla" href="#icerik">İçeriğe atla</a>
<header class="ust">
 <a class="marka" href="{kok}index.html">nereye<b>parkedicem</b></a>
 <nav aria-label="Ana"><a href="{kok}harita/">Harita</a><a href="{kok}index.html#ilceler">İlçeler</a><a href="{kok}fiyat-endeksi/">Fiyat</a></nav>
</header>
<main id="icerik">{govde}</main>
<footer class="alt">
 {kaynak_html}
 <p><a href="{kok}gizlilik/">Gizlilik ve KVKK</a></p>
 <p class="uretim">Sayfa üretimi: {simdi}</p>
</footer>
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
    toplam_kap = sum(k["kapasite"] or 0 for k in d)
    fiyat = sorted(k["ilk_saat_tl"] for k in d if k["ilk_saat_tl"])
    medyan = fiyat[len(fiyat)//2]

    ilce_kart = "".join(
        f'<a class="ilce" href="ilce/{s}/"><b>{v["ad"]}</b>'
        f'<span>{len(v["kayit"])} otopark · {v["kapasite"]:,} yer</span>'.replace(",", ".") +
        f'<span class="fiyat">ilk saat medyan {tl(v["medyan"])} ₺</span></a>'
        for s, v in g.items())

    govde = f'''<section class="kahraman">
 <h1>En yakın otoparkı <em>saniyede</em> bul</h1>
 <p class="alt-baslik">İstanbul'da {len(d)} İSPARK noktası, {len(g)} ilçe. Doluluk ve tarife
 İBB Açık Veri Portalı'ndan canlı. Uygulama indirmene gerek yok.</p>
 <div class="rakamlar">
  <div><b>{len(d)}</b><span>otopark</span></div>
  <div><b>{toplam_kap:,}</b><span>toplam yer</span></div>
  <div><b data-doluluk>—</b><span>şehir geneli dolu</span></div>
  <div><b>{tl(medyan)} ₺</b><span>ilk saat medyan</span></div>
 </div>
 <button id="yakin" class="birincil">📍 En yakın otoparkları göster</button>
 <p id="konum-durum" class="durum" role="status"></p>
</section>
<section id="sonuc" hidden><h2>Sana en yakın 10 otopark</h2><div class="liste" id="yakin-liste"></div></section>
<section id="ilceler"><h2>İlçeye göre</h2><div class="ilce-izgara">{ilce_kart}</div></section>
<section id="sehirler"><h2>Diğer şehirler</h2>
 <div class="ilce-izgara">
  <a class="ilce" href="izmir/"><b>İzmir</b><span>{iz_n} İZELMAN otoparkı · {iz_i} ilçe</span>
   <span class="fiyat">{iz_t} otoparkın tarifesi</span></a>
  <a class="ilce" href="ankara/"><b>Ankara</b><span>{an_n} ANPARK otoparkı · {an_i} ilçe</span>
   <span class="fiyat">tarife yayınlanmıyor</span></a>
 </div></section>'''.replace(
        f"{toplam_kap:,}", f"{toplam_kap:,}".replace(",", "."))

    open(f"{CIKTI}/index.html", "w", encoding="utf-8").write(sayfa(
        "İstanbul Otopark — Canlı Doluluk ve Tarife | nereyeparkedicem",
        f"İstanbul'da {len(d)} İSPARK otoparkının canlı doluluk oranı ve tam tarifesi. "
        f"En yakın otoparkı bul, tek dokunuşla yol tarifi al.", govde))

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
<section class="liste">{kartlar}</section>
{sss_schema(v["ad"], len(v["kayit"]), v["medyan"])}'''.replace(f'{v["kapasite"]:,}', f'{v["kapasite"]:,}'.replace(",", "."))
        open(f"{CIKTI}/ilce/{s}/index.html", "w", encoding="utf-8").write(sayfa(
            f"{v['ad']} Otopark — Canlı Doluluk ve Fiyat | nereyeparkedicem",
            f"{v['ad']} ilçesindeki {len(v['kayit'])} İSPARK otoparkının canlı doluluk oranı, "
            f"tam tarifesi ve yol tarifi. İlk saat medyan {tl(v['medyan'])} TL.",
            gv, kok="../../"))

    yaz_gizlilik(); yaz_404(); yaz_endeks(d, g)
    harita_var = os.path.exists(f"{CIKTI}/veri/iller.json")
    if harita_var:
        import harita_sayfa; harita_sayfa.yaz()
    else:
        print("harita atlandi: site/veri/iller.json yok (once koord_tek.py + harita_veri.py)")

    # sitemap + robots
    url = "https://nereyeparkedicem.vercel.app"
    sm = "".join(f"<url><loc>{url}/ilce/{s}/</loc><changefreq>daily</changefreq></url>" for s in g)
    for kod, gg in sg.items():
        sm += f"<url><loc>{url}/{kod}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>"
        sm += "".join(f"<url><loc>{url}/{kod}/ilce/{x}/</loc><changefreq>weekly</changefreq></url>" for x in gg)
    if harita_var:
        sm += f"<url><loc>{url}/harita/</loc><changefreq>weekly</changefreq><priority>0.9</priority></url>"
    open(f"{CIKTI}/sitemap.xml","w",encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'<url><loc>{url}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>'
        f'{sm}<url><loc>{url}/fiyat-endeksi/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>'
        f'<url><loc>{url}/gizlilik/</loc><changefreq>yearly</changefreq><priority>0.1</priority></url></urlset>')
    open(f"{CIKTI}/robots.txt","w",encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {url}/sitemap.xml\n")
    json.dump([{k: r[k] for k in ("id","ad","lat","lng","ilce","kapasite","ilk_saat_tl","saat","tip")} for r in d],
              open(f"{CIKTI}/otoparklar.json","w",encoding="utf-8"), ensure_ascii=False)
    ss = sum(len(x) for x in sg.values())
    print(f"uretildi: {CIKTI}/ · 1 ana sayfa + {len(g)} ilce + {len(sg)} sehir + {ss} sehir-ilce sayfasi + sitemap")


GIZLILIK = """<section class="kahraman dar">
<h1>Gizlilik ve KVKK</h1>
<p class="alt-baslik">Kısa versiyon: sunucumuz yok, hesabınız yok, konumunuz bize gelmiyor.</p>
</section>
<section class="metin">
<h2>Hangi veriyi topluyoruz</h2>
<p><strong>Hiçbirini.</strong> Bu site statik dosyalardan oluşur. Kayıt, giriş, çerez veya
izleme betiği yoktur. Sunucu tarafı kodu çalışmaz, veritabanı bulunmaz.</p>

<h2>Konum bilgisi</h2>
<p>&quot;En yakın otoparkları göster&quot; düğmesine bastığınızda tarayıcınız konum izni ister.
Verilen konum <strong>yalnızca cihazınızın içinde</strong> kullanılır: mesafe hesabı tarayıcıda
yapılır, sonuç ekranda gösterilir. Konum <strong>hiçbir sunucuya gönderilmez, kaydedilmez,
üçüncü tarafla paylaşılmaz.</strong> Sayfayı kapattığınızda kaybolur. İzin vermek zorunda
değilsiniz; ilçe listesinden de gezebilirsiniz.</p>

<h2>Dışarıya giden tek istek</h2>
<p>Canlı doluluk için tarayıcınız doğrudan İstanbul Büyükşehir Belediyesi Açık Veri
Portalı'na (<code>api.ibb.gov.tr</code>) istek atar. Bu istekte konumunuz veya kimliğiniz yer
almaz; yalnızca otopark listesi çekilir. İçerik Güvenliği Politikamız (CSP) başka hiçbir
dış adrese bağlantı kurulmasına izin vermez.</p>

<h2>Barındırma kayıtları</h2>
<p>Site Vercel üzerinde barındırılır. Her web sunucusu gibi Vercel de teknik erişim kaydı
(IP, tarayıcı bilgisi, istenen adres) tutabilir. Bu kayıtlar barındırma sağlayıcısına aittir
ve tarafımızca okunmaz veya işlenmez.</p>

<h2>KVKK</h2>
<p>6698 sayılı Kişisel Verilerin Korunması Kanunu anlamında tarafımızca <strong>işlenen
kişisel veri yoktur</strong>; bu nedenle veri sorumlusu sıfatıyla tutulan bir kayıt ortamı
bulunmamaktadır. Yine de sorunuz olursa GitHub deposundan issue açabilirsiniz.</p>

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

def yaz_gizlilik():
    open(f"{CIKTI}/gizlilik.html", "w", encoding="utf-8").write(sayfa(
        "Gizlilik ve KVKK | nereyeparkedicem",
        "Sunucumuz yok, hesabınız yok, konumunuz cihazınızdan çıkmıyor. "
        "Toplanan kişisel veri bulunmuyor.", GIZLILIK))

def yaz_404():
    open(f"{CIKTI}/404.html", "w", encoding="utf-8").write(sayfa(
        "Sayfa bulunamadı | nereyeparkedicem",
        "Aradığınız sayfa bulunamadı.", DORTYUZDORT))


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
        "İstanbul Otopark Fiyat Endeksi — İlçe İlçe Tarife | nereyeparkedicem",
        f"İstanbul'da {len(d)} İSPARK otoparkının ilçe bazında tarife medyanı. "
        f"İlk saat {tl(st.median(ilk))} ₺, tam gün {tl(st.median(gun))} ₺. "
        f"En pahalı {pahali['ad']}, en ucuz {ucuz['ad']} — {kat:.1f} kat fark.",
        gv, kok="../"))

if __name__ == "__main__": uret()
