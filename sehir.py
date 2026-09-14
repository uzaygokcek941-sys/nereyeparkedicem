# -*- coding: utf-8 -*-
"""Izmir ve Ankara sayfalari. uret.py'nin yardimcilarini aynen kullanir;
tek fark kaynak/lisans metni ve canli doluluk olmamasi.

ISPARK canli bos kapasite veriyor, IZELMAN ve ANPARK vermiyor. O yuzden bu
sayfalarda uygulama.js yuklenmez (js=False) — yoksa Istanbul verisini cekip
yanlis doluluk gosterir."""
import json, os
from uret import CIKTI, slug, tr_baslik, tl, kart, sayfa, ilce_grupla

SEHIR = {
    "izmir": {
        "ad": "İzmir", "dosya": "veri/izmir.json", "isletme": "İZELMAN",
        "kaynak": (
            '<p>Veri: <a href="https://acikveri.bizizmir.com/" target="_blank" rel="noopener">'
            'İzmir Büyükşehir Belediyesi Açık Veri Portalı</a> — İZELMAN A.Ş. otopark '
            'lokasyon, kapasite ve ücret veri setleri.</p>'
            '<p><strong>Bağımsız uygulamadır.</strong> İzmir Büyükşehir Belediyesi veya '
            'İZELMAN A.Ş. ile resmî bağlantısı yoktur. <strong>Canlı doluluk yoktur</strong> — '
            'İzmir açık verisi anlık boş kapasite yayınlamıyor, yalnız toplam kapasite veriyor.</p>'),
    },
    "ankara": {
        "ad": "Ankara", "dosya": "veri/ankara.json", "isletme": "ANPARK",
        "kaynak": (
            '<p>Veri: <a href="https://www.anpark.com.tr/" target="_blank" rel="noopener">'
            'ANPARK</a> açık uç noktası — Ankara Büyükşehir Belediyesi iştiraki.</p>'
            '<p><strong>Bağımsız uygulamadır.</strong> Ankara Büyükşehir Belediyesi veya ANPARK ile '
            'resmî bağlantısı yoktur. <strong>Tarife ve canlı doluluk yoktur</strong> — ANPARK '
            'fiyat listesini yalnızca görsel olarak yayınlıyor, makine okunur tarife vermiyor.</p>'),
    },
}

def yukle(yol):
    d = json.load(open(yol, encoding="utf-8"))
    for k in d:
        k["slug"] = slug(k["ilce"]); k["ad_tr"] = tr_baslik(k["ad"])
    return d

def uret_sehir(kod, s):
    d = yukle(s["dosya"]); g = ilce_grupla(d)
    kap = sum(k["kapasite"] or 0 for k in d)
    tarifeli = sum(1 for k in d if k["tarife"])
    nokta = lambda n: f"{n:,}".replace(",", ".")

    f = sorted(k["ilk_saat_tl"] for k in d if k["ilk_saat_tl"])
    med = f[len(f)//2] if f else None
    fiyat_kutu = (f'<div><b>{tl(med)} ₺</b><span>ilk saat medyan</span></div>'
                  if med else f'<div><b>{tarifeli}</b><span>tarifesi yayınlanan</span></div>')

    kartlar = "".join(
        f'<a class="ilce" href="ilce/{k}/"><b>{v["ad"]}</b>'
        f'<span>{len(v["kayit"])} otopark · {nokta(v["kapasite"])} yer</span>'
        + (f'<span class="fiyat">ilk saat medyan {tl(v["medyan"])} ₺</span>'
           if v["medyan"] else '<span class="fiyat">tarife yayınlanmıyor</span>')
        + '</a>' for k, v in g.items())

    govde = f'''<nav class="iz"><a href="../index.html">Ana sayfa</a> › <span>{s["ad"]}</span></nav>
<section class="kahraman">
 <h1>{s["ad"]} otoparkları — konum, kapasite ve tarife</h1>
 <p class="alt-baslik">{s["ad"]}'de {len(d)} {s["isletme"]} otoparkı, {len(g)} ilçe.
 Veri {s["ad"]} açık veri kaynağından alınır; uygulama indirmene gerek yok.</p>
 <div class="rakamlar">
  <div><b>{len(d)}</b><span>otopark</span></div>
  <div><b>{nokta(kap)}</b><span>toplam yer</span></div>
  <div><b>{len(g)}</b><span>ilçe</span></div>
  {fiyat_kutu}
 </div>
</section>
<section id="ilceler"><h2>İlçeye göre</h2><div class="ilce-izgara">{kartlar}</div></section>'''

    os.makedirs(f"{CIKTI}/{kod}", exist_ok=True)
    open(f"{CIKTI}/{kod}/index.html", "w", encoding="utf-8").write(sayfa(
        f"{s['ad']} Otopark — Konum, Kapasite ve Tarife | nereyeparkedicem",
        f"{s['ad']}'de {len(d)} {s['isletme']} otoparkının konumu, kapasitesi ve "
        f"{'tarifesi' if tarifeli else 'çalışma saatleri'}. İlçe ilçe liste, tek dokunuşla yol tarifi.",
        govde, kok="../", kaynak_html=s["kaynak"], js=False))

    for sl, v in g.items():
        os.makedirs(f"{CIKTI}/{kod}/ilce/{sl}", exist_ok=True)
        alt = (f'ilk saat medyan {tl(v["medyan"])} ₺' if v["medyan"] else 'tarife yayınlanmıyor')
        gv = f'''<nav class="iz"><a href="../../../index.html">Ana sayfa</a> ›
 <a href="../../index.html">{s["ad"]}</a> › <span>{v["ad"]}</span></nav>
<section class="kahraman dar">
 <h1>{v["ad"]} otoparkları — {s["ad"]}</h1>
 <p class="alt-baslik">{len(v["kayit"])} {s["isletme"]} noktası ·
 {nokta(v["kapasite"])} yer · {alt}</p>
</section>
<section class="liste">{"".join(kart(k) for k in v["kayit"])}</section>'''
        open(f"{CIKTI}/{kod}/ilce/{sl}/index.html", "w", encoding="utf-8").write(sayfa(
            f"{v['ad']} Otopark — {s['ad']} | nereyeparkedicem",
            f"{s['ad']} {v['ad']} ilçesindeki {len(v['kayit'])} {s['isletme']} otoparkı: "
            f"konum, kapasite, çalışma saati ve yol tarifi.",
            gv, kok="../../../", kaynak_html=s["kaynak"], js=False))

    print(f"{s['ad']:<7} {len(d):>3} otopark · {len(g)} ilce sayfasi · tarifeli {tarifeli}")
    return g

def uret_hepsi():
    return {k: uret_sehir(k, s) for k, s in SEHIR.items()}

if __name__ == "__main__":
    uret_hepsi()
