# nereyeparkedicem

İstanbul'daki **247 İSPARK otoparkının** canlı doluluk oranını, tam tarifesini ve
yol tarifini gösteren statik web uygulaması. Uygulama indirmeye gerek yok.

**Canlı:** _(deploy sonrası eklenecek)_

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
python kontrol.py       # 375/768/1440 tarayıcı kontrolü, hata varsa exit 1
```

## Veri kaynakları ve lisans

| Kaynak | Kullanım | Lisans |
|---|---|---|
| [İBB Açık Veri Portalı](https://data.ibb.gov.tr/) — `api.ibb.gov.tr/ispark` | otopark, doluluk, tarife | **CC BY 4.0** |
| [OpenStreetMap](https://www.openstreetmap.org/) — `amenity=parking` | kapsam ölçümü | **ODbL** |
| Kod | — | **MIT** (`LICENSE`) |

**Bağımsız uygulamadır.** İstanbul Büyükşehir Belediyesi, İSPARK A.Ş. veya İSTMOP ile
resmî bağlantısı yoktur. Doluluk verisi İBB'nin güncelleme aralığına bağlıdır.

Google Maps kazınmaz — hizmet şartları ihlalidir. Tüm veri açık lisanslı kaynaklardan gelir.
