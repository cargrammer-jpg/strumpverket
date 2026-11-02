# Strumpverket (exempelsajt)

Statisk exempelsajt för Strumpverket, en butik som bara säljer svarta strumpor i bambuviskos.
Ren HTML, CSS och JS utan ramverk. Förhandsvisning: https://cargrammer-jpg.github.io/strumpverket/

- Sidorna genereras av `python3 tools/build.py` (`tools/shell.template.html`, `tools/home.html`).
- Varukorgen sparas i localStorage. Kassan och nyhetsbrevet är demo och skickar ingen data.
- Sidan har `noindex` tills den riktiga domänen strumpverket.se kopplas.
- Priser är exempelpriser. Bilder och video är AI-genererade platshållare, se CREDITS.md.
- Publik adress: `SITE` och `ASSET_ORIGIN` överst i `tools/build.py`. Sidor (canonical, sitemap, robots, og:url, JSON-LD url) använder `SITE`. Bilder som måste gå att hämta idag (og:image, Twitter, JSON-LD) använder `ASSET_ORIGIN`. När strumpverket.se svarar: sätt `ASSET_ORIGIN = SITE` och bygg om.
