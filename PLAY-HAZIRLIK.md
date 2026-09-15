# Google Play yayın hazırlığı

> **İki sarmalayıcı var, birini seçeceksin.** `twa/` = Trusted Web Activity
> (reklamsız, hızlı, `assetlinks.json` şart). `wv/` = WebView + AdMob banner
> (reklam gelirinin tek yolu, Politika 4.3 riski daha yüksek). Paket adı ikisinde
> de aynı: `app.vercel.nereyeparkedicem` — Play'e **yalnız biri** yüklenir.
> Ayrıntı ve AdMob adımları: `ADMOB-KURULUM.md`.

> **Adım adım ne yapılacağı ve bütün Play Console form cevapları
> `PLAY-FORM.md` dosyasında.** Burası teknik durum tablosu.

Durum: **kod, paket, mağaza metinleri ve görselleri hazır.** Kalanlar: iki
Supabase SQL'i, AdMob kimlikleri, imza anahtarı ve 12 tester — hepsi Uzay'ın
adımı; asistan hesap açamaz, parola belirleyemez.

## Hazır olanlar (ölçüldü, 2026-09-15)

| | Durum |
|---|---|
| **AAB derlemesi** | `twa/app/build/outputs/bundle/release/app-release.aab` · **1.103.253 bayt** · `BUILD SUCCESSFUL in 3m 2s` · **imzasız** (imza yayın anahtarıyla atılacak) |
| AAB içeriği | 476 dosya · `BundleConfig.pb`, `base/dex/classes.dex`, `base/resources.pb` var · paket `app.vercel.nereyeparkedicem` · host `nereyeparkedicem.vercel.app` (`resources.pb` içinde) |
| İmzalı APK (emülatör testi) | `twa/app-release-signed.apk` 1.028.878 bayt — **yalnız test anahtarıyla**, Play'e gitmez |
| **Ekran görüntüleri** | `magaza/ekran-0*.png` · **6 adet, 1080×1920** (Play şartı: ≥2 adet, 320–3840 px) — gerçek canlı uygulamadan |
| **Feature graphic** | `magaza/feature-graphic-1024x500.png` — rakamlar `site/veri/iller.json`'dan, uydurma yok |
| Uygulama ikonu 512×512 | `site/simge-512.png` |
| Gizlilik politikası URL | `https://nereyeparkedicem.vercel.app/gizlilik/` (HTTP 200) |
| `.well-known/assetlinks.json` | canlıda **HTTP 200** — ama parmak izi **TEST anahtarının**, aşağıya bak |
| Mock / TODO / placeholder | kaynak taraması **temiz**; `console.log` yok, doldurulmamış yer tutucu yok |
| Otomatik kontroller | `test_uret.py` 133/133 · `kontrol.py` 15 sayfa × 3 genişlik **HATA 0** · `kontrol_favori.py` hepsi geçti |

## Emülatörde ölçülen (AVD `np-test`, Android 16, `google_apis_playstore` x86_64)

| Test | Sonuç |
|---|---|
| Kurulum | `Success` |
| Başlatma | `LauncherActivity` → `TranslucentCustomTabActivity` |
| **Digital Asset Links** | **geçti — URL çubuğu YOK** (doğrulama başarısız olsaydı adres çubuklu Custom Tab açılırdı) |
| Tema rengi | durum çubuğu `#0b3d2e` |
| Canlı veri | İstanbul doluluk %56 (İBB API uygulama içinden çalışıyor) |
| Konum | emülatör Ankara'ya sabitlendi → en yakın otopark **Ankara 0,4 km** |
| Harita | fayanslar + il balonları render oldu |
| **Çevrimdışı, önbellekte olmayan sayfa** | kendi "Bağlantı yok" sayfamız — **çökme yok** |
| **Çevrimdışı, önbellekteki sayfa** | ana sayfa tam açıldı, İstanbul doluluk `—` (eski sayı canlı gibi gösterilmiyor) |
| Çökme / ANR | crash tamponu boş |

**Not:** bu ölçüm hesap sistemi eklenmeden önceki APK ile yapıldı. Web içeriği
TWA'ya canlı siteden geldiği için yeni arayüz ve giriş ekranı **yeniden derleme
gerektirmeden** görünür; yine de yayın APK'sı üretildikten sonra emülatör testi
tekrarlanmalı.

## ⛔ Tek gerçek bloke: imza zinciri

`site/.well-known/assetlinks.json` şu an **test anahtarının** parmak izini taşıyor:
`C4:B8:90:...:2C:A8`. Yayında bu **geçersiz** olur ve TWA adres çubuklu açılır —
yani uygulama "tarayıcı görünümüne" düşer.

**Sıralama kaçınılmaz: parmak izini önceden bilmek mümkün değil.**

1. Play Console hesabı aç (**25 $** tek seferlik + kimlik doğrulama).
2. **Yükleme (upload) anahtarı üret** — parola sende kalır, asistan parola belirleyemez:
   ```
   keytool -genkeypair -v -keystore yayin.keystore -alias yayin \
     -keyalg RSA -keysize 2048 -validity 10000
   ```
   **Bu dosyayı ve parolasını kaybedersen uygulamayı bir daha güncelleyemezsin.**
3. AAB'yi bu anahtarla imzala (`twa-manifest.json` → `signingKey` yayın anahtarına):
   ```
   cd twa
   bubblewrap update --skipVersionUpgrade --appVersionName=1.0.0
   ./gradlew.bat bundleRelease            # bubblewrap'in kendi cagrisi gradlew'u bulamiyor
   jarsigner -keystore yayin.keystore \
     app/build/outputs/bundle/release/app-release.aab yayin
   ```
4. AAB'yi Play Console'a yükle. **Play App Signing** açıksa Google kendi imza
   anahtarını üretir.
5. **Play Console → Uygulama bütünlüğü → App signing key certificate → SHA-256**
   değerini al, `site/.well-known/assetlinks.json` içindeki test parmak izinin
   yerine yaz. Aynı dosyada birden çok parmak izi listelenebilir — upload
   anahtarınınkini de eklersen yerel derlemen de doğrulanmaya devam eder.
6. `git push` → Vercel deploy → **sonra** uygulamayı test et. Assetlinks canlıda
   güncellenmeden TWA doğrulaması geçmez.

## Data safety formu — giriş AÇILDI, buna göre doldur

Hesap sistemi **canlı**: `site/veri/auth.json` gerçek Supabase projesi taşıyor,
`public.favoriler` tablosu kurulu, RLS ölçülerek doğrulandı (anon INSERT → 401).
Artık "veri toplamıyor" beyanı **yanlış** olur. Formda:

- **Kişisel bilgiler → E-posta adresleri**: toplanıyor, hesap yönetimi amaçlı,
  **isteğe bağlı** (giriş yapmadan uygulama tam çalışır).
- **Uygulama etkinliği → Uygulama içi etkinlik**: favori otopark listesi,
  uygulama işlevselliği amaçlı, isteğe bağlı.
- **Konum**: *toplanmıyor* — ama **paylaşılıyor** işaretlenmeli. Mesafe hesabı
  cihazda yapılıyor ve konum bize hiç gelmiyor; **fakat kullanıcı "Yol tarifi"ne
  bastığında başlangıç/varış koordinatı OSRM sunucusuna (üçüncü taraf) gidiyor.**
  Formda: Konum → *Yaklaşık konum* → **paylaşılıyor**, amaç *Uygulama
  işlevselliği*, **isteğe bağlı** (düğmeye basılmazsa hiç gönderilmez).
  Aynı şekilde adres arama kutusuna yazılan metin Nominatim'e gider — bu kişisel
  veri kategorisi değil ama gizlilik sayfasında adıyla yazılı.
- "Veri aktarımda şifreleniyor" → **evet** (HTTPS + Supabase).
- "Kullanıcı silme talep edebilir" → **evet** (tablo `on delete cascade`).

Formu yanlış doldurmak Play'de askıya alma sebebi; gizlilik sayfasıyla birebir
tutarlı olmalı.

## Kalan mağaza adımları

- İçerik derecelendirme anketi, hedef kitle ve içerik beyanı.
- **Kapalı test: 12 test kullanıcısı × 14 gün** kesintisiz. Yeni kişisel
  geliştirici hesaplarında zorunlu — **yayın tarihini belirleyen madde budur**,
  kodla kısaltılamaz.
- Mağaza açıklaması (kısa 80 karakter + tam 4000 karakter).

## Dürüst risk: Politika 4.3 (Minimum Functionality)

Play, yalnızca bir siteyi saran paketleri reddediyor. Lehimize olanlar: konum
tabanlı en yakın otopark, 81 il haritası, çevrimdışı çalışma, ücretsiz filtre,
favori sistemi ve hesap senkronu. Yine de garanti değil; red gelirse ilk
bakılacak yer burasıdır. Red sonrası bekleme süresi yok, düzeltip hemen
yeniden gönderilebilir.

## Araç yolları

JDK 17 `C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot` ·
Android SDK `D:\dev\android-sdk` · Bubblewrap `D:\apps\bubblewrap\bubblewrap.cmd` ·
AVD `D:\dev\avd`.

**Bubblewrap tuzakları:** SDK kökünde `bin/` klasörü arıyor (eski düzen),
`D:\dev\android-sdk\bin` junction olarak `cmdline-tools\latest\bin`'e bağlandı.
build-tools **36.1.0** şart (36.0.0 yetmiyor). `twa-manifest.json` kısayol alanı
`shortName` olmalı, `short_name` değil. `bubblewrap build` kendi `gradlew.bat`
çağrısını bulamıyor — doğrudan `./gradlew.bat` çalıştır.
