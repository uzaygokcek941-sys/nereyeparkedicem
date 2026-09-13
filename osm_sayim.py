"""OSM amenity=parking Turkiye kapsam olcumu. Overpass count sorgulari. Stdlib, bagimlilik yok."""
import json, time, urllib.request, urllib.parse, sys

AYNALAR = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

def sor(q):
    body = urllib.parse.urlencode({"data": q}).encode()
    son = None
    for url in AYNALAR:
        try:
            req = urllib.request.Request(url, data=body,
                headers={"User-Agent": "parking-coverage-research/1.0 (kapsam olcumu)"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            son = f"{url.split('/')[2]}: {e}"
            print(f"  ! {son}", file=sys.stderr); time.sleep(5)
    raise RuntimeError(son)

TR_AREA = 3600174737  # OSM relation 174737 = Turkiye. Sabit id: ayna farklarini eler.

def sayim(filtre, alan=None):
    alan = alan or f'area({TR_AREA})->.a;'
    q = f'[out:json][timeout:280];{alan}(nwr{filtre}(area.a););out count;'
    return int(sor(q)["elements"][0]["tags"]["total"])

FILTRELER = [
    ("TOPLAM otopark",           '[amenity=parking]'),
    ("  + isim (name)",          '[amenity=parking][name]'),
    ("  + ucretli mi (fee)",     '[amenity=parking][fee]'),
    ("  + tarife (charge)",      '[amenity=parking][charge]'),
    ("  + saat (opening_hours)", '[amenity=parking][opening_hours]'),
    ("  + kapasite",             '[amenity=parking][capacity]'),
    ("  + isletmeci (operator)", '[amenity=parking][operator]'),
]

if __name__ == "__main__":
    print("=== TURKIYE GENELI (OSM, amenity=parking) ===")
    sonuc, t0 = {}, time.time()
    for ad, f in FILTRELER:
        n = sayim(f); sonuc[ad.strip()] = n
        print(f"{ad:28s} {n:>8,}   ({time.time()-t0:.0f}s)", flush=True)
        time.sleep(2)
    top = sonuc["TOPLAM otopark"]
    print("\n--- EKSIKLIK ---")
    for ad in sonuc:
        if ad.startswith("+"):
            print(f"{ad:28s} eksik %{100-sonuc[ad]/top*100:.1f}")
    json.dump(sonuc, open("osm_turkiye.json","w"), ensure_ascii=False, indent=1)
