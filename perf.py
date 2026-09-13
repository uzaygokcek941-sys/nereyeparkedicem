# -*- coding: utf-8 -*-
"""Canli site performans olcumu. LCP / CLS / TTFB / transfer boyutu.
Lighthouse kurulmadi (disk kritik); PerformanceObserver dogrudan okunuyor."""
import sys
from playwright.sync_api import sync_playwright

U = "https://nereyeparkedicem.vercel.app"
SAYFA = ["/", "/ilce/fatih/"]
HEDEF = {"LCP": 2500, "CLS": 0.1, "TTFB": 800, "JS_KB": 150, "CSS_KB": 30}

TOPLA = """() => new Promise(res => {
  const o = {lcp:0, cls:0};
  new PerformanceObserver(l => { for (const e of l.getEntries()) o.lcp = e.startTime; })
    .observe({type:'largest-contentful-paint', buffered:true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if(!e.hadRecentInput) o.cls += e.value; })
    .observe({type:'layout-shift', buffered:true});
  setTimeout(() => {
    const n = performance.getEntriesByType('navigation')[0] || {};
    const r = performance.getEntriesByType('resource');
    const boyut = t => r.filter(x => x.initiatorType === t)
                        .reduce((a,x) => a + (x.transferSize||x.encodedBodySize||0), 0);
    res({lcp:Math.round(o.lcp), cls:+o.cls.toFixed(4),
         ttfb:Math.round(n.responseStart||0), dcl:Math.round(n.domContentLoadedEventEnd||0),
         html:Math.round((n.transferSize||0)/1024*10)/10, cache:(performance.getEntriesByType('navigation')[0]||{}).deliveryType||'',
         js:Math.round(boyut('script')/1024*10)/10, css:Math.round(boyut('link')/1024*10)/10,
         istek:r.length});
  }, 4000);
})"""

kotu = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, ad in [(390, 844, "mobil"), (1440, 900, "masaustu")]:
        for y in SAYFA:
            pg = b.new_page(viewport={"width": w, "height": h})
            # DNS + TLS el sikismasi sayfanin performansi degil: bir kez isit, sonra olc
            pg.goto(U + "/robots.txt", wait_until="load")
            pg.goto(U + y, wait_until="load")
            m = pg.evaluate(TOPLA)
            print(f"{ad:<10}{y:<16} LCP {m['lcp']:>5}ms  CLS {m['cls']:<7} TTFB {m['ttfb']:>4}ms  "
                  f"HTML {m['html']:>5}KB  JS {m['js']:>5}KB  CSS {m['css']:>5}KB  istek {m['istek']}")
            if m["lcp"] > HEDEF["LCP"]:  kotu.append(f"{ad}{y}: LCP {m['lcp']}ms > {HEDEF['LCP']}")
            if m["cls"] > HEDEF["CLS"]:  kotu.append(f"{ad}{y}: CLS {m['cls']} > {HEDEF['CLS']}")
            if m["ttfb"] > HEDEF["TTFB"]:kotu.append(f"{ad}{y}: TTFB {m['ttfb']}ms > {HEDEF['TTFB']}")
            if m["js"] > HEDEF["JS_KB"]: kotu.append(f"{ad}{y}: JS {m['js']}KB > {HEDEF['JS_KB']}")
            if m["css"] > HEDEF["CSS_KB"]:kotu.append(f"{ad}{y}: CSS {m['css']}KB > {HEDEF['CSS_KB']}")
            pg.close()
    b.close()
print("\nHEDEF ASIMI:", len(kotu)); [print("  x", x) for x in kotu]
sys.exit(1 if kotu else 0)
