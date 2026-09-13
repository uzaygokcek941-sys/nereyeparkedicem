# Reel 01 — "Belediyenin uygulaması 1,9 puan"

Anahtar: **PARK** (4 harf — ölçüm: ≤4 harf → 2,2 kat yorum, 2,3 kat izlenme)
Süre: 40-48 sn · 9:16 · altyazılı · ekran kaydı ağırlıklı

## Kanca — iki aday, biri seçilecek

**A (rakip zaafı, en güçlü kanıt):**
> "İBB'nin otopark uygulaması 100 bin kişinin telefonunda. Puanı 1,9.
> Son güncelleme: Şubat 2025."

**B (kıtlık aritmetiği, daha geniş kitle):**
> "Ankara'da 2.884 otopark var. Dördünün çalışma saati biliniyor. Dördünün."

Öneri: **A** — ekranda gösterilecek somut kanıtı var (mağaza sayfası + yorum),
B'nin görseli soyut kalıyor.

## 6 parça

| # | Sn | Ne | Ekranda |
|---|---|---|---|
| 1 | 0-4 | Kanca A | Play Store sayfası: **1,9 · 302 yorum · 100 B+ · 20 Şub 2025** |
| 2 | 4-11 | "Neden nefret ediliyor, yoruma bak" | Gerçek yorum, sarı vurgu: *"Kayaşehir'deki konuma Git tuşuna basıyorum **Kahire Mısır'a** navigasyon açılıyor"* |
| 3 | 11-20 | "Veri belediyenin, herkese açık, bedava" | Terminal: `curl api.ibb.gov.tr/ispark/Park` → JSON akıyor · alt yazı: **CC BY 4.0** |
| 4 | 20-33 | "Bir günde yaptım" — ekran kaydı | Telefonda site: konum izni → **en yakın 10 otopark** → boş yer sayısı yeşil → Google Maps'e bas → **doğru yere** gidiyor |
| 5 | 33-40 | Çalışan sonucu göster | Fatih sayfası: **%23 dolu · 5.849 boş yer** · tarife listesi açılıyor (110₺/140₺/170₺…) |
| 6 | 40-46 | Sürtünmeyi kaldır + CTA | "Site bedava, indirme yok, link bio'da. Kodun tamamı açık." → **"Takip et, yoruma PARK yaz, DM'den göndereyim"** |

## Çekim listesi

1. Play Store `com.p4c.ispark` — puan + yorum sayısı + güncelleme tarihi tek karede
2. Aynı sayfada Kahire yorumuna kaydırma (gerçek, düzenlenmemiş)
3. Terminal: `python ispark_cek.py` çıktısı — `247 kayit · tarifesi olan: 247/247`
4. Telefon ekran kaydı: `nereyeparkedicem.vercel.app` → "En yakın otoparkları göster" → liste
5. Google Maps'e basış → navigasyon açılıyor (Kahire kontrastı için kritik kare)
6. `/ilce/fatih/` canlı doluluk satırı

## Caption

```
İBB'nin otopark uygulaması 100 bin indirme almış, puanı 1,9.
Bir kullanıcı "Kayaşehir'e basıyorum Kahire'ye navigasyon açılıyor" yazmış.

Veri zaten herkese açık: İBB Açık Veri Portalı, CC BY 4.0.
Aynı veriyle çalışan bir site yaptım — 247 otopark, canlı doluluk, tam tarife,
doğru yol tarifi. İndirme yok, ücret yok.

Kodun tamamı açık. Kendi şehrinin verisini nasıl çıkaracağını da anlatıyorum.

Takip et ve yoruma PARK yaz, DM'den göndereyim.
```

İlk satırda huni yok — kanca önce. **İlk DM'de link yok, fiyat yok** (DOA kazanan mekanik).
DM'de gönderilecek: site adresi + repo + `osm_sayim.py`/`osm_sehir.py`.

## Kullanılan sayılar — hepsi bu oturumda ölçüldü

| İddia | Kaynak |
|---|---|
| 1,9 puan · 302 yorum · 100 B+ · 20 Şub 2025 | Play Store, `scrapling stealthy-fetch`, 2026-09-13 |
| Kahire yorumu | Aynı sayfa, birebir alıntı |
| 247 otopark, 247/247 tarife | `veri/ispark.json`, `ispark_cek.py` çıktısı |
| Fatih %23 dolu / 5.849 boş | Canlı site ölçümü, `api.ibb.gov.tr` |
| Ankara 2.884 / 4 saat | `osm_sehirler.json` |
| Türkiye 24.418 otopark / 52 tarife / 163 saat | `osm_turkiye.json` |

**Uydurma sayı yok. Her cümlenin sütunu var.**

## Yasak

- Rakip uygulamayı kişiselleştirip hakaret etme — sayı ve yorum konuşsun
- "En iyi otopark uygulaması" gibi kanıtlanamaz üstünlük iddiası
- Sahte kontenjan, sahte aciliyet
- Otomatik DM aracı (Instagram TOS) — DM elle veya resmî araçla
