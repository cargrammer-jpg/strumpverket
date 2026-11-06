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
ASSET_ORIGIN = SITE

LASTMOD = "2026-11-06"
OG_HOME = f"{ASSET_ORIGIN}/assets/og.jpg?v=3"
OG_HOME_ALT = "Strumpverkets logotyp, en svart skylt med texten STRUMPVERKET, bredvid rubriken Svarta strumpor. Inget annat."
MATERIAL = "78\u00a0% viskos från bambu, 18\u00a0% polyamid, 4\u00a0% lycra."
CARE = "Tvätta i 40 grader, gärna ut och in, och låt strumporna lufttorka. Exakta skötselråd står på förpackningen."
MAT_ALT = "Närbild på svart stickad strumptextil som ligger på ljust linne"
SHIPPING = 39
SHIP_LINE = f"Frakt {SHIPPING} kr tillkommer. PostNord till din brevlåda."
CHECKOUT_SOON = "Kassan öppnar snart. Du kan lägga strumporna i varukorgen redan nu, men inga köp genomförs och ingen betalning dras ännu."

# EU shoe size to sock size. Same interval until the supplier confirms a
# real measurement. Grouped rows, not a claim that the socks have been fitted.
SHOE_ROWS = [
    ("36, 37, 38, 39, 40", "36-40"),
    ("41, 42, 43, 44, 45", "41-45"),
    ("46, 47, 48", "46-48"),
]

def icon_path(name):
    svg = (ROOT / "tools" / "icons" / f"si-{name}.svg").read_text()
    return re.search(r' d="([^"]+)"', svg).group(1)

SOCIAL = [
    ("instagram", "Instagram", "https://www.instagram.com/strumpverket"),
    ("x", "X", "https://x.com/STRUMPVERKET"),
    ("tiktok", "TikTok", "https://www.tiktok.com/@strumpverket.se"),
]
def social_svg(n):
    d = icon_path(n)
    if n == "tiktok":
        # TikTok's own look: cyan and red copies offset behind a white mark.
        # Solid vector fills, no filters, so it stays sharp at 1x and 2x.
        return ('<svg viewBox="-1 -1 26 26" aria-hidden="true" focusable="false">'
                f'<path fill="#25F4EE" transform="translate(-0.9 -0.9)" d="{d}"/>'
                f'<path fill="#FE2C55" transform="translate(0.9 0.9)" d="{d}"/>'
                f'<path fill="#FFFFFF" d="{d}"/></svg>')
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{d}"/></svg>'

socials = "\n".join(
    f'<li><a class="soc soc--{n}" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="STRUMPVERKET på {label}">{social_svg(n)}</a></li>'
    for n, label, url in SOCIAL)
SAME_AS = [url for _, _, url in SOCIAL]

PRODUCT_NAME = "Premium bambustrumpor, svarta"
PRODUCTS = [
    dict(id="5-pack", slug="5-pack", nr="01", name="5-pack", pairs=5, price=249, img="lada",
         alt="En öppen vit kartong med fem rullade par svarta strumpor",
         desc="Fem par svarta premiumstrumpor. Lagom för att komma igång.",
         more="Fem likadana par i samma storlek. Alla par matchar varandra, så du slipper para ihop strumpor efter tvätten."),
    dict(id="10-pack", slug="10-pack", nr="02", name="10-pack", pairs=10, price=449, img="3pack",
         alt="Vikta par svarta strumpor staplade på varandra på ljus bakgrund",
         desc="Tio par svarta premiumstrumpor. Byt ut hela lådan på en gång.",
         more="Tio likadana par i samma storlek. Det lägsta priset per par när du köper styckvis."),
]
for _p in PRODUCTS:
    _p["full_name"] = f'Premium bambustrumpor, {_p["name"]}'
    _p["title"] = f'{_p["name"]} premium bambustrumpor, svarta | Strumpverket'
    _p["og_title"] = f'{_p["name"]} premium bambustrumpor, svarta'
    _p["blurb"] = (f'{_p["pairs"]} par svarta premiumstrumpor i viskos från bambu för {_p["price"]} kr inkl. moms. '
                   f'Frakt {SHIPPING} kr tillkommer, PostNord till brevlådan.')
BY_ID = {p["id"]: p for p in PRODUCTS}
SIZES = ["36-40", "41-45", "46-48"]

# Subscriptions: price includes shipping. Saving is shown against buying the
# same pack once and paying shipping, computed here, never typed by hand.
SUBS = [
    dict(id="pren-5", pack="5-pack", every="var 3:e månad", short="Var 3:e månad", price=229),
    dict(id="pren-10", pack="10-pack", every="var 4:e månad", short="Var 4:e månad", price=379),
]
for _s in SUBS:
    _pk = BY_ID[_s["pack"]]
    _s["oneoff"] = _pk["price"] + SHIPPING
    _s["saved"] = _s["oneoff"] - _s["price"]
    if _s["saved"] <= 0:
        raise SystemExit(f'no subscription saving for {_s["id"]}')
    _s["pct"] = int(round(_s["saved"] * 100 / _s["oneoff"]))
SUB_FROM = min(sb["price"] for sb in SUBS)
SUB_MAX_SAVED = max(sb["saved"] for sb in SUBS)
SUB_BY_PACK = {sb["pack"]: sb for sb in SUBS}

def per_pair(p):
    return f'{p["price"] / p["pairs"]:.2f}'.replace(".", ",") + " kr per par"

def pack_saving(p):
    """10-pack against two 5-packs, product price only."""
    small = BY_ID["5-pack"]
    if p["id"] == small["id"]:
        return None
    n = p["pairs"] // small["pairs"]
    full = small["price"] * n
    saved = full - p["price"]
    return dict(full=full, saved=saved, n=n) if saved > 0 else None

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

CARD_SIZES = "(min-width: 40rem) 46vw, 92vw"

def save_badge(p):
    d = pack_saving(p)
    if not d:
        return ""
    return (f'<p class="save-line"><span class="save-badge">Spara {d["saved"]} kr</span>'
            f'<span class="save-note">jämfört med {d["n"]} st 5-pack ({d["full"]} kr)</span></p>')

def form_attrs(p_id, name, price, img, ship):
    return (f'data-product="{p_id}" data-name="{name}" data-price="{price}" '
            f'data-img="assets/img/{img}-400.webp" data-ship="{ship}"')

def sub_nudge(p):
    sb = SUB_BY_PACK.get(p["id"])
    if not sb:
        return ""
    return (f'<a class="sub-nudge" href="{{{{ROOT}}}}#prenumeration"><span class="sub-nudge__tag">Prenumerera</span>'
            f'<span class="sub-nudge__text">{sb["price"]} kr {sb["every"]}, frakt ingår. Spara {sb["saved"]} kr.</span>'
            f'<span class="sub-nudge__arrow" aria-hidden="true">{ARROW}</span></a>')

cards = []
for i, p in enumerate(PRODUCTS):
    pic = picture(p["img"], p["alt"], CARD_SIZES, [400, 768], 768, 1024)
    href = "{{ROOT}}strumpor/" + p["slug"] + "/"
    cards.append(f'''
<li class="product-card" data-reveal style="--d:{i}">
  <a class="product__media-link" href="{href}">
    <span class="visually-hidden">Produktsida för {p["full_name"]}. </span>
    <div class="product__media">{pic}<span class="product__tag" aria-hidden="true">Nr. {p["nr"]}</span></div>
  </a>
  <form class="product" {form_attrs(p["id"], p["full_name"], p["price"], p["img"], 1)} aria-labelledby="p-{p["id"]}">
    <div class="product__placard">
      <div class="product__row">
        <h3 class="product__name" id="p-{p["id"]}"><a class="u-link hit-slop" href="{href}">{p["name"]}</a></h3>
        <p class="product__price"><span class="price-now">{p["price"]} kr</span><span class="price-unit">{per_pair(p)}</span></p>
      </div>
      <div class="product__meta"><p class="label">{p["pairs"]} par · Premium bambustrumpor · Svart</p></div>
      {save_badge(p)}
      <p class="product__desc">{p["desc"]}</p>
      <p class="ship-line"><span>Inkl. moms.</span> <strong>Frakt {SHIPPING} kr tillkommer.</strong> <span>PostNord till brevlådan.</span></p>
      {size_fieldset()}
      {guide_link()}
      {add_button(desc="p-" + p["id"])}
      {sub_nudge(p)}
    </div>
  </form>
</li>''')

sub_cards = []
for i, sb in enumerate(SUBS):
    pk = BY_ID[sb["pack"]]
    featured = sb["saved"] == SUB_MAX_SAVED
    flag = '<span class="sub__flag">Störst besparing</span>' if featured else ""
    sub_cards.append(f'''
<li class="sub-card{" sub-card--featured" if featured else ""}" data-reveal style="--d:{i}">
  <form class="sub" {form_attrs(sb["id"], f'Prenumeration {pk["name"]}, {sb["every"]}', sb["price"], pk["img"], 0)} aria-labelledby="s-{sb["id"]}">
    <div class="sub__top"><p class="label">Prenumeration · {pk["pairs"]} par</p>{flag}</div>
    <h3 class="sub__name" id="s-{sb["id"]}">{pk["name"]} <span>{sb["every"]}</span></h3>
    <p class="sub__price"><strong>{sb["price"]} kr</strong> <span class="sub__per">per leverans, inkl. frakt</span></p>
    <p class="save-line"><span class="save-badge">Spara {sb["saved"]} kr</span><span class="save-note">jämfört med {pk["price"]} kr + {SHIPPING} kr frakt ({sb["oneoff"]} kr)</span></p>
    <ul class="box__list">
      <li>{pk["pairs"]} par i din storlek {sb["every"]}</li>
      <li>Frakten ingår, PostNord till brevlådan</li>
      <li>Ungefär {sb["pct"]}\u00a0% lägre pris per leverans än ett vanligt köp med frakt</li>
    </ul>
    {size_fieldset()}
    {add_button("Lägg prenumerationen i varukorg", desc="s-" + sb["id"])}
  </form>
</li>''')

CHECK_ICON = '<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M4.5 10.5l3.5 3.5 7.5-8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SUB_PERKS_LIST = [
    ("Frakten ingår", "PostNord till brevlådan, utan fraktavgift."),
    (f"Spara upp till {SUB_MAX_SAVED} kr", "per leverans, jämfört med ett vanligt köp med frakt."),
    ("Samma strumpa varje gång", "Bästa kvalitet i varje par, i din storlek."),
]
sub_perks = "".join(f'<li>{CHECK_ICON}<span><strong>{t}</strong> {d}</span></li>' for t, d in SUB_PERKS_LIST)

def sub_highlight(p):
    sb = SUB_BY_PACK.get(p["id"])
    if not sb:
        return ""
    return f'''<aside class="pdp-sub" aria-labelledby="pdp-sub-title">
        <div class="pdp-sub__head"><p class="label pdp-sub__label">Prenumeration · Startar snart</p><span class="save-badge">Spara {sb["saved"]} kr</span></div>
        <h2 id="pdp-sub-title" class="pdp-sub__title">Prenumerera på {p["name"]}, {sb["every"]}</h2>
        <p class="pdp-sub__price"><strong>{sb["price"]} kr</strong> <span>per leverans, frakten ingår</span></p>
        <p class="pdp-sub__text">Jämfört med {p["price"]} kr + {SHIPPING} kr frakt ({sb["oneoff"]} kr) vid ett vanligt köp. Samma strumpa, bästa kvalitet, hem till brevlådan.</p>
        <a class="btn btn--block" href="{{{{ROOT}}}}#prenumeration">Välj prenumeration {{{{ARROW}}}}</a>
      </aside>'''

mat_pic = picture("material", MAT_ALT, "(min-width: 60rem) 46vw, 92vw", [640, 1024], 1024, 768)

FAQ = [
 ("Kan jag beställa redan nu?", "Inte riktigt än. Du kan lägga 5-pack, 10-pack och prenumerationer i varukorgen, men kassan är inte öppen. Inga köp genomförs, ingen betalning dras och inga uppgifter skickas. Följ oss på Instagram (@strumpverket), X (@STRUMPVERKET) och TikTok (@strumpverket.se) så får du veta när vi öppnar."),
 ("Vad kostar frakten?", f"Frakten kostar {SHIPPING} kr per beställning och tillkommer på priset för 5-pack och 10-pack. Vi skickar med PostNord direkt till din brevlåda. I prenumerationen ingår frakten."),
 ("Hur fungerar prenumerationen?", "Du väljer mellan två upplägg. " + " ".join(
     f'{BY_ID[sb["pack"]]["name"]} {sb["every"]} för {sb["price"]} kr inkl. frakt, {sb["saved"]} kr mindre än ett vanligt köp med frakt ({sb["oneoff"]} kr).' for sb in SUBS)
   + " Prenumerationen startar snart och går inte att teckna ännu."),
 ("Varför bara svarta strumpor?", "Svart fungerar till kostym, jeans och träningsskor. När alla par är likadana behöver du aldrig para ihop strumpor efter tvätten, och ett borttappat par spelar ingen roll."),
 ("Vad är viskos från bambu?", f"En viskosfiber som tillverkas av cellulosa från bambu. Den är mjuk och slät mot huden. Våra strumpor består av {MATERIAL[:-1]}, där polyamid och lycra ger stretch och hållbarhet."),
 ("Hur tvättar jag strumporna?", "Tvätta i 40 grader, gärna ut och in, och låt dem lufttorka. Exakta skötselråd står på förpackningen."),
 ("Vilken storlek ska jag välja?", 'Strumporna finns i tre storlekar: 36-40, 41-45 och 46-48. Ligger du mellan två storlekar är den större ofta det bekvämare valet. I <a class="u-link hit" href="{{ROOT}}storleksguide/#tabell">storleksguiden</a> ser du vilken strumpstorlek som hör till din skostorlek.'),
]
faq_html = "\n".join(
  f'<details><summary>{q}<span class="plus" aria-hidden="true"></span></summary><div class="answer"><p>{a}</p></div></details>' for q, a in FAQ)

def product_path(p):
    return f'/strumpor/{p["slug"]}/'

def abs_page(path):
    return SITE + path

def offer_ld(p):
    return {
        "@type": "Offer",
        "name": p["full_name"],
        "sku": p["id"],
        "price": f'{p["price"]}.00',
        "priceCurrency": "SEK",
        "availability": "https://schema.org/PreOrder",
        "url": abs_page(product_path(p)),
        "shippingDetails": {
            "@type": "OfferShippingDetails",
            "shippingRate": {"@type": "MonetaryAmount", "value": f"{SHIPPING}.00", "currency": "SEK"},
            "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "SE"},
        },
    }

def product_ld(products, url, image):
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": PRODUCT_NAME if len(products) > 1 else products[0]["full_name"],
        "description": "Svarta premiumstrumpor i viskos från bambu. " + MATERIAL + " Finns i 5-pack och 10-pack.",
        "image": image,
        "url": url,
        "color": "Svart",
        "material": MATERIAL[:-1],
        "brand": {"@type": "Brand", "name": "Strumpverket"},
        "offers": [offer_ld(p) for p in products] if len(products) > 1 else offer_ld(products[0]),
    }

def ld_scripts(blocks):
    return "\n".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in blocks)

home_ld = ld_scripts([
    {"@context": "https://schema.org", "@type": "Organization", "name": "Strumpverket",
     "url": abs_page("/"), "logo": f"{ASSET_ORIGIN}/android-chrome-512.png",
     "sameAs": SAME_AS,
     "description": "Strumpverket säljer svarta premiumstrumpor i viskos från bambu, i 5-pack och 10-pack."},
    product_ld(PRODUCTS, abs_page("/#strumpor"),
               [f'{ASSET_ORIGIN}/assets/img/{p["img"]}-768.jpg' for p in PRODUCTS]),
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

def related_list(exclude=None):
    items = []
    for other in PRODUCTS:
        if other["id"] == exclude:
            continue
        items.append(
            f'<li><a href="{{{{ROOT}}}}strumpor/{other["slug"]}/"><span>{other["full_name"]}</span>'
            f'<span class="label">{other["price"]} kr + frakt</span></a></li>')
    for sb in SUBS:
        items.append(
            f'<li><a href="{{{{ROOT}}}}#prenumeration"><span>Prenumeration {BY_ID[sb["pack"]]["name"]}, {sb["every"]}</span>'
            f'<span class="label">{sb["price"]} kr inkl. frakt</span></a></li>')
    return f'<ul class="related">{"".join(items)}</ul>'

def product_main(p):
    hero = picture(p["img"], p["alt"], PDP_SIZES, [400, 768], 768, 1024, lazy=False, priority="high")
    detail = picture("material", MAT_ALT, PDP_SIZES, [640, 1024], 1024, 768, lazy=True)
    price = (f'<div class="pdp__price"><strong>{p["price"]} kr</strong>'
             f'<span class="label">inkl. moms · {per_pair(p)}</span></div>')
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
      <p class="label pdp__label">Nr. {p["nr"]} · {p["pairs"]} par · Viskos från bambu</p>
      <h1>{p["full_name"]}</h1>
      <p class="pdp__lede">{p["desc"]}</p>
      <p class="pdp__more-text">{p["more"]}</p>
      {price}
      {save_badge(p)}
      {sub_highlight(p)}
      <p class="callout"><strong>{SHIP_LINE}</strong> {CHECKOUT_SOON}</p>
      <form class="pdp__form" {form_attrs(p["id"], p["full_name"], p["price"], p["img"], 1)} aria-label="{p["full_name"]}">
        {size_fieldset()}
        {guide_link()}
        {add_button()}
      </form>
      <section class="pdp__block"><h2>Material</h2><p>{MATERIAL}</p></section>
      <section class="pdp__block"><h2>Frakt</h2><p>{SHIPPING} kr per beställning. Vi skickar med PostNord direkt till din brevlåda.</p></section>
      <section class="pdp__block"><h2>Skötsel</h2><p>{CARE}</p></section>
    </div>
  </article>
  <aside class="pdp__more">
    <h2>Fler sätt att köpa</h2>
    {related_list(p["id"])}
  </aside>
</div>'''

def guide_main():
    head = "".join(f"<th scope=\"col\">{name}</th>" for name in ("EU-skostorlek", "Strumpstorlek"))
    body = "".join(f"<tr><th scope=\"row\">{shoes}</th><td>{sock}</td></tr>" for shoes, sock in SHOE_ROWS)
    return f'''
<article class="guide wrap">
  {crumbs([("Startsida", "{{ROOT}}"), ("Storleksguide", None)])}
  <h1>Storleksguide</h1>
  <p class="lede">Tre strumpstorlekar, valda efter skostorlek. Samma storlekar gäller för 5-pack, 10-pack och prenumerationerna.</p>
  <p class="callout">Tabellen är ett vanligt EU-intervall. Måtten ska bekräftas med leverantören.</p>
  <div class="table-wrap" id="tabell">
    <table class="size-table">
      <caption>EU-skostorlek till strumpstorlek</caption>
      <thead><tr>{head}</tr></thead>
      <tbody>{body}</tbody>
    </table>
  </div>
  <h2>Mellan två storlekar</h2>
  <p>Välj den större. Sko 35 och mindre, och sko 49 och större, ryms inte i storlekarna.</p>
  <h2>Så är intervallen satta</h2>
  <p>36-40, 41-45 och 46-48 är vanliga strumpintervall i EU-skor. Om leverantörens mått skiljer sig åt uppdateras den här sidan.</p>
  <h2>Köp</h2>
  {related_list()}
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
              'imagesizes="(min-width: 86rem) 80rem, 90vw" fetchpriority="high">')

def render(prefix, main, meta):
    html = SHELL.replace("{{MAIN}}", main).replace("{{SOCIALS}}", socials)
    html = html.replace("{{CSS}}", css_for(prefix))
    html = html.replace("{{EXTRA_HEAD}}", meta.get("extra", ""))
    html = html.replace("{{LD}}", meta.get("ld", ""))
    for key in ("TITLE", "OG_TITLE", "DESCRIPTION", "CANONICAL", "OG_IMAGE", "OG_W", "OG_H", "OG_ALT"):
        html = html.replace("{{" + key + "}}", meta[key])
    html = html.replace("{{ARROW}}", ARROW).replace("{{ROOT}}", prefix)
    html = html.replace("{{SHIPPING}}", str(SHIPPING)).replace("{{SUB_FROM}}", str(SUB_FROM))
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
             .replace("{{SUBS}}", "".join(sub_cards))
             .replace("{{SUB_PERKS}}", sub_perks)
             .replace("{{MAT_PIC}}", mat_pic)
             .replace("{{MATERIAL}}", MATERIAL)
             .replace("{{SHIP_LINE}}", SHIP_LINE)
             .replace("{{FAQ}}", faq_html))

pages = [("index.html", "", home_main, dict(
    TITLE="Strumpverket · Svarta premium bambustrumpor i 5-pack och 10-pack",
    OG_TITLE="Strumpverket · Svarta bambustrumpor i 5-pack och 10-pack",
    DESCRIPTION=(f"Svarta premium bambustrumpor i 5-pack för {BY_ID['5-pack']['price']} kr och 10-pack för "
                 f"{BY_ID['10-pack']['price']} kr. Frakt {SHIPPING} kr med PostNord till brevlådan. "
                 f"Prenumeration från {min(sb['price'] for sb in SUBS)} kr inkl. frakt startar snart."),
    CANONICAL=abs_page("/"),
    OG_IMAGE=OG_HOME, OG_W="1200", OG_H="630", OG_ALT=OG_HOME_ALT,
    extra=HOME_EXTRA, ld=home_ld,
))]

guide_desc = "Storleksguide för Strumpverkets svarta bambustrumpor i 5-pack och 10-pack. EU-skostorlek till strumpstorlek 36-40, 41-45 och 46-48."
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
    preload = (
        '<link rel="preload" as="image" type="image/avif" imagesrcset="'
        f'{{{{ROOT}}}}assets/img/{p["img"]}-400.avif 400w, {{{{ROOT}}}}assets/img/{p["img"]}-768.avif 768w" '
        f'imagesizes="{PDP_SIZES}" fetchpriority="high">'
    )
    pages.append((f'strumpor/{p["slug"]}/index.html', "../../", product_main(p), dict(
        TITLE=p["title"],
        OG_TITLE=p["og_title"],
        DESCRIPTION=p["blurb"],
        CANONICAL=abs_page(product_path(p)),
        OG_IMAGE=f'{ASSET_ORIGIN}/assets/img/{p["img"]}-768.jpg',
        OG_W="768", OG_H="1024", OG_ALT=p["alt"],
        extra=preload,
        ld=ld_scripts([
            product_ld([p], abs_page(product_path(p)), f'{ASSET_ORIGIN}/assets/img/{p["img"]}-768.jpg'),
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
    "# Förhandsvisning. Sidorna har dessutom meta robots noindex.\n"
    "User-agent: *\n"
    "Allow: /\n"
    f"Sitemap: {abs_page('/sitemap.xml')}\n"
)
(ROOT / "robots.txt").write_text(robots)

# Old product pages from the four-model range are gone.
for old in ("ankel", "vardag", "knastrumpa", "fyrpack"):
    f = ROOT / "strumpor" / old / "index.html"
    if f.exists():
        f.unlink()
        f.parent.rmdir()

for rel, prefix, main, meta in pages:
    write(rel, render(prefix, main, meta))

print(f"SITE={SITE}")
print(f"ASSET_ORIGIN={ASSET_ORIGIN}")
print("go-live: set ASSET_ORIGIN = SITE, then rebuild")
for p in PRODUCTS:
    print(f'{p["name"]}: {p["price"]} kr, {per_pair(p)}, + {SHIPPING} kr frakt = {p["price"] + SHIPPING} kr')
for sb in SUBS:
    print(f'Prenumeration {sb["pack"]} {sb["every"]}: {sb["price"]} kr inkl. frakt vs {sb["oneoff"]} kr, spara {sb["saved"]} kr ({sb["pct"]} %)')
