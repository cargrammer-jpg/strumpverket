# Strumpverket

Statisk sajt för Strumpverket, en butik som bara säljer svarta premiumstrumpor i viskos från bambu.
Ren HTML, CSS och JS utan ramverk. Förhandsvisning: https://strumpverket.se/ (tidigare https://cargrammer-jpg.github.io/strumpverket/)

- Sortiment: 5-pack 249 kr och 10-pack 449 kr inkl. moms. Frakt 39 kr per beställning tillkommer (PostNord till brevlådan).
- Prenumeration: 5-pack var 3:e månad 229 kr och 10-pack var 4:e månad 379 kr, båda inkl. frakt. Startar snart.
- Material: 78 % viskos från bambu, 18 % polyamid, 4 % lycra.
- Priser, frakt och prenumerationer står på ett ställe: `PRODUCTS`, `SHIPPING` och `SUBS` i `tools/build.py`. Besparingar räknas ut där.
- Sidorna genereras av `python3 tools/build.py` (`tools/shell.template.html`, `tools/home.html`).
- Det finns ingen kassa eller betallösning ännu. Varukorgen sparas bara i webbläsarens localStorage. "Till kassan" visar att kassan öppnar snart. Inget skickas någonstans, och nyhetsbrevsformuläret sparar ingen data.
- Sidan har `noindex` tills den riktiga domänen strumpverket.se kopplas.
- Bilder och video är AI-genererade platshållare, se CREDITS.md.
- Publik adress: `SITE` och `ASSET_ORIGIN` överst i `tools/build.py`. Sidor (canonical, sitemap, robots, og:url, JSON-LD url) använder `SITE`. Bilder som måste gå att hämta idag (og:image, Twitter, JSON-LD) använder `ASSET_ORIGIN`. När strumpverket.se svarar: sätt `ASSET_ORIGIN = SITE` och bygg om.
