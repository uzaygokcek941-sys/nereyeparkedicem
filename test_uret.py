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


# --- denetimde bulunan eksikler: canonical, ikon/manifest, il sayfalari ---
_ana = "site/index.html"
if os.path.exists(_ana):
    _h = open(_ana, encoding="utf-8").read()
    es("ana sayfa canonical", 'rel="canonical"' in _h, True)
    es("ana sayfa ld+json WebSite", '"WebSite"' in _h, True)
    es("ana sayfa manifest", 'rel="manifest"' in _h, True)
    es("ana sayfa theme-color", 'name="theme-color"' in _h, True)
    es("ana sayfa baslik <=60",
       len(_h.split("<title>")[1].split("</title>")[0]) <= 60, True)

for _f in ("site/simge.svg", "site/simge-192.png", "site/simge-512.png",
           "site/manifest.json"):
    es(f"{_f} var", os.path.exists(_f), True)

if os.path.exists("site/manifest.json"):
    _m = json.load(open("site/manifest.json", encoding="utf-8"))
    es("manifest start_url", _m["start_url"], "/")
    es("manifest ikon sayisi >=2", len(_m["icons"]) >= 2, True)

if os.path.exists("site/veri/iller.json"):
    _o = json.load(open("site/veri/iller.json", encoding="utf-8"))
    _eksik = [x["ad"] for x in _o["iller"]
              if not os.path.exists(f'site/il/{uret.slug(x["ad"])}/index.html')]
    es("il sayfasi eksigi", _eksik, [])
    es("il dizini var", os.path.exists("site/il/index.html"), True)
    es("ucretsiz sayfasi var", os.path.exists("site/ucretsiz-otopark/index.html"), True)
    _uc = sum(x.get("uc", 0) for x in _o["iller"])
    _up = sum(x.get("up", 0) for x in _o["iller"])
    es("ucretsiz+ucretli <= toplam", _uc + _up <= _o["toplam"], True)
    if os.path.exists("site/ucretsiz-otopark/index.html"):
        _uh = open("site/ucretsiz-otopark/index.html", encoding="utf-8").read()
        es("ucretsiz sayfasi dogru sayiyi yaziyor", uret.tl(_uc) in _uh, True)
        # eksik veriyi "ucretli" gibi sunmamak icin uyari sart
        es("ucretsiz sayfasi bilinmiyor uyarisi", "bilinmiyor" in _uh, True)

_f34 = "site/ilce/fatih/index.html"
if os.path.exists(_f34):
    _h = open(_f34, encoding="utf-8").read()
    es("ilce sayfasi olcum tarihi", "<time datetime=" in _h, True)
    es("ilce sayfasi h2 var (h1->h3 atlamasi yok)", "<h2>" in _h, True)
    es("ilce canonical", 'rel="canonical"' in _h, True)

# --- hesap / favori katmani (2026-09-15) ---
_g  = open("site/giris/index.html", encoding="utf-8").read()
_f  = open("site/favoriler/index.html", encoding="utf-8").read()
_a  = json.load(open("site/veri/auth.json", encoding="utf-8"))
_sw = open("site/sw.js", encoding="utf-8").read()
_cs = open("site/stil.css", encoding="utf-8").read()
_vj = open("vercel.json", encoding="utf-8").read()
_gz = open("site/gizlilik.html", encoding="utf-8").read()

es("giris sayfasi e-posta alani", 'id="eposta"' in _g, True)
es("giris sayfasi Google dugmesi", 'id="google-giris"' in _g, True)
es("giris sayfasi noindex", 'name="robots" content="noindex"' in _g, True)
es("giris sayfasi hesap.js", "/hesap.js" in _g, True)
es("favoriler listesi", 'id="favori-liste"' in _f, True)
es("favoriler bos durumu", 'id="favori-bos"' in _f, True)
es("favoriler cikis dugmesi", 'id="cikis"' in _f, True)
es("auth.json iki alan", sorted(_a), ["anonKey", "url"])

# ASIL DEGISMEZ: gizlilik metni auth DURUMUYLA TUTARLI olmali. Sabit "kapali"
# beklemek, giris acilinca testi kirar ve asil tehlikeyi (acikken hâlâ
# "kisisel veri yok" demesi) kacirir.
_acik = uret.auth_acik()
if _acik:
    es("auth acik: anon anahtar (service_role DEGIL)",
       json.loads(__import__("base64").urlsafe_b64decode(
           _a["anonKey"].split(".")[1] + "==").decode())["role"], "anon")
    es("auth acik: anahtar url ile ayni proje",
       json.loads(__import__("base64").urlsafe_b64decode(
           _a["anonKey"].split(".")[1] + "==").decode())["ref"],
       _a["url"].split("//")[1].split(".")[0])
    es("auth acik: gizlilik KVKK aydinlatmasi", "yurt dışına aktarım" in _gz.lower()
       or "Yurt dışına aktarım" in _gz, True)
    es("auth acik: gizlilik supabase'i soyluyor", "supabase.co" in _gz, True)
    es("auth acik: 'kisisel veri yoktur' IDDIASI YOK",
       "işlenen kişisel veri yoktur" in _gz, False)
else:
    es("auth kapali: gizlilik kapali diyor", "kapalıdır" in _gz, True)
    es("auth kapali: gizlilik supabase demiyor", "supabase.co" in _gz, False)

# yeni kabuk: her sayfada alt sekme + oturum.js
for _ad, _y in [("ana", "site/index.html"), ("harita", "site/harita/index.html"),
                ("ucretsiz", "site/ucretsiz-otopark/index.html"),
                ("ilce", "site/ilce/fatih/index.html"),
                ("gizlilik", "site/gizlilik.html"), ("404", "site/404.html")]:
    _s = open(_y, encoding="utf-8").read()
    es(f"{_ad}: alt sekme", _s.count('class="alt-sekme"'), 1)
    es(f"{_ad}: oturum.js", "/oturum.js" in _s, True)
    es(f"{_ad}: hesap dugmesi", "data-hesap" in _s, True)

# kart: favori icin gereken nitelikler + doluluk cubugu
_i = open("site/ilce/fatih/index.html", encoding="utf-8").read()
es("kartta data-ad", 'data-ad="' in _i, True)
es("kartta data-ilce", 'data-ilce="' in _i, True)
es("kartta doluluk cubugu", 'class="dolu-cubuk"' in _i, True)
es("dolu-cubuk basta gizli", 'class="dolu-cubuk" hidden' in _i, True)

# service worker yeni varliklari onden onbellege alsin
es("sw oturum.js onden", '"/oturum.js"' in _sw, True)
es("sw auth.json onden", '"/veri/auth.json"' in _sw, True)
es("sw surum yukseldi", "np-v2" in _sw, True)

# CSP: supabase eklenmis, joker yalniz supabase.co'da
es("CSP supabase connect-src", "https://*.supabase.co" in _vj, True)
es("CSP form-action", "form-action 'self'" in _vj, True)
es("CSP script-src hâlâ self", "script-src 'self';" in _vj, True)

# tasarim sistemi
for _k in [".alt-sekme", ".yildiz", ".dolu-cubuk", ".hesap-dug", ".giris", "--sekme"]:
    es(f"stil.css {_k}", _k in _cs, True)
es("stil.css guvenli alan", "safe-area-inset-bottom" in _cs, True)

# Beyan edilen yetenek gercekten var mi: ana sayfa schema.org SearchAction
# /harita/?q= ilan ediyor; harita.js o parametreyi OKUMALI.
_hj = open("site/harita.js", encoding="utf-8").read()
_ix = open("site/index.html", encoding="utf-8").read()
es("schema SearchAction ?q= ilan ediyor", "?q={search_term_string}" in _ix, True)
es("harita.js ?q= okuyor", 'SORGU.get("q")' in _hj, True)
es("oturum.js var", os.path.exists("site/oturum.js"), True)
es("hesap.js var", os.path.exists("site/hesap.js"), True)
es("supabase vendor var", os.path.exists("site/vendor/supabase.js"), True)

print(f"\n{gecti} gecti, {basarisiz} basarisiz")
sys.exit(1 if basarisiz else 0)
