# -*- coding: utf-8 -*-
"""81 il otopark KOORDINATLARI -> veri/koord/il{NN}.json

Olculmus gercek (2026-09-15): overpass.private.coffee ve overpass.kumi.systems
/api/status'a bos donuyor - kullanilamiyor. Tek calisan ayna overpass-api.de ve
`Rate limit: 2`. Onceki surum 3 is parcacigiyla ustune gidip 429 aldi; bu surum
sunucunun kendi sinirina uyar:
  - en fazla 2 es zamanli sorgu (aynanin ilan ettigi slot sayisi)
  - her sorgudan ONCE /api/status okunur, bos slot yoksa aynanin verdigi
    "Slot available after ... in N seconds" suresi kadar beklenir
  - 429 gelirse ayni yol izlenir, koru koru tekrar denenmez

Etiket cekilmiyor (`out skel center`); etiketler veri/il{NN}.json'da duruyor ve
harita_veri.py (tip,id) ile birlestiriyor.
Bos ya da koordinatsiz sonuc asla onbeklenmez -> kesilirse kaldigi yerden devam eder."""
import json, os, re, threading, time, urllib.error, urllib.parse, urllib.request

AYNA = "https://overpass-api.de/api/interpreter"
DURUM = "https://overpass-api.de/api/status"
UA = {"User-Agent": "parking-coverage-research/1.0 (kapsam olcumu; tek kullanici)"}
ILLER = json.load(open("veri/_iller.json", encoding="utf-8"))
os.makedirs("veri/koord", exist_ok=True)
kilit = threading.Lock()
slot_kilit = threading.Lock()          # status okumasi da istek, seri yapilir

def yaz(*a):
    with kilit: print(*a, flush=True)

def slot_bekle(tavan=180):
    """Aynanin ilan ettigi bos slot yoksa soyledigi kadar bekle."""
    with slot_kilit:
        try:
            r = urllib.request.Request(DURUM, headers=UA)
            with urllib.request.urlopen(r, timeout=30) as x:
                t = x.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(5); return
        m = re.search(r"(\d+) slots? available now", t)
        if m and int(m.group(1)) > 0: return
        b = re.search(r"in (\d+) seconds", t)
        s = min(int(b.group(1)) + 2, tavan) if b else 15
        yaz(f"  . slot yok, {s} sn bekleniyor")
        time.sleep(s)

def cek(kod):
    q = (f'[out:json][timeout:180];area({ILLER[f"TR-{kod:02d}"]})->.a;'
         f'(nwr[amenity=parking](area.a););out skel center;')
    b = urllib.parse.urlencode({"data": q}).encode()
    r = urllib.request.Request(AYNA, data=b, headers=UA)
    with urllib.request.urlopen(r, timeout=200) as x:
        return json.loads(x.read().decode())

def isci(sira, kilitli_liste):
    while True:
        with kilit:
            if not kilitli_liste: return
            kod = kilitli_liste.pop(0)
        yol = f"veri/koord/il{kod:02d}.json"
        if os.path.exists(yol):
            try:
                if json.load(open(yol, encoding="utf-8"))["elements"]: continue
            except ValueError: pass
            os.remove(yol)
        for deneme in range(3):
            slot_bekle()
            try:
                d = cek(kod)
                el = d["elements"]
                kk = sum(1 for e in el if "lat" in e or "center" in e)
                if not el or not kk:
                    yaz(f"il{kod:02d} bos/koordinatsiz (eleman {len(el)}, koord {kk})")
                    break
                json.dump(d, open(yol, "w", encoding="utf-8"),
                          ensure_ascii=False, separators=(",", ":"))
                yaz(f"il{kod:02d} {kk:>6,} koordinat")
                break
            except urllib.error.HTTPError as e:
                yaz(f"il{kod:02d} HTTP {e.code} (deneme {deneme+1}/3)")
                time.sleep(20 if e.code == 429 else 8)
            except Exception as e:
                yaz(f"il{kod:02d} HATA {type(e).__name__}: {e} (deneme {deneme+1}/3)")
                time.sleep(8)

if __name__ == "__main__":
    t0 = time.time()
    for tur in (1, 2, 3):
        eksik = [k for k in range(1, 82) if not os.path.exists(f"veri/koord/il{k:02d}.json")]
        if not eksik: break
        yaz(f"=== tur {tur}: {len(eksik)} il eksik · 2 es zamanli sorgu ===")
        ts = [threading.Thread(target=isci, args=(i, eksik), daemon=True) for i in (0, 1)]
        for t in ts: t.start()
        for t in ts: t.join()
    var = sorted(int(f[2:4]) for f in os.listdir("veri/koord") if f.startswith("il"))
    top = sum(sum(1 for e in json.load(open(f"veri/koord/il{k:02d}.json", encoding="utf-8"))["elements"]
                  if "lat" in e or "center" in e) for k in var)
    yaz(f"\nTAMAM {len(var)}/81 il · {top:,} koordinatli nokta · {(time.time()-t0)/60:.1f} dk")
    if len(var) < 81: yaz("eksik:", [k for k in range(1, 82) if k not in var])
