# -*- coding: utf-8 -*-
"""Sehir bazli otopark kapsam olcumu (OSM).
Adim 1: il relation id'si (ISO3166-2 tam eslesme, ucuz).
Adim 2: area(3600000000+id) ile otopark etiketleri, sehir basina TEK cagri.
Adim 3: sayim yerelde. veri/ cache'li -> kesilirse kaldigi yerden devam eder."""
import json, os, sys, time
from osm_sayim import sor

# 81 il: ISO3166-2 TR-01..TR-81 deterministik, pahali regex sorgusu gerekmez.
SEHIRLER = [(f"il{i:02d}", f"TR-{i:02d}") for i in range(1, 82)]

ETIKET = ["name","fee","charge","opening_hours","capacity","operator"]
os.makedirs("veri", exist_ok=True)

def alan_id(kod):
    yol = "veri/_iller.json"
    harita = json.load(open(yol, encoding="utf-8")) if os.path.exists(yol) else {}
    if kod in harita: return harita[kod]
    d = sor(f'[out:json][timeout:120];relation[admin_level=4]["ISO3166-2"="{kod}"];out ids;')
    if not d["elements"]: raise RuntimeError(f"{kod} relation bulunamadi")
    harita[kod] = 3600000000 + d["elements"][0]["id"]
    json.dump(harita, open(yol, "w", encoding="utf-8"))
    return harita[kod]

def cek(sehir, kod, deneme=3):
    yol = f"veri/{sehir}.json"
    if os.path.exists(yol):
        d = json.load(open(yol, encoding="utf-8"))
        if d["elements"]: return d
        os.remove(yol)                      # bos sonuc asla onbeklenmez
    a = alan_id(kod)
    q = f'[out:json][timeout:240];area({a})->.a;(nwr[amenity=parking](area.a););out tags;'
    for i in range(deneme):
        d = sor(q)
        if d["elements"]:
            json.dump(d, open(yol, "w", encoding="utf-8"), ensure_ascii=False); return d
        print(f"  ! {sehir} bos, tekrar {i+1}/{deneme}", file=sys.stderr, flush=True); time.sleep(8)
    raise RuntimeError(f"{sehir} bos dondu")

def analiz(d):
    el = d["elements"]; s = {"toplam": len(el)}
    for t in ETIKET: s[t] = sum(1 for e in el if t in e.get("tags", {}))
    s["ucretli"] = sum(1 for e in el if e.get("tags",{}).get("fee") == "yes")
    s["ispark"]  = sum(1 for e in el if "ispark" in str(e.get("tags",{}).get("operator","")).lower())
    return s

if __name__ == "__main__":
    top = {k:0 for k in ["toplam"]+ETIKET+["ucretli","ispark"]}; cikti={}
    print(f'{"SEHIR":<10}{"toplam":>8}{"isim":>7}{"ucret":>7}{"tarife":>7}{"saat":>6}{"kapas":>7}{"islet":>7}{"saat%":>7}', flush=True)
    for s, kod in SEHIRLER:
        try:
            a = analiz(cek(s, kod)); cikti[s]=a
            for k in top: top[k]+=a[k]
            print(f'{s:<10}{a["toplam"]:>8,}{a["name"]:>7,}{a["fee"]:>7,}{a["charge"]:>7,}'
                  f'{a["opening_hours"]:>6,}{a["capacity"]:>7,}{a["operator"]:>7,}'
                  f'{a["opening_hours"]/a["toplam"]*100:>6.1f}%', flush=True)
        except Exception as e:
            print(f'{s:<10} HATA: {e}', file=sys.stderr, flush=True)
        time.sleep(2)
    t = top["toplam"] or 1
    print(f'{"TOPLAM":<10}{top["toplam"]:>8,}{top["name"]:>7,}{top["fee"]:>7,}{top["charge"]:>7,}'
          f'{top["opening_hours"]:>6,}{top["capacity"]:>7,}{top["operator"]:>7,}{top["opening_hours"]/t*100:>6.1f}%')
    print(f'\nfee=yes: {top["ucretli"]:,}   operator=ISPARK: {top["ispark"]:,}')
    print("--- EKSIKLIK ---")
    for k in ETIKET: print(f'  {k:<15} eksik %{100-top[k]/t*100:.1f}')
    cikti["_TOPLAM"]=top
    json.dump(cikti, open("osm_sehirler.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
