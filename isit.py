# -*- coding: utf-8 -*-
"""Deploy sonrasi edge cache isitma. Ilk ziyaretci soguk iskaya denk gelmesin.
Olculdu: soguk MISS 7.479 ms, isinmis HIT ~200 ms."""
import re, ssl, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
import truststore

TABAN = sys.argv[1] if len(sys.argv) > 1 else "https://nereyeparkedicem.vercel.app"
CTX = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

def al(u):
    r = urllib.request.Request(u, headers={"User-Agent": "isitma/1.0"})
    t0 = time.time()
    with urllib.request.urlopen(r, timeout=45, context=CTX) as x:
        x.read()
        return u, x.status, x.headers.get("x-vercel-cache", "?"), (time.time()-t0)*1000

sm = al(f"{TABAN}/sitemap.xml")
with urllib.request.urlopen(f"{TABAN}/sitemap.xml", timeout=45, context=CTX) as x:
    urller = re.findall(r"<loc>([^<]+)</loc>", x.read().decode())
urller += [f"{TABAN}/otoparklar.json", f"{TABAN}/stil.css", f"{TABAN}/uygulama.js"]

t0 = time.time(); miss = 0; hata = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    for u, s, c, ms in ex.map(lambda u: al(u), urller):
        if s != 200: hata += 1; print(f"  ! {s} {u}")
        if c.upper().startswith("MISS"): miss += 1
print(f"isitildi: {len(urller)} adres · {time.time()-t0:.1f}s · MISS {miss} · hata {hata}")
sys.exit(1 if hata else 0)
