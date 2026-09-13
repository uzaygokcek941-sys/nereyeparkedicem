# nereyeparkedicem

İstanbul'daki **247 İSPARK otoparkının** canlı doluluk oranını, tam tarifesini ve
yol tarifini gösteren statik web uygulaması. Uygulama indirmeye gerek yok.

**Canlı:** https://nereyeparkedicem.vercel.app

## Neden

İSPARK'ın resmî mobil uygulaması Google Play'de **1,9 puan / 302 yorum** ve
**20 Şubat 2025'ten beri güncellenmemiş** (ölçüm: 2026-09-13). En sık şikâyet edilen
şey yol tarifinin yanlış koordinata gitmesi. Bu site o boşluğu kapatır.

## Nasıl çalışır

Çerçeve yok, build adımı yok, sunucu yok, veritabanı yok.

```
ispark.py       → İBB Açık Veri API istemcisi (TLS: truststore, doğrulama açık)
ispark_cek.py   → 247 otoparkın listesi + detayı → veri/ispark.json
uret.py         → veri/ispark.json → site/ (1 ana sayfa + 34 ilçe sayfası)
kontrol.py      → teslim öncesi tarayıcı ölçümü (hesaplanan değer, taşma, dokunma alanı)
perf.py         → canlı performans ölçümü (LCP / CLS / TTFB / transfer)
isit.py         → deploy sonrası edge cache ısıtma
og_uret.py      → paylaşım görseli (1200x630), sayılar veriden üretilir
test_uret.py    → 38 birim test, çerçeve yok
osm_sayim.py    → OpenStreetMap otopark kapsam ölçümü (Overpass)
osm_sehir.py    → il bazlı OSM kapsamı (resumable, önbellekli)
```

Canlı doluluk **tarayıcıda** İBB API'sinden çekilir (`Access-Control-Allow-Origin: *`),
o yüzden sunucu tarafı gerekmiyor. Tarifeler üretim anındaki anlık görüntüdür.

### Yeniden üretme

```bash
pip install truststore
python ispark_cek.py    # veri/ispark.json tazelenir
python uret.py          # site/ yeniden üretilir
python test_uret.py     # 38 birim test
python kontrol.py       # 375/768/1440 tarayıcı kontrolü, hata varsa exit 1
python og_uret.py       # site/og.png
python isit.py          # deploy sonrası cache ısıtma
python perf.py          # canlı Core Web Vitals
```

## Veri kaynakları ve lisans

| Kaynak | Kullanım | Lisans |
|---|---|---|
| [İBB Açık Veri Portalı](https://data.ibb.gov.tr/) — `api.ibb.gov.tr/ispark` | otopark, doluluk, tarife | **CC BY 4.0** |
| [OpenStreetMap](https://www.openstreetmap.org/) — `amenity=parking` | kapsam ölçümü | **ODbL** |
| Kod | — | **MIT** (`LICENSE`) |

**Bağımsız uygulamadır.** İstanbul Büyükşehir Belediyesi, İSPARK A.Ş. veya İSTMOP ile
resmî bağlantısı yoktur. Doluluk verisi İBB'nin güncelleme aralığına bağlıdır.

## Ölçülen performans (canlı)

LCP 308-364 ms · CLS 0 · TTFB 61-66 ms · JS 2,3 KB · CSS 2,5 KB · 3 istek

## Gizlilik

Sunucu yok, hesap yok, çerez yok, izleme betiği yok. Konum izni verilirse mesafe
hesabı **tarayıcıda** yapılır; konum hiçbir yere gönderilmez. Ayrıntı: `/gizlilik/`

Google Maps kazınmaz — hizmet şartları ihlalidir. Tüm veri açık lisanslı kaynaklardan gelir.
