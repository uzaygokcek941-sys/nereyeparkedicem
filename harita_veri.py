# -*- coding: utf-8 -*-
"""veri/koord/il*.json -> site/veri/il-NN.json (il basina) + site/veri/iller.json (ozet)

Bicim bilerek dar: koordinatlar tek duz dizide [lat,lng,lat,lng,...], ek bilgi
yalnizca sahip olan noktalar icin seyrek harita. OSM'de otoparklarin %93'unde isim,
%96,8'inde kapasite yok - her nokta icin nesne yazmak dosyayi bosuna 3 katina cikarirdi."""
import json, os, statistics as st

PLAKA = {1:"Adana",2:"Adıyaman",3:"Afyonkarahisar",4:"Ağrı",5:"Amasya",6:"Ankara",
 7:"Antalya",8:"Artvin",9:"Aydın",10:"Balıkesir",11:"Bilecik",12:"Bingöl",13:"Bitlis",
 14:"Bolu",15:"Burdur",16:"Bursa",17:"Çanakkale",18:"Çankırı",19:"Çorum",20:"Denizli",
 21:"Diyarbakır",22:"Edirne",23:"Elazığ",24:"Erzincan",25:"Erzurum",26:"Eskişehir",
 27:"Gaziantep",28:"Giresun",29:"Gümüşhane",30:"Hakkari",31:"Hatay",32:"Isparta",
 33:"Mersin",34:"İstanbul",35:"İzmir",36:"Kars",37:"Kastamonu",38:"Kayseri",
 39:"Kırklareli",40:"Kırşehir",41:"Kocaeli",42:"Konya",43:"Kütahya",44:"Malatya",
 45:"Manisa",46:"Kahramanmaraş",47:"Mardin",48:"Muğla",49:"Muş",50:"Nevşehir",
 51:"Niğde",52:"Ordu",53:"Rize",54:"Sakarya",55:"Samsun",56:"Siirt",57:"Sinop",
 58:"Sivas",59:"Tekirdağ",60:"Tokat",61:"Trabzon",62:"Tunceli",63:"Şanlıurfa",
 64:"Uşak",65:"Van",66:"Yozgat",67:"Zonguldak",68:"Aksaray",69:"Bayburt",70:"Karaman",
 71:"Kırıkkale",72:"Batman",73:"Şırnak",74:"Bartın",75:"Ardahan",76:"Iğdır",
 77:"Yalova",78:"Karabük",79:"Kilis",80:"Osmaniye",81:"Düzce"}

CIKTI = "site/veri"

def konum(e):
    if "lat" in e: return e["lat"], e["lon"]
    c = e.get("center")
    return (c["lat"], c["lon"]) if c else None

def slug_tip(t):
    return {"surface":"açık","multi-storey":"katlı","underground":"yeraltı",
            "rooftop":"çatı","carports":"sundurma","garage_boxes":"garaj",
            "street_side":"yol kenarı","lane":"şerit"}.get(t, t)

def koord_tablosu():
    """koord_tum.json tek bbox sorgusuyla cekildi; 'out skel center' oldugu icin
    etiket tasimiyor. Il uyeligi ve etiketler onceki olcumden (veri/il{NN}.json,
    'out tags') geliyor. Iki kaynak (tip,id) ile eslesir."""
    d = json.load(open("veri/koord_tum.json", encoding="utf-8"))
    t = {}
    for e in d["elements"]:
        p = konum(e)
        if p: t[(e["type"], e["id"])] = p
    return t

KOORD = {}

def il_uret(kod):
    yol = f"veri/il{kod:02d}.json"
    if not os.path.exists(yol): return None
    el = json.load(open(yol, encoding="utf-8"))["elements"]
    k, bilgi = [], {}
    for e in el:
        p = KOORD.get((e["type"], e["id"]))
        if not p: continue
        i = len(k) // 2
        k += [round(p[0], 5), round(p[1], 5)]
        t = e.get("tags", {})
        b = {}
        if t.get("name"): b["a"] = t["name"][:60]
        if t.get("fee") == "yes": b["u"] = 1
        elif t.get("fee") == "no": b["u"] = 0
        if t.get("capacity", "").isdigit(): b["k"] = int(t["capacity"])
        if t.get("parking"): b["t"] = slug_tip(t["parking"])
        if t.get("opening_hours"): b["s"] = t["opening_hours"][:40]
        if t.get("operator"): b["o"] = t["operator"][:40]
        if b: bilgi[str(i)] = b
    if not k: return None
    lat = k[0::2]; lng = k[1::2]
    d = {"p": kod, "ad": PLAKA[kod], "n": len(lat),
         "c": [round(st.median(lat), 4), round(st.median(lng), 4)],
         "bb": [round(min(lat), 4), round(min(lng), 4), round(max(lat), 4), round(max(lng), 4)],
         "k": k, "b": bilgi}
    json.dump(d, open(f"{CIKTI}/il-{kod:02d}.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    return d

if __name__ == "__main__":
    os.makedirs(CIKTI, exist_ok=True)
    KOORD.update(koord_tablosu())
    print(f"koord tablosu: {len(KOORD):,} eleman\n")
    ozet, top, boy = [], 0, 0
    for kod in range(1, 82):
        d = il_uret(kod)
        if not d:
            print(f"il{kod:02d} {PLAKA[kod]:<16} VERI YOK", flush=True); continue
        bo = os.path.getsize(f"{CIKTI}/il-{kod:02d}.json")
        top += d["n"]; boy += bo
        ozet.append({"p": kod, "ad": d["ad"], "c": d["c"], "bb": d["bb"],
                     "n": d["n"], "b": len(d["b"])})
        print(f'il{kod:02d} {d["ad"]:<16}{d["n"]:>6,} nokta · {len(d["b"]):>5,} bilgili'
              f' · {bo/1024:>7.1f} KB', flush=True)
    ozet.sort(key=lambda x: -x["n"])
    json.dump({"toplam": top, "iller": ozet},
              open(f"{CIKTI}/iller.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f'\nTOPLAM {top:,} nokta · {len(ozet)} il · {boy/1048576:.2f} MB'
          f' · ozet {os.path.getsize(f"{CIKTI}/iller.json")/1024:.1f} KB')
