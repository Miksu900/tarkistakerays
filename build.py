#!/usr/bin/env python3
"""Keräysvahti – staattisen sivuston rakentaja.

Lukee data/luvat.json (Poliisihallituksen voimassa olevien rahankeräyslupien lista,
luettu PDF:stä työkalulla tyokalut/lue-pdf.py) ja kirjoittaa sivuston repon juureen:
  index.html              etusivu ja haku
  haku.json               kevyt hakuindeksi
  j/<slug>/index.html     sivu jokaiselle luvalle
  kunta/<slug>/index.html kotipaikkakunnan luvat
  kunnat/index.html       kaikki kotipaikat
  tietoa/index.html       palvelusta, tietosuoja, yhteystiedot
  404.html, sitemap.xml, robots.txt

Käyttö: python3 build.py
"""
import html, json, os, re, shutil, unicodedata
from collections import defaultdict
from datetime import date

SITE = "https://keraysvahti.fi"
ROOT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "data", "luvat.json"), encoding="utf-8"))
LISTA_PVM = D["paivays"]  # esim. "25.8.2026"
L = D["luvat"]
YHTEYS = "miika@eduskuntaseuranta.fi"
BUILD_PVM = date.today().isoformat()
import hashlib, sys
sys.path.insert(0, os.path.join(ROOT, "tyokalut"))
import jakokuvat
CSS_V = hashlib.md5(open(os.path.join(ROOT, "style.css"), "rb").read()).hexdigest()[:8]  # välimuistin ohitus

esc = lambda s: html.escape(s or "", quote=True)


def slug(s):
    s = unicodedata.normalize("NFKD", (s or "").lower())
    s = s.replace("ø", "o").replace("æ", "ae").replace("ß", "ss")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80].rstrip("-") or "x"


def iban_fmt(s):
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4)) if s else ""


def pvm_iso(p):
    d, m, y = p.split(".")
    return f"{y}-{m}-{d}"


def kaytto_html(t):
    """Palauttaa käyttötarkoituksen kappaleina; luettelot (•, -, 1.) omille riveilleen."""
    t = re.sub(r"\s+", " ", t or "").strip()
    t = re.sub(r"(?<=[:.;,])\s+(?=(?:•|-|–|\d{1,2}[.)])\s)", "\n", t)
    t = re.sub(r"\s(?=•\s)", "\n", t)
    rivit = [r.strip() for r in t.split("\n") if r.strip()]
    out, lista = [], []
    def tyhjenna():
        if lista:
            out.append("<ul>" + "".join(f"<li>{esc(x)}</li>" for x in lista) + "</ul>")
            lista.clear()
    for r in rivit:
        m = re.match(r"^(?:•|-|–|\d{1,2}[.)])\s+(.*)$", r)
        if m:
            lista.append(m.group(1))
        else:
            tyhjenna(); out.append(f"<p>{esc(r)}</p>")
    tyhjenna()
    return "".join(out)


# ---- slugit ----
kaytetty = set()
for o in sorted(L, key=lambda x: (x["yhteiso"], x["nro"])):
    base = slug(o["yhteiso"])
    s = base
    if s in kaytetty and o["kotipaikka"]:
        s = f"{base}-{slug(o['kotipaikka'])}"
    if s in kaytetty:
        s = f"{base}-{slug(o['nro'].replace('RA/', ''))}"
    kaytetty.add(s)
    o["slug"] = s
    o["kunta_slug"] = slug(o["kotipaikka"]) if o["kotipaikka"] else ""

kunnat = defaultdict(list)
for o in L:
    if o["kotipaikka"]:
        kunnat[o["kotipaikka"]].append(o)
uusimmat = sorted(L, key=lambda o: pvm_iso(o["alku"]), reverse=True)

# ---- yhteiset osat ----
LOGO = ('<svg class="logo-mark" viewBox="0 0 32 32" aria-hidden="true"><path d="M16 2.5 4.5 7v8.2c0 7 4.8 12.6 11.5 14.3 6.7-1.7 11.5-7.3 11.5-14.3V7z" fill="var(--acc)"/>'
        '<path d="m10.2 16.3 4 4 7.6-8.1" fill="none" stroke="var(--acc-ink)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def ik(nimi, cls="ico"):
    """Pienet viivaikonit (24x24, currentColor)."""
    P = {
        "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
        "search": '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>',
        "hash": '<path d="M9 4 7 20M17 4l-2 16M4.5 9h16M3.5 15h16"/>',
        "card": '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M3 10h18M7 15h4"/>',
        "list": '<path d="M9 6.5h11M9 12h11M9 17.5h11"/><circle cx="4.8" cy="6.5" r="1.1"/><circle cx="4.8" cy="12" r="1.1"/><circle cx="4.8" cy="17.5" r="1.1"/>',
        "alert": '<path d="M12 3.5 2.8 19.5h18.4z"/><path d="M12 10v4.5M12 17.2v.1"/>',
        "pin": '<path d="M12 21s-6.5-6.2-6.5-11a6.5 6.5 0 0 1 13 0c0 4.8-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
        "shield": '<path d="M12 2.8 4.5 5.8v5.6c0 4.8 3.2 8.6 7.5 9.8 4.3-1.2 7.5-5 7.5-9.8V5.8z"/><path d="m8.6 12.2 2.4 2.4 4.6-4.9"/>',
    }[nimi]
    return (f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{P}</svg>')


def sivu(polku, otsikko, kuvaus, runko, *, h_canonical=None, jsonld=None, skripti="", noindex=False, lang="fi", og_kuva="/og.png"):
    canonical = h_canonical or f"{SITE}{polku}"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/")}</script>' if jsonld else ""
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(otsikko)}</title>
<meta name="description" content="{esc(kuvaus)}">
{robots}<link rel="canonical" href="{esc(canonical)}">
<meta property="og:site_name" content="Keräysvahti">
<meta property="og:title" content="{esc(otsikko)}">
<meta property="og:description" content="{esc(kuvaus)}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="{ {"fi":"fi_FI","sv":"sv_FI","en":"en_GB"}[lang] }">
<meta property="og:image" content="{SITE}{og_kuva}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1e6b4f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Keräysvahti">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="/style.css?v={CSS_V}">
{ld}
</head>
<body>
<a class="skip" href="#sisalto">Siirry sisältöön</a>
<header class="hd"><div class="hd-in">
<a class="brand" href="/">{LOGO}<span>Keräysvahti</span></a>
<nav aria-label="Päävalikko"><a href="/">Haku</a><a href="/huijaukset/">Huijaukset</a><a href="/kunnat/">Paikkakunnat</a><a href="/tietoa/">Tietoa</a></nav>
</div></header>
<main id="sisalto" class="wrap">
{runko}
{VAROITA if lang == "fi" else ""}
</main>
<footer class="ft"><div class="ft-in">
<p><b>Keräysvahti</b> kokoaa Poliisihallituksen julkaiseman listan voimassa olevista rahankeräysluvista haettavaan muotoon. Palvelu ei ole viranomaisen palvelu.</p>
<p>Lupatiedot: Poliisihallitus, lista {esc(LISTA_PVM)}. <a href="/tietoa/">Tietoa ja käyttöehdot</a> · <a href="/tietosuoja/">Tietosuojaseloste</a> · Palaute ja korjaukset: <span class="mono">{YHTEYS}</span></p>
<p class="mute">Keräysvahti on osa <a href="https://faktapiste.fi">Faktapistettä</a>. Muita palveluja: <a href="https://pykalavahti.fi">Pykälävahti</a> · <a href="https://eduskuntaseuranta.fi">Eduskuntaseuranta</a> · <a href="https://nytpuhutaan.fi">Nytpuhutaan</a></p>
</div></footer>
{skripti}
{ASENNUSJS}
{VAROITAJS}
</body>
</html>
"""


VAROITA = '<section class="varoita" aria-label="Varoita läheistä">\n<p><b>Tunnetko jonkun, jolle ovelle tulee kerääjiä?</b> Lähetä hänelle vinkki – se vie viisi sekuntia.</p>\n<button type="button" class="btn" id="varoita">📲 Varoita läheistä</button>\n</section>'
VAROITAJS = '<script>(function(){var b=document.getElementById("varoita");if(!b)return;b.onclick=function(){\nvar t="Hei! Ovelle tulee nykyään myös huijarikerääjiä. Tällä voi tarkistaa ilmaiseksi, onko keräyksellä poliisin lupa ja mihin tilille lahjoitus kuuluu:",u="https://keraysvahti.fi/";\nif(navigator.share)navigator.share({text:t,url:u}).catch(function(){});else location.href="https://wa.me/?text="+encodeURIComponent(t+" "+u)}})();</script>'
ASENNUS = ('<div class="asenna-laatikko" id="asenna-l" hidden><button type="button" class="btn" id="asenna">Asenna sovellukseksi puhelimeen</button>'
           '<p class="small mute" id="asenna-ios" hidden>📱 Sovellukseksi iPhoneen: paina Safarin <b>Jaa</b>-painiketta ja valitse <b>Lisää Koti-valikkoon</b>.</p></div>')
ASENNUSJS = ('<script>(function(){if("serviceWorker" in navigator)navigator.serviceWorker.register("/sw.js").catch(function(){});'
             'var L=document.getElementById("asenna-l");if(!L)return;'
             'if(window.matchMedia("(display-mode: standalone)").matches||navigator.standalone)return;'
             'var A=document.getElementById("asenna"),I=document.getElementById("asenna-ios"),ip=null;'
             'window.addEventListener("beforeinstallprompt",function(e){e.preventDefault();ip=e;L.hidden=false;A.hidden=false});'
             'A.onclick=function(){if(!ip)return;ip.prompt();ip.userChoice.then(function(){L.hidden=true;ip=null})};'
             'if(/iphone|ipad|ipod/i.test(navigator.userAgent)){L.hidden=false;A.hidden=true;I.hidden=false}})();</script>')


def jaa_osio(teksti, url, otsikko="Lähetä tämä tarkistus eteenpäin",
             selite="Kun joku kysyy, onko keräys oikea, vastaa tällä linkillä. Esikatselussa näkyy suoraan, onko lupa voimassa."):
    from urllib.parse import quote
    t = quote(teksti + " " + url, safe="")
    return (f'<section class="jaa" data-teksti="{esc(teksti)}" data-url="{esc(url)}" aria-label="Jaa tarkistus">'
            f'<p><b>{esc(otsikko)}</b> {esc(selite)}</p><div class="jaa-napit">'
            '<button type="button" class="btn" data-jaa>📲 Jaa</button>'
            f'<a class="btn toissij" href="https://wa.me/?text={t}" target="_blank" rel="noopener">WhatsApp</a>'
            f'<a class="btn toissij" href="https://www.facebook.com/sharer/sharer.php?u={quote(url, safe="")}" target="_blank" rel="noopener">Facebook</a>'
            f'<a class="btn toissij" href="https://x.com/intent/post?text={t}" target="_blank" rel="noopener">X</a>'
            '<button type="button" class="btn toissij" data-kopioi-linkki>Kopioi linkki</button></div></section>')


JAAJS = ('<script>document.addEventListener("click",function(e){var j=e.target.closest("[data-jaa],[data-kopioi-linkki]");if(!j)return;'
         'var s=j.closest(".jaa"),t=s.getAttribute("data-teksti"),u=s.getAttribute("data-url");'
         'if(j.hasAttribute("data-jaa")){if(navigator.share){navigator.share({text:t,url:u}).catch(function(){})}'
         'else{location.href="https://wa.me/?text="+encodeURIComponent(t+" "+u)}return}'
         'function ok(){j.textContent="Linkki kopioitu";setTimeout(function(){j.textContent="Kopioi linkki"},1800)}'
         'if(navigator.clipboard){navigator.clipboard.writeText(u).then(ok,function(){prompt("Kopioi linkki:",u)})}else prompt("Kopioi linkki:",u)});</script>')


def kirjoita(polku, sisalto):
    p = os.path.join(ROOT, polku.lstrip("/"))
    if p.endswith("/"):
        p += "index.html"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(sisalto)


def kortti(o, h="h3"):
    kp = f' · {esc(o["kotipaikka"])}' if o["kotipaikka"] else ""
    return (f'<a class="item" href="/j/{o["slug"]}/"><span class="ok-badge" title="Lupa voimassa">{ik("check")}</span>'
            f'<span class="item-txt"><{h} class="name">{esc(o["yhteiso"])}</{h}>'
            f'<span class="meta">{esc(o["nro"])} · voimassa {esc(o["alku"])} alkaen{kp}</span></span></a>')


OHJEET = """<section class="guide" aria-labelledby="ohje-h">
<h2 id="ohje-h">Näin tunnistat laillisen keräyksen</h2>
<ol class="steps">
<li>{I1}<div><b>Kysy keräysnumero.</b> Laillisen keräyksen järjestäjän on kerrottava itsestään, keräyksen käyttötarkoitus ja lupa- tai pienkeräysnumero. Jos numeroa ei anneta, älä lahjoita.</div></li>
<li>{I2}<div><b>Tarkista tilinumero.</b> Huijari voi käyttää oikean järjestön nimeä mutta omaa tilinumeroaan. Hae tilinumerolla ja varmista, että se kuuluu juuri tälle järjestölle.</div></li>
<li>{I3}<div><b>Pienkeräykset ovat eri listalla.</b> Pienkeräys (enintään 10 000 €, enintään 3 kuukautta) ilmoitetaan poliisilaitokselle, eikä se näy täällä. Pyydä pienkeräysnumero ja tarvittaessa tarkista se poliisilta.</div></li>
<li>{I4}<div><b>Epäiletkö huijausta?</b> Ilmoita poliisille. Luvaton rahankeräys on rikos, samoin keräysvarojen käyttäminen muuhun kuin ilmoitettuun tarkoitukseen.</div></li>
</ol>
</section>""".format(I1=ik("hash", "step-ico"), I2=ik("card", "step-ico"), I3=ik("list", "step-ico"), I4=ik("alert", "step-ico warn"))

COPYJS = ('<script>document.addEventListener("click",function(e){var b=e.target.closest(".copy");if(!b)return;'
          'var t=b.getAttribute("data-copy");function ok(){b.textContent="Kopioitu";setTimeout(function(){b.textContent="Kopioi"},1600)}'
          'function fb(){var r=document.createRange();r.selectNodeContents(document.getElementById("iban"));var s=getSelection();s.removeAllRanges();s.addRange(r)}'
          'if(navigator.clipboard){navigator.clipboard.writeText(t).then(ok,fb)}else fb()});</script>')

# ---- järjestösivut ----
shutil.rmtree(os.path.join(ROOT, "j"), ignore_errors=True)
shutil.rmtree(os.path.join(ROOT, "kunta"), ignore_errors=True)
for o in L:
    nimi = o["yhteiso"]
    kp = o["kotipaikka"]
    otsikko = f"{nimi} – rahankeräyslupa {o['nro']} | Keräysvahti"
    kuvaus = (f"{nimi}{' (' + kp + ')' if kp else ''}: rahankeräyslupa {o['nro']} voimassa {o['alku']} alkaen. "
              "Tarkista keräyksen tilinumero ja mihin varat käytetään.")
    rivit = []
    rivit.append(f'<div class="fact"><dt>Keräysnumero</dt><dd class="mono">{esc(o["nro"])}</dd></div>')
    rivit.append(f'<div class="fact"><dt>Voimassa</dt><dd>{esc(o["alku"])} alkaen</dd></div>')
    if o["iban"]:
        rivit.append(f'<div class="fact wide tili"><dt>{ik("card", "dt-ico")}Oikea keräystili</dt><dd class="mono iban"><span id="iban">{esc(iban_fmt(o["iban"]))}</span>'
                     f'<button type="button" class="copy" data-copy="{esc(o["iban"])}">Kopioi</button></dd>'
                     '<p class="tili-ohje">Lahjoita vain tälle tilille. Jos sinulle annettiin eri tilinumero, älä maksa.</p></div>')
    else:
        rivit.append('<div class="fact wide"><dt>Keräystili</dt><dd>Ei ilmoitettu poliisin listassa. Varmista tilinumero järjestöltä.</dd></div>')
    if re.fullmatch(r"\d{7}-\d", o["ytunnus"]):
        rivit.append(f'<div class="fact"><dt>Y-tunnus</dt><dd class="mono"><a href="https://tietopalvelu.ytj.fi/yritys/{esc(o["ytunnus"])}" rel="nofollow noopener" target="_blank">{esc(o["ytunnus"])}</a></dd></div>')
    if kp:
        rivit.append(f'<div class="fact"><dt>Kotipaikka</dt><dd><a href="/kunta/{o["kunta_slug"]}/">{esc(kp)}</a></dd></div>')
    rivit.append('<div class="fact"><dt>Luvan myöntäjä</dt><dd>Poliisihallitus</dd></div>')
    samat = [x for x in kunnat.get(kp, []) if x is not o][:6] if kp else []
    muut = (f'<section><h2>Muita rahankeräyksiä: {esc(kp)}</h2><div class="list">' + "".join(kortti(x) for x in samat) +
            f'</div><p><a href="/kunta/{o["kunta_slug"]}/">Kaikki {len(kunnat[kp])} lupaa: {esc(kp)} →</a></p></section>') if samat else ""
    murut = [("Keräysvahti", "/")] + ([(kp, f"/kunta/{o['kunta_slug']}/")] if kp else []) + [(nimi, f"/j/{o['slug']}/")]
    jsonld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(murut)]}
    nav = '<nav class="crumbs" aria-label="Murupolku">' + " › ".join(f'<a href="{u}">{esc(n)}</a>' for n, u in murut[:-1]) + "</nav>"
    runko = f"""{nav}
<article class="org">
<h1>{esc(nimi)}</h1>
<div class="status ok big">{ik("shield", "status-ico")}<div><b>Rahankeräyslupa voimassa</b><span>Poliisihallituksen listalla {esc(LISTA_PVM)}. Lupa on voimassa toistaiseksi, ellei poliisi peruuta sitä.</span></div></div>
<dl class="facts">{''.join(rivit)}</dl>
<section class="purpose"><h2>Mihin keräysvarat käytetään</h2>{kaytto_html(o["kayttotarkoitus"]) or "<p>Käyttötarkoitusta ei ole ilmoitettu listassa.</p>"}
<p class="mute">Teksti on Poliisihallituksen listasta sellaisenaan.</p></section>
<aside class="note"><b>Pyydettiinkö sinulta lahjoitusta tämän järjestön nimissä?</b> Vertaa annettua tilinumeroa yllä olevaan. Jos numero on eri, älä lahjoita, vaan ota yhteys järjestöön suoraan tai ilmoita poliisille.</aside>
</article>
{muut}
<p class="mute small">Onko tieto väärin tai vanhentunut? Ilmoita: <span class="mono">{YHTEYS}</span></p>"""
    jakoteksti = (f"✅ {nimi}: rahankeräyslupa on voimassa ({o['nro']})." +
                  (f" Oikea keräystili: {iban_fmt(o['iban'])}." if o["iban"] else "") +
                  " Tarkista itse ennen kuin lahjoitat:")
    runko = runko.replace('<section class="purpose">', jaa_osio(jakoteksti, f"{SITE}/j/{o['slug']}/") + '\n<section class="purpose">', 1)
    jakokuvat.lupa(o, os.path.join(ROOT, "j", o["slug"], "jako.png"), LISTA_PVM)
    kirjoita(f"/j/{o['slug']}/", sivu(f"/j/{o['slug']}/", otsikko, kuvaus, runko, jsonld=jsonld, skripti=COPYJS + JAAJS,
                                      og_kuva=f"/j/{o['slug']}/jako.png"))

# ---- kuntasivut ----
for kp, lst in kunnat.items():
    ks = slug(kp)
    lst = sorted(lst, key=lambda o: o["yhteiso"].lower())
    otsikko = f"Rahankeräykset: {kp} – {len(lst)} voimassa olevaa lupaa | Keräysvahti"
    kuvaus = f"Kaikki {len(lst)} voimassa olevaa rahankeräyslupaa, joiden järjestäjän kotipaikka on {kp}. Tarkista järjestö ja tilinumero ennen kuin lahjoitat."
    runko = (f'<nav class="crumbs" aria-label="Murupolku"><a href="/">Keräysvahti</a> › <a href="/kunnat/">Paikkakunnat</a></nav>'
             f'<h1>Rahankeräykset: {esc(kp)}</h1><p class="lead">{len(lst)}\u00a0voimassa olevaa rahankeräyslupaa järjestöillä, joiden kotipaikka on {esc(kp)}.</p>'
             f'<div class="list">' + "".join(kortti(o, "h2") for o in lst) + "</div>" + OHJEET)
    kirjoita(f"/kunta/{ks}/", sivu(f"/kunta/{ks}/", otsikko, kuvaus, runko))

ks_sorted = sorted(kunnat.items(), key=lambda kv: kv[0].lower())
MAXK = max(len(v) for v in kunnat.values())


def kaupunki(k, v, palkki=True):
    w = max(2, round(100 * len(v) / MAXK))
    return (f'<li><a href="/kunta/{slug(k)}/"><span class="c-row"><span class="c-name">{esc(k)}</span>'
            f'<span class="c-n">{len(v)}</span></span>' + (f'<span class="bar" aria-hidden="true"><i style="width:{w}%"></i></span>' if palkki else '') + '</a></li>')
runko = ('<nav class="crumbs" aria-label="Murupolku"><a href="/">Keräysvahti</a></nav><h1>Rahankeräykset paikkakunnittain</h1>'
         '<p class="lead">Järjestön kotipaikan mukaan. Keräys voi silti tapahtua missä päin Suomea tahansa.</p><ul class="cities">' +
         "".join(kaupunki(k, v, False) for k, v in ks_sorted) + "</ul>")
kirjoita("/kunnat/", sivu("/kunnat/", "Rahankeräykset paikkakunnittain | Keräysvahti",
                          "Voimassa olevat rahankeräysluvat järjestön kotipaikkakunnan mukaan.", runko))

# ---- hakuindeksi ----
indeksi = [[o["nro"], o["yhteiso"], o["kotipaikka"], o["ytunnus"], o["iban"], o["slug"], o["alku"]] for o in uusimmat]
json.dump({"paivays": LISTA_PVM, "l": indeksi}, open(os.path.join(ROOT, "haku.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

# ---- etusivu ----
top_kunnat = sorted(kunnat.items(), key=lambda kv: -len(kv[1]))[:12]
runko = f"""<section class="hero">
<div class="hero-mark" aria-hidden="true">{LOGO.replace('class="logo-mark"', 'class="hero-logo"')}</div>
<p class="eyebrow">Ennen kuin lahjoitat</p>
<h1>Onko keräyksellä lupa?</h1>
<p class="lead">Hae järjestön nimellä, keräysnumerolla, Y-tunnuksella tai tilinumerolla. Mukana kaikki {len(L):,} Poliisihallituksen myöntämää voimassa olevaa rahankeräyslupaa.</p>
<form class="search" role="search" onsubmit="return false">
<label for="q" class="sr">Hae rahankeräystä</label>
{ik("search", "search-ico")}
<input id="q" type="search" autocomplete="off" spellcheck="false" enterkeyhint="search" placeholder="Järjestö, RA/2025/918 tai FI12 3456 …">
</form>
<dl class="stats"><div><dt>Lupaa voimassa</dt><dd>{len(L):,}</dd></div><div><dt>Paikkakuntaa</dt><dd>{len(kunnat)}</dd></div><div><dt>Poliisin lista</dt><dd>{esc(LISTA_PVM)}</dd></div></dl>
<div class="ex" aria-label="Esimerkkihaut"><button type="button" data-q="Punainen Risti">Punainen Risti</button><button type="button" data-q="Lions Club">Lions Club</button><button type="button" data-q="Oulu">Oulu</button><button type="button" data-q="Pelastakaa Lapset">Pelastakaa Lapset</button></div>
{ASENNUS}
</section>
<p class="count" id="count" aria-live="polite">Ladataan lupatietoja…</p>
<div class="list" id="tulos"></div>
<noscript><p>Haku vaatii JavaScriptin. Voit selata lupia <a href="/kunnat/">paikkakunnittain</a>.</p></noscript>
{OHJEET}
<section><h2>Selaa paikkakunnittain</h2><ul class="cities">{''.join(kaupunki(k, v) for k, v in top_kunnat)}</ul>
<p><a href="/kunnat/">Kaikki paikkakunnat →</a></p></section>
<section><h2>Uusimmat luvat</h2><div class="list">{''.join(kortti(o) for o in uusimmat[:8])}</div></section>""".replace(f"{len(L):,}", f"{len(L):,}".replace(",", "\u00a0"))
HAKUJS = """<script>
(function(){
var q=document.getElementById("q"),out=document.getElementById("tulos"),cnt=document.getElementById("count"),L=[],shown=0,hits=[];
function fold(s){return(s||"").toLowerCase().normalize("NFKD").replace(/[\\u0300-\\u036f]/g,"").replace(/\\s+/g," ").trim()}
function ibanF(s){return s?s.replace(/(.{4})/g,"$1 ").trim():""}
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
var OK=CHECK;
function card(o){var a=el("a","item");a.href="/j/"+o[5]+"/";var b=el("span","ok-badge");b.title="Lupa voimassa";b.innerHTML=OK;a.appendChild(b);
 var x=el("span","item-txt");x.appendChild(el("h3","name",o[1]));
 var m=o[0]+" · voimassa "+o[6]+" alkaen"+(o[2]?" · "+o[2]:"");x.appendChild(el("span","meta",m));
 if(o[4]){x.appendChild(el("span","meta mono","Tili "+ibanF(o[4])))}a.appendChild(x);return a}
function more(){var b=document.getElementById("more");if(b)b.remove();hits.slice(shown,shown+20).forEach(function(o){out.appendChild(card(o))});shown+=20;
 if(shown<hits.length){var x=el("button","more","Näytä lisää ("+(hits.length-shown)+")");x.id="more";x.type="button";x.onclick=more;out.appendChild(x)}}
function run(){var raw=q.value.trim(),f=fold(raw),ib=raw.toUpperCase().replace(/\\s+/g,"");out.innerHTML="";shown=0;
 try{history.replaceState(null,"",raw?"#"+encodeURIComponent(raw).replace(/%20/g,"_"):location.pathname)}catch(e){}
 if(!f){cnt.textContent=L.length.toLocaleString("fi-FI")+" voimassa olevaa lupaa. Aloita kirjoittamalla hakuun.";return}
 if(/^FI\\d{4,}/.test(ib))hits=L.filter(function(o){return o[4]&&o[4].indexOf(ib)===0});
 else hits=L.filter(function(o){return o._s.indexOf(f)>-1}).sort(function(a,b){return(b._n.indexOf(f)===0)-(a._n.indexOf(f)===0)||a[1].localeCompare(b[1],"fi")});
 if(!hits.length){cnt.textContent="";var n=el("div","status warn");n.appendChild(el("span","dot"));var d=el("div");d.appendChild(el("b","","Voimassa olevaa lupaa ei löytynyt"));
  d.appendChild(el("span","","Haulla ”"+raw+"” ei löytynyt Poliisihallituksen myöntämää rahankeräyslupaa. Tarkista kirjoitusasu. Kyse voi olla myös pienkeräyksestä, joita ei ole tällä listalla: pyydä järjestäjältä pienkeräysnumero. Jos tilinumero ei täsmää minkään luvan kanssa, älä lahjoita ennen kuin asia on selvä."));
  n.appendChild(d);out.appendChild(n);
  var u="https://keraysvahti.fi/ei-loytynyt/?h="+encodeURIComponent(raw),s=el("section","jaa");
  s.setAttribute("data-teksti","⚠️ Hain Keräysvahdista ”"+raw+"”, eikä poliisin rahankeräyslupaa löytynyt. Pyydä keräysnumero ennen kuin lahjoitat:");s.setAttribute("data-url",u);
  var p=el("p");p.appendChild(el("b","","Varoita muita."));p.appendChild(document.createTextNode(" Lähetä tämä tulos esimerkiksi Facebook-ryhmään, jossa keräyksestä kysyttiin."));s.appendChild(p);
  var r=el("div","jaa-napit"),b1=el("button","btn","📲 Jaa varoitus");b1.type="button";b1.setAttribute("data-jaa","");r.appendChild(b1);
  var b2=el("button","btn toissij","Kopioi linkki");b2.type="button";b2.setAttribute("data-kopioi-linkki","");r.appendChild(b2);s.appendChild(r);out.appendChild(s);return}
 cnt.textContent=hits.length.toLocaleString("fi-FI")+(hits.length===1?" lupa löytyi.":" lupaa löytyi.");more()}
var t;q.addEventListener("input",function(){clearTimeout(t);t=setTimeout(run,120)});
document.querySelectorAll(".ex button").forEach(function(b){b.onclick=function(){q.value=b.getAttribute("data-q");run();q.focus()}});
fetch("/haku.json").then(function(r){return r.json()}).then(function(d){L=d.l;L.forEach(function(o){o._s=fold(o[1]+" "+o[0]+" "+o[2]+" "+o[3]);o._n=fold(o[1])});
 var h=decodeURIComponent((location.hash||"").slice(1)).replace(/_/g," ");if(h)q.value=h;run()}).catch(function(){cnt.textContent="Lupatietojen lataus epäonnistui. Päivitä sivu."});
})();
</script>"""
jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": "Keräysvahti", "url": SITE + "/",
          "description": "Tarkista, onko rahankeräyksellä poliisin lupa."}
HAKUJS = HAKUJS.replace("var OK=CHECK;", "var OK=" + json.dumps(ik("check")) + ";")
kirjoita("/", sivu("/", "Keräysvahti – tarkista rahankeräys ennen kuin lahjoitat",
                   "Onko keräyksellä poliisin lupa? Hae kaikki voimassa olevat rahankeräysluvat järjestön nimellä, keräysnumerolla, Y-tunnuksella tai tilinumerolla.",
                   runko, jsonld=jsonld, skripti=HAKUJS + JAAJS))

# ---- jaettava "lupaa ei löytynyt" -tulos ----
jakokuvat.ei_loytynyt(os.path.join(ROOT, "ei-loytynyt", "jako.png"))
runko = f"""<nav class="crumbs" aria-label="Murupolku"><a href="/">Keräysvahti</a></nav>
<h1>Lupaa ei löytynyt</h1>
<div class="status warn big"><span class="dot"></span><div><b id="el-otsikko">Tälle keräykselle ei löytynyt poliisin rahankeräyslupaa</b>
<span>Haettu Poliisihallituksen listasta voimassa olevista rahankeräysluvista ({esc(LISTA_PVM)}). Kyse voi olla myös kirjoitusvirheestä tai pienkeräyksestä, joka ei ole tällä listalla. Pyydä järjestäjältä keräysnumero ennen kuin lahjoitat.</span></div></div>
<p><a class="btn" id="el-hae" href="/">Tarkista itse →</a></p>
{OHJEET}"""
ELJS = """<script>(function(){var h=new URLSearchParams(location.search).get("h");if(!h)return;h=h.slice(0,120);
document.getElementById("el-otsikko").textContent="Haulla ”"+h+"” ei löytynyt poliisin rahankeräyslupaa";
document.getElementById("el-hae").href="/#"+encodeURIComponent(h).replace(/%20/g,"_")})();</script>"""
kirjoita("/ei-loytynyt/", sivu("/ei-loytynyt/", "Rahankeräyslupaa ei löytynyt | Keräysvahti",
                              "Tälle keräykselle ei löytynyt poliisin rahankeräyslupaa. Pyydä keräysnumero ja tarkista tili ennen kuin lahjoitat.",
                              runko, skripti=ELJS, noindex=True, og_kuva="/ei-loytynyt/jako.png"))

# ---- tietoa ----
runko = f"""<nav class="crumbs" aria-label="Murupolku"><a href="/">Keräysvahti</a></nav>
<h1>Tietoa Keräysvahdista</h1>
<div class="prose">
<p>Keräysvahti auttaa tarkistamaan ennen lahjoittamista, onko rahankeräyksellä poliisin lupa ja kuuluuko annettu tilinumero todella keräyksen järjestäjälle.</p>
<h2>Mistä tiedot ovat peräisin</h2>
<p>Tiedot ovat Poliisihallituksen julkaisemasta listasta voimassa olevista rahankeräysluvista (lista {esc(LISTA_PVM)}). Poliisi päivittää listan kerran kuukaudessa, ja Keräysvahti päivitetään sen mukaan. Rahankeräyslain (863/2019) 33 §:n mukaan rahankeräysrekisterin tietoja luvan haltijasta ja keräyksen käyttötarkoituksesta saa saattaa yleisön tietoon.</p>
<p>Listassa ovat vain Poliisihallituksen myöntämät rahankeräysluvat. Pienkeräykset, jotka ilmoitetaan poliisilaitokselle, eivät ole mukana. Jos keräystä ei löydy, se ei siis automaattisesti tarkoita, että keräys olisi laiton: kysy järjestäjältä pienkeräysnumero.</p>
<h2>Kuka ylläpitää</h2>
<p>Keräysvahti on yksityinen avoimuuspalvelu, ei viranomaisen palvelu. Ylläpitäjä on Miika Koskela, joka ylläpitää myös <a href="https://eduskuntaseuranta.fi">Eduskuntaseurantaa</a>. Valvova viranomainen on Poliisihallitus. Jos tieto on epäselvä, varmista se Poliisihallituksen arpajaishallinnosta.</p>
<h2>Tietosuoja</h2>
<p>Keräysvahti ei käytä evästeitä eikä vaadi kirjautumista. Haku tehdään kokonaan omassa selaimessasi, eikä hakusanoja lähetetä minnekään. Kävijämäärät lasketaan Cloudflare Web Analytics -palvelulla, joka ei käytä evästeitä eikä tunnista yksittäisiä kävijöitä. Sivusto toimii GitHub Pages- ja Cloudflare-palveluissa, jotka voivat tallentaa teknisiä lokitietoja (kuten IP-osoitteen) palvelun toiminnan ja turvallisuuden vuoksi.</p>
<p><b>Nimettömät huijauskertomukset.</b> Jos lähetät kertomuksen <a href="/huijaukset/kerro/">lomakkeella</a>, viesti tallennetaan enintään 12 kuukaudeksi Cloudflaren palveluun ja välitetään ylläpitäjän sähköpostiin (Brevo). Lähettäjän nimeä, yhteystietoja tai IP-osoitetta ei tallenneta; roskapostin estämiseksi IP-osoitteesta lasketaan tunnin ajan säilyvä tunnistamaton tiiviste. Kertomusta käytetään nimettömänä varoituksissa ja mainonnassa vain, jos lähettäjä on antanut siihen luvan. Voit pyytää kertomuksen poistamista kertomalla sen sisällön ja lähetysajan osoitteeseen <span class="mono">{YHTEYS}</span>.</p>
<p>Sivustolla julkaistaan vain järjestöjen (yhdistysten, säätiöiden ja seurakuntien) lupatietoja sellaisina kuin poliisi on ne julkaissut. Fontit ladataan Googlen Fonts-palvelusta.</p>
<h2>Käyttöehdot ja maksullisuus</h2>
<p>Keräysvahti on tällä hetkellä maksuton. Ylläpitäjä pidättää oikeuden muuttaa palvelun sisältöä ja käyttöehtoja sekä ottaa käyttöön maksullisia palveluita tai ominaisuuksia. Muutoksista kerrotaan tällä sivulla etukäteen. Jo käytetyistä maksuttomista palveluista ei peritä maksua jälkikäteen.</p>
<p>Palvelun tiedot ovat yleistä ohjeistusta, eivät oikeudellista neuvontaa. Ylläpitäjä ei vastaa tietojen virheettömyydestä tai niiden perusteella tehdyistä päätöksistä. Varmista tarvittaessa tieto viranomaiselta.</p>
<h2>Virheet ja korjaukset</h2>
<p>Jos järjestönne tieto on väärin tai lupa on päättynyt, ilmoita osoitteeseen <span class="mono">{YHTEYS}</span>. Korjaamme tiedon tai poistamme sen, jos se ei enää ole poliisin listalla.</p>
<h2>Tulossa</h2>
<p>Keräysvahti on pyytänyt Poliisihallitukselta tiedot myös pienkeräyksistä sekä keräysten tuotoista ja kuluista. Tavoitteena on, että jokaisesta keräyksestä näkee jatkossa myös, paljonko rahaa kerättiin ja mihin se käytettiin.</p>
</div>"""
kirjoita("/tietoa/", sivu("/tietoa/", "Tietoa ja tietosuoja | Keräysvahti",
                          "Mistä Keräysvahdin tiedot ovat peräisin, kuka palvelua ylläpitää ja miten tietosuoja on hoidettu.", runko))


# ---- tietosuojaseloste ----
from tietosuoja import seloste
_ts = seloste(palvelu="Keräysvahti (keraysvahti.fi)", rekisterinpitaja="Miika Koskela (yksityinen ylläpitäjä)", yhteys=YHTEYS,
    tiedot=[("Haku", "haku tehdään kokonaan omassa selaimessasi. Hakusanoja ei lähetetä palvelimelle."),
            ("Nimettömät huijauskertomukset", "lomakkeella lähetetty kertomus (tyyppi, teksti, paikkakunta ja lupa nimettömään käyttöön). Nimeä, yhteystietoja tai IP-osoitetta ei tallenneta; roskapostin estoon IP-osoitteesta lasketaan tunnin ajan säilyvä tunnistamaton tiiviste."),
            ("Kävijätilastot", "Cloudflare Web Analytics laskee kävijämääriä ilman evästeitä eikä tunnista yksittäisiä kävijöitä."),
            ("Tekniset lokitiedot", "palvelimet käsittelevät laitteesi IP-osoitteen ja selaimen tiedot sivuston toimittamiseksi ja tietoturvaa varten."),
            ("Sähköpostit", "jos otat yhteyttä, käsittelemme viestisi ja yhteystietosi vastataksemme sinulle.")],
    tarkoitus="Tietoja käsitellään huijauksista varoittamiseen (oikeutettu etu ja kertomuksen lähettäjän antama lupa nimettömään käyttöön), sivuston toimivuuteen ja tietoturvaan (oikeutettu etu) sekä yhteydenottoihin vastaamiseen.",
    kasittelijat=[("GitHub, Inc. (GitHub Pages)", "sivuston julkaisu"), ("Cloudflare, Inc.", "verkko, kävijätilastot ja kertomusten tallennus"), ("Brevo", "kertomusten välitys ylläpitäjän sähköpostiin"), ("Telegram", "ilmoitus uudesta kertomuksesta ylläpitäjälle"), ("Google LLC (Google Fonts)", "kirjasintiedostot; laitteesi IP-osoite välittyy Googlelle")],
    sailytys="Huijauskertomukset säilytetään enintään 12 kuukautta. Tekniset lokitiedot poistuvat palveluntarjoajien järjestelmistä lyhyen ajan kuluessa. Sähköpostit säilytetään niin kauan kuin asian hoitaminen vaatii.",
    evasteet="Keräysvahti ei käytä evästeitä. Sovellukseksi asennettava versio tallentaa sivujen välimuistin laitteellesi, jotta palvelu toimii nopeasti.",
    lisa="<h2>Julkaistavat lupatiedot</h2><p>Sivustolla julkaistaan vain järjestöjen (yhdistysten, säätiöiden ja seurakuntien) rahankeräyslupatiedot sellaisina kuin Poliisihallitus on ne julkaissut.</p>")
kirjoita("/tietosuoja/", sivu("/tietosuoja/", "Tietosuojaseloste | Keräysvahti", "Keräysvahdin tietosuojaseloste.", _ts))

# ---- huijaukset: ks. huijaukset.py ----
import huijaukset
HUIJ_URLS = huijaukset.rakenna(sivu, kirjoita, esc, ik)

# ---- 404 ----
kirjoita("/404.html", sivu("/404.html", "Sivua ei löytynyt | Keräysvahti", "Sivua ei löytynyt.",
    '<h1>Sivua ei löytynyt</h1><p class="lead">Lupa on voinut poistua poliisin listalta, tai osoite on kirjoitettu väärin.</p><p><a class="btn" href="/">Hae keräystä →</a></p>', noindex=True))

# ---- sitemap & robots ----
urls = ["/", "/kunnat/", "/tietoa/", "/tietosuoja/"] + HUIJ_URLS + [f"/kunta/{slug(k)}/" for k in kunnat] + [f"/j/{o['slug']}/" for o in L]
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f"<url><loc>{SITE}{u}</loc><lastmod>{BUILD_PVM}</lastmod></url>" for u in urls]
sm.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")
json.dump({"name": "Keräysvahti – tarkista rahankeräys", "short_name": "Keräysvahti", "lang": "fi",
           "description": "Tarkista, onko rahankeräyksellä poliisin lupa ja kuuluuko tilinumero järjestölle.",
           "start_url": "/", "scope": "/", "display": "standalone", "background_color": "#f4f6f3", "theme_color": "#1e6b4f",
           "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                     {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]},
          open(os.path.join(ROOT, "manifest.webmanifest"), "w"), ensure_ascii=False, indent=1)
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print(f"Valmis: {len(L)} järjestösivua, {len(kunnat)} paikkakuntaa, {len(urls)} osoitetta sivukartassa.")
