# -*- coding: utf-8 -*-
"""ISPARK: liste + tum detaylar -> veri/ispark.json (tek normalize dosya).
Kaynak: IBB Acik Veri Portali (CC BY 4.0). Atif zorunlu."""
import json, os, re, time, sys
from ispark import liste, detay

os.makedirs("veri", exist_ok=True)

def tarife_ayikla(t):
    """'0-1 Saat : 110,00;1-2 Saat : 140,00' -> [{'aralik':'0-1 Saat','tl':110.0}, ...]"""
    if not t: return []
    out = []
    for p in str(t).split(";"):
        if ":" not in p: continue
        ad, _, fiyat = p.rpartition(":")
        f = re.sub(r"[^\d,\.]", "", fiyat).replace(".", "").replace(",", ".")
        try: out.append({"aralik": ad.strip(), "tl": float(f)})
        except ValueError: pass
    return out

def main():
    l = liste()
    print(f"liste: {len(l)} nokta", flush=True)
    kayitlar, hata = [], 0
    for i, p in enumerate(l, 1):
        pid = p["parkID"]
        try:
            d = detay(pid)
            d = d[0] if isinstance(d, list) and d else (d if isinstance(d, dict) else {})
        except Exception as e:
            hata += 1; d = {}
            print(f"  ! {pid}: {e}", file=sys.stderr, flush=True)
        tar = tarife_ayikla(d.get("tariff"))
        kayitlar.append({
            "kaynak": "ispark", "id": pid, "ad": p["parkName"],
            "lat": float(p["lat"]), "lng": float(p["lng"]),
            "ilce": p.get("district"), "adres": d.get("address"),
            "tip": p.get("parkType"), "saat": p.get("workHours"),
            "kapasite": p.get("capacity"), "bos": p.get("emptyCapacity"),
            "acik": bool(p.get("isOpen")), "ucretsiz_dk": p.get("freeTime"),
            "aylik_tl": d.get("monthlyFee"), "tarife": tar,
            "ilk_saat_tl": tar[0]["tl"] if tar else None,
            "guncelleme": d.get("updateDate"),
        })
        if i % 50 == 0: print(f"  {i}/{len(l)}", flush=True)
        time.sleep(0.15)
    json.dump(kayitlar, open("veri/ispark.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
    tl = [k["ilk_saat_tl"] for k in kayitlar if k["ilk_saat_tl"]]
    tl.sort()
    print(f"\nyazildi: veri/ispark.json · {len(kayitlar)} kayit · detay hatasi {hata}")
    print(f"tarifesi olan: {len(tl)}/{len(kayitlar)}")
    if tl: print(f"1. saat TL -> min {tl[0]:.0f} · medyan {tl[len(tl)//2]:.0f} · max {tl[-1]:.0f}")
    ilce = {}
    for k in kayitlar: ilce[k["ilce"]] = ilce.get(k["ilce"],0)+1
    print(f"ilce sayisi: {len(ilce)}")

if __name__ == "__main__": main()
