# Credits och licenser

## Bilder och video
Sökningar på Pexels och Unsplash efter fria bilder på svarta strumpor mot ljus bakgrund gav inga användbara träffar
(Pexels-sökningen gav främst vita strumpor och skor, Unsplash gick inte att nå från byggmiljön).
Därför är alla bilder och videon AI-genererade för den här exempelsajten, med Grok Bots inbyggda verktyg:

| Fil | Källa | Beskrivning |
| --- | --- | --- |
| assets/img/hero-* | AI-genererad (GenerateImage) | Vikt par svarta strumpor på ljust linne, 16:9 |
| assets/img/ankel-*, vardag-*, kna-*, 3pack-*, lada-* | AI-genererade (GenerateImage) | Produktbilder på ljus bakgrund, 3:4. Bakgrundston normaliserad till #EEEBE6 |
| assets/img/material-* | AI-genererad (GenerateImage) | Närbild på stickad textil |
| assets/video/hero.mp4, hero.webm | AI-genererad (GenerateVideo, bild till video från hero-bilden, första och sista bildruta samma för sömlös loop) | 7 s, 1280x720, utan ljud |
| assets/og.jpg | Renderad lokalt med Chrome headless (Playwright) från tools/og.html, med plåtlogotypen | 1200x630 |

Bilderna föreställer inga verkliga produkter. De ska bytas mot riktiga produktfoton innan lansering.

## Logotyp och favicons
Identitet STRUMPVERKET (riktning E, "Maker's plate") av Mark, källfiler och regler i brand/final/ (README.md).
- assets/brand/strumpverket-wordmark-black.svg (plåt, header på desktop), -plain-black.svg (header mobil och kompakt), -plain-white.svg (footer). SVGO-optimerade, pixelidentiska med originalen.
- favicon.ico, favicon.svg, favicon-16/-32.png, apple-touch-icon.png, android-chrome-192/-512.png och site.webmanifest i sajtroten, från brand/final/favicon/.
- Bokstäverna är konturerade (Archivo, SIL OFL 1.1). Ingen font behövs för att visa logotypen.

## Typsnitt
- Schibsted Grotesk (variabel, 400-800), SIL Open Font License 1.1. Copyright 2023 The Schibsted-Grotesk Project Authors. https://github.com/schibsted/schibsted-grotesk
- IBM Plex Mono 400, SIL Open Font License 1.1. Copyright 2017 IBM Corp. https://github.com/IBM/plex

Båda är självhostade som woff2, subsettade till latin (inkl. å, ä, ö).

## Ikoner
Sociala ikoner (Instagram, X, TikTok) från Simple Icons, CC0 1.0. https://simpleicons.org/
De länkar till Instagram @strumpverket, X @STRUMPVERKET och TikTok @strumpverket.se. YouTube, Facebook och Pinterest visas inte.

## Betalmärken
Varumärkena tillhör respektive ägare. Märkena visas som exempel på planerade betalsätt. Butiken tar inte betalt ännu. Filerna är oförändrade utom att Mastercard-filen har fått `viewBox` så den skalar jämnt. Proportioner och färger är inte ändrade.

- Visa: ordmärket från 2021, Visa Blue `#1434CB`. Källa: den publicerade vektorfilen för Visa Inc. logo (2021-present). Riktlinjer: märket ska vara blått på ljust underlag, utan omfärgning, skugga eller tänjning. https://corporate.visa.com/en/about-visa.html
- Mastercard: symbolen i fullfärg, `#EB001B`, `#F79E1B` och överlapp `#FF5F00`. Källa: Mastercard Symbol-geometrin. Riktlinjer: symbolen signalerar acceptans och ska vara i fullfärg, inte i gråskala. https://www.mastercard.com/brandcenter/us/en/home.html
- Apple Pay: svart låsning med äpplet och ordet Pay som konturer. Källa: det publicerade Apple Pay-märket. Riktlinjer: använd märket som det är, sätt inte ordet Pay i ett annat typsnitt. https://developer.apple.com/apple-pay/marketing/
- Google Pay: det officiella acceptansmärket (vit pillerform, text `#3C4043`, G i `#4285F4`, `#34A853`, `#FABB05`, `#E94235`). Källa: märket i Googles riktlinjer, via den fil som anger den sidan som källa. Riktlinjer: ändra inte märket och gör det inte mindre än de andra. https://developers.google.com/pay/api/web/guides/brand-guidelines
- Klarna: det rosa betalningsmärket `#FFA8CD` med ordmärke `#0B051D`. Källa: Klarna Payment Badge. Riktlinjer: behåll den rosa färgen och ordmärkets form.
- Swish: den liggande logotypen som Swish själva serverar, https://www.swish.com/assets/swish-logotype-C2_aqj3N.svg. Riktlinjer: https://www.swish.com/marknadsmaterial/logotyp. Redigera inte filen. Mot mörk bakgrund ska den ligga på en vit platta, vilket den gör. Swish föredrar den stående varianten när det finns plats. I den här raden är höjden densamma som de andra märkena, så den liggande filen används oförändrad.
