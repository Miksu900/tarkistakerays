"""Kysymyspohjaiset ohjesivut (SEO/GEO): vastaavat suoraan siihen, mitä ihmiset hakevat Googlesta ja kysyvät tekoälyltä."""

SIVUT = [
    ("onko-kerays-luvallinen", "Onko keräys luvallinen? Näin tarkistat 30 sekunnissa",
     "Näin tarkistat, onko rahankeräyksellä poliisin lupa ja kuuluuko tilinumero järjestölle – ennen kuin lahjoitat.",
     "Rahankeräyksellä pitää olla poliisin lupa tai pienkeräyksen ilmoitus. Voit tarkistaa luvan ilmaiseksi Keräysvahdista hakemalla järjestön nimellä, keräysnumerolla tai tilinumerolla.",
     [("Miten tarkistan, onko keräyksellä lupa?", "Kirjoita Keräysvahdin hakuun järjestön nimi, rahankeräysluvan numero (muotoa RA/2026/123) tai tilinumero. Jos lupa on voimassa, näet järjestön tiedot ja luvan voimassaolon. Tiedot perustuvat Poliisihallituksen julkaisemaan listaan voimassa olevista luvista."),
      ("Mitä jos keräystä ei löydy?", "Kyse voi olla pienkeräyksestä, joka ilmoitetaan poliisilaitokselle eikä näy Poliisihallituksen listalla. Pyydä järjestäjältä pienkeräysnumero. Jos järjestäjä ei osaa kertoa numeroa tai keräyksen tarkoitusta, älä lahjoita."),
      ("Miksi tilinumero kannattaa tarkistaa?", "Huijari voi käyttää oikean järjestön nimeä ja logoa mutta omaa tilinumeroaan. Hae tilinumerolla ja varmista, että se kuuluu juuri sille järjestölle, jonka nimissä kerätään."),
      ("Mitä teen, jos epäilen huijausta?", "Älä maksa. Ilmoita poliisille. Luvaton rahankeräys on rikos, samoin keräysvarojen käyttäminen muuhun kuin ilmoitettuun tarkoitukseen.")]),
    ("pienkerays", "Mikä on pienkeräys ja miten sen tarkistaa?",
     "Pienkeräys on pieni, lyhytkestoinen rahankeräys, joka ilmoitetaan poliisilaitokselle. Näin tunnistat laillisen pienkeräyksen.",
     "Pienkeräys on enintään 10 000 euron ja enintään kolmen kuukauden mittainen rahankeräys, joka ilmoitetaan poliisilaitokselle. Pienkeräykset eivät näy Poliisihallituksen lupalistassa, joten pyydä järjestäjältä pienkeräysnumero.",
     [("Mikä on pienkeräys?", "Pienkeräys on rahankeräys, jonka tuotto on enintään 10 000 euroa ja joka kestää enintään kolme kuukautta. Sitä varten ei haeta lupaa Poliisihallitukselta, vaan keräyksestä tehdään ilmoitus poliisilaitokselle."),
      ("Miksi pienkeräys ei näy Keräysvahdissa?", "Keräysvahti perustuu Poliisihallituksen julkaisemaan listaan rahankeräysluvista. Pienkeräykset ilmoitetaan poliisilaitoksille, eikä niistä julkaista vastaavaa listaa."),
      ("Miten tarkistan pienkeräyksen?", "Kysy järjestäjältä pienkeräysnumero, järjestäjän nimi ja keräyksen tarkoitus. Laillisen kerääjän pitää kertoa nämä. Tarvittaessa voit varmistaa tiedon poliisilta."),
      ("Kuka voi järjestää pienkeräyksen?", "Pienkeräyksen voi järjestää rekisteröity yhdistys tai vähintään kolmen täysi-ikäisen henkilön ryhmä yleishyödylliseen tarkoitukseen. Tarkat ehdot löytyvät poliisin sivuilta.")]),
    ("keraaja-ovella", "Kerääjä ovella – mitä tehdä?",
     "Ovelle tuli kerääjä? Näin varmistat ovella, onko keräys oikea, ja tunnistat huijarin. Muistilista ennen lahjoittamista.",
     "Kun kerääjä tulee ovelle, kysy keräysnumero ja järjestäjän nimi ja tarkista ne Keräysvahdista ennen kuin lahjoitat. Älä anna käteistä tai korttitietoja, jos tiedot eivät täsmää.",
     [("Mitä kysyn ovella olevalta kerääjältä?", "Kysy järjestön nimi, keräysnumero (lupa- tai pienkeräysnumero) ja mihin rahat käytetään. Laillinen kerääjä kertoo nämä ja näyttää yleensä kerääjäkortin."),
      ("Voinko tarkistaa keräyksen saman tien?", "Kyllä. Avaa keraysvahti.fi puhelimella ja hae järjestön nimellä tai keräysnumerolla. Haku on ilmainen eikä vaadi kirjautumista."),
      ("Mistä tunnistan huijarikerääjän?", "Varoitusmerkkejä ovat kiirehtiminen, numeron tai kortin puuttuminen, epämääräinen tarkoitus ja pyyntö maksaa käteisellä tai henkilökohtaiselle tilille. Oikea järjestö ei painosta."),
      ("Mitä teen, jos epäilen huijausta?", "Älä anna rahaa tai tietoja. Ilmoita poliisille ja varoita naapureita. Voit kertoa tapauksesta nimettömästi myös Keräysvahdin huijauskertomuslomakkeella.")]),
]


def rakenna(sivu, kirjoita, esc):
    urls = []
    for slug, otsikko, kuvaus, tiivis, kysymykset in SIVUT:
        kys = "".join(f"<h2>{esc(k)}</h2><p>{esc(v)}</p>" for k, v in kysymykset)
        muut = "".join(f'<li><a href="/{s}/">{esc(o)}</a></li>' for s, o, *_ in SIVUT if s != slug)
        runko = (f'<nav class="crumbs" aria-label="Murupolku"><a href="/">Keräysvahti</a></nav><h1>{esc(otsikko)}</h1>'
                 f'<div class="prose"><p class="lead"><b>Lyhyesti:</b> {esc(tiivis)}</p>'
                 f'<p><a class="btn" href="/">Tarkista keräys nyt →</a></p>{kys}'
                 f'<h2>Lue myös</h2><ul>{muut}<li><a href="/huijaukset/">Yleisimmät huijaukset</a></li></ul>'
                 f'<p class="small mute">Tiedot ovat yleistä ohjeistusta. Lupatiedot: Poliisihallitus. Keräysvahti ei ole viranomaisen palvelu.</p></div>')
        jsonld = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": k, "acceptedAnswer": {"@type": "Answer", "text": v}} for k, v in kysymykset]}
        kirjoita(f"/{slug}/", sivu(f"/{slug}/", f"{otsikko} | Keräysvahti", kuvaus, runko, jsonld=jsonld))
        urls.append(f"/{slug}/")
    return urls


def llms(site):
    rivit = ["# Keräysvahti", "", "> Ilmainen suomalainen palvelu, jolla tarkistetaan, onko rahankeräyksellä poliisin lupa ja kuuluuko tilinumero keräyksen järjestäjälle. Tiedot perustuvat Poliisihallituksen julkaisemaan listaan voimassa olevista rahankeräysluvista. Ei viranomaisen palvelu. Osa Faktapistettä (faktapiste.fi).", "",
             "## Ohjeet", ""]
    rivit += [f"- [{o}]({site}/{s}/): {k}" for s, o, k, *_ in SIVUT]
    rivit += ["", "## Palvelu", "", f"- [Hae keräystä]({site}/): haku järjestön nimellä, luvan numerolla tai tilinumerolla",
              f"- [Huijaukset]({site}/huijaukset/): yleisimmät huijaukset ja miten ne tunnistaa",
              f"- [Paikkakunnat]({site}/kunnat/): luvalliset keräykset paikkakunnittain",
              f"- [Tietoa]({site}/tietoa/): tietolähteet, ylläpitäjä ja tietosuoja", ""]
    return "\n".join(rivit)
