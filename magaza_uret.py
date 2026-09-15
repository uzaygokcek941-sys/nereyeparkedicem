# -*- coding: utf-8 -*-
"""Magaza varliklari: karakter siniri denetimi + basligi uzerinde ekran gorseli.

Iki is yapar, ikisi de Play'in reddettigi/zayiflattigi seyleri onler:

1) magaza/magaza-metni.md icindeki ad / kisa aciklama / tam aciklama bloklarini
   Play'in sinirlarina karsi OLCER (30 / 80 / 4000). Sinir asilirsa exit 1.
2) magaza/ekran-*.png dosyalarinin ustune FAYDA cumlesi basar ->
   magaza/kapak/ekran-*.png. Ham ekran goruntusu yuklemek en sik hata:
   kullanici listede once gorseli goruyor ve cogu kisi ilk ikiden otesini
   kaydirmiyor, o yuzden cumle gorselin UZERINDE olmali.

Calistir: python magaza_uret.py
"""
import io, os, re, sys
from PIL import Image, ImageDraw, ImageFont

KAYNAK = "magaza"
CIKIS = "magaza/kapak"
METIN = "magaza/magaza-metni.md"
VURGU = (11, 61, 46)          # #0B3D2E, sitenin vurgu rengi
BEYAZ = (255, 255, 255)
FONT = r"C:\Windows\Fonts\segoeuib.ttf"

# Ozellik degil FAYDA: "harita var" degil "en yakini saniyede bul".
BASLIK = {
    # Sayfanin kendi h1'ini tekrarlama: ekran goruntusunde zaten yaziyor,
    # ayni cumle iki kez cikinca ozensiz duruyor.
    "ekran-01-ana.png":       "81 ilde 24.460 otopark,\ncebinde",
    "ekran-02-harita.png":    "81 ilin tamamı\ntek haritada",
    "ekran-03-ilce.png":      "İstanbul'da canlı doluluk\nve gerçek tarife",
    "ekran-04-ucretsiz.png":  "Ücretsiz otoparkları\ntek dokunuşla süz",
    "ekran-05-favoriler.png": "Favorilerin bütün\ncihazlarında",
    "ekran-06-fiyat.png":     "Hangi ilçe ucuz,\ntablo söylüyor",
}
SINIR = [("Uygulama adı", 30), ("Kısa açıklama", 80), ("Tam açıklama", 4000)]

hata = []

def bloklar():
    """magaza-metni.md'deki ``` bloklarini basliklariyla eslestirir."""
    s = io.open(METIN, encoding="utf-8").read()
    d = {}
    for baslik, govde in re.findall(r"^## ([^\n(]+?)\s*(?:\(|$)[^\n]*\n+```\n(.*?)\n```",
                                    s, re.S | re.M):
        d[baslik.strip()] = govde
    return d

def metin_olc():
    d = bloklar()
    for ad, sinir in SINIR:
        if ad not in d:
            hata.append(f"{ad}: blok bulunamadi")
            continue
        n = len(d[ad])
        ok = n <= sinir
        print(f"  {'OK ' if ok else 'X  '} {ad}: {n}/{sinir} karakter")
        if not ok:
            hata.append(f"{ad} {n} > {sinir}")

def kapak_uret():
    os.makedirs(CIKIS, exist_ok=True)
    for ad, yazi in BASLIK.items():
        yol = f"{KAYNAK}/{ad}"
        if not os.path.exists(yol):
            hata.append(f"{yol} yok")
            continue
        kaynak = Image.open(yol).convert("RGB")
        G, Y = 1080, 1920                      # Play ekran goruntusu olcusu
        tuval = Image.new("RGB", (G, Y), VURGU)
        ciz = ImageDraw.Draw(tuval)

        # Baslik alani: iki satira sigacak punto, tasarsa kucult.
        punto = 74
        while punto > 40:
            f = ImageFont.truetype(FONT, punto)
            en = max(ciz.textbbox((0, 0), s, font=f)[2] for s in yazi.split("\n"))
            if en <= G - 150:
                break
            punto -= 4
        f = ImageFont.truetype(FONT, punto)
        TEPE, BOSLUK = 112, 46
        ciz.multiline_text((G // 2, TEPE), yazi, font=f, fill=BEYAZ,
                           anchor="ma", align="center", spacing=14)

        # OLCULDU: sabit 268 px ust bant iki satirlik basligi kesiyordu -
        # ekran goruntusu ikinci satirin uzerine biniyordu. Bant artik
        # yazinin GERCEK yuksekliginden hesaplaniyor.
        alt_kenar = ciz.multiline_textbbox((G // 2, TEPE), yazi, font=f,
                                           anchor="ma", align="center", spacing=14)[3]
        ust = int(alt_kenar) + BOSLUK
        yeni_g = min(936, G - 96)
        yeni_y = round(kaynak.height * yeni_g / kaynak.width)
        if ust + yeni_y > Y:                   # sigmazsa yuksekligi tabana oturt
            yeni_y = Y - ust
            yeni_g = round(kaynak.width * yeni_y / kaynak.height)
        k = kaynak.resize((yeni_g, yeni_y), Image.LANCZOS)
        tuval.paste(k, ((G - yeni_g) // 2, ust))

        cikti = f"{CIKIS}/{ad}"
        tuval.save(cikti, "PNG", optimize=True)
        print(f"  OK  {cikti} {tuval.size} {os.path.getsize(cikti)} bayt")

if __name__ == "__main__":
    print("=== karakter sinirlari ===")
    metin_olc()
    print("=== kapakli ekran goruntuleri ===")
    kapak_uret()
    print("\nMAGAZA: " + (", ".join(hata) if hata else "hepsi gecti"))
    sys.exit(1 if hata else 0)
