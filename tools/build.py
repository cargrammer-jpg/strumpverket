#!/usr/bin/env python3
"""Generate the static site. Run: python3 tools/build.py

Public page URLs (canonical, sitemap, robots, og:url, JSON-LD url) use SITE.
Image URLs that must resolve today (og:image, twitter:image, JSON-LD image and
logo) use ASSET_ORIGIN.

Go-live switch, one line, once https://strumpverket.se answers:
    ASSET_ORIGIN = SITE
That moves og:image, twitter:image and JSON-LD images onto the shop domain.
Page URLs already point at SITE and do not move.
"""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# --- origins (see module docstring) ---
SITE = "https://strumpverket.se"
ASSET_ORIGIN = "https://cargrammer-jpg.github.io/strumpverket"

LASTMOD = "2026-11-02"
OG_HOME = f"{ASSET_ORIGIN}/assets/og.jpg?v=2"
OG_HOME_ALT = "Strumpverkets logotyp, en svart skylt med texten STRUMPVERKET, bredvid rubriken Svarta strumpor. Inget annat."
MATERIAL = "Exempel på materialsammansättning: 80 % bambuviskos, 17 % polyamid, 3 % elastan. Slutlig sammansättning anges när sortimentet är klart."
CARE = "Tvätta i 40 grader, gärna ut och in, och låt strumporna lufttorka. Exakta skötselråd anges på förpackningen när sortimentet lanseras."
MAT_ALT = "Närbild på svart stickad strumptextil som ligger på ljust linne"

# EU shoe size to the sock size already used in the shop. Same interval for
# every model until the supplier confirms a real measurement. Grouped rows,
# not a claim that the socks have been fitted.
SHOE_ROWS = [
    ("36, 37, 38, 39, 40", "36-40"),
    ("41, 42, 43, 44, 45", "41-45"),
    ("46, 47, 48", "46-48"),
]

def icon_path(name):
    svg = (ROOT / "tools" / "icons" / f"si-{name}.svg").read_text()
    return re.search(r' d="([^"]+)"', svg).group(1)

SOCIAL = [
    ("instagram", "Instagram", "https://www.instagram.com/strumpverket/"),
    ("x", "X", "https://x.com/strumpverket"),
    ("tiktok", "TikTok", "https://www.tiktok.com/@strumpverket"),
]
socials = "\n".join(
    f'<li><a href="{url}" target="_blank" rel="noopener noreferrer" aria-label="STRUMPVERKET på {label}"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{icon_path(n)}"/></svg></a></li>'
    for n, label, url in SOCIAL)
SAME_AS = [url for _, _, url in SOCIAL]

PRODUCTS = [
    dict(id="ankel", slug="ankel", nr="01", name="Ankel", price=129, img="ankel",
         alt="Ett par svarta ankelstrumpor liggande sida vid sida på ljus bakgrund",
         desc="Låg modell med ribbad kant. För sneakers, loafers och varma dagar.",
         more="Ankel slutar strax ovanför skon. Ribben håller strumpan på plats. Samma svarta stickning som de andra modellerna.",
         meta="Låg",
         title="Ankel · Svart strumpa | Strumpverket",
         og_title="Ankel · Svart strumpa",
         blurb="Svart ankelstrumpa i bambuviskos. Låg modell med ribbad kant för sneakers och loafers."),
    dict(id="vardag", slug="vardag", nr="02", name="Vardag", price=149, img="vardag",
         alt="Ett par svarta mellanhöga strumpor med ribbat skaft på ljus bakgrund",
         desc="Mellanhög med ribbat skaft. Den du tar på dig varje morgon.",
         more="Vardag når upp över ankeln. Det är den här modellen som ligger i Fyrpack Vardag och i Strumplådan.",
         meta="Mellanhög",
         title="Vardag · Svart strumpa | Strumpverket",
         og_title="Vardag · Svart strumpa",
         blurb="Svart mellanhög strumpa i bambuviskos. Vardag har ribbat skaft och är den du tar på dig varje morgon."),
    dict(id="kna", slug="knastrumpa", nr="03", name="Knästrumpa", price=179, img="kna",
         alt="Ett par långa svarta knästrumpor liggande parallellt på ljus bakgrund",
         desc="Lång och slät. För kostym, kängor och kalla dagar.",
         more="Knästrumpan går högre upp på benet och kan kännas snävare än Ankel och Vardag i samma storlek. Ligger du på gränsen, börja med den större.",
         meta="Knähög",
         title="Knästrumpa · Svart strumpa | Strumpverket",
         og_title="Knästrumpa · Svart strumpa",
         blurb="Svart knästrumpa i bambuviskos. Lång och slät, för kostym, kängor och kalla dagar."),
    dict(id="fyrpack", slug="fyrpack", nr="04", name="Fyrpack Vardag", price=499, img="3pack",
         alt="Fyra vikta par svarta strumpor staplade på varandra på ljus bakgrund",
         desc="Fyra par Vardag. Samma strumpa, färre beslut.",
         more="Paketet innehåller fyra par av modellen Vardag, i en och samma storlek.",
         meta="4 par",
         title="Fyrpack Vardag · Svarta strumpor | Strumpverket",
         og_title="Fyrpack Vardag · Svarta strumpor",
         blurb="Fyra par Vardag, svarta strumpor i bambuviskos.",
         pack_of="vardag", pack_count=4, save_as="kr"),
]
BY_ID = {p["id"]: p for p in PRODUCTS}
BOX = dict(price=549, pack_of="vardag", pack_count=5, save_as="pct")
SIZES = ["36-40", "41-45", "46-48"]

def deal_for(price, pack_of, pack_count):
    """Savings against loose pairs. Prices come from PRODUCTS / BOX, never from a brief."""
    unit = BY_ID[pack_of]["price"]
    full = unit * pack_count
    saved = full - price
    if saved <= 0:
        raise SystemExit(f"no saving: {price} kr vs {pack_count} x {unit} kr")
    pct = int(round(saved * 100 / full))
    return dict(unit=unit, count=pack_count, full=full, saved=saved, pct=pct, of=pack_of)

def badge_label(deal, save_as):
    if save_as == "pct":
        return f"Spara {deal['pct']} %"
    return f"Spara {deal['saved']} kr"

def deal_detail(deal):
    return (f"{deal['saved']} kr billigare än {deal['count']} lösa par à {deal['unit']} kr, "
            f"totalt {deal['full']} kr ({deal['pct']} %).")

FYR_DEAL = deal_for(BY_ID["fyrpack"]["price"], "vardag", 4)
BOX_DEAL = deal_for(BOX["price"], BOX["pack_of"], BOX["pack_count"])

def picture(img, alt, sizes, widths, w, h, lazy=True, priority=""):
    def srcset(ext):
        return ", ".join(f"{{{{ROOT}}}}assets/img/{img}-{n}.{ext} {n}w" for n in widths)
    attrs = []
    if priority == "high":
        attrs.append('fetchpriority="high"')
    elif priority == "low":
        attrs.append('fetchpriority="low"')
    if lazy:
        attrs.append('loading="lazy"')
    if priority == "high" and lazy:
        raise SystemExit("fetchpriority=high must not be combined with loading=lazy")
    attrs.append('decoding="async"')
    extra = " ".join(attrs)
    return (
        f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
        f'<source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
        f'<img src="{{{{ROOT}}}}assets/img/{img}-{widths[-1]}.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" alt="{alt}" width="{w}" height="{h}" {extra}></picture>'
    )

ARROW = '<svg class="btn__arrow" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M3 10h13M11 5l5 5-5 5" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>'
CHECK = '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'

def add_button(label="Lägg i varukorg", desc=""):
    d = f' aria-describedby="{desc}"' if desc else ""
    return (f'<button class="btn add-btn" type="submit"{d}><span class="add-btn__label">{label}</span>'
            f'<span class="add-btn__done" aria-hidden="true">{CHECK} Tillagd</span></button>')

def size_fieldset(default="41-45"):
    opts = "".join(
        f'<label class="chip"><input type="radio" name="storlek" value="{s}"{" checked" if s==default else ""}><span>{s}</span></label>'
        for s in SIZES)
    return f'<fieldset class="sizes"><legend class="label">Storlek</legend><div class="sizes__opts">{opts}</div></fieldset>'

def guide_link():
    return '<p class="size-extra"><a class="u-link hit" href="{{ROOT}}storleksguide/#tabell">Storleksguide</a></p>'

CARD_SIZES = "(min-width: 72rem) 22vw, 46vw"

def card_price(p, deal):
    if not deal:
        return f'<p class="product__price">{p["price"]} kr</p>'
    return (
        f'<p class="product__price"><del class="price-was"><span class="visually-hidden">Ordinarie pris </span>{deal["full"]} kr</del>'
        f'<span class="price-now"><span class="visually-hidden">Pris </span>{p["price"]} kr</span></p>'
    )

def card_save(deal, save_as):
    if not deal:
        return ""
    return (f'<p class="save-line"><span class="save-badge">{badge_label(deal, save_as)}</span>'
            f'<span class="visually-hidden"> {deal_detail(deal)}</span></p>')

cards = []
for i, p in enumerate(PRODUCTS):
    deal = deal_for(p["price"], p["pack_of"], p["pack_count"]) if p.get("pack_of") else None
    pic = picture(p["img"], p["alt"], CARD_SIZES, [400, 768], 768, 1024)
    href = "{{ROOT}}strumpor/" + p["slug"] + "/"
    cards.append(f'''
<li class="product-card" data-reveal style="--d:{i}">
  <a class="product__media-link" href="{href}">
    <span class="visually-hidden">Produktsida för {p["name"]}. </span>
    <div class="product__media">{pic}<span class="product__tag" aria-hidden="true">Nr. {p["nr"]}</span></div>
  </a>
  <form class="product" data-product="{p["id"]}" data-name="{p["name"]}" data-price="{p["price"]}" data-img="assets/img/{p["img"]}-400.webp" aria-labelledby="p-{p["id"]}">
    <div class="product__placard">
      <div class="product__row">
        <h3 class="product__name" id="p-{p["id"]}"><a class="u-link hit-slop" href="{href}">{p["name"]}</a></h3>
        {card_price(p, deal)}
      </div>
      <div class="product__meta"><p class="label">{p["meta"]} · Bambuviskos</p></div>
      {card_save(deal, p.get("save_as", "kr"))}
      <p class="product__desc">{p["desc"]}</p>
      {size_fieldset()}
      {guide_link()}
      {add_button(desc="p-" + p["id"])}
    </div>
  </form>
</li>''')

box_pic = picture("lada", "En öppen vit kartong med fem rullade par svarta strumpor", "(min-width: 60rem) 44vw, 92vw", [400, 768], 768, 1024)
mat_pic = picture("material", MAT_ALT, "(min-width: 60rem) 46vw, 92vw", [640, 1024], 1024, 768)
box_price = (
    f'<div class="box__price"><del class="price-was"><span class="visually-hidden">Ordinarie pris </span>{BOX_DEAL["full"]} kr</del>'
    f'<strong><span class="visually-hidden">Pris </span>{BOX["price"]} kr</strong>'
    f'<span class="save-badge">{badge_label(BOX_DEAL, "pct")}</span>'
    f'<span class="visually-hidden"> {deal_detail(BOX_DEAL)}</span>'
    f'<span class="label">per leverans</span></div>'
)

FAQ = [
 ("Är det här en riktig butik?", "Inte än. Det här är en exempelsajt för Strumpverket. Produkter, priser och bilder är exempel och inga köp kan genomföras."),
 ("Varför bara svarta strumpor?", "Svart fungerar till kostym, jeans och träningsskor. När alla par är likadana behöver du aldrig para ihop strumpor efter tvätten, och ett borttappat par spelar ingen roll."),
 ("Vad är bambuviskos?", "En viskosfiber som tillverkas av cellulosa från bambu. Den är mjuk och slät mot huden och används ofta i strumpor och underkläder. För stretch och hållbarhet blandas den nästan alltid med andra fibrer, till exempel polyamid och elastan."),
 ("Hur tvättar jag strumporna?", "Ett allmänt råd för viskosblandningar är att tvätta i 40 grader, gärna ut och in, och låta dem lufttorka. Exakta skötselråd anges på förpackningen när sortimentet lanseras."),
 ("Vilken storlek ska jag välja?", 'Strumporna planeras i tre storlekar: 36-40, 41-45 och 46-48. Ligger du mellan två storlekar är den större ofta det bekvämare valet. I <a class="u-link hit" href="{{ROOT}}storleksguide/#tabell">storleksguiden</a> ser du vilken strumpstorlek som hör till din skostorlek. Måtten ska bekräftas med leverantören.'),
 ("Hur ska Strumplådan fungera?", "Tanken är att du väljer storlek och intervall, så kommer fem par Vardag hem till dig med jämna mellanrum. Du ska kunna pausa eller avsluta när du vill. Tjänsten är inte lanserad ännu."),
]
faq_html = "\n".join(
  f'<details><summary>{q}<span class="plus" aria-hidden="true"></span></summary><div class="answer"><p>{a}</p></div></details>' for q, a in FAQ)

def schema_name(p):
    if p["id"] == "fyrpack":
        return "Fyrpack Vardag, svarta strumpor"
    return f'{p["name"]} svart strumpa'

def product_path(p):
    return f'/strumpor/{p["slug"]}/'

def abs_page(path):
    return SITE + path

def product_ld_item(p, position=None):
    deal = deal_for(p["price"], p["pack_of"], p["pack_count"]) if p.get("pack_of") else None
    desc = p["desc"] + " Exempelprodukt."
    if deal:
        desc += " " + deal_detail(deal)
    item = {
        "@type": "Product",
        "name": schema_name(p),
        "description": desc,
        "image": f'{ASSET_ORIGIN}/assets/img/{p["img"]}-768.jpg',
        "sku": p["id"],
        "color": "Svart",
        "material": "Bambuviskos",
        "brand": {"@type": "Brand", "name": "Strumpverket"},
        "offers": {
            "@type": "Offer",
            "price": str(p["price"]),
            "priceCurrency": "SEK",
            "availability": "https://schema.org/PreOrder",
            "url": abs_page(product_path(p)),
        },
    }
    if position is None:
        return item
    return {"@type": "ListItem", "position": position, "item": item}

def ld_scripts(blocks):
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in blocks)

home_ld = ld_scripts([
    {"@context": "https://schema.org", "@type": "Organization", "name": "Strumpverket",
     "url": abs_page("/"), "logo": f"{ASSET_ORIGIN}/android-chrome-512.png",
     "sameAs": SAME_AS,
     "description": "Exempelsajt för en butik som endast säljer svarta strumpor i bambuviskos."},
    {"@context": "https://schema.org", "@type": "ItemList", "name": "Strumpor (exempel)",
     "itemListElement": [product_ld_item(p, i + 1) for i, p in enumerate(PRODUCTS)]},
])

def crumbs(items):
    parts = []
    for i, (name, href) in enumerate(items):
        if i:
            parts.append('<span aria-hidden="true">/</span>')
        if href:
            parts.append(f'<a class="u-link hit" href="{href}">{name}</a>')
        else:
            parts.append(f'<span aria-current="page">{name}</span>')
    return f'<nav class="crumbs" aria-label="Brödsmulor">{"".join(parts)}</nav>'

def breadcrumb_ld(items):
    """items: list of (name, absolute url or None for current)."""
    elements = []
    for i, (name, url) in enumerate(items, start=1):
        el = {"@type": "ListItem", "position": i, "name": name}
        if url:
            el["item"] = url
        elements.append(el)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": elements}

PDP_SIZES = "(min-width: 60rem) 46vw, 92vw"

def product_main(p):
    deal = deal_for(p["price"], p["pack_of"], p["pack_count"]) if p.get("pack_of") else None
    hero = picture(p["img"], p["alt"], PDP_SIZES, [400, 768], 768, 1024, lazy=False, priority="high")
    detail = picture("material", MAT_ALT, PDP_SIZES, [640, 1024], 1024, 768, lazy=True)
    if deal:
        price = (
            f'<div class="pdp__price"><del class="price-was"><span class="visually-hidden">Ordinarie pris </span>{deal["full"]} kr</del>'
            f'<strong><span class="visually-hidden">Pris </span>{p["price"]} kr</strong>'
            f'<span class="save-badge">{badge_label(deal, p.get("save_as", "kr"))}</span>'
            f'<span class="visually-hidden"> {deal_detail(deal)}</span></div>'
        )
    else:
        price = f'<div class="pdp__price"><strong>{p["price"]} kr</strong></div>'
    others = []
    for other in PRODUCTS:
        if other["id"] == p["id"]:
            continue
        others.append(
            f'<li><a href="{{{{ROOT}}}}strumpor/{other["slug"]}/"><span>{other["name"]}</span>'
            f'<span class="label">{other["price"]} kr</span></a></li>'
        )
    return f'''
<div class="wrap pdp-page">
  {crumbs([("Startsida", "{{ROOT}}"), ("Strumpor", "{{ROOT}}#strumpor"), (p["name"], None)])}
  <article class="pdp">
    <div class="pdp__gallery">
      <div class="gallery">
        <figure>{hero}<figcaption class="label">Fig. 01 · {p["name"]}</figcaption></figure>
        <figure>{detail}<figcaption class="label">Fig. 02 · Stickning i närbild</figcaption></figure>
      </div>
    </div>
    <div class="pdp__info">
      <p class="label pdp__label">Nr. {p["nr"]} · {p["meta"]} · Bambuviskos</p>
      <h1>{p["name"]}</h1>
      <p class="pdp__lede">{p["desc"]}</p>
      <p class="pdp__more-text">{p["more"]}</p>
      {price}
      <p class="callout">Exempelpris. Siffran kan ändras innan öppning.</p>
      <form class="pdp__form" data-product="{p["id"]}" data-name="{p["name"]}" data-price="{p["price"]}" data-img="assets/img/{p["img"]}-400.webp" aria-label="{p["name"]}">
        {size_fieldset()}
        {guide_link()}
        {add_button()}
      </form>
      <section class="pdp__block"><h2>Material</h2><p>{MATERIAL}</p></section>
      <section class="pdp__block"><h2>Skötsel</h2><p>{CARE}</p></section>
    </div>
  </article>
  <aside class="pdp__more">
    <h2>Andra modeller</h2>
    <ul class="related">{"".join(others)}</ul>
  </aside>
</div>'''

def guide_main():
    head = "".join(f"<th scope=\"col\">{name}</th>" for name in ("EU-skostorlek", "Ankel", "Vardag", "Knä<wbr>strumpa"))
    body = []
    for shoes, sock in SHOE_ROWS:
        body.append(
            "<tr>"
            f"<th scope=\"row\">{shoes}</th>"
            f"<td>{sock}</td><td>{sock}</td><td>{sock}</td>"
            "</tr>"
        )
    models = "".join(
        f'<li><a href="{{{{ROOT}}}}strumpor/{p["slug"]}/"><span>{p["name"]}</span><span class="label">{p["price"]} kr</span></a></li>'
        for p in PRODUCTS)
    return f'''
<article class="guide wrap">
  {crumbs([("Startsida", "{{ROOT}}"), ("Storleksguide", None)])}
  <h1>Storleksguide</h1>
  <p class="lede">Tre strumpstorlekar, valda efter skostorlek. Fyrpack och Strumplådan är Vardag, så de följer den kolumnen.</p>
  <p class="callout">Att bekräfta med leverantören. Tabellen är ett vanligt EU-intervall, inte ett mått på Strumpverkets egna plagg. Inget plagg är i produktion ännu.</p>
  <div class="table-wrap" id="tabell">
    <table class="size-table">
      <caption>EU-skostorlek till strumpstorlek per modell</caption>
      <thead><tr>{head}</tr></thead>
      <tbody>{"".join(body)}</tbody>
    </table>
  </div>
  <h2>Mellan två storlekar</h2>
  <p>Välj den större. Knästrumpan sitter högre och kan kännas snävare än Ankel och Vardag. Sko 35 och mindre, och sko 49 och större, ryms inte i de planerade storlekarna.</p>
  <h2>Så är intervallen satta</h2>
  <p>36-40, 41-45 och 46-48 är vanliga strumpintervall i EU-skor. Tills leverantören säger annat använder alla tre modeller samma karta. Då kan kolumnerna skilja sig åt, och den här sidan uppdateras.</p>
  <h2>Modellerna</h2>
  <ul class="related">{models}</ul>
</article>'''

def css_for(prefix):
    css = (ROOT / "assets" / "css" / "main.css").read_text()
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css).replace(";}", "}")
    css = css.replace("../fonts/", "assets/fonts/")
    if prefix:
        css = css.replace("assets/fonts/", f"{prefix}assets/fonts/")
    return css

SHELL = (ROOT / "tools" / "shell.template.html").read_text()
HOME = (ROOT / "tools" / "home.html").read_text()
HOME_EXTRA = ('<link rel="preload" as="image" type="image/avif" '
              'imagesrcset="{{ROOT}}assets/img/hero-640.avif 640w, {{ROOT}}assets/img/hero-1280.avif 1280w" '
              'imagesizes="(min-width: 90rem) 84rem, 94vw" fetchpriority="high">')

def render(prefix, main, meta):
    html = SHELL.replace("{{MAIN}}", main).replace("{{SOCIALS}}", socials)
    html = html.replace("{{CSS}}", css_for(prefix))
    html = html.replace("{{EXTRA_HEAD}}", meta.get("extra", ""))
    html = html.replace("{{LD}}", meta.get("ld", ""))
    for key in ("TITLE", "OG_TITLE", "DESCRIPTION", "CANONICAL", "OG_IMAGE", "OG_W", "OG_H", "OG_ALT"):
        html = html.replace("{{" + key + "}}", meta[key])
    html = html.replace("{{ARROW}}", ARROW).replace("{{ROOT}}", prefix)
    leftover = re.findall(r"\{\{[A-Z0-9_]+\}\}", html)
    if leftover:
        raise SystemExit(f"unreplaced placeholders: {leftover}")
    bad = [c for c in html if c in "\u2013\u2014"]
    if bad:
        raise SystemExit("en/em dash found")
    return html

def write(rel, html):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html)
    print(rel, len(html))

home_main = (HOME.replace("{{CARDS}}", "".join(cards))
             .replace("{{BOX_PIC}}", box_pic)
             .replace("{{MAT_PIC}}", mat_pic)
             .replace("{{FAQ}}", faq_html)
             .replace("{{SIZES_BOX}}", size_fieldset())
             .replace("{{ADD_BOX}}", add_button("Lägg Strumplådan i varukorg"))
             .replace("{{BOX_PRICE}}", box_price))

pages = [("index.html", "", home_main, dict(
    TITLE="Strumpverket · Svarta strumpor i bambuviskos. Inget annat.",
    OG_TITLE="Strumpverket · Svarta strumpor. Inget annat.",
    DESCRIPTION="Strumpverket säljer bara en sak: svarta premiumstrumpor i bambuviskos. Ankel, Vardag, Knästrumpa och Strumplådan. Exempelsajt med exempelpriser.",
    CANONICAL=abs_page("/"),
    OG_IMAGE=OG_HOME, OG_W="1200", OG_H="630", OG_ALT=OG_HOME_ALT,
    extra=HOME_EXTRA, ld=home_ld,
))]

guide_desc = "Storleksguide för Strumpverkets svarta strumpor. EU-skostorlek till strumpstorlek för Ankel, Vardag och Knästrumpa. Riktvärden som ska bekräftas med leverantören."
pages.append(("storleksguide/index.html", "../", guide_main(), dict(
    TITLE="Storleksguide | Strumpverket",
    OG_TITLE="Storleksguide | Strumpverket",
    DESCRIPTION=guide_desc,
    CANONICAL=abs_page("/storleksguide/"),
    OG_IMAGE=OG_HOME, OG_W="1200", OG_H="630", OG_ALT=OG_HOME_ALT,
    extra="",
    ld=ld_scripts([breadcrumb_ld([
        ("Startsida", abs_page("/")),
        ("Storleksguide", abs_page("/storleksguide/")),
    ])]),
)))

for p in PRODUCTS:
    deal = deal_for(p["price"], p["pack_of"], p["pack_count"]) if p.get("pack_of") else None
    desc = p["blurb"] + f' Exempelpris {p["price"]} kr.'
    if deal:
        desc += " " + deal_detail(deal)
    desc += " Exempelsajt, inga köp genomförs."
    preload = (
        '<link rel="preload" as="image" type="image/avif" imagesrcset="'
        f'{{{{ROOT}}}}assets/img/{p["img"]}-400.avif 400w, {{{{ROOT}}}}assets/img/{p["img"]}-768.avif 768w" '
        f'imagesizes="{PDP_SIZES}" fetchpriority="high">'
    )
    pages.append((f'strumpor/{p["slug"]}/index.html', "../../", product_main(p), dict(
        TITLE=p["title"],
        OG_TITLE=p["og_title"],
        DESCRIPTION=desc,
        CANONICAL=abs_page(product_path(p)),
        OG_IMAGE=f'{ASSET_ORIGIN}/assets/img/{p["img"]}-768.jpg',
        OG_W="768", OG_H="1024", OG_ALT=p["alt"],
        extra=preload,
        ld=ld_scripts([
            {"@context": "https://schema.org", **product_ld_item(p)},
            breadcrumb_ld([
                ("Startsida", abs_page("/")),
                ("Strumpor", abs_page("/#strumpor")),
                (p["name"], abs_page(product_path(p))),
            ]),
        ]),
    )))

sitemap_paths = ["/"] + [product_path(p) for p in PRODUCTS] + ["/storleksguide/"]
sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path in sitemap_paths:
    sitemap.append(f"  <url><loc>{abs_page(path)}</loc><lastmod>{LASTMOD}</lastmod></url>")
sitemap.append("</urlset>\n")
(ROOT / "sitemap.xml").write_text("\n".join(sitemap))

robots = (
    "# Exempelsajt. Sidorna har dessutom meta robots noindex.\n"
    "User-agent: *\n"
    "Allow: /\n"
    f"Sitemap: {abs_page('/sitemap.xml')}\n"
)
(ROOT / "robots.txt").write_text(robots)

for rel, prefix, main, meta in pages:
    write(rel, render(prefix, main, meta))

print(f"SITE={SITE}")
print(f"ASSET_ORIGIN={ASSET_ORIGIN}")
print("go-live: set ASSET_ORIGIN = SITE, then rebuild")
print(f"Fyrpack: {FYR_DEAL['count']} x {FYR_DEAL['unit']} = {FYR_DEAL['full']}; "
      f"{FYR_DEAL['full']} - {BY_ID['fyrpack']['price']} = {FYR_DEAL['saved']} kr ({FYR_DEAL['pct']} %)")
print(f"Strumplådan: {BOX_DEAL['count']} x {BOX_DEAL['unit']} = {BOX_DEAL['full']}; "
      f"{BOX_DEAL['full']} - {BOX['price']} = {BOX_DEAL['saved']} kr ({BOX_DEAL['pct']} %)")
print("Ankel", BY_ID["ankel"]["price"], "kr and Knästrumpa", BY_ID["kna"]["price"], "kr are single pairs, no badge")
