package app.vercel.nereyeparkedicem;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.webkit.GeolocationPermissions;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;

import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.MobileAds;
import com.google.android.ump.ConsentInformation;
import com.google.android.ump.ConsentRequestParameters;
import com.google.android.ump.UserMessagingPlatform;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Site + alt banner. TWA yerine WebView kullanmamizin TEK sebebi bu banner:
 * TWA tam ekran Chrome cizdigi icin uzerine native reklam konamiyor
 * (android-browser-helper #535 hala acik). Bedeli: Chrome'un kendi
 * guncellemeleri, install banner'i ve site ayarlari kisayolu yok.
 */
public class AnaActivity extends android.app.Activity {

    private static final int KONUM_ISTEK = 41;
    private WebView web;
    private AdView banner;
    private GeolocationPermissions.Callback konumCevap;
    private String konumKaynak;
    // Mobile Ads yalniz BIR kez baslatilir: riza geri cagrisi iki daldan da
    // gelebiliyor, ikisi birden dusarse banner iki kez eklenirdi.
    private final AtomicBoolean reklamKuruldu = new AtomicBoolean(false);

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.ana);

        web = findViewById(R.id.web);
        webKur();
        web.loadUrl(getString(R.string.baslangic_url));

        rizaSor();
    }

    private void webKur() {
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);        // favoriler localStorage'da duruyor
        s.setGeolocationEnabled(true);
        s.setSupportMultipleWindows(false);  // target=_blank ayni pencereye duser,
                                             // asagidaki dis-baglanti dali yakalar
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setMediaPlaybackRequiresUserGesture(true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if (u.getHost() != null && u.getHost().equals(getString(R.string.konak)))
                    return false;
                // Google Maps / Yandex / OSM baglantilari: uygulamanin icinde
                // acilirsa kullanici geri donemiyor. Disariya ver.
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (android.content.ActivityNotFoundException e) {
                    Toast.makeText(AnaActivity.this, R.string.cevrimdisi,
                            Toast.LENGTH_SHORT).show();
                }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String kaynak,
                                                           GeolocationPermissions.Callback cb) {
                // Iki katmanli izin: once Android'in kendi izni, sonra sayfaya
                // izin. Ilkini atlarsan sayfa izin aldigini saniyor ama konum
                // hic gelmiyor - sessiz hata.
                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                        == PackageManager.PERMISSION_GRANTED) {
                    cb.invoke(kaynak, true, false);
                    return;
                }
                konumKaynak = kaynak;
                konumCevap = cb;
                requestPermissions(new String[]{
                        Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.ACCESS_COARSE_LOCATION}, KONUM_ISTEK);
            }
        });
    }

    @Override
    public void onRequestPermissionsResult(int kod, String[] izin, int[] sonuc) {
        super.onRequestPermissionsResult(kod, izin, sonuc);
        if (kod != KONUM_ISTEK || konumCevap == null) return;
        boolean ok = sonuc.length > 0 && sonuc[0] == PackageManager.PERMISSION_GRANTED;
        konumCevap.invoke(konumKaynak, ok, false);
        konumCevap = null;
        konumKaynak = null;
    }

    /**
     * AB/UK kullanicisi icin riza formu (UMP). Turkiye'de form gerekmiyor ve
     * SDK sessizce "gerekli degil" donuyor - kod her yerde ayni, davranis
     * kullanicinin bolgesine gore degisiyor. Reklam SDK'si riza sonucu belli
     * olunca baslatilir.
     */
    private void rizaSor() {
        ConsentInformation ci = UserMessagingPlatform.getConsentInformation(this);
        ci.requestConsentInfoUpdate(this, new ConsentRequestParameters.Builder().build(),
                () -> UserMessagingPlatform.loadAndShowConsentFormIfRequired(this,
                        hata -> reklamBaslat()),
                hata -> reklamBaslat());   // riza servisine ulasilamadi: reklam
                                           // yine de yuklenir, kisisellestirilmemis
    }

    private void reklamBaslat() {
        if (!reklamKuruldu.compareAndSet(false, true)) return;
        MobileAds.initialize(this, durum -> { });
        banner = new AdView(this);
        banner.setAdUnitId(getString(R.string.admob_banner_id));
        banner.setAdSize(uyarlanabilirBoy());
        ((FrameLayout) findViewById(R.id.reklam_kap)).addView(banner);
        banner.loadAd(new AdRequest.Builder().build());
    }

    /** Sabit 320x50 yerine ekran genisligine oturan banner: ayni yerde daha
     *  buyuk gosterim, daha iyi doluluk. */
    private AdSize uyarlanabilirBoy() {
        DisplayMetrics m = getResources().getDisplayMetrics();
        int genislikDp = (int) (m.widthPixels / m.density);
        return AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(this, genislikDp);
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    @Override protected void onPause() { if (banner != null) banner.pause(); super.onPause(); }
    @Override protected void onResume() { super.onResume(); if (banner != null) banner.resume(); }

    @Override
    protected void onDestroy() {
        if (banner != null) banner.destroy();
        super.onDestroy();
    }
}
