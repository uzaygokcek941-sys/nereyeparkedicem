# Play Console — mağaza metinleri

Rakamlar `site/veri/iller.json`'dan; uydurma sayı yok. Karakter sınırları
`magaza_uret.py` ile ölçülür.

---

## Uygulama adı (≤30 karakter)

```
nereyeparkedicem — Otopark
```

## Kısa açıklama (≤80 karakter) — listede başlığın altında çıkar

```
81 ilde 24.460 otopark. En yakınını bul, ücretsizleri süz, yol tarifini al.
```

## Tam açıklama (≤4000 karakter)

```
Arabayı nereye bırakacağını düşünmekle geçen dakikalar bitsin.

nereyeparkedicem, Türkiye'nin 81 ilindeki 24.460 otopark noktasını tek haritada
toplar. Konumunu aç, en yakın otoparkı saniyeler içinde gör; ya da adresi yaz,
o adresin çevresindeki otoparklar mesafeye göre sıralansın.

NE YAPAR

• En yakın otoparkı bulur — konumuna göre sıralı liste, mesafesiyle birlikte.
• Adres araması — "Kadıköy İstanbul" yaz, çevredeki otoparkları gör.
• Uygulama içinde yol tarifi — seçtiğin otoparka rota haritaya çizilir,
  adımlar Türkçe olarak sayfada listelenir. Başka uygulamaya geçmene gerek yok.
• İstanbul'da CANLI DOLULUK — İBB Açık Veri Portalı'ndan gelen anlık boş yer
  sayısı ve gerçek tarife. Dolu otoparka boşuna gitme.
• İzmir'de tarife — İzmir Büyükşehir verisiyle saatlik ücretler.
• Ücretsiz otoparklar — 1.857 nokta, tek dokunuşla süzülür.
• Favoriler — sık gittiğin otoparkları yıldızla. Hesap açarsan bütün
  cihazlarında görünür; açmazsan cihazında kalır ve yine çalışır.
• Fiyat endeksi — hangi ilçe ucuz, tablo söylüyor.
• İnternet kesilse bile daha önce açtığın sayfalar açılır.

VERİ NEREDEN GELİYOR

Otopark noktaları OpenStreetMap topluluğunun girdiği açık veridir (ODbL).
Dürüst olalım: OSM noktalarının çoğunda fiyat ve çalışma saati bilgisi YOK,
bu yüzden ücret ve saat çoğu noktada boş görünür. İstanbul, İzmir ve Ankara
için belediye açık verisiyle kurulmuş ayrıntılı sayfalar ayrıca vardır.
Canlı doluluk yalnız İstanbul'da, İBB'nin yayınladığı otoparklar için geçerlidir.

KONUM VE GİZLİLİK

Konumun cihazında kalır; mesafe hesabı telefonda yapılır, bize gönderilmez.
Tek istisna senin başlattığın yol tarifidir: rotayı hesaplayabilmek için
başlangıç ve varış koordinatı rota sunucusuna gider. Düğmeye basmazsan bu
istek hiç olmaz. Konum izni vermek zorunda değilsin — il ve ilçe listesinden
de gezebilirsin.

Uygulama ücretsizdir ve alt kısmında reklam gösterir.

Gizlilik politikası: https://nereyeparkedicem.vercel.app/gizlilik/

Bağımsız bir uygulamadır; hiçbir belediyenin, otopark işletmecisinin veya
OpenStreetMap Vakfı'nın resmî uygulaması değildir.
```

## Kategori ve sınıflandırma

| Alan | Değer |
|---|---|
| Uygulama türü | Uygulama (Oyun değil) |
| Kategori | **Haritalar ve Navigasyon** |
| Etiketler | otopark, park yeri, navigasyon, harita, ücretsiz otopark |
| Hedef kitle yaşı | **18 ve üzeri** (Families politikasının ek yükünü açmamak için) |
| Çocuklara yönelik mi | **Hayır** |
| Reklam içerir | **Evet** |
| Ücretli mi | Hayır — ücretsiz, uygulama içi satın alma yok |
| Gizlilik politikası URL | `https://nereyeparkedicem.vercel.app/gizlilik/` |
| İletişim e-postası | **[SENİN E-POSTAN — Play'de herkese açık görünür]** |
| Web sitesi | `https://nereyeparkedicem.vercel.app` |

## ASO — anahtar kelimeler metne gömülü

Play'de ayrı anahtar kelime alanı yoktur; başlık, kısa açıklama ve tam
açıklamadaki kelimeler taranır. Yukarıdaki metinde geçenler:
**otopark, park yeri, en yakın otopark, ücretsiz otopark, otopark ücreti,
otopark doluluk, İstanbul otopark, İzmir otopark, Ankara otopark, yol tarifi,
harita, tarife**.

Başlıktaki "Otopark" kelimesi en ağırlıklı sinyaldir; değiştirme.

## 12 tester'a gönderilecek davet metni

```
Selam, bir otopark uygulaması yaptım: 81 ildeki 24.460 otoparkı tek haritada
gösteriyor, İstanbul'da anlık boş yer sayısını da veriyor.

Google Play'de yayınlayabilmem için 12 kişinin 14 gün boyunca test grubunda
kayıtlı kalması gerekiyor — Google'ın kuralı. Senden istediğim tek şey: aşağıdaki
bağlantıdan test grubuna katıl, uygulamayı bir kez kur ve telefonunda bırak.
Kullanmak zorunda değilsin; kullanır da bozuk bir şey görürsen bana yaz.

Kurulum bağlantısı: [PLAY CONSOLE'UN VERDİĞİ OPT-IN LİNKİ]

Önemli: 14 gün dolmadan gruptan çıkma, sayaç sıfırlanıyor.
```

**Uyarı:** tester sayısı 14 gün boyunca **kesintisiz** 12'nin altına düşmemeli;
biri çıkarsa sayaç sıfırlanır. 12 değil **14-15 kişi** davet et.
