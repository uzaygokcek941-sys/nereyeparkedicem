# Reel 04 — "Fiyatı kimse yazmıyor"

Anahtar: **PARK** · 40-46 sn · 9:16 · ekran kaydı + terminal

En sert sayı burada. Diğer üç reel "veri var, kimse kullanmıyor" diyor;
bu reel **neyin gerçekten eksik olduğunu** gösteriyor: fiyat.

## Kanca
> "İstanbul'da 247 İSPARK otoparkı var. OpenStreetMap bunların
> **243'ünün fiyatını bilmiyor.** Dördünü biliyor. Dördünü."

## 6 parça

| # | Sn | Ne | Ekranda |
|---|---|---|---|
| 1 | 0-5 | Kanca | Ekranda **247** → altına kırmızı **4** |
| 2 | 5-12 | "Herkes aynı veriyi çekiyor, mesele o değil" | Play Store: 5 otopark uygulaması yan yana |
| 3 | 12-24 | Eşleştirmeyi çalıştır | Terminal: `python osm_ispark.py` → çıktı akıyor, `OSM'de YOK 73 / 247` satırında dur |
| 4 | 24-32 | Sonucu oku | `eşleşende tarife var: 4` satırı büyütülmüş |
| 5 | 32-40 | "Ben tarifeyi taşıyorum" | Site: bir otopark kartı açılıyor, `0-1 Saat 110 ₺ … Tam Gün 370 ₺` |
| 6 | 40-46 | CTA | "Eşleştirme kodunu göndereyim — yoruma **PARK** yaz" |

## Caption
```
Otopark uygulamalarının hepsi aynı açık veriyi çekiyor. Veri çekmek
ayırt edici değil — ölçtüm.

150 metre yarıçapla İSPARK'ın 247 otoparkını OpenStreetMap'in
İstanbul'daki 5.007 otoparkıyla eşleştirdim:

· 73'ü OSM'de hiç kayıtlı değil
· eşleşen 174'ün yalnız 4'ünde fiyat etiketi var

Yani harita "burada otopark var" diyor, "kaça" demiyor.
Sitede 247 otoparkın 247'sinde tam tarife duruyor.

Eşleştirme kodu 60 satır. Göndereyim — yoruma PARK yaz.
```

## Kaynak
`veri/osm_ispark.json` — `osm_ispark.py` çıktısı, 150 m eşik, bu makinede üretildi.
İSPARK tarafı `veri/ispark.json` (İBB Açık Veri, CC BY 4.0).

**Çekim notu:** 3. parçada terminal çıktısı gerçek olmalı. `python osm_ispark.py`
önbellekten saniyeler içinde koşar; sahte terminal kaydı kullanma.

---

# Reel 05 — "İzmir'in verisi duruyor, Ankara fiyatı resim olarak yayınlıyor"

Anahtar: **PARK** · 42-50 sn · 9:16 · ekran kaydı

## Kanca
> "İzmir bütün otopark verisini CSV olarak veriyor. Ankara fiyat listesini
> **JPEG olarak** yayınlıyor. Aynı ülke, aynı yıl."

## 6 parça

| # | Sn | Ne | Ekranda |
|---|---|---|---|
| 1 | 0-5 | Kanca | Yan yana: temiz CSV tablosu ↔ bulanık fiyat görseli |
| 2 | 5-13 | İzmir portalı | `acikveri.bizizmir.com` → otopark veri setleri, CSV indir |
| 3 | 13-22 | Çekiciyi çalıştır | Terminal: `python sehir_cek.py` → `izmir: 99 otopark · tarifesi olan 21` |
| 4 | 22-32 | ANPARK'a geç | anpark.com.tr → fiyat düğmesine bas → **resim** açılıyor, metin seçilemiyor |
| 5 | 32-42 | İki şehir sayfası | Site `/izmir/` ve `/ankara/` — Ankara kartında açıkça "tarife yayınlanmıyor" |
| 6 | 42-50 | CTA | "Kendi şehrin hangisi, bakayım — yoruma **PARK** yaz" |

## Caption
```
Türkiye'de belediye açık verisi şehirden şehre değişiyor, ölçtüm:

İstanbul — İSPARK API'si: 247 otopark, canlı boş yer, tam tarife
İzmir — İZELMAN CSV'si: 99 otopark, kapasite, 21'inin tarifesi
Ankara — ANPARK: 24 otopark, konum ve kapasite var,
fiyat listesi yalnızca görsel olarak yayınlanıyor

Üçünü de siteye koydum. Ankara sayfasında fiyat yok, çünkü kaynakta yok —
tahmin yazmadım.

Kendi şehrinde ne var bakmamı istersen yoruma PARK yaz.
```

## Kaynak
`veri/izmir.json` (İzmir Büyükşehir Açık Veri Portalı) ·
`veri/ankara.json` (ANPARK `/wp-json/anpark/v1/parks`) · `veri/ispark.json` (İBB).

**Dürüstlük notu:** 21 rakamı, tarife CSV'sindeki 39 kaydın konum listesiyle kesin
eşleşen kısmı. Kalanlar İzmir'in kendi konum dosyalarında yok. Reel'de "İzmir'in
tamamı" denmeyecek.

---

## Beş reel'in sırası

| Sıra | Reel | İşi |
|---|---|---|
| 1 | **02** | Erişim — geniş veri merakı |
| 2 | **04** | Dönüşüm — en sert tek sayı (247 → 4) |
| 3 | **01** | Rakip zaafı — Play Store 1,9 puan |
| 4 | **05** | Kapsam — üç şehir, dürüst eksik |
| 5 | **03** | Teknik güven — kodu göster |

Kanun 1: huni dönüşüm aracı, erişim aracı değil — beşinde de anahtar **PARK**,
dört harf (ölçülmüş eşik ≤4 harf).
Kanun 3: tempo günde 1.
