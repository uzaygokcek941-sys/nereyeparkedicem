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

def kapakla(kaynak, yazi, G, Y):
    """Ekran goruntusunun ustune fayda cumlesi basar, {G}x{Y} tuval dondurur."""
    tuval = Image.new("RGB", (G, Y), VURGU)
    ciz = ImageDraw.Draw(tuval)
    punto = int(G * 0.069)
    while punto > 24:
        f = ImageFont.truetype(FONT, punto)
        en = max(ciz.textbbox((0, 0), x, font=f)[2] for x in yazi.splitlines())
        if en <= G - int(G * 0.14):
            break
        punto -= 4
    f = ImageFont.truetype(FONT, punto)
    TEPE, BOSLUK = int(Y * 0.058), int(Y * 0.024)
    ciz.multiline_text((G // 2, TEPE), yazi, font=f, fill=BEYAZ,
                       anchor="ma", align="center", spacing=14)
    # OLCULDU: sabit ust bant iki satirlik basligi kesiyordu - bant artik
    # yazinin GERCEK yuksekliginden hesaplaniyor.
    alt = ciz.multiline_textbbox((G // 2, TEPE), yazi, font=f, anchor="ma",
                                 align="center", spacing=14)[3]
    ust = int(alt) + BOSLUK
    yeni_g = G - int(G * 0.089)
    yeni_y = round(kaynak.height * yeni_g / kaynak.width)
    if ust + yeni_y > Y:
        yeni_y = Y - ust
        yeni_g = round(kaynak.width * yeni_y / kaynak.height)
    tuval.paste(kaynak.resize((yeni_g, yeni_y), Image.LANCZOS), ((G - yeni_g) // 2, ust))
    return tuval

def kapak_uret():
    os.makedirs(CIKIS, exist_ok=True)
    for ad, yazi in BASLIK.items():
        yol = f"{KAYNAK}/{ad}"
        if not os.path.exists(yol):
            hata.append(f"{yol} yok")
            continue
        t = kapakla(Image.open(yol).convert("RGB"), yazi, 1080, 1920)
        cikti = f"{CIKIS}/{ad}"
        t.save(cikti, "PNG", optimize=True)
        print(f"  OK  {cikti} {t.size} {os.path.getsize(cikti)} bayt")


# --- tablet ekran goruntuleri + tanitim videosu ---
TABLET = "magaza/tablet"
VIDEO = "magaza/tanitim-9x16.mp4"
# Play: tablet icin ayri gorsel istiyor. 1600x2560 oran 10:16 - izin verilen
# 9:16 ile 16:9 araliginda.
TABLET_SAYFA = [
    ("tablet-01-ana.png", "/", "81 ilde 24.460 otopark,\ncebinde"),
    ("tablet-02-harita.png", "/harita/", "81 ilin tamamı\ntek haritada"),
    ("tablet-03-ilce.png", "/ilce/kadikoy/", "İstanbul'da canlı doluluk\nve gerçek tarife"),
    ("tablet-04-ucretsiz.png", "/ucretsiz-otopark/", "Ücretsiz otoparkları\ntek dokunuşla süz"),
]

def tablet_cek(taban="https://nereyeparkedicem.vercel.app"):
    """Canli siteden tablet genisliginde cekim. Uydurma mockup degil, gercek sayfa."""
    from playwright.sync_api import sync_playwright
    os.makedirs(TABLET, exist_ok=True)
    with sync_playwright() as pw:
        t = pw.chromium.launch()
        s = t.new_context(viewport={"width": 800, "height": 1280},
                          device_scale_factor=2, locale="tr-TR")
        p = s.new_page()
        for ad, yol, yazi in TABLET_SAYFA:
            p.goto(taban + yol, wait_until="networkidle")
            p.wait_for_timeout(2500)
            ham = f"{TABLET}/_ham.png"
            p.screenshot(path=ham)
            k = kapakla(Image.open(ham).convert("RGB"), yazi, 1600, 2560)
            cikti = f"{TABLET}/{ad}"
            k.save(cikti, "PNG", optimize=True)
            print(f"  OK  {cikti} {k.size} {os.path.getsize(cikti)} bayt")
        os.remove(f"{TABLET}/_ham.png")
        t.close()

def video_uret(sure=3.4, gecis=0.5):
    """Kapakli gorsellerden 9:16 tanitim videosu. Ses YOK - uydurma muzik
    eklemiyoruz; Play tanitim videosu YouTube baglantisi olarak veriliyor,
    bu dosya ayrica sosyal medyada kullanilabilir."""
    import subprocess
    kare = [f"{CIKIS}/{a}" for a in BASLIK if os.path.exists(f"{CIKIS}/{a}")]
    if len(kare) < 2:
        hata.append("video: yeterli kapak yok")
        return
    d = int(sure * 25)
    girdi, suz = [], []
    for i, k in enumerate(kare):
        # OLCULDU: "-loop 1 -t" ile beslenince zoompan HER GIRIS KARESI icin d
        # kare uretiyor (85x85=7225 kare, 303 sn). Tek kare ver, sureyi zoompan
        # kendi d degeriyle olustursun.
        girdi += ["-i", k]
        suz.append(f"[{i}:v]scale=1080:1920,zoompan=z='min(zoom+0.0009,1.12)'"
                   f":d={d}:s=1080x1920:fps=25,setsar=1[v{i}]")
    onceki, ofset = "v0", sure - gecis
    for i in range(1, len(kare)):
        cikis = f"x{i}"
        suz.append(f"[{onceki}][v{i}]xfade=transition=fade:duration={gecis}"
                   f":offset={ofset:.2f}[{cikis}]")
        onceki, ofset = cikis, ofset + sure - gecis
    komut = ["ffmpeg", "-y", *girdi, "-filter_complex", ";".join(suz),
             "-map", f"[{onceki}]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-r", "25", "-preset", "fast", "-crf", "23", VIDEO]
    r = subprocess.run(komut, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(VIDEO):
        hata.append("video uretilemedi")
        print(r.stderr[-600:])
        return
    bek = len(kare) * sure - (len(kare) - 1) * gecis
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", VIDEO], capture_output=True, text=True)
    olculen = float(o.stdout.strip() or 0)
    ok = abs(olculen - bek) < 1.5
    if not ok:
        hata.append(f"video suresi {olculen:.1f}s, beklenen {bek:.1f}s")
    print(f"  {'OK ' if ok else 'X  '} {VIDEO} {os.path.getsize(VIDEO)} bayt · "
          f"{olculen:.1f} sn (beklenen {bek:.1f})")

if __name__ == "__main__":
    print("=== karakter sinirlari ===")
    metin_olc()
    print("=== kapakli ekran goruntuleri ===")
    kapak_uret()
    if "--tablet" in sys.argv:
        print("=== tablet (canli siteden) ===")
        tablet_cek()
    if "--video" in sys.argv:
        print("=== tanitim videosu ===")
        video_uret()
    print("\nMAGAZA: " + (", ".join(hata) if hata else "hepsi gecti"))
    sys.exit(1 if hata else 0)
