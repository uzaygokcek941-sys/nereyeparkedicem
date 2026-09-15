# -*- coding: utf-8 -*-
"""81 il sayfasi: /il/ dizini + /il/<slug>/.

Denetimde olculdu: harita 81 ili kapsiyor ama "Bursa otopark" aramasinin
karsiligi yoktu - harita var, sayfa yok. Veri zaten site/veri/il-NN.json'da.

Nokta sayisi bir ilde 5.121'e cikabiliyor; sayfaya hepsi yazilmaz. Basa alinan:
ismi olan otoparklar (OSM'de azinlik) ve ucretsiz olanlar - kullanicinin
arayabilecegi ayirt edici bilgi bunlar."""
import html, json, os

from uret import CIKTI, URL, sayfa, slug, tl

LIMIT = 40   # sayfa basina liste uzunlugu; gerisi haritada

KAYNAK = (
 '<p>Konum verisi: <a href="https://www.openstreetmap.org/copyright" target="_blank" '
 'rel="noopener">OpenStreetMap</a> katkıcıları, lisans ODbL.</p>'
 '<p><strong>Bağımsız uygulamadır.</strong> OSM otoparkların büyük bölümünde fiyat ve '
 'çalışma saati taşımıyor; bu sayfada yalnızca kaynakta <em>bulunan</em> bilgi gösterilir, '
 'eksik alan uydurulmaz. İstanbul, İzmir ve Ankara için belediye açık verisiyle kurulan '
 'ayrıntılı sayfalar menüdedir.</p>')

AYRINTI = {34: ("İstanbul", "/", "İSPARK canlı doluluk + tam tarife"),
           35: ("İzmir", "/izmir/", "İZELMAN tarifeleri"),
           6:  ("Ankara", "/ankara/", "ANPARK otopark listesi")}


def il_yukle(kod):
    yol = f"{CIKTI}/veri/il-{kod:02d}.json"
    if not os.path.exists(yol): return None
    return json.load(open(yol, encoding="utf-8"))


def noktalar(d):
    """il-NN.json duz diziyi nesneye cevirir. b seyrek: bilgisi olmayan
    noktalar bos sozluk alir."""
    k, b, out = d["k"], d.get("b", {}), []
    for i in range(0, len(k), 2):
        bi = b.get(str(i // 2), {})
        out.append({"lat": k[i], "lng": k[i + 1], "ad": bi.get("a"),
                    "u": bi.get("u"), "kap": bi.get("k"),
                    "tip": bi.get("t"), "saat": bi.get("s"), "isl": bi.get("o")})
    return out


def kart(p, il):
    ad = html.escape(p["ad"] or "Otopark")
    ucret = "bilinmiyor" if p["u"] is None else ("ücretli" if p["u"] else "ücretsiz")
    ek = " · ".join(x for x in [
        f'{p["kap"]} kapasite' if p["kap"] else "",
        html.escape(p["tip"] or ""), html.escape(p["saat"] or ""),
        html.escape(p["isl"] or "")] if x)
    return f'''<article class="otopark">
 <header><h3>{ad}</h3><p class="adres">{il}</p></header>
 <dl class="ozet">
  <div><dt>Ücret</dt><dd>{ucret}</dd></div>
  <div><dt>Kapasite</dt><dd>{p["kap"] or "—"}</dd></div>
 </dl>
 {f'<p class="saat">{ek}</p>' if ek else ""}
 <div class="git">
  <a href="https://www.google.com/maps/dir/?api=1&destination={p["lat"]},{p["lng"]}" target="_blank" rel="noopener">Google Maps</a>
  <a href="https://yandex.com.tr/harita/?rtext=~{p["lat"]},{p["lng"]}&rtt=auto" target="_blank" rel="noopener">Yandex</a>
 </div></article>'''


def schema(ad, n, uc, sl):
    d = {"@context": "https://schema.org", "@type": "CollectionPage",
         "name": f"{ad} otoparkları", "url": f"{URL}/il/{sl}/",
         "inLanguage": "tr-TR",
         "description": f"{ad} ilinde OpenStreetMap'te kayıtlı {n} otopark, "
                        f"{uc} tanesi ücretsiz."}
    return f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'


def il_yaz(x):
    d = il_yukle(x["p"])
    if not d: return None
    sl = slug(x["ad"])
    p = noktalar(d)
    # bilgi tasiyan nokta basa: once isimli, sonra ucretsiz, sonra kapasiteli
    p.sort(key=lambda q: (q["ad"] is None, q["u"] != 0, -(q["kap"] or 0)))
    gosterilen = p[:LIMIT]
    uc, up = x.get("uc", 0), x.get("up", 0)
    bilinmeyen = x["n"] - uc - up
    ay = AYRINTI.get(x["p"])
    ay_html = (f'<p><a class="birincil" href="{ay[1]}">{ay[0]} ayrıntılı sayfa</a> '
               f'<span class="durum">{ay[2]}</span></p>') if ay else ""
    kalan = (f"({tl(x['n'] - len(gosterilen))} nokta daha haritada)"
             if x["n"] > len(gosterilen) else "")

    govde = f'''<nav class="iz"><a href="../../index.html">Ana sayfa</a> ›
 <a href="../index.html">İller</a> › <span>{x["ad"]}</span></nav>
<section class="kahraman dar">
 <h1>{x["ad"]} otoparkları — {tl(x["n"])} nokta</h1>
 <p class="alt-baslik">{tl(x["n"])} otopark haritada · {tl(uc)} ücretsiz ·
 {tl(up)} ücretli · {tl(bilinmeyen)} ücret bilgisi yok</p>
 {ay_html}
 <p><a class="ikincil" href="../../harita/?il={x["p"]}">🗺️ {x["ad"]}&#8217;ı haritada aç</a></p>
</section>
<section class="liste-bolum">
 <h2>Bilgisi olan otoparklar</h2>
 <p class="alt-baslik">{len(gosterilen)} otopark listelendi {kalan}.
 Sıralama: adı olanlar, sonra ücretsizler.</p>
 <div class="liste">{"".join(kart(q, x["ad"]) for q in gosterilen)}</div>
</section>
{schema(x["ad"], x["n"], uc, sl)}'''

    os.makedirs(f"{CIKTI}/il/{sl}", exist_ok=True)
    open(f"{CIKTI}/il/{sl}/index.html", "w", encoding="utf-8").write(sayfa(
        f"{x['ad']} Otopark — {tl(x['n'])} Nokta, {tl(uc)} Ücretsiz",
        f"{x['ad']} ilinde kayıtlı {tl(x['n'])} otoparkın konumu; {tl(uc)} tanesi ücretsiz. "
        f"Haritadan en yakınını bul, tek dokunuşla yol tarifi al.",
        govde, kok="../../", kaynak_html=KAYNAK, js=False,
        canonical=f"{URL}/il/{sl}/"))
    return sl


def dizin_yaz(o, sluglar):
    kart_html = "".join(
        f'<a class="ilce" href="{sluglar[x["p"]]}/"><b>{x["ad"]}</b>'
        f'<span>{tl(x["n"])} otopark</span>'
        f'<span class="fiyat">{tl(x.get("uc", 0))} ücretsiz</span></a>'
        for x in o["iller"] if x["p"] in sluglar)
    govde = f'''<nav class="iz"><a href="../index.html">Ana sayfa</a> › <span>İller</span></nav>
<section class="kahraman dar">
 <h1>{len(sluglar)} ilin otopark listesi</h1>
 <p class="alt-baslik">{tl(o["toplam"])} otopark noktası, otopark sayısına göre sıralı.</p>
 <p><a class="birincil" href="../harita/">🗺️ Haritayı aç</a>
    <a class="ikincil" href="../ucretsiz-otopark/">Ücretsiz otoparklar</a></p>
</section>
<section id="iller"><h2>İl listesi</h2>
 <div class="ilce-izgara">{kart_html}</div></section>'''
    os.makedirs(f"{CIKTI}/il", exist_ok=True)
    open(f"{CIKTI}/il/index.html", "w", encoding="utf-8").write(sayfa(
        f"{len(sluglar)} İlin Otopark Listesi — Türkiye Otopark Rehberi",
        f"Türkiye'nin {len(sluglar)} ilinde toplam {tl(o['toplam'])} otopark noktası. "
        f"İl seç, en yakın otoparkı ve ücretsiz olanları gör.",
        govde, kok="../", kaynak_html=KAYNAK, js=False,
        canonical=f"{URL}/il/"))


def ucretsiz_yaz(o, sluglar):
    """OSM'de fee=no isaretli otoparklar. Turkiye'de baska yerde yayinlanmayan
    bir liste; ama kapsam durustce yazilir - noktalarin %88'inde ucret bilgisi
    hic yok, yani "ucretsiz degil" demek DEGIL, "bilinmiyor" demek."""
    sirali = sorted((x for x in o["iller"] if x["p"] in sluglar),
                    key=lambda x: -x.get("uc", 0))
    top_uc = sum(x.get("uc", 0) for x in sirali)
    top_up = sum(x.get("up", 0) for x in sirali)
    bilinmeyen = o["toplam"] - top_uc - top_up
    satir = "".join(
        f'<tr><th scope="row"><a href="../il/{sluglar[x["p"]]}/">{x["ad"]}</a></th>'
        f'<td>{tl(x.get("uc", 0))}</td><td>{tl(x.get("up", 0))}</td>'
        f'<td>{tl(x["n"])}</td></tr>'
        for x in sirali if x.get("uc", 0))
    govde = f'''<nav class="iz"><a href="../index.html">Ana sayfa</a> ›
 <span>Ücretsiz otoparklar</span></nav>
<section class="kahraman dar">
 <h1>Ücretsiz otoparklar — {tl(top_uc)} nokta</h1>
 <p class="alt-baslik">OpenStreetMap&#8217;te <code>fee=no</code> işaretli, yani
 kaynağında açıkça ücretsiz olduğu yazan otoparklar. {len(sirali)} ilin
 {sum(1 for x in sirali if x.get("uc", 0))} tanesinde kayıt var.</p>
 <p><a class="birincil" href="../harita/?ucretsiz=1">🗺️ Haritada yalnız ücretsizleri göster</a></p>
</section>
<section class="metin">
 <h2>Bu sayıyı nasıl okumalı</h2>
 <p>{tl(o["toplam"])} otopark noktasının <strong>{tl(top_uc)} tanesinde ücretsiz</strong>,
 {tl(top_up)} tanesinde ücretli bilgisi var. Kalan <strong>{tl(bilinmeyen)} noktada ücret
 bilgisi hiç yok</strong> — bu &quot;ücretli&quot; demek değil, <em>bilinmiyor</em> demek.
 Ücretsiz listesi bu yüzden bir alt sınırdır: sahada daha fazlası vardır, OSM&#8217;de
 işaretlenmemiştir.</p>
 <p>İstanbul, İzmir ve Ankara için belediye açık verisiyle kurulan tarife sayfaları
 menüdedir; oradaki fiyatlar bu listeden bağımsızdır.</p>
</section>
<section class="liste-bolum">
 <h2>İl il ücretsiz otopark sayısı</h2>
 <div class="tablo-sar">
 <table class="endeks">
  <thead><tr><th scope="col">İl</th><th scope="col">Ücretsiz</th>
   <th scope="col">Ücretli</th><th scope="col">Toplam nokta</th></tr></thead>
  <tbody>{satir}</tbody>
 </table></div>
</section>'''
    os.makedirs(f"{CIKTI}/ucretsiz-otopark", exist_ok=True)
    open(f"{CIKTI}/ucretsiz-otopark/index.html", "w", encoding="utf-8").write(sayfa(
        f"Ücretsiz Otopark — {tl(top_uc)} Nokta, İl İl Liste",
        f"Türkiye'de OpenStreetMap'te ücretsiz olarak işaretli {tl(top_uc)} otopark. "
        f"İl il liste, haritada ücretsiz filtresi, tek dokunuşla yol tarifi.",
        govde, kok="../", kaynak_html=KAYNAK, js=False,
        canonical=f"{URL}/ucretsiz-otopark/"))
    return top_uc


def yaz():
    o = json.load(open(f"{CIKTI}/veri/iller.json", encoding="utf-8"))
    sluglar = {}
    for x in o["iller"]:
        sl = il_yaz(x)
        if sl: sluglar[x["p"]] = sl
    dizin_yaz(o, sluglar)
    uc = ucretsiz_yaz(o, sluglar)
    print(f"uretildi: {CIKTI}/il/ · {len(sluglar)} il sayfasi + dizin · "
          f"ucretsiz-otopark/ {tl(uc)} nokta")
    return sluglar


if __name__ == "__main__":
    yaz()
