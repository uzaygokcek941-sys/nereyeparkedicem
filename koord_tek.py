"""Butun Turkiye'nin otopark koordinatini TEK Overpass sorgusuyla ceker.

81 ayri il sorgusu aynanin hiz sinirina (2 slot) carpiyor ve 429/504 veriyor.
Il uyeligi zaten elimizde: veri/il*.json her ilin eleman kimliklerini tasiyor
(onceki 'out tags' olcumunden). O yuzden burada yalniz (tip,id) -> koordinat
tablosu cekilir, il eslesmesi yerelde yapilir.
"""
import json, os, urllib.parse, urllib.request

import truststore

truststore.inject_into_ssl()

AYNA = "https://overpass-api.de/api/interpreter"
UA = {"User-Agent": "parking-coverage-research/1.0 (kapsam olcumu; tek kullanici)"}
KUTU = "35.7,25.5,42.3,44.9"  # Turkiye sinirlari; komsudan tasan noktalar il eslesmesinde duser
CIKTI = "veri/koord_tum.json"

SORGU = f"[out:json][timeout:900];nwr[amenity=parking]({KUTU});out skel center;"


def main():
    if os.path.exists(CIKTI):
        print(f"{CIKTI} zaten var, atlandi")
        return
    veri = urllib.parse.urlencode({"data": SORGU}).encode()
    r = urllib.request.Request(AYNA, data=veri, headers=UA)
    print("sorgu gonderildi, bekleniyor...")
    with urllib.request.urlopen(r, timeout=1200) as x:
        ham = x.read()
    print(f"{len(ham)} bayt geldi")
    d = json.loads(ham)
    el = d["elements"]
    koordlu = sum(1 for e in el if "lat" in e or "center" in e)
    if not koordlu:
        raise RuntimeError("koordinat yok, sorgu yanlis")
    os.makedirs("veri", exist_ok=True)
    with open(CIKTI, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    print(f"eleman {len(el)} · koordinatli {koordlu} -> {CIKTI}")


if __name__ == "__main__":
    main()
