# Google Play yayın hazırlığı

Durum: **TWA paketi çalışıyor ve emülatörde doğrulandı.** Kalan adımlar hesap,
imza ve mağaza formları — hepsi Uzay'ın yapması gereken adımlar.

## Emülatörde ölçülen (2026-09-15)

Cihaz: AVD `np-test`, Android 16, `google_apis_playstore` x86_64 (Chrome + Play Store içerir).
APK: `twa/app-release-signed.apk`, 1.028.878 bayt, `app.vercel.nereyeparkedicem`,
versionName 1.0.0, minSdk 21, targetSdk 36.

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

## Sende kalan adımlar

1. **Play Console hesabı** — 25 $ tek seferlik + kimlik doğrulama.
2. **Yayın imza anahtarı üret.** Depodaki `twa/test-anahtar.keystore` yalnız
   emülatör içindir, `.gitignore`'da ve **yayında kullanılmaz**.
   ```
   keytool -genkeypair -v -keystore yayin.keystore -alias yayin \
     -keyalg RSA -keysize 2048 -validity 10000
   ```
   Bu dosyayı ve parolasını kaybedersen uygulamayı bir daha güncelleyemezsin.
3. **`assetlinks.json`'u değiştir.** `site/.well-known/assetlinks.json` şu an
   TEST anahtarının parmak izini taşıyor. Play App Signing kullanacaksan
   Play Console → Uygulama bütünlüğü → SHA-256 parmak izini oradan al ve yaz.
   Birden çok parmak izi aynı dosyada listelenebilir.
4. **AAB üret** (Play, APK değil AAB ister):
   ```
   cd twa && bubblewrap build
   ```
   `twa-manifest.json` içindeki `signingKey` alanını yayın anahtarına çevir.
5. **Kapalı test:** yeni kişisel geliştirici hesaplarında **12 test kullanıcısı,
   14 gün** sürekli kullanım şartı var. Yayın tarihini belirleyen madde budur.
6. **Mağaza formları:** Data safety (veri güvenliği), içerik derecelendirme,
   hedef kitle, gizlilik politikası URL'i (`https://nereyeparkedicem.vercel.app/gizlilik/`).
   **Data safety hesap özelliğine bağlı:** giriş `site/veri/auth.json` yer tutucu
   iken uygulama hiçbir kişisel veri toplamaz. `SUPABASE-KURULUM.md` adımları
   uygulanıp giriş açılırsa formda **E-posta adresi** ve **Uygulama içi etkinlik**
   (favori listesi) beyan edilmeli, "veri şifreli aktarılıyor" ve "kullanıcı silme
   talep edebilir" işaretlenmeli. Formu yanlış doldurmak Play'de askıya alma sebebi.
7. **Görseller:** 512×512 uygulama ikonu (`site/simge-512.png` kullanılabilir),
   1024×500 feature graphic, en az 2 telefon ekran görüntüsü.

## Dürüst risk: Politika 4.3 (Minimum Functionality)

Play, yalnızca bir siteyi saran paketleri reddediyor. Bizim lehimize olanlar:
konum tabanlı en yakın otopark, 81 il haritası, çevrimdışı çalışma, ücretsiz
otopark filtresi. Yine de red gelirse ilk bakılacak yer burasıdır; red sonrası
bekleme süresi yok, düzeltip hemen yeniden gönderilebilir.

## Yeniden derleme

```
cd twa
bubblewrap update --skipVersionUpgrade --appVersionName=1.0.0
./gradlew.bat assembleRelease            # bubblewrap'in kendi cagrisi gradlew'u bulamiyor
zipalign -p -f 4 app/build/outputs/apk/release/app-release-unsigned.apk app-release-signed.apk
apksigner sign --ks <anahtar> --ks-key-alias <alias> app-release-signed.apk
```

Araç yolları: JDK 17 `C:\Program Files\Microsoft\jdk-17.0.19.10-hotspot`,
Android SDK `D:\dev\android-sdk`, Bubblewrap `D:\apps\bubblewrap\bubblewrap.cmd`,
AVD `D:\dev\avd`.

**Not:** Bubblewrap SDK kökünde `bin/` klasörü arıyor (eski düzen);
`D:\dev\android-sdk\bin` bir junction olarak `cmdline-tools\latest\bin`'e bağlandı.
Ayrıca build-tools **36.1.0** şart (36.0.0 yetmiyor).
