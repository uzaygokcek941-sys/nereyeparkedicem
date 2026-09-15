# AdMob — reklamdan gelir

## Neden `wv/` diye ikinci bir uygulama var

`twa/` Trusted Web Activity. TWA'da **AdMob gösterilemez**: ekranı baştan sona
Chrome çiziyor, üstüne native `AdView` koyacak bir API yok. Google'ın kendi
deposundaki istek hâlâ açık ve uygulanmamış:
<https://github.com/GoogleChrome/android-browser-helper/issues/535>.

`wv/` bu yüzden var: aynı siteyi bir `WebView`'da açıyor, **altına** banner
koyuyor. Aynı paket adını (`app.vercel.nereyeparkedicem`) taşıyor — Play'de tek
liste olacak, ikisinden **birini** yükleyeceksin.

| | `twa/` (TWA) | `wv/` (WebView + AdMob) |
|---|---|---|
| Reklam | **imkânsız** | banner çalışıyor |
| Açılış | Chrome motoru, hızlı | WebView, biraz yavaş |
| Adres çubuğu | assetlinks doğrulanırsa yok | hiç yok |
| `assetlinks.json` | **şart** | gerekmiyor |
| Play Politika 4.3 riski | orta | **daha yüksek** (saf site sarmalayıcı) |

## Şu an ne var, ne yok

Kodda **Google'ın resmî TEST kimlikleri** duruyor
(`res/values/admob.xml`): test reklamı gösterir, **para kazandırmaz**. Kendi
AdMob hesabın olmadan gerçek kimlik koymak yasak; kendi reklamına tıklamak
sayılır ve hesap kapatılır.

**Asistan AdMob hesabı açamaz** — Google girişi ve ödeme profili gerekiyor.

## Senin adımların

1. <https://admob.google.com> → hesap aç, **ödeme profili** ve vergi bilgisi gir.
2. **Uygulamalar → Uygulama ekle**. "Play'de yayında mı?" → henüz değil.
   Çıkan **Uygulama kimliği** `ca-app-pub-XXXX~YYYY` biçiminde olur.
3. **Reklam birimleri → Banner** oluştur. Kimlik `ca-app-pub-XXXX/ZZZZ`.
4. `wv/app/src/main/res/values/admob.xml` içindeki iki değeri bunlarla değiştir.
   Başka yeri elleme; kimlikler tek yerde duruyor.
5. **app-ads.txt**: AdMob panelinin verdiği satırı sitenin köküne koy
   (`site/app-ads.txt`). Bu dosya olmadan gelirin ciddi biçimde düşer — alıcılar
   doğrulanmamış envanteri istemez. Play listesindeki "Web sitesi" alanı bu alan
   adını göstermeli.
6. **AB kullanıcısı için rıza mesajı**: AdMob → Gizlilik ve mesajlaşma → GDPR.
   Kod tarafı hazır (UMP entegre); mesajı panelde oluşturmazsan AB'de
   kişiselleştirilmiş reklam sunulamaz.

## Emülatörde ölçülen (AVD `np-test`, Android 16 x86_64, 2026-09-15)

| Test | Sonuç |
|---|---|
| `assembleDebug` | başarılı, `app-debug.apk` **6.975.573 bayt** |
| `bundleRelease` (R8 açık) | `BUILD SUCCESSFUL in 2m 59s`, `app-release.aab` **4.544.180 bayt**, imzasız |
| Kurulum + açılış | `Displayed .AnaActivity +23s345ms` (emülatörde ilk soğuk açılış; APK kurulumu sonrası ART derlemesi) |
| Site yükleniyor mu | evet — canlı doluluk **%55** ekranda |
| **Banner** | **görüldü:** "This is a 320x50 test ad", alt sekme çubuğunun altında |
| Uyarlanabilir boy | geniş ekranda kendiliğinden **468x60**'a çıktı |
| Sayfa geçişi | alt sekmeyle Harita'ya geçildi, banner yerinde kaldı |
| Konum izni | Android izin diyaloğu çıktı → verilince site konumu aldı |
| Konumdan arama | **"8 otopark bulundu — en yakını 290 m."** |
| Çökme | `AndroidRuntime` / `FATAL` kaydı yok |

**Test edilmedi, dürüstçe:** balondaki Google Maps / Yandex bağlantısının dışarıda
açılması (emülatörde Play Store ve harita uygulaması yok) ve uygulama içi OSRM yol
tarifinin WebView'da çalışması. İkisi de canlı sitede Chrome'da doğrulandı; WebView
aynı motor ailesi ama **ölçülmedi**.

## Derleme

```bash
cd wv
JAVA_HOME="C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot" \
ANDROID_HOME="D:\dev\android-sdk" ./gradlew.bat assembleDebug   # APK, test icin
JAVA_HOME=... ANDROID_HOME=... ./gradlew.bat bundleRelease      # AAB, Play icin
```
İmzalama `twa/` ile aynı: `keytool` ile yayın anahtarı üret, `jarsigner` ile imzala
(`PLAY-HAZIRLIK.md`).

## Data safety formu — reklam eklenince DEĞİŞİR

Reklam SDK'sı cihaz kimliği topluyor. Formda ek olarak:

- **Cihaz veya diğer kimlikler** → toplanıyor **ve paylaşılıyor**, amaç
  *Reklamcılık veya pazarlama*, **zorunlu** (reklam kapatılamıyor).
- Uygulama listesinde **"Reklam içerir"** işaretlenmeli.
- Konum zaten paylaşılıyor işaretli (yol tarifi → OSRM).

Yanlış doldurmak askıya alma sebebi.

## Dürüst beklenti

Gelir = gösterim × RPM. Türkiye'de banner RPM'i düşük; kaba mertebe 1.000
gösterimde birkaç TL. **Bin kullanıcı yoksa gelir de yok.** Bu dosyadaki iş
reklamı *mümkün* kılar, para getirmez — parayı trafik getirir: Play yayını,
12 test kullanıcısı × 14 gün, ve sitenin SEO trafiği.
