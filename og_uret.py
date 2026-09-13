# -*- coding: utf-8 -*-
"""OG gorseli uretici. Paylasim onizlemesi icin 1200x630 PNG.
Sayilar veri/ispark.json'dan gelir; elle yazilmaz."""
import json, pathlib
from playwright.sync_api import sync_playwright

d = json.load(open("veri/ispark.json", encoding="utf-8"))
n = len(d)
ilce = len({k["ilce"] for k in d})
yer = sum(k["kapasite"] or 0 for k in d)
f = sorted(k["ilk_saat_tl"] for k in d if k["ilk_saat_tl"])
medyan = f[len(f)//2]
tl = lambda x: f"{x:,.0f}".replace(",", ".")

HTML = f"""<!doctype html><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}}
body{{width:1200px;height:630px;background:#111310;color:#eceade;
 font:400 20px/1.4 ui-sans-serif,system-ui,"Segoe UI",Arial,sans-serif;
 padding:72px 80px;display:flex;flex-direction:column;justify-content:space-between;
 background-image:radial-gradient(900px 420px at 88% -10%, rgba(74,222,128,.16), transparent 70%)}}
.marka{{font-size:26px;font-weight:600;letter-spacing:-.02em}}
.marka b{{color:#4ade80;font-weight:800}}
h1{{font-size:80px;line-height:1.02;letter-spacing:-.04em;font-weight:700;max-width:15ch}}
h1 em{{font-style:normal;color:#4ade80}}
.r{{display:flex;gap:0;border:1px solid #2c302a;border-radius:18px;overflow:hidden}}
.r div{{flex:1;padding:22px 26px;background:#1a1d19;border-right:1px solid #2c302a}}
.r div:last-child{{border-right:0}}
.r b{{display:block;font-size:42px;font-weight:700;letter-spacing:-.03em;
 font-variant-numeric:tabular-nums;line-height:1.1}}
.r span{{color:#9c9a8e;font-size:17px}}
.alt{{color:#9c9a8e;font-size:18px}}
</style>
<div class="marka">nereye<b>parkedicem</b></div>
<h1>En yakın otoparkı <em>saniyede</em> bul</h1>
<div class="r">
 <div><b>{n}</b><span>İSPARK otoparkı</span></div>
 <div><b>{ilce}</b><span>ilçe</span></div>
 <div><b>{tl(yer)}</b><span>toplam yer</span></div>
 <div><b>{tl(medyan)} ₺</b><span>ilk saat medyan</span></div>
</div>
<div class="alt">Canlı doluluk ve tam tarife · İBB Açık Veri (CC BY 4.0) · uygulama indirmeden</div>
"""

pathlib.Path("og_sablon.html").write_text(HTML, encoding="utf-8")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
    pg.goto("file://" + str(pathlib.Path("og_sablon.html").resolve()).replace("\\", "/"))
    pg.wait_for_timeout(400)
    pg.screenshot(path="site/og.png")
    b.close()
kb = pathlib.Path("site/og.png").stat().st_size / 1024
print(f"site/og.png uretildi · {kb:.0f} KB · 1200x630 · {n} otopark, {ilce} ilce")
