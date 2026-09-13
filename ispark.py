# -*- coding: utf-8 -*-
"""ISPARK acik veri istemcisi. Kaynak: IBB Acik Veri Portali, CC BY 4.0.
TLS: truststore ile Windows sertifika deposu -> bu makinedeki araya girmeyi asar,
dogrulama ACIK kalir (verify=False ASLA kullanilmaz)."""
import json, ssl, urllib.parse, urllib.request
import truststore

TABAN = "https://api.ibb.gov.tr/ispark"
_CTX = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

def _al(yol, **p):
    url = f"{TABAN}/{yol}" + (f"?{urllib.parse.urlencode(p)}" if p else "")
    r = urllib.request.Request(url, headers={"User-Agent": "nereyeparkedicem/0.1"})
    with urllib.request.urlopen(r, timeout=45, context=_CTX) as x:
        return json.loads(x.read().decode("utf-8"))

def liste():
    """Tum otoparklar + canli bos kapasite."""
    return _al("Park")

def detay(park_id):
    """Tek otoparkin detayi (tarife burada olabilir)."""
    return _al("ParkDetay", id=park_id)

if __name__ == "__main__":
    d = liste()
    print(f"liste: {len(d)} nokta")
    ilk = d[0]["parkID"]
    try:
        det = detay(ilk)
        print(f"detay({ilk}) tip={type(det).__name__}")
        o = det[0] if isinstance(det, list) and det else det
        print("DETAY ALANLARI:", list(o.keys()) if isinstance(o, dict) else o)
        print(json.dumps(o, ensure_ascii=False)[:600])
    except Exception as e:
        print("detay HATA:", type(e).__name__, e)
