# -*- coding: utf-8 -*-
"""OSM <-> ISPARK eslestirme. Kapsam boslugu olcumu.
Cache'teki il34.json koordinat tasimiyor (out tags), o yuzden Istanbul'u
'out center' ile bir kez daha ceker. 150 m yaricap = ayni otopark sayilir."""
import json, math, os, sys
from osm_sayim import sor

ESIK_M = 150
YOL = "veri/il34_center.json"

def cek():
    if os.path.exists(YOL):
        d = json.load(open(YOL, encoding="utf-8"))
        if d["elements"]: return d
        os.remove(YOL)
    a = json.load(open("veri/_iller.json", encoding="utf-8"))["TR-34"]
    d = sor(f'[out:json][timeout:240];area({a})->.a;(nwr[amenity=parking](area.a););out center;')
    if not d["elements"]: raise RuntimeError("Istanbul bos dondu")
    json.dump(d, open(YOL, "w", encoding="utf-8"), ensure_ascii=False)
    return d

def konum(e):
    if "lat" in e: return e["lat"], e["lon"]
    c = e.get("center")
    return (c["lat"], c["lon"]) if c else None

def metre(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(h))

if __name__ == "__main__":
    osm = [(konum(e), e.get("tags", {})) for e in cek()["elements"]]
    osm = [(k, t) for k, t in osm if k]
    isp = json.load(open("veri/ispark.json", encoding="utf-8"))
    print(f"OSM Istanbul koordinatli: {len(osm):,}   ISPARK: {len(isp)}", flush=True)

    eslesen, eksik, isimli, tarifeli = [], [], 0, 0
    for p in isp:
        k = (p["lat"], p["lng"])
        yakin = min(((metre(k, o), t) for o, t in osm), default=None)
        if yakin and yakin[0] <= ESIK_M:
            eslesen.append((p, yakin[1]))
            if "name" in yakin[1]: isimli += 1
            if yakin[1].get("fee") == "yes" and "charge" in yakin[1]: tarifeli += 1
        else:
            eksik.append(p)

    n = len(isp)
    print(f"\nOSM'de var   : {len(eslesen):>3} / {n}  (%{len(eslesen)/n*100:.1f})")
    print(f"OSM'de YOK   : {len(eksik):>3} / {n}  (%{len(eksik)/n*100:.1f})")
    print(f"  esleseninde isim var  : {isimli}")
    print(f"  esleseninde tarife var: {tarifeli}")

    ilce = {}
    for p in eksik: ilce[p["ilce"]] = ilce.get(p["ilce"], 0) + 1
    print("\nOSM'de olmayan ISPARK - ilce basina ilk 10:")
    for i, s in sorted(ilce.items(), key=lambda x: -x[1])[:10]:
        print(f"  {i:<18}{s:>3}")

    json.dump({"esik_m": ESIK_M, "ispark_toplam": n, "osm_var": len(eslesen),
               "osm_yok": len(eksik), "eslesen_isimli": isimli,
               "eslesen_tarifeli": tarifeli, "eksik_ilce": ilce},
              open("veri/osm_ispark.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
