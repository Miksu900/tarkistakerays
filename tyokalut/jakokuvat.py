"""Keräysvahti – jakokuvat (og:image) jokaiselle luvalle ja "lupaa ei löytynyt" -tulokselle.

Kun joku jakaa järjestön sivun WhatsAppissa, Facebookissa tai X:ssä, linkin esikatseluun tulee kortti:
"✓ Rahankeräyslupa voimassa · <järjestö> · RA/… · oikea tili". Kuvat ovat deterministisiä,
joten uudelleenrakennus ei kasvata git-historiaa, jos tieto ei muutu.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
F600 = os.path.join(HERE, "fontit", "Montserrat-600.ttf")
F800 = os.path.join(HERE, "fontit", "Montserrat-800.ttf")
W, H = 1200, 630
BG, INK, MUTE, LINE = (244, 246, 243), (24, 34, 29), (90, 104, 96), (215, 223, 217)
OK, WARN, WHITE = (30, 107, 79), (168, 70, 31), (255, 255, 255)
X0 = 72


def f(paino, koko):
    return ImageFont.truetype(F800 if paino == 800 else F600, koko)


def kilpi(d, x, y, s, vari, ruksi=True):
    """Kilpi-logo (sama muoto kuin sivuston logossa), koko s px."""
    k = s / 32
    pts = [(16, 2.5), (4.5, 7), (4.5, 15.2), (5.4, 19.6), (8, 23.6), (11.6, 26.9), (16, 29.5),
           (20.4, 26.9), (24, 23.6), (26.6, 19.6), (27.5, 15.2), (27.5, 7)]
    d.polygon([(x + px * k, y + py * k) for px, py in pts], fill=vari)
    if ruksi:
        d.line([(x + 10.2 * k, y + 16.3 * k), (x + 14.2 * k, y + 20.3 * k), (x + 21.8 * k, y + 12.2 * k)],
               fill=WHITE, width=max(2, round(3 * k)), joint="curve")


def rivita(d, teksti, fontti, leveys):
    sanat, rivit, r = teksti.split(), [], ""
    for s in sanat:
        koe = (r + " " + s).strip()
        if d.textlength(koe, font=fontti) <= leveys or not r:
            r = koe
        else:
            rivit.append(r); r = s
    if r:
        rivit.append(r)
    return rivit


def otsikko(d, teksti, y, maxrivit=3, koot=(76, 66, 58, 50, 44, 38), korkeus=None):
    """Piirtää nimen suurimmalla koolla, joka mahtuu riveille (ja korkeuteen). Palauttaa alareunan y:n."""
    for koko in koot:
        fo = f(800, koko)
        if korkeus:
            maxrivit = max(1, min(3, int(korkeus // round(koko * 1.14))))
        rivit = rivita(d, teksti, fo, W - 2 * X0)
        if len(rivit) <= maxrivit and all(d.textlength(r, font=fo) <= W - 2 * X0 for r in rivit):
            break
    else:
        rivit = rivit[:maxrivit]
        while rivit and d.textlength(rivit[-1] + "…", font=fo) > W - 2 * X0:
            rivit[-1] = rivit[-1][:-1]
        rivit[-1] = rivit[-1].rstrip() + "…"
    vali = round(koko * 1.14)
    for r in rivit:
        d.text((X0, y), r, font=fo, fill=INK)
        y += vali
    return y


def pilleri(d, x, y, teksti, fontti, tausta, vari=WHITE, px=22, py=12, ikoni=None):
    tl = d.textlength(teksti, font=fontti)
    asc, desc = fontti.getmetrics()
    ik_w = 0
    if ikoni:
        ik_w = asc + 10
    w, h = tl + 2 * px + ik_w, asc + 2 * py
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=tausta)
    if ikoni == "check":
        s = asc * 0.8; cx, cy = x + px, y + py + asc * 0.12
        d.line([(cx, cy + s * .55), (cx + s * .38, cy + s * .92), (cx + s, cy + s * .15)], fill=vari, width=max(3, round(asc / 7)), joint="curve")
    elif ikoni == "alert":
        s = asc * 0.86; cx, cy = x + px, y + py + asc * 0.06
        d.polygon([(cx + s / 2, cy), (cx, cy + s), (cx + s, cy + s)], outline=vari, width=max(3, round(asc / 9)))
        d.line([(cx + s / 2, cy + s * .38), (cx + s / 2, cy + s * .68)], fill=vari, width=max(3, round(asc / 9)))
        d.point((cx + s / 2, cy + s * .82), fill=vari)
        d.ellipse([cx + s / 2 - 2.5, cy + s * .8 - 2.5, cx + s / 2 + 2.5, cy + s * .8 + 2.5], fill=vari)
    d.text((x + px + ik_w, y + py - 1), teksti, font=fontti, fill=vari)
    return y + h


def pohja(korostus):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 14], fill=korostus)
    kilpi(d, X0, 46, 52, OK)
    d.text((X0 + 64, 52), "Keräysvahti", font=f(800, 36), fill=INK)
    return im, d


def alaosa(d, teksti):
    d.line([(X0, H - 112), (W - X0, H - 112)], fill=LINE, width=2)
    d.text((X0, H - 86), teksti, font=f(600, 28), fill=MUTE)
    fo = f(800, 30)
    url = "keraysvahti.fi"
    d.text((W - X0 - d.textlength(url, font=fo), H - 88), url, font=fo, fill=OK)


def tallenna(im, polku):
    os.makedirs(os.path.dirname(polku), exist_ok=True)
    im.quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(polku, optimize=True)


def iban_fmt(s):
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4)) if s else ""


def lupa(o, polku, lista_pvm):
    im, d = pohja(OK)
    y = pilleri(d, X0, 140, "RAHANKERÄYSLUPA VOIMASSA", f(800, 30), OK, ikoni="check")
    y = otsikko(d, o["yhteiso"], y + 30, korkeus=(H - 125) - (y + 30) - (96 if o.get("iban") else 50))
    y += 8
    d.text((X0, y), f"Lupa {o['nro']} · Poliisihallitus", font=f(600, 30), fill=MUTE)
    if o.get("iban"):
        d.text((X0, y + 46), "Oikea tili: " + iban_fmt(o["iban"]), font=f(800, 30), fill=INK)
    alaosa(d, f"Tarkistettu poliisin listasta {lista_pvm}")
    tallenna(im, polku)


def ei_loytynyt(polku):
    im, d = pohja(WARN)
    y = pilleri(d, X0, 140, "LUPAA EI LÖYTYNYT", f(800, 30), WARN, ikoni="alert")
    y = otsikko(d, "Tälle keräykselle ei löytynyt poliisin rahankeräyslupaa", y + 30, maxrivit=3, koot=(62, 56, 50))
    d.text((X0, y + 18), "Pyydä keräysnumero ja tarkista tili ennen kuin lahjoitat.", font=f(600, 30), fill=MUTE)
    alaosa(d, "Tarkista itse ilmaiseksi")
    tallenna(im, polku)
