# Play Console — sırayla yapılacaklar ve form cevap anahtarı

Seçilen paket: **`wv/`** (WebView + AdMob). `twa/` reklamsız alternatif olarak
duruyor; Play'e **yalnız biri** yüklenir, paket adı ikisinde de
`app.vercel.nereyeparkedicem`.

---

## SIRA

### 1 · Supabase'de iki SQL — 5 dakika, ZORUNLU
`SUPABASE-KURULUM.md` adım **2** (favoriler tablosu + RLS) ve adım **2b**
(`hesabimi_sil()` fonksiyonu). 2b olmadan hesap silme düğmesi çalışmaz ve
**Play uygulamayı reddeder**. Adım 3'teki Redirect URL listesini de doldur.

### 2 · AdMob kimlikleri
1. AdMob'da uygulama + banner birimi aç (`ADMOB-KURULUM.md`).
2. `wv/app/src/main/res/values/admob.xml` içindeki iki test kimliğini değiştir.
3. `site/veri/admob.json` → `{"publisherId": "pub-…"}`, sonra `python uret.py`:
   `site/app-ads.txt` kendiliğinden yazılır. Kimlik boşken dosya **bilerek**
   üretilmez (boş app-ads.txt "yetkili satıcı yok" demektir, geliri düşürür).
4. `git push` → Vercel deploy. app-ads.txt canlıda olmalı.

### 3 · Yayın anahtarı
```powershell
keytool -genkeypair -v -keystore yayin.keystore -alias yayin `
  -keyalg RSA -keysize 2048 -validity 10000
```
**Bu dosyayı ve parolasını kaybedersen uygulamayı bir daha güncelleyemezsin.**

### 4 · İmzalı AAB
```powershell
cd wv
.\imzala.ps1 -Keystore "C:\yol\yayin.keystore" -Alias yayin
```
Parolayı jarsigner sorar; script parolayı saklamaz.

### 5 · Play Console kaydı
Uygulama oluştur → paket `app.vercel.nereyeparkedicem` → ücretsiz → mağaza
kaydını `magaza/magaza-metni.md`'den doldur → görseller:
`magaza/kapak/ekran-0*.png` (**kapaklı olanlar**, ham olanlar değil),
`magaza/feature-graphic-1024x500.png`, ikon `site/simge-512.png`.

### 6 · Formlar
Aşağıdaki cevap anahtarını birebir uygula.

### 7 · Kapalı test
14-15 kişi davet et (12 şart, düşene karşı pay). Davet metni
`magaza/magaza-metni.md` sonunda. **14 gün kesintisiz** sayaç.

### 8 · Yayın başvurusu, sonra 48 saat
Çökme raporları, yorumlara aynı gün cevap, en çok tekrar eden şikâyeti düzelt.

---

## Data safety formu — cevap anahtarı

**"Uygulamanız kullanıcı verisi topluyor veya paylaşıyor mu?" → EVET**

| Veri türü | Toplanıyor | Paylaşılıyor | Zorunlu mu | Amaç |
|---|---|---|---|---|
| Kişisel bilgiler → **E-posta adresleri** | Evet | Hayır | **İsteğe bağlı** | Hesap yönetimi |
| Konum → **Yaklaşık konum** | Evet | **Evet** (rota sunucusu) | **İsteğe bağlı** | Uygulama işlevselliği |
| Uygulama etkinliği → **Uygulama içi arama geçmişi** | Evet | **Evet** (adres arama servisi) | İsteğe bağlı | Uygulama işlevselliği |
| Uygulama etkinliği → **Diğer kullanıcı tarafından oluşturulan içerik** (favori listesi) | Evet | Hayır | İsteğe bağlı | Uygulama işlevselliği |
| **Cihaz veya diğer kimlikler** | Evet | **Evet** (reklam ağı) | **Zorunlu** | Reklamcılık veya pazarlama |

Gerekçeler — inceleme sorarsa:
- **Konum paylaşılıyor**, çünkü "Yol tarifi"ne basınca başlangıç/varış koordinatı
  OSRM sunucusuna gidiyor. Basılmazsa hiç gitmiyor → *isteğe bağlı*.
- **Arama geçmişi paylaşılıyor**, çünkü yazılan adres metni Nominatim'e gidiyor.
- **Cihaz kimliği zorunlu**, çünkü reklam kapatılamıyor.
- E-posta ve favori listesi bizim Supabase örneğimizde kalıyor, üçüncü tarafa
  aktarılmıyor → *paylaşılmıyor*.

**Güvenlik ve silme**
- Aktarımda şifreleme → **Evet** (HTTPS).
- Kullanıcı silme talep edebilir mi → **Evet**.
- **Hesap silme URL'si** → `https://nereyeparkedicem.vercel.app/hesap-sil/`
- Bağımsız güvenlik incelemesi → **Hayır**.

## Uygulama içeriği — cevap anahtarı

| Soru | Cevap |
|---|---|
| Gizlilik politikası | `https://nereyeparkedicem.vercel.app/gizlilik/` |
| **Reklam içerir** | **Evet** |
| Uygulama içi satın alma | Hayır |
| Hedef kitle yaşı | **18 ve üzeri** |
| Çocuklara yönelik mi | Hayır |
| Haber uygulaması mı | Hayır |
| COVID-19 izleme | Hayır |
| Devlet uygulaması mı | Hayır |
| Finans ürünü mü | Hayır |
| Arka planda konum kullanıyor mu | **Hayır** — yalnız ekran açıkken ve kullanıcı isteyince |

## İçerik derecelendirme (IARC) — cevap anahtarı

Kategori: **Yardımcı program / Üretkenlik**.

| Soru | Cevap |
|---|---|
| Şiddet, korku, cinsellik, küfür, uyuşturucu, kumar | **Hepsi hayır** |
| Kullanıcılar birbiriyle iletişim kurabiliyor mu | **Hayır** (sohbet yok, yorum yok) |
| Kullanıcının konumu diğer kullanıcılarla paylaşılıyor mu | **Hayır** |
| Kişisel bilgi paylaşımı | **Hayır** |
| Dijital satın alma | Hayır |
| Reklam gösteriliyor mu | **Evet** |

Beklenen sonuç: **3+ / Herkes**.

## Politika 4.3 (Minimum Functionality) — hazırlıklı ol

Play saf site sarmalayıcılarını reddediyor. İnceleme notuna yazılabilecek somut
maddeler:

- Konum tabanlı en yakın otopark listesi (mesafe hesabı cihazda)
- Adres araması + uygulama içi adım adım Türkçe yol tarifi
- İstanbul için canlı doluluk (İBB Açık Veri), İzmir/Ankara için tarife
- 81 il haritası, 24.460 nokta, çevrimdışı çalışma
- Favoriler, cihazlar arası eşitleme, hesap silme akışı

Red gelirse düzelt ve **hemen** yeniden gönder; bekleme süresi yok.

## Yükleme öncesi son kontrol

```bash
python uret.py && python test_uret.py && python kontrol_favori.py
python kontrol_adres.py && python kontrol.py && python magaza_uret.py
git push          # gizlilik + hesap-sil + app-ads.txt canliya cikmali
```
`/hesap-sil/` canlıda çalışmadan AAB yükleme: form o URL'yi soruyor ve inceleme
fiilen deniyor.
