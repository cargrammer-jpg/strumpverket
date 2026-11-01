#!/usr/bin/env python3
"""Generates index.html from the template pieces below. Run: python3 tools/build.py"""
import re, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

def icon_path(name):
    svg = (ROOT / "tools" / "icons" / f"si-{name}.svg").read_text()
    return re.search(r' d="([^"]+)"', svg).group(1)

SOCIAL = [("instagram","Instagram"),("x","X"),("tiktok","TikTok"),("youtube","YouTube"),("facebook","Facebook"),("pinterest","Pinterest")]
socials = "\n".join(
    f'<li><a href="#" aria-label="Strumpverket på {label} (kommer snart)"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{icon_path(n)}"/></svg></a></li>'
    for n, label in SOCIAL)

PRODUCTS = [
    dict(id="ankel", nr="01", name="Ankel", price=129, img="ankel", alt="Ett par svarta ankelstrumpor liggande sida vid sida på ljus bakgrund",
         desc="Låg modell med ribbad kant. För sneakers, loafers och varma dagar.", meta="Låg"),
    dict(id="vardag", nr="02", name="Vardag", price=149, img="vardag", alt="Ett par svarta mellanhöga strumpor med ribbat skaft på ljus bakgrund",
         desc="Mellanhög med ribbat skaft. Den du tar på dig varje morgon.", meta="Mellanhög"),
    dict(id="kna", nr="03", name="Knästrumpa", price=179, img="kna", alt="Ett par långa svarta knästrumpor liggande parallellt på ljus bakgrund",
         desc="Lång och slät. För kostym, kängor och kalla dagar.", meta="Knähög"),
    dict(id="fyrpack", nr="04", name="Fyrpack Vardag", price=499, img="3pack", alt="Fyra vikta par svarta strumpor staplade på varandra på ljus bakgrund",
         desc="Fyra par Vardag. Samma strumpa, färre beslut.", meta="4 par"),
]
SIZES = ["36-40", "41-45", "46-48"]

def picture(img, alt, sizes, widths, w, h, lazy=True, cls=""):
    def srcset(ext): return ", ".join(f"assets/img/{img}-{x}.{ext} {x}w" for x in widths)
    load = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture{c}><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
            f'<img src="assets/img/{img}-{widths[-1]}.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" alt="{alt}" width="{w}" height="{h}" {load}></picture>')

ARROW = '<svg class="btn__arrow" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M3 10h13M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
CHECK = '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

def add_button(label="Lägg i varukorg", desc=""):
    d = f' aria-describedby="{desc}"' if desc else ""
    return (f'<button class="btn add-btn" type="submit"{d}><span class="add-btn__label">{label}</span>'
            f'<span class="add-btn__done" aria-hidden="true">{CHECK} Tillagd</span></button>')

def size_fieldset(pid, default="41-45"):
    opts = "".join(
        f'<label class="chip"><input type="radio" name="storlek" value="{s}"{" checked" if s==default else ""}><span>{s}</span></label>'
        for s in SIZES)
    return f'<fieldset class="sizes"><legend class="label">Storlek</legend><div class="sizes__opts">{opts}</div></fieldset>'

cards = []
for i, p in enumerate(PRODUCTS):
    pic = picture(p["img"], p["alt"], "(min-width: 72rem) 22vw, (min-width: 34rem) 46vw, 92vw", [400, 768], 768, 1024)
    cards.append(f'''
<li>
<form class="product" data-product="{p["id"]}" data-name="{p["name"]}" data-price="{p["price"]}" data-img="assets/img/{p["img"]}-400.webp" data-reveal style="--d:{i}" aria-labelledby="p-{p["id"]}">
  <div class="product__media">{pic}<span class="product__tag">Nr. {p["nr"]}</span></div>
  <div class="product__placard">
    <div class="product__row"><h3 class="product__name" id="p-{p["id"]}">{p["name"]}</h3><p class="product__price">{p["price"]} kr</p></div>
    <div class="product__meta"><p class="label">{p["meta"]} · Bambuviskos</p><p class="label">Exempelpris</p></div>
    <p class="product__desc">{p["desc"]}</p>
    {size_fieldset(p["id"])}
    {add_button(desc="p-" + p["id"])}
  </div>
</form>
</li>''')

box_pic = picture("lada", "En öppen vit kartong med fem rullade par svarta strumpor", "(min-width: 60rem) 44vw, 92vw", [400, 768], 768, 1024)
mat_pic = picture("material", "Närbild på svart stickad strumptextil som ligger på ljust linne", "(min-width: 60rem) 46vw, 92vw", [640, 1024], 1024, 768)

FAQ = [
 ("Är det här en riktig butik?", "Inte än. Det här är en exempelsajt för Strumpverket. Produkter, priser och bilder är exempel och inga köp kan genomföras."),
 ("Varför bara svarta strumpor?", "Svart fungerar till kostym, jeans och träningsskor. När alla par är likadana behöver du aldrig para ihop strumpor efter tvätten, och ett borttappat par spelar ingen roll."),
 ("Vad är bambuviskos?", "En viskosfiber som tillverkas av cellulosa från bambu. Den är mjuk och slät mot huden och används ofta i strumpor och underkläder. För stretch och hållbarhet blandas den nästan alltid med andra fibrer, till exempel polyamid och elastan."),
 ("Hur tvättar jag strumporna?", "Ett allmänt råd för viskosblandningar är att tvätta i 40 grader, gärna ut och in, och låta dem lufttorka. Exakta skötselråd anges på förpackningen när sortimentet lanseras."),
 ("Vilken storlek ska jag välja?", "Strumporna planeras i tre storlekar: 36-40, 41-45 och 46-48. Ligger du mellan två storlekar är den större ofta det bekvämare valet."),
 ("Hur ska Strumplådan fungera?", "Tanken är att du väljer storlek och intervall, så kommer fem par Vardag hem till dig med jämna mellanrum. Du ska kunna pausa eller avsluta när du vill. Tjänsten är inte lanserad ännu."),
]
faq_html = "\n".join(
  f'<details><summary>{q}<span class="plus" aria-hidden="true"></span></summary><div class="answer"><p>{a}</p></div></details>' for q, a in FAQ)

ld = [
  {"@context":"https://schema.org","@type":"Organization","name":"Strumpverket","url":"https://strumpverket.se/",
   "logo":"https://strumpverket.se/android-chrome-512.png","description":"Exempelsajt för en butik som endast säljer svarta strumpor i bambuviskos."},
  {"@context":"https://schema.org","@type":"ItemList","name":"Strumpor (exempel)","itemListElement":[
    {"@type":"ListItem","position":i+1,"item":{"@type":"Product","name":f'{p["name"]} svart strumpa',
     "description":p["desc"]+" Exempelprodukt.","image":f'https://strumpverket.se/assets/img/{p["img"]}-768.jpg',
     "color":"Svart","material":"Bambuviskos","brand":{"@type":"Brand","name":"Strumpverket"},
     "offers":{"@type":"Offer","price":str(p["price"]),"priceCurrency":"SEK","availability":"https://schema.org/PreOrder","url":f'https://strumpverket.se/#strumpor'}}}
    for i,p in enumerate(PRODUCTS)]}
]
ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)


css = (ROOT / "assets" / "css" / "main.css").read_text()
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
css = re.sub(r"\s+", " ", css)
css = re.sub(r"\s*([{};,>])\s*", r"\1", css).replace(";}", "}").replace("../fonts/", "assets/fonts/")
tpl = (ROOT / "tools" / "index.template.html").read_text()
out = (tpl.replace("{{SOCIALS}}", socials).replace("{{CARDS}}", "".join(cards))
          .replace("{{BOX_PIC}}", box_pic).replace("{{MAT_PIC}}", mat_pic).replace("{{FAQ}}", faq_html)
          .replace("{{LD}}", ld_html)
          .replace("{{SIZES_BOX}}", size_fieldset("lada")).replace("{{ADD_BOX}}", add_button("Lägg Strumplådan i varukorg"))
          .replace("{{ARROW}}", ARROW).replace("{{CSS}}", css))
assert "{{" not in out, re.findall(r"\{\{\w+\}\}", out)
bad = [c for c in out if c in "\u2013\u2014"]
assert not bad, "en/em dash found"
(ROOT / "index.html").write_text(out)
print("index.html", len(out))
