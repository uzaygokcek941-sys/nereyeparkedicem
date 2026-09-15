# -*- coding: utf-8 -*-
"""/harita/ sayfasi. Leaflet kendi sunucumuzda (site/vendor), CDN yok -> CSP
script-src 'self' bozulmuyor. Tek dis kaynak fayans gorselleri."""
import json, os
from uret import CIKTI, URL, sayfa

KAYNAK = (
 '<p>Harita verisi: <a href="https://www.openstreetmap.org/copyright" target="_blank" '
 'rel="noopener">OpenStreetMap</a> katkıcıları, lisans ODbL. Fayanslar OpenStreetMap '
 'Vakfı sunucularından gelir.</p>'
 '<p><strong>Bağımsız uygulamadır.</strong> Noktalar OSM topluluğunun girdiği verilerdir; '
 'OSM otoparkların <strong>%99,8&#8217;inde fiyat, %99,3&#8217;ünde çalışma saati '
 'taşımıyor</strong> — bu yüzden ücret ve saat çoğu noktada boştur. İstanbul, İzmir ve '
 'Ankara için belediye açık verisiyle kurulan ayrıntılı sayfalar menüdedir.</p>')

def yaz():
    o = json.load(open(f"{CIKTI}/veri/iller.json", encoding="utf-8"))
    n, il = o["toplam"], len(o["iller"])
    # 81'in tamami listelenir: her ile rozetten gidilebilsin, kullanici ili
    # yakinlastirarak aramak zorunda kalmasin. Siralama otopark sayisina gore.
    rozet = "".join(
        f'<button class="il-rozet" data-lat="{x["c"][0]}" data-lng="{x["c"][1]}">'
        f'{x["ad"]} <b>{x["n"]:,}</b></button>'.replace(",", ".") for x in o["iller"])

    govde = f'''<nav class="iz"><a href="../index.html">Ana sayfa</a> › <span>Harita</span></nav>
<section class="kahraman dar">
 <h1>Türkiye otopark haritası — {il} il</h1>
 <p class="alt-baslik"><b id="harita-toplam">{n:,}</b> otopark noktası haritada.
 İl balonuna dokun, yakınlaş, otoparklar yüklensin.</p>
 <div class="harita-arac">
  <button id="harita-konum" class="birincil">Konumuma git</button>
  <p id="harita-durum" class="durum" role="status"></p>
 </div>
 <p id="harita-filtre" class="durum" hidden><strong>Filtre açık:</strong> yalnızca
  OpenStreetMap&#8217;te ücretsiz işaretli otoparklar gösteriliyor ·
  <a href="?">filtreyi kaldır</a></p>
</section>
<div id="harita" role="application" aria-label="Türkiye otopark haritası"></div>
<section class="metin">
 <h2>{il} ilin tamamı — otopark sayısına göre</h2>
 <p class="il-ara-satir">
  <label for="il-ara">İl ara</label>
  <input id="il-ara" type="search" inputmode="search" autocomplete="off"
   placeholder="Ankara, Bursa, Van…" aria-describedby="il-ara-sayac">
  <span id="il-ara-sayac" class="durum" role="status"></span>
 </p>
 <div class="rozetler">{rozet}</div>
 <h2>Bu harita ne gösteriyor</h2>
 <p>OpenStreetMap&#8217;te <code>amenity=parking</code> etiketiyle kayıtlı bütün noktalar —
 {il} ilin tamamı, {n:,} otopark. Yeşil nokta ücret bilgisi olmayan ya da ücretsiz,
 turuncu nokta <code>fee=yes</code> işaretli otoparktır.</p>
 <p>Veri sadece görünen alandaki iller için indirilir; haritayı açmak bütün ülkeyi
 yüklemez.</p>
</section>'''.replace(f"{n:,}", f"{n:,}".replace(",", "."))

    ek_head = '<link rel="stylesheet" href="../vendor/leaflet.css">'
    ek_js = ('<script src="../vendor/leaflet.js" defer></script>'
             '<script src="../harita.js" defer></script>')

    os.makedirs(f"{CIKTI}/harita", exist_ok=True)
    open(f"{CIKTI}/harita/index.html", "w", encoding="utf-8").write(sayfa(
        f"Türkiye Otopark Haritası — {il} İl, {n:,} Nokta".replace(",", "."),
        f"Türkiye genelinde {n:,} otopark noktası tek haritada. ".replace(",", ".") +
        f"{il} il, OpenStreetMap verisiyle; konumuna en yakın otoparkı haritadan bul.",
        govde, kok="../", kaynak_html=KAYNAK, js=False, sekme="harita",
        ek_head=ek_head, ek_js=ek_js, canonical=f"{URL}/harita/"))
    print(f"uretildi: {CIKTI}/harita/ · {il} il · {n:,} nokta")
    return o

if __name__ == "__main__":
    yaz()
