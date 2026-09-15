# -*- coding: utf-8 -*-
"""Site simgesi + manifest. Denetimde olculdu: /favicon.ico 404, hic
<link rel=icon> yok, manifest yok -> sekmede bos simge, telefona eklenemiyor.

SVG birincil (her boyutta keskin), PNG'ler iOS ve manifest icin.
Tasarim: koyu yesil kare + beyaz 'P' + turuncu konum noktasi."""
import json, os

from PIL import Image, ImageDraw, ImageFont

CIKTI = "site"
YESIL = (11, 61, 46)
VURGU = (240, 165, 0)

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0b3d2e"/>
<text x="32" y="45" font-family="Helvetica,Arial,sans-serif" font-size="40"
 font-weight="700" fill="#fff" text-anchor="middle">P</text>
<circle cx="48" cy="18" r="6" fill="#f0a500"/>
</svg>
'''

def yazitipi(boy):
    for y in (r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\segoeuib.ttf"):
        if os.path.exists(y):
            return ImageFont.truetype(y, boy)
    return ImageFont.load_default()

def png(boy, yol):
    im = Image.new("RGBA", (boy, boy), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, boy - 1, boy - 1], radius=int(boy * 0.22), fill=YESIL)
    d.text((boy * 0.5, boy * 0.54), "P", font=yazitipi(int(boy * 0.62)),
           fill=(255, 255, 255), anchor="mm")
    n = int(boy * 0.1)
    d.ellipse([boy * 0.72 - n, boy * 0.2 - n, boy * 0.72 + n, boy * 0.2 + n], fill=VURGU)
    im.save(yol, "PNG", optimize=True)
    return os.path.getsize(yol)

MANIFEST = {
    "name": "nereyeparkedicem — Türkiye otopark haritası",
    "short_name": "parkedicem",
    "description": "81 ilde otopark konumu, İstanbul'da canlı doluluk ve tarife.",
    "start_url": "/",
    "scope": "/",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#0b3d2e",
    "lang": "tr",
    "icons": [
        {"src": "/simge-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "/simge-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "any"},
        {"src": "/simge-maskable-512.png", "sizes": "512x512", "type": "image/png",
         "purpose": "maskable"},
        {"src": "/simge.svg", "sizes": "any", "type": "image/svg+xml"},
    ],
    "shortcuts": [
        {"name": "Harita", "url": "/harita/"},
        {"name": "Ücretsiz otoparklar", "url": "/ucretsiz-otopark/"},
    ],
}

def ico(yol):
    """Tarayicilar <link rel=icon> olsa bile /favicon.ico istiyor; olculdu: 404.
    Cok boyutlu ICO tek dosyada."""
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 63, 63], radius=14, fill=YESIL)
    d.text((32, 34), "P", font=yazitipi(40), fill=(255, 255, 255), anchor="mm")
    d.ellipse([40, 6, 52, 18], fill=VURGU)
    im.save(yol, "ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    return os.path.getsize(yol)

def maskable(boy, yol):
    """Maskable ikon KENARDAN KENARA dolu olmali. Olculdu: simge-512.png
    koselerinin alfasi 0 oldugu hâlde manifest 'any maskable' diyordu ->
    Android maskeleyince ikon kirpiliyordu. Guvenli alan %80 (ic daire)."""
    im = Image.new("RGBA", (boy, boy), YESIL + (255,))
    d = ImageDraw.Draw(im)
    d.text((boy * 0.5, boy * 0.53), "P", font=yazitipi(int(boy * 0.44)),
           fill=(255, 255, 255), anchor="mm")
    n = int(boy * 0.07)
    d.ellipse([boy * 0.65 - n, boy * 0.33 - n, boy * 0.65 + n, boy * 0.33 + n], fill=VURGU)
    im.save(yol, "PNG", optimize=True)
    return os.path.getsize(yol)

def yaz():
    os.makedirs(CIKTI, exist_ok=True)
    open(f"{CIKTI}/simge.svg", "w", encoding="utf-8").write(SVG)
    boy = {b: png(b, f"{CIKTI}/simge-{b}.png") for b in (180, 192, 512)}
    boy["ico"] = ico(f"{CIKTI}/favicon.ico")
    boy["maskable"] = maskable(512, f"{CIKTI}/simge-maskable-512.png")
    json.dump(MANIFEST, open(f"{CIKTI}/manifest.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return boy

if __name__ == "__main__":
    b = yaz()
    print("simge.svg", len(SVG), "bayt")
    for k, v in b.items():
        ad = {"ico": "favicon.ico", "maskable": "simge-maskable-512.png"}.get(k, f"simge-{k}.png")
        print(f"{ad} {v:,} bayt")
    print("manifest.json", os.path.getsize(f"{CIKTI}/manifest.json"), "bayt")
