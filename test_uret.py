# -*- coding: utf-8 -*-
"""Birim testler. Cerceve yok: `python test_uret.py`, hata varsa exit 1."""
import json, sys, os
import uret
from ispark_cek import tarife_ayikla

gecti = basarisiz = 0
def es(ad, olan, beklenen):
    global gecti, basarisiz
    if olan == beklenen: gecti += 1
    else:
        basarisiz += 1
        print(f"  X {ad}\n      beklenen: {beklenen!r}\n      olan     : {olan!r}")

# --- tr_baslik: Python .title() I/i ayrimini bilmez, asil hata buydu
es("tr_baslik KADIKOY",  uret.tr_baslik("KADIKÖY"), "Kadıköy")
es("tr_baslik BAKIRKOY", uret.tr_baslik("BAKIRKÖY"), "Bakırköy")
es("tr_baslik BAGCILAR", uret.tr_baslik("BAĞCILAR"), "Bağcılar")
es("tr_baslik UMRANIYE", uret.tr_baslik("ÜMRANİYE"), "Ümraniye")
es("tr_baslik ISTANBUL", uret.tr_baslik("İSTANBUL"), "İstanbul")
es("tr_baslik SISLI",    uret.tr_baslik("ŞİŞLİ"), "Şişli")
es("tr_baslik iki kelime", uret.tr_baslik("KAPALI OTOPARK"), "Kapalı Otopark")
es("tr_baslik bos",     uret.tr_baslik(""), "")
es("tr_baslik None",    uret.tr_baslik(None), "")

# --- slug: URL guvenli, Turkce karakter cozulmus
es("slug Kadikoy",  uret.slug("KADIKÖY"), "kadikoy")
es("slug Bagcilar", uret.slug("BAĞCILAR"), "bagcilar")
es("slug bosluk",   uret.slug("KÜÇÜK ÇEKMECE"), "kucuk-cekmece")
es("slug bos",      uret.slug(""), "")
es("slug noktalama", uret.slug("Şişli / Mecidiyeköy"), "sisli-mecidiyekoy")

# --- tl bicimlendirme
es("tl binlik", uret.tl(4700), "4.700")
es("tl kucuk",  uret.tl(140), "140")
es("tl None",   uret.tl(None), "—")

# --- tarife ayiklama: gercek ISPARK bicimi
t = tarife_ayikla("0-1 Saat : 110,00;1-2 Saat : 140,00;Tam Gün : 370,00")
es("tarife adet", len(t), 3)
es("tarife ilk aralik", t[0]["aralik"], "0-1 Saat")
es("tarife ilk tl", t[0]["tl"], 110.0)
es("tarife son tl", t[-1]["tl"], 370.0)
es("tarife bos", tarife_ayikla(""), [])
es("tarife None", tarife_ayikla(None), [])
es("tarife bozuk giris", tarife_ayikla("saçma metin"), [])
es("tarife binlik ayraci", tarife_ayikla("Aylık : 1.250,50")[0]["tl"], 1250.50)

# --- veri butunlugu: uretilen site gercek veriyle tutarli mi
if os.path.exists("veri/ispark.json"):
    d = uret.kayitlar()
    es("kayit sayisi 247", len(d), 247)
    es("tarifesiz kayit yok", sum(1 for k in d if not k["tarife"]), 0)
    es("koordinatsiz kayit yok", sum(1 for k in d if not (k["lat"] and k["lng"])), 0)
    es("Istanbul enlem araliginda", all(40.7 < k["lat"] < 41.7 for k in d), True)
    es("Istanbul boylam araliginda", all(27.9 < k["lng"] < 29.9 for k in d), True)
    g = uret.ilce_grupla(d)
    es("ilce sayisi 34", len(g), 34)
    es("her ilcede kayit var", all(v["kayit"] for v in g.values()), True)
    es("slug cakismasi yok", len(g), len({uret.slug(k["ilce"]) for k in d}))

# --- uretilen HTML
if os.path.exists("site/index.html"):
    h = open("site/index.html", encoding="utf-8").read()
    es("index yer tutucu yok", "{" in h.split("<style")[0] and "{ilce" in h, False)
    es("index lisans atifi var", "CC BY 4.0" in h, True)
    es("index bagimsizlik notu var", "Bağımsız uygulamadır" in h, True)
    es("index lang tr", 'lang="tr"' in h, True)
    es("index viewport var", "width=device-width" in h, True)

# --- sehir katmani (Izmir / Ankara)
import sehir_cek as sc
es("anahtar: tip kelimeleri atilir",
   sc.anahtar("KONAK KATLI OTOPARKI"), sc.anahtar("Konak Otopark"))
es("anahtar: I/i Turkce katlama", sc.anahtar("İZMİR"), sc.anahtar("izmir"))
es("anahtar: farkli otopark karismaz",
   sc.anahtar("Bornova Pazaryeri") == sc.anahtar("Konak Pazaryeri"), False)
es("sayi: TR ondalik", sc.sayi("1.250,50"), 1250.5)
es("sayi: bos -> None", sc.sayi(""), None)

for _ad, _yol, _kaynak in [("izmir", "veri/izmir.json", "izelman"),
                           ("ankara", "veri/ankara.json", "anpark")]:
    if os.path.exists(_yol):
        _d = json.load(open(_yol, encoding="utf-8"))
        es(f"{_ad}: kayit var", len(_d) > 0, True)
        es(f"{_ad}: kaynak etiketi", {k["kaynak"] for k in _d}, {_kaynak})
        es(f"{_ad}: koordinat tam", all(k["lat"] and k["lng"] for k in _d), True)
        es(f"{_ad}: ispark ile ayni sema",
           set(_d[0]) >= {"id","ad","lat","lng","ilce","kapasite","tarife","ilk_saat_tl"}, True)
        es(f"{_ad}: canli bos yok (kaynak vermiyor)",
           all(k["bos"] is None for k in _d), True)

es("ankara: tarife yok, uydurulmuyor",
   all(not k["tarife"] and k["ilk_saat_tl"] is None
       for k in json.load(open("veri/ankara.json", encoding="utf-8"))), True)

for _s in ["site/izmir/index.html", "site/ankara/index.html"]:
    if os.path.exists(_s):
        _h = open(_s, encoding="utf-8").read()
        es(f"{_s}: uygulama.js yok", "uygulama.js" in _h, False)
        es(f"{_s}: ISPARK atfi yok", "İSPARK otopark servisi" in _h, False)
        es(f"{_s}: kendi kaynagini atfeder", "Açık Veri" in _h or "ANPARK" in _h, True)

print(f"\n{gecti} gecti, {basarisiz} basarisiz")
sys.exit(1 if basarisiz else 0)
