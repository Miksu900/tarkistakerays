# Keräysvahti – keraysvahti.fi

Hakupalvelu Poliisihallituksen voimassa olevista rahankeräysluvista. Haku nimellä, keräysnumerolla,
Y-tunnuksella ja tilinumerolla; oma sivu jokaiselle luvalle ja paikkakunnalle.

## Päivitys (kerran kuussa)
1. Lataa poliisin lista: https://poliisi.fi/documents/25235045/123492012/Lista-rahankerayksista-FI.pdf
2. `python3 tyokalut/lue-pdf.py` (lukee `lista.pdf` → `luvat.json`), siirrä tulos `data/luvat.json` ja päivitä `paivays`
3. `python3 build.py` ja commit. GitHub Pages julkaisee.

## Rakenne
- `build.py` – generoi koko sivuston (`index.html`, `j/`, `kunta/`, `kunnat/`, `tietoa/`, `haku.json`, `sitemap.xml`)
- `style.css`, `favicon.svg`, `og.png` – ulkoasu ja jakokuva
- `data/luvat.json` – lähdedata
