/* Service worker kaydi. Ayri dosya, cunku CSP script-src 'self' - satir ici
   betik engelli. uygulama.js yalniz Istanbul sayfalarinda yuklendigi icin
   kayit oraya konamaz; bu dosya HER sayfada var. */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("/sw.js").catch(function (e) {
      // SW kaydedilemezse site cevrimici calismaya devam eder
      console.warn("service worker kaydedilemedi:", e && e.message);
    });
  });
}
