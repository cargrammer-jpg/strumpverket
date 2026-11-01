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
Sociala ikoner (Instagram, X, TikTok, YouTube, Facebook, Pinterest) från Simple Icons, CC0 1.0. https://simpleicons.org/
Varumärkena tillhör respektive ägare. Länkarna är platshållare (href="#"), inga konton finns ännu.
