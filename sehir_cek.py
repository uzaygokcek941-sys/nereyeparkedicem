# -*- coding: utf-8 -*-
"""Izmir (IZELMAN) ve Ankara (ANPARK) otoparklari -> veri/izmir.json, veri/ankara.json
ispark.json ile AYNI sema, boylece uret.py yardimcilari degismeden calisir.

Izmir : acikveri.bizizmir.com CKAN, 4 konum CSV + 1 tarife CSV (Izmir Acik Veri Lisansi)
Ankara: anpark.com.tr WordPress REST /anpark/v1/parks — tarife YOK, ANPARK fiyati
        yalnizca gorsel olarak yayinliyor, o yuzden tarife alani bos birakilir."""
import csv, io, json, os, re, ssl, sys, urllib.request
import truststore

_CTX = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
os.makedirs("veri", exist_ok=True)

IZ = "https://acikveri.bizizmir.com/dataset"
IZ_KONUM = [
    ("yol kenarı", f"{IZ}/bbd99177-529e-401a-85b1-9d369dae0148/resource/a982c5d9-931d-4a75-a61d-23127d8ddad2/download/izelman-yol-kenari-otoparklar.csv"),
    ("kapalı",     f"{IZ}/bbd99177-529e-401a-85b1-9d369dae0148/resource/6ad4ad67-5923-49ec-8725-3f44f6f72aec/download/izelman-kapalialan-otoparklar.csv"),
    ("açık alan",  f"{IZ}/bbd99177-529e-401a-85b1-9d369dae0148/resource/959c08c4-3e62-4e20-9e45-c334b0df31b1/download/izelman-yolkenari-disinda-acikalan-otoparklar.csv"),
    ("abone",      f"{IZ}/bbd99177-529e-401a-85b1-9d369dae0148/resource/22cf1829-b59b-4366-9169-8542f39de992/download/izelman-aboneli-otopark.csv"),
]
IZ_TARIFE = f"{IZ}/8863674c-c082-4f55-ab1d-dc75219aca4f/resource/8dca3fb5-b7fe-4f16-91af-d8248da59f87/download/otopark-ucretleri.csv"
ANKARA = "https://www.anpark.com.tr/wp-json/anpark/v1/parks"

def al(url):
    r = urllib.request.Request(url, headers={"User-Agent": "nereyeparkedicem/0.1"})
    with urllib.request.urlopen(r, timeout=60, context=_CTX) as x:
        return x.read()

def csv_oku(url):
    """Ayirici ; veya , olabiliyor, ikisi de sahada goruldu."""
    t = al(url).decode("utf-8-sig")
    ilk = t.splitlines()[0]
    d = ";" if ilk.count(";") > ilk.count(",") else ","
    return list(csv.DictReader(io.StringIO(t), delimiter=d))

def sayi(s):
    s = re.sub(r"[^\d,\.]", "", str(s or "")).replace(".", "").replace(",", ".")
    try: return float(s)
    except ValueError: return None

def anahtar(ad):
    """Tarife CSV'si ile konum CSV'si farkli yaziyor; eslestirme icin sadelestir."""
    a = (ad or "").replace("I", "ı").replace("İ", "i").lower()
    a = re.sub(r"[^a-zçğıöşü\s]", " ", a)
    at = {"otopark", "otoparkı", "otoparki", "katlı", "katli", "kapalı", "kapali",
          "açık", "acik", "yeraltı", "yeralti", "tam", "otomatik", "alan", "yol", "kenarı", "kenari"}
    return " ".join(sorted(k for k in a.split() if k and k not in at))

def izmir_tarife():
    """{anahtar: (tarife listesi, ilk_saat_tl, aylik_tl)}"""
    out = {}
    for s in csv_oku(IZ_TARIFE):
        ad = (s.get("Otopark / Fiyat") or "").replace("\n", " ").strip()
        if not ad: continue
        tar = [{"aralik": k.strip(), "tl": sayi(v)}
               for k, v in s.items()
               if k and k != "Otopark / Fiyat" and "Abone" not in k
               and "Kayıp" not in k and sayi(v)]
        aylik = sayi(s.get("Aylık Abone Ücreti"))
        # ilk saat = en kisa sureli kalem; "0-1" yoksa "0-2" gecerli baslangic
        ilk = tar[0]["tl"] if tar else None
        out[anahtar(ad)] = (tar, ilk, aylik, ad)
    return out

def izmir():
    tar = izmir_tarife()
    kayit, eslesen = [], 0
    for tip, url in IZ_KONUM:
        for s in csv_oku(url):
            ad = (s.get("OTOPARK_ADI") or s.get("BLOK_ADI") or "").strip()
            lat, lng = sayi(s.get("ENLEM")), sayi(s.get("BOYLAM"))
            if not ad or lat is None or lng is None: continue
            t, ilk, aylik, _ = tar.get(anahtar(ad), ([], None, None, None))
            if t: eslesen += 1
            ac, kap = (s.get("ACILIS_SAATI") or "").strip(), (s.get("KAPANIS_SAATI") or "").strip()
            kayit.append({
                "kaynak": "izelman", "id": f"izelman-{len(kayit)+1}", "ad": ad,
                "lat": lat, "lng": lng,
                "ilce": (s.get("ILCE") or "").strip(),
                "adres": (s.get("ADRES") or s.get("ADRES_VEYA_TARIF") or "").strip(),
                "tip": tip, "saat": f"{ac}-{kap}" if ac and kap else None,
                "kapasite": int(sayi(s.get("KAPASITE")) or 0) or None, "bos": None,
                "acik": True, "ucretsiz_dk": None, "aylik_tl": aylik,
                "tarife": t, "ilk_saat_tl": ilk, "guncelleme": None,
            })
    json.dump(kayit, open("veri/izmir.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"izmir : {len(kayit)} otopark · tarifesi olan {eslesen} · "
          f"tarife CSV'sinde {len(tar)} kayit · ilce {len({k['ilce'] for k in kayit})}")
    return kayit

def ankara():
    d = json.loads(al(ANKARA).decode("utf-8"))
    kayit = [{
        "kaynak": "anpark", "id": f"anpark-{p['id']}", "ad": p["name"],
        "lat": float(p["lat"]), "lng": float(p["lng"]),
        "ilce": p.get("district"), "adres": p.get("address"),
        "tip": p.get("type"), "saat": p.get("schedule"),
        "kapasite": p.get("capacity"), "bos": None,
        "acik": bool(p.get("active")), "ucretsiz_dk": None,
        "aylik_tl": None, "tarife": [], "ilk_saat_tl": None, "guncelleme": None,
    } for p in d if p.get("lat") and p.get("lng")]
    json.dump(kayit, open("veri/ankara.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"ankara: {len(kayit)} otopark · tarifesi olan 0 "
          f"(ANPARK tarifeyi yalniz gorsel olarak yayinliyor) · "
          f"ilce {len({k['ilce'] for k in kayit})}")
    return kayit

if __name__ == "__main__":
    izmir(); ankara()
