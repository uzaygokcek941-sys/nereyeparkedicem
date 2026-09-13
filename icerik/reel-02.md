# Reel 02 — "Ankara'da 2.884 otopark var, dördünün saati biliniyor"

Anahtar: **PARK** · 38-45 sn · 9:16 · veri görselleştirme ağırlıklı

## Kanca
> "Ankara'da 2.884 otopark kayıtlı. Dördünün çalışma saati biliniyor.
> Dördünün. Antalya'da bir tane."

## 6 parça

| # | Sn | Ne | Ekranda |
|---|---|---|---|
| 1 | 0-5 | Kanca | Büyük sayı: **2.884** → yanına küçücük **4** |
| 2 | 5-11 | "Bu veri kimsenin sırrı değil, OpenStreetMap'te" | osm.org haritası, otopark ikonları |
| 3 | 11-22 | Sorguyu çalıştır | Terminal: `python osm_sehir.py` → tablo satır satır akıyor |
| 4 | 22-32 | Tabloyu göster | 10 şehir tablosu; **tarife eksik %99,8**, **saat eksik %99,4** vurgulu |
| 5 | 32-38 | "İstanbul'da bu boşluğu kapattım" | Site: Fatih sayfası, 28 otoparkta canlı doluluk + tam tarife |
| 6 | 38-44 | CTA | "Kendi şehrinin verisini çıkarmak istersen — yoruma **PARK** yaz" |

## Caption
```
Türkiye'de OpenStreetMap'te kayıtlı 24.418 otopark var.
52'sinde fiyat bilgisi var. 163'ünde çalışma saati.

Yani %99,8'inde "burada otopark var" yazıyor, "açık mı, kaça" yazmıyor.

Ankara 2.884 otopark / 4 saat. Antalya 1.351 / 1. Konya 714 / 0.
İstanbul'da İSPARK'ın açık verisi olduğu için orayı kapattım:
247 otopark, canlı doluluk, tam tarife.

Sorguyu nasıl çalıştıracağını anlatan dosyayı göndereyim — yoruma PARK yaz.
```

## Kaynak
`osm_turkiye.json` · `osm_sehirler.json` — ikisi de bu makinede üretildi, Overpass API.

---

# Reel 03 — "Belediyenin verisi bedava, kimse kullanmıyor"

Anahtar: **PARK** · 40-48 sn · ekran kaydı

## Kanca
> "İBB bütün otopark verisini bedava dağıtıyor. Canlı doluluk, tam tarife, koordinat.
> Kimse kullanmıyor."

## 6 parça

| # | Sn | Ne | Ekranda |
|---|---|---|---|
| 1 | 0-4 | Kanca | `data.ibb.gov.tr` ana sayfa |
| 2 | 4-12 | "Tek satır istek, tek cevap" | `curl api.ibb.gov.tr/ispark/Park` → JSON akışı |
| 3 | 12-22 | Detayı aç | Tek otoparkın `tariff` alanı: `0-1 Saat : 110,00; ... Tam Gün : 370,00` |
| 4 | 22-32 | "247 otoparkın 247'sinde tarife var" | `ispark_cek.py` çıktısı: `tarifesi olan: 247/247` |
| 5 | 32-40 | Siteye dönüştür | Site açılıyor, ilçe seçiliyor, canlı doluluk düşüyor |
| 6 | 40-46 | CTA | "Kodun tamamı açık. İstersen DM'den atayım — yoruma **PARK**" |

## Caption
```
İBB Açık Veri Portalı'nda İSPARK'ın tüm verisi duruyor: konum, kapasite,
anlık boş yer, tam tarife, çalışma saati. Lisans CC BY 4.0, anahtar yok,
ücret yok, izin istemiyor.

247 otoparkın 247'sinde tarife dolu.

Bu veriyle çerçeve kullanmadan, sunucusuz, tek statik siteyle
çalışan bir şey yaptım. Sayfa 2,4 KB, ilk boya 344 ms.

Kodu da veriyi de göndereyim — yoruma PARK yaz.
```

## Üç reel'in sırası
02 → **erişim** (geniş kitle, veri merakı) · 01 → **dönüşüm** (rakip zaafı, en somut) ·
03 → **teknik güven** (yapabildiğini kanıtlar)

Kanun 3 gereği tempo günde 1. Üçü bittiğinde 15 konuluk listeden devam
(CLAUDE.md **INSTA CLAUDE** içerik hattı).
