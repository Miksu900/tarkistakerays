"""Huijausosio: /huijaukset/ ja alasivut, sekä ruotsin- ja englanninkieliset versiot.
Kutsutaan build.py:stä: rakenna(sivu, kirjoita, esc, ik) -> julkiset osoitteet sivukarttaan."""
import json
from huijaukset_data import TYYPIT, VISA, KAUSI, LAHTEET

# False = luonnos (noindex, ei valikossa eikä sivukartassa). True = julkinen.
JULKINEN = True

SULKU = '<a class="soita" href="tel:+35820333"><b>020 333</b><span>Sulkupalvelu: kortit ja verkkopankki kiinni, 24 h</span></a>'
HATA = '<a class="soita hata" href="tel:112"><b>112</b><span>Hätänumero, kun vaara on päällä</span></a>'
RIKU = '<a class="soita" href="tel:116006"><b>116 006</b><span>Rikosuhripäivystys: tukea ja neuvoja</span></a>'


def murut(*osat):
    return '<nav class="crumbs" aria-label="Murupolku">' + " › ".join(f'<a href="{u}">{n}</a>' for n, u in osat) + "</nav>"


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


KAUSIJS = ("<script>(function(){var K=" + json.dumps([[k, o, t, l] for k, o, t, l in KAUSI], ensure_ascii=False) + ";"
           "var m=new Date().getMonth()+1,e=document.getElementById('kausi');if(!e)return;"
           "for(var i=0;i<K.length;i++){if(K[i][0].indexOf(m)>-1){e.querySelector('b').textContent=K[i][1];"
           "e.querySelector('span').textContent=K[i][2];e.href=K[i][3];e.hidden=false;return}}})();</script>")

VAROJS = """<script>(function(){var b=document.getElementById('varo');if(!b)return;
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
fetch('/huijaukset/varoitukset.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(function(d){
 var raja=Date.now()-14*864e5,u=d.u.filter(function(x){return Date.parse(x.a)>raja}).slice(0,8);
 if(!u.length){b.querySelector('.mute').textContent='Ei uusia huijausuutisia viimeisen kahden viikon ajalta.';return}
 var ul=el('ul','varo-lista');u.forEach(function(x){var li=el('li'),a=el('a','',x.o);a.href=x.l;a.rel='noopener nofollow';a.target='_blank';
  var t=new Date(x.a);li.appendChild(a);li.appendChild(el('span','meta',x.s+' · '+t.getDate()+'.'+(t.getMonth()+1)+'.'));ul.appendChild(li)});
 b.querySelector('.mute').replaceWith(ul);
 var p=new Date(d.p);b.appendChild(el('p','mute small','Päivitetty '+p.getDate()+'.'+(p.getMonth()+1)+'. klo '+p.getHours()+'.'+String(p.getMinutes()).padStart(2,'0')+'. Otsikot linkkeineen ovat alkuperäisistä lähteistä (Kyberturvallisuuskeskus ja suomalaiset mediat).'))
}).catch(function(){b.querySelector('.mute').textContent='Uutisten lataus ei onnistunut.'})})();</script>"""


def tyokalurivi():
    return ('<div class="tyokalut">'
            '<a class="tk" href="/huijaukset/tarkista-viesti/"><b>Tarkista viesti</b><span>Liitä epäilyttävä viesti, ja näet varoitusmerkit.</span></a>'
            '<a class="tk" href="/huijaukset/visa/"><b>Tunnistatko huijauksen?</b><span>10 esimerkkiä. Testaa itsesi.</span></a>'
            '<a class="tk" href="/huijaukset/muistilista/"><b>Muistilista vanhemmille</b><span>Tulosta tai lähetä läheisellesi.</span></a></div>')


def rakenna(sivu, kirjoita, esc, ik):
    ni = not JULKINEN
    urls = []

    def k(polku, otsikko, kuvaus, runko, **kw):
        kirjoita(polku, sivu(polku, otsikko, kuvaus, runko, noindex=ni, **kw))
        urls.append(polku)

    apunappi = '<a class="apunappi" href="/huijaukset/apua/">Jouduin huijatuksi, mitä nyt? →</a>'

    # ---- pääsivu ----
    kortit = "".join(f'<a class="tyyppi" href="/huijaukset/{t["slug"]}/"><h3>{esc(t["ots"])}</h3><p>{esc(t["lyhyt"])}</p></a>' for t in TYYPIT)
    runko = f"""{murut(("Keräysvahti", "/"))}
<h1>Tunnista huijaus</h1>
<p class="lead">Huijari kiirehtii, vetoaa tunteisiin ja pyytää rahaa tai tunnuksia. Täältä löydät yleisimmät huijaukset Suomessa, työkalut epäilyttävän viestin tarkistamiseen ja ohjeet, jos jotain jo tapahtui.</p>
{apunappi}
<a class="kausi" id="kausi" href="#" hidden><small>Ajankohtaista nyt</small><b></b><span></span></a>
<div class="huij-kolme"><div><b>1.</b> Pysähdy. Kiire on huijarin työkalu.</div><div><b>2.</b> Älä anna tunnuksia, kortin tietoja tai henkilötunnusta.</div><div><b>3.</b> Tarkista itse virallisesta lähteestä.</div></div>
{tyokalurivi()}
<section class="varo" id="varo" aria-labelledby="varo-h"><h2 id="varo-h">Huijaukset uutisissa nyt</h2><p class="mute">Ladataan…</p></section>
<section aria-labelledby="tyypit-h"><h2 id="tyypit-h">Yleisimmät huijaukset</h2><div class="tyypit">{kortit}</div></section>
<p class="kielet">På svenska: <a href="/sv/bedragerier/" hreflang="sv" lang="sv">Känn igen bedrägerier</a> · In English: <a href="/en/scams/" hreflang="en" lang="en">Recognise a scam</a></p>
<p class="mute small">{LAHTEET}</p>"""
    k("/huijaukset/", "Tunnista huijaus | Keräysvahti",
      "Yleisimmät huijaukset Suomessa, viestintarkistin, testi ja ohjeet, jos huijaus jo tapahtui. Ajankohtaiset huijausuutiset yhdessä paikassa.",
      runko, skripti=KAUSIJS + VAROJS)

    # ---- tyyppisivut ----
    for i, t in enumerate(TYYPIT):
        muut = [x for x in TYYPIT if x is not t][:4]
        lst = lambda xs: "".join(f"<li>{x}</li>" for x in xs)
        runko = f"""{murut(("Keräysvahti", "/"), ("Huijaukset", "/huijaukset/"))}
<article class="huij-art">
<h1>{esc(t["ots"])}</h1>
<p class="lead">{esc(t["intro"])}</p>
<section class="huij"><h2>Näin huijaus etenee</h2><ol>{lst(esc(x) for x in t["etenee"])}</ol></section>
<section class="huij varoitus"><h2>Varoitusmerkit</h2><ul>{lst(esc(x) for x in t["merkit"])}</ul></section>
<section class="huij"><h2>Toimi näin</h2><ul>{lst(t["toimi"])}</ul></section>
{apunappi}
<section><h2>Usein kysyttyä</h2>{"".join(f'<details class="faq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in t["faq"])}</section>
</article>
{tyokalurivi()}
<section><h2>Muut huijaukset</h2><div class="tyypit">{"".join(f'<a class="tyyppi" href="/huijaukset/{x["slug"]}/"><h3>{esc(x["ots"])}</h3><p>{esc(x["lyhyt"])}</p></a>' for x in muut)}</div>
<p><a href="/huijaukset/">Kaikki huijaukset →</a></p></section>
<p class="mute small">{LAHTEET}</p>"""
        k(f"/huijaukset/{t['slug']}/", f"{t['ots']} | Keräysvahti", t["meta"], runko, jsonld=faq_ld(t["faq"]))

    # ---- jos huijaus jo tapahtui ----
    runko = f"""{murut(("Keräysvahti", "/"), ("Huijaukset", "/huijaukset/"))}
<h1>Jouduin huijatuksi, mitä nyt?</h1>
<p class="lead">Toimi heti. Mitä nopeammin pankki saa tiedon, sitä paremmat mahdollisuudet on pysäyttää maksut. Huijatuksi tuleminen ei ole häpeä: huijarit ovat ammattilaisia.</p>
<div class="soitot">{SULKU}{HATA}{RIKU}</div>
<ol class="apu-askeleet">
<li><b>Lopeta yhteys huijariin.</b> Sulje puhelu ja lopeta viestittely. Älä maksa enempää, vaikka sinua uhattaisiin.</li>
<li><b>Soita heti pankkiin.</b> Pyydä sulkemaan kortit ja verkkopankkitunnukset ja pysäyttämään maksut. Oman pankkisi numero on kortin takana ja pankin sivuilla. Kun pankin asiakaspalvelu ei vastaa, Sulkupalvelu palvelee ympäri vuorokauden: <a href="tel:+35820333">020 333</a>.</li>
<li><b>Jos annoit etäyhteyden koneeseesi,</b> irrota kone verkosta. Älä käytä sillä verkkopankkia ennen kuin kone on tarkistettu.</li>
<li><b>Vaihda salasanat,</b> jotka huijari on voinut nähdä. Aloita sähköpostista ja tee vaihto toisella laitteella.</li>
<li><b>Tee rikosilmoitus</b> poliisille. Sen voi tehdä verkossa: <a href="https://poliisi.fi" rel="noopener">poliisi.fi</a>. Liitä mukaan viestit, puhelinnumerot, tilinumerot ja kuitit. Pankki voi tarvita rikosilmoituksen.</li>
<li><b>Jos henkilötunnuksesi tai henkilötietosi joutuivat huijarille,</b> voit pyytää luottotietoihisi maksuttoman väärinkäytösmerkinnän (Suomen Asiakastieto). Se vaikeuttaa luoton ottamista nimissäsi.</li>
<li><b>Ilmoita huijauksesta</b> <a href="https://www.kyberturvallisuuskeskus.fi" rel="noopener">Kyberturvallisuuskeskukselle</a>, niin muita voidaan varoittaa. Sijoitushuijauksesta voi ilmoittaa myös <a href="https://www.finanssivalvonta.fi" rel="noopener">Finanssivalvonnalle</a>.</li>
<li><b>Hae tukea.</b> Rikosuhripäivystys auttaa maksutta: <a href="tel:116006">116 006</a>, <a href="https://www.riku.fi" rel="noopener">riku.fi</a>. Kerro myös läheiselle.</li>
</ol>
<aside class="note"><b>Varo \"rahojen palautuspalveluita\".</b> Huijauksen jälkeen voi tulla yhteydenottoja, joissa luvataan saada rahat takaisin maksua vastaan. Ne ovat usein saman huijauksen jatkoa.</aside>
<p><a href="/huijaukset/muistilista/">Tulosta muistilista, jossa nämä numerot ovat valmiina →</a></p>
<p class="mute small">{LAHTEET}</p>"""
    k("/huijaukset/apua/", "Jouduin huijatuksi – mitä nyt? | Keräysvahti",
      "Toimi heti, jos jouduit huijatuksi: soita pankkiin (Sulkupalvelu 020 333), tee rikosilmoitus ja hae tukea. Ohjeet vaihe vaiheelta.", runko)

    # ---- viestintarkistin ----
    runko = f"""{murut(("Keräysvahti", "/"), ("Huijaukset", "/huijaukset/"))}
<h1>Tarkista epäilyttävä viesti</h1>
<p class="lead">Liitä tekstiviesti, sähköposti tai some-viesti alle. Näet, mitä huijausviestin tunnusmerkkejä siinä on.</p>
<p class="yksityisyys">{ik("shield", "ico")} Tarkistus tehdään kokonaan omassa selaimessasi. Viestiä ei lähetetä eikä tallenneta minnekään.</p>
<label for="viesti" class="sr">Viesti</label>
<textarea id="viesti" rows="7" placeholder="Liitä viesti tähän…"></textarea>
<div class="napit"><button type="button" class="btn" id="tarkista">Tarkista</button><button type="button" class="btn toissij" id="esim">Kokeile esimerkillä</button></div>
<div id="tulos" aria-live="polite"></div>
<aside class="note">Työkalu etsii tyypillisiä varoitusmerkkejä. Se ei voi taata, että viesti on turvallinen. Jos viesti pyytää rahaa, tunnuksia tai kiirettä, tarkista asia aina itse virallisesta lähteestä.</aside>
{apunappi}
<p class="mute small">{LAHTEET}</p>"""
    k("/huijaukset/tarkista-viesti/", "Tarkista onko viesti huijaus | Keräysvahti",
      "Liitä epäilyttävä tekstiviesti tai sähköposti ja näe huijausviestin varoitusmerkit. Tarkistus tehdään selaimessa, viestiä ei tallenneta.",
      runko, skripti=TARKISTINJS)

    # ---- visa ----
    runko = f"""{murut(("Keräysvahti", "/"), ("Huijaukset", "/huijaukset/"))}
<h1>Tunnistatko huijauksen?</h1>
<p class="lead">Kymmenen esimerkkiä viesteistä ja tilanteista. Päätä jokaisesta: huijaus vai todennäköisesti aito?</p>
<div id="visa" class="visa"><p class="mute">Ladataan…</p></div>
<noscript><p>Testi vaatii JavaScriptin.</p></noscript>
<p class="mute small">Esimerkit ovat keksittyjä mutta perustuvat todellisiin huijaustapoihin. Nimet, numerot ja osoitteet ovat kuvitteellisia.</p>"""
    visa_js = "<script>var VISA=" + json.dumps(VISA, ensure_ascii=False).replace("</", "<\\/") + ";</script>" + VISAJS
    k("/huijaukset/visa/", "Tunnistatko huijauksen? Testaa itsesi | Keräysvahti",
      "Kymmenen esimerkkiä huijausviesteistä ja -puheluista. Testaa, tunnistatko huijauksen, ja jaa testi läheisillesi.", runko, skripti=visa_js)

    # ---- muistilista (tulostettava A4) ----
    runko = f"""<div class="ei-tulostu">{murut(("Keräysvahti", "/"), ("Huijaukset", "/huijaukset/"))}
<h1>Muistilista huijauksia vastaan</h1>
<p class="lead">Tulosta tämä jääkaapin oveen tai lähetä linkki vanhemmillesi. Teksti on isolla, ja numerot ovat valmiina.</p>
<div class="napit"><button type="button" class="btn" onclick="print()">Tulosta</button><button type="button" class="btn toissij" id="jaa">Lähetä läheiselle</button></div>
<p id="jaettu" class="small mute" aria-live="polite"></p></div>
<div class="a4">
<h2>Huijari kiirehtii. Pysähdy aina.</h2>
<ol class="a4-lista">
<li>Pankki, poliisi tai Kela <b>ei koskaan</b> kysy pankkitunnuksia, tunnuslukuja tai kortin tietoja puhelimessa tai viestillä.</li>
<li><b>Älä avaa viestin linkkiä.</b> Mene palveluun itse.</li>
<li><b>Turvatiliä ei ole.</b> Älä siirrä rahaa kenenkään ohjeesta.</li>
<li>Jos läheinen pyytää rahaa <b>uudesta numerosta</b>, soita hänen vanhaan numeroonsa.</li>
<li><b>Älä hyväksy</b> pankkisovelluksessa mitään, mitä et itse aloittanut.</li>
<li><b>Älä asenna ohjelmaa</b> soittajan pyynnöstä.</li>
<li>Laillinen kerääjä kertoo <b>keräysluvan numeron</b>. Tarkista: keraysvahti.fi</li>
<li>Jos epäilet, <b>lopeta puhelu</b> ja kysy läheiseltä.</li>
</ol>
<div class="a4-numerot">
<p><b>Jos huijaus jo tapahtui, soita heti pankkiin.</b></p>
<p>Kortit ja verkkopankki kiinni ympäri vuorokauden: <b>Sulkupalvelu 020 333</b></p>
<p>Hätätilanteessa: <b>112</b></p>
<p class="tayta">Oman pankkini numero: <span></span></p>
<p class="tayta">Läheiseni numero: <span></span></p>
</div>
<p class="a4-ala">keraysvahti.fi/huijaukset</p>
</div>"""
    k("/huijaukset/muistilista/", "Tulostettava muistilista huijauksia vastaan | Keräysvahti",
      "Tulostettava A4-muistilista huijauksia vastaan isolla tekstillä: tärkeimmät säännöt ja numerot. Lähetä vanhemmillesi.", runko, skripti=JAAJS)

    # ---- joulu ----
    runko = f"""{murut(("Keräysvahti", "/"), ("Huijaukset", "/huijaukset/"))}
<h1>Joulun keräys- ja pakettihuijaukset</h1>
<p class="lead">Joulun alla moni haluaa auttaa, ja paketteja liikkuu enemmän kuin muulloin. Sitä käyttävät myös huijarit: valekerääjät kaupan ovella ja huijausviestit pakettien nimissä.</p>
<section class="huij"><h2>Ennen kuin lahjoitat</h2><ul>
<li>Kysy kerääjältä keräysluvan tai pienkeräyksen numero.</li>
<li>Tarkista keräys <a href="/">Keräysvahdista</a> ja lahjoita vain luvassa näkyvälle tilille.</li>
<li>Lahjoita mieluummin suoraan järjestön omille sivuille kirjoittamalla osoite itse.</li>
<li>Somessa leviävät \"hätäkeräykset\" yksityishenkilön tilille ovat riski. Varmista, kuka kerää ja millä luvalla.</li></ul></section>
<section class="huij varoitus"><h2>Pakettiviestit</h2><ul>
<li>Viesti tullimaksusta, toimitusmaksusta tai osoitteen vahvistamisesta, jossa on linkki, on lähes aina huijaus.</li>
<li>Tarkista lähetykset itse kuljetusyhtiön sovelluksesta tai sivulta.</li>
<li>Voit tarkistaa viestin <a href="/huijaukset/tarkista-viesti/">viestintarkistimella</a>.</li></ul></section>
<section class="huij"><h2>Lahjaostokset netissä</h2><ul>
<li>Merkkituote puoleen hintaan tuntemattomasta kaupasta on huijaus.</li>
<li>Maksa kortilla, jolloin voit pyytää maksun palautusta.</li></ul></section>
{apunappi}
<p class="mute small">{LAHTEET}</p>"""
    k("/huijaukset/joulu/", "Joulun keräys- ja pakettihuijaukset | Keräysvahti",
      "Näin vältät joulun valekerääjät, pakettiviestihuijaukset ja valeverkkokaupat. Tarkista keräyksen lupa ennen lahjoittamista.", runko)

    # ---- ruotsi ja englanti ----
    for kieli, polku, d in (("sv", "/sv/bedragerier/", SV), ("en", "/en/scams/", EN)):
        tyypit = "".join(f'<section class="huij"><h2>{esc(o)}</h2><p>{esc(t)}</p><ul>' + "".join(f"<li>{esc(x)}</li>" for x in ohj) + "</ul></section>" for o, t, ohj in d["tyypit"])
        runko = f"""<h1>{d["h1"]}</h1>
<p class="lead">{d["lead"]}</p>
<div class="huij-kolme">{"".join(f"<div><b>{n}.</b> {x}</div>" for n, x in enumerate(d["kolme"], 1))}</div>
<section><h2>{d["apu_h"]}</h2><div class="soitot">
<a class="soita" href="tel:+35820333"><b>020 333</b><span>{d["sulku"]}</span></a>
<a class="soita hata" href="tel:112"><b>112</b><span>{d["hata"]}</span></a>
<a class="soita" href="tel:116006"><b>116 006</b><span>{d["riku"]}</span></a></div>
<ol class="apu-askeleet">{"".join(f"<li>{x}</li>" for x in d["askeleet"])}</ol></section>
{tyypit}
<p>{d["fi"]} <a href="/huijaukset/" hreflang="fi" lang="fi">Tunnista huijaus (suomeksi)</a> · <a href="/" hreflang="fi" lang="fi">Keräysvahti</a></p>
<p class="mute small">{d["lahteet"]}</p>"""
        k(polku, d["title"], d["meta"], runko, lang=kieli)

    return urls if JULKINEN else []


# ---------- skriptit ----------
TARKISTINJS = r"""<script>(function(){
var V=document.getElementById('viesti'),T=document.getElementById('tulos');
var S=[
 [/\b(heti|välittömästi|viimeistään|24 ?h|24 tunni|48 tunni|tänään|vanhenee|suljetaan|lukitaan|jäädytetään|estetään|kiireelli|viimeinen (päivä|mahdollisuus|muistutus))/i,2,'Kiire tai uhkailu','Huijari yrittää saada sinut toimimaan ennen kuin ehdit ajatella.'],
 [/(pankkitunnu|verkkopankk|tunnuslu|tunnistau|kirjaudu|vahvista (henkilöllisyy|tieto|tili)|mobiilivarmen|päivitä tieto)/i,3,'Pyyntö kirjautua tai vahvistaa tietoja','Pankit ja viranomaiset eivät pyydä kirjautumaan viestin linkin kautta.'],
 [/(kortin numero|korttinumero|korttitied|cvv|cvc|turvakoodi|luottokort)/i,3,'Kortin tietoja pyydetään','Älä koskaan anna kortin tietoja viestin perusteella.'],
 [/(tullimaksu|toimitusmaksu|lähetysmaksu|käsittelymaksu|maksa \d|\d+[,.]\d{2} ?(€|eur)|€ ?\d+[,.]\d{2})/i,2,'Pieni maksu','Pieni summa, kuten 1,99 € tullimaksu, on tyypillinen tapa kalastella kortin tietoja.'],
 [/(uusi numero|uusi numeroni|vaihdoin numero|puhelimeni hajosi|puhelin hajosi|kännykkä hajosi|tallenna (tämä|uusi) numero|hei äiti|hei isä|moi äiti|moi isä)/i,3,'"Uusi numero" -tarina','Soita läheisesi vanhaan, tuttuun numeroon ennen kuin teet mitään.'],
 [/(voisitko maksaa|voitko maksaa|maksaisitko|lainaisitko|lainata rahaa|tarvitsen rahaa|lasku pitäisi maksaa|maksan huomenna takaisin)/i,3,'Rahapyyntö','Varmista aina toista kautta, kuka rahaa pyytää.'],
 [/(turvatili|turvalliselle tilille|siirrä (rahasi|varat|rahat))/i,4,'"Turvatili"','Turvatiliä ei ole olemassa. Kukaan oikea taho ei pyydä siirtämään rahoja turvaan.'],
 [/(anydesk|teamviewer|quicksupport|etäyhtey|etäkäyt|asenna (sovellus|ohjelma))/i,4,'Pyyntö asentaa ohjelma tai antaa etäyhteys','Etäyhteydellä huijari pääsee koneellesi ja verkkopankkiisi.'],
 [/(lahjakort|gift ?card|google play|itunes|steam-kort|apple-kort)/i,3,'Lahjakortit','Maksu lahjakortteina on lähes aina huijaus.'],
 [/(voitit|voittaja|olet voittanut|palkinto odottaa|arvonnan voit|ilmainen iphone)/i,2,'Voitto tai palkinto','Et voi voittaa arvonnassa, johon et osallistunut.'],
 [/(tuotto|tuplaa|sijoita|kryptosijoit|bitcoin|passiivista tuloa|tienasin)/i,2,'Sijoitus- tai tuottolupaus','Suuret ja varmat tuotot ovat sijoitushuijauksen tunnusmerkki.'],
 [/(älä kerro|pidä tämä (salassa|meidän välisenä)|kenellekään muulle|salassa)/i,3,'Salailu','Huijari haluaa estää sinua kysymästä neuvoa läheiseltä.'],
 [/(poliisi|kela|verohallinto|veronpalautu|tulli|traficom|ulosotto|oikeus ?ministeriö)/i,1,'Viranomaisen nimi','Viranomaisten nimiä käytetään usein huijauksissa. Tarkista asia viranomaisen omasta palvelusta.'],
 [/(paketti|lähetys|seurantanumero|toimitus epäonnistu|noutamaton)/i,1,'Pakettiviesti','Tarkista lähetykset itse kuljetusyhtiön sovelluksesta.']
];
var BRAND={posti:['posti.fi'],vero:['vero.fi'],kela:['kela.fi'],nordea:['nordea.fi','nordea.com'],danske:['danskebank.fi','danskebank.com'],'s-pankki':['s-pankki.fi'],spankki:['s-pankki.fi'],aktia:['aktia.fi'],traficom:['traficom.fi'],poliisi:['poliisi.fi'],tulli:['tulli.fi'],dhl:['dhl.com','dhl.fi'],mobilepay:['mobilepay.fi','mobilepay.dk'],op:['op.fi'],omavero:['vero.fi'],suomi:['suomi.fi'],netflix:['netflix.com'],microsoft:['microsoft.com']};
var LYH=/^(bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly|rb\.gy|shorturl\.at|ow\.ly|t\.ly|tiny\.cc|s\.id|rebrand\.ly)$/i;
var TLD=/\.(top|xyz|icu|shop|live|online|click|info|site|buzz|cyou|rest|sbs|cfd|lol|vip|win|loan|support|help|link)$/i;
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function domainit(s){var r=[],m,re=/\b((?:https?:\/\/)?(?:www\.)?((?:[a-z0-9-]+\.)+[a-z]{2,})(?:[\/?#][^\s]*)?)/ig;
 while((m=re.exec(s))){var d=m[2].toLowerCase();if(/\.(fi|com|net|org|info|io|me|ly|co|top|xyz|icu|shop|live|online|click|site|app|link|ru|cn|cc|eu|de|se|uk|us)$/.test(d)||/^https?:/i.test(m[1]))r.push(d)}return r}
function rek(d){var p=d.split('.');return p.slice(-2).join('.')}
function tarkista(){var s=V.value.trim();T.innerHTML='';if(!s){T.appendChild(el('p','mute','Liitä ensin viesti.'));return}
 var osumat=[],pisteet=0;
 S.forEach(function(r){if(r[0].test(s)){osumat.push([r[2],r[3],r[1]]);pisteet+=r[1]}});
 var ds=domainit(s);
 if(ds.length){pisteet+=1;osumat.push(['Viestissä on linkki','Älä avaa linkkiä. Mene palveluun itse kirjoittamalla osoite tai käyttämällä sovellusta.',1])}
 ds.forEach(function(d){var r=rek(d);
  if(LYH.test(r)||LYH.test(d)){pisteet+=3;osumat.push(['Lyhennetty linkki: '+d,'Lyhennetty linkki piilottaa, minne se oikeasti vie.',3])}
  if(/^\d+\.\d+\.\d+\.\d+$/.test(d)||/xn--/.test(d)){pisteet+=4;osumat.push(['Epätavallinen osoite: '+d,'Osoite on IP-numero tai käyttää merkkejä, joilla matkitaan oikeaa nimeä.',4])}
  else if(TLD.test(d)){pisteet+=2;osumat.push(['Epätavallinen verkkotunnus: '+d,'Suomalaiset palvelut käyttävät yleensä .fi- tai .com-osoitteita.',2])}
  Object.keys(BRAND).forEach(function(b){var re=new RegExp('(^|[.-])'+b.replace('-','\\-')+'([.-]|$)');
   if(re.test(d)&&BRAND[b].indexOf(r)<0){pisteet+=4;osumat.push(['Osoite matkii palvelua: '+d,'Osoite näyttää liittyvän palveluun '+b+', mutta oikea osoite on '+BRAND[b][0]+'.',4])}})});
 var taso=pisteet>=6?['Paljon huijauksen merkkejä','korkea','Älä vastaa, älä avaa linkkejä äläkä maksa. Poista viesti. Jos jo toimit viestin ohjeiden mukaan, katso ohjeet alta.']
  :pisteet>=3?['Useita varoitusmerkkejä','kohtalainen','Ole varovainen. Tarkista asia itse virallisesta lähteestä ennen kuin teet mitään.']
  :['Ei selviä huijauksen merkkejä','matala','Tämä ei tarkoita, että viesti on varmasti turvallinen. Jos viestissä pyydetään rahaa tai tunnuksia, tarkista asia aina itse.'];
 var b=el('div','arvio '+taso[1]);b.appendChild(el('b','',taso[0]));b.appendChild(el('p','',taso[2]));T.appendChild(b);
 if(osumat.length){var ul=el('ul','merkit');osumat.sort(function(a,b){return b[2]-a[2]}).forEach(function(o){var li=el('li');li.appendChild(el('b','',o[0]));li.appendChild(el('span','',o[1]));ul.appendChild(li)});
  T.appendChild(el('h2','','Löydetyt merkit'));T.appendChild(ul)}
 if(taso[1]==='korkea'){var a=el('a','apunappi','Jos jo avasit linkin tai maksoit: ohjeet →');a.href='/huijaukset/apua/';T.appendChild(a)}
 T.scrollIntoView({behavior:'smooth',block:'start'})}
document.getElementById('tarkista').onclick=tarkista;
document.getElementById('esim').onclick=function(){V.value='Posti: Lähetyksesi on pysäytetty puuttuvan tullimaksun (2,99 €) vuoksi. Maksa 24 tunnin kuluessa, muuten paketti palautetaan: https://posti-fi-seuranta.top/maksu';tarkista()};
})();</script>"""

VISAJS = r"""<script>(function(){
var B=document.getElementById('visa'),i=0,oik=0;
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function nayta(){B.innerHTML='';
 if(i>=VISA.length){var r=el('div','visa-tulos');r.appendChild(el('b','',oik+' / '+VISA.length+' oikein'));
  r.appendChild(el('p','',oik>=9?'Erinomaista! Jaa testi läheisillesi, jotta hekin oppivat tunnistamaan huijaukset.':oik>=6?'Hyvä! Muutama jäi kiinni. Lue lisää huijaustyypeistä.':'Huijarit ovat taitavia. Lue huijaustyypit ja kokeile uudelleen.'));
  var n=el('div','napit'),j=el('button','btn','Jaa testi');j.type='button';j.onclick=function(){var u=location.href,t='Tunnistatko huijauksen? Sain '+oik+'/'+VISA.length+'. Kokeile:';
   if(navigator.share)navigator.share({title:document.title,text:t,url:u}).catch(function(){});else location.href='https://wa.me/?text='+encodeURIComponent(t+' '+u)};
  var u=el('button','btn toissij','Aloita alusta');u.type='button';u.onclick=function(){i=0;oik=0;nayta()};n.appendChild(j);n.appendChild(u);r.appendChild(n);
  var l=el('a','','Lue yleisimmät huijaukset →');l.href='/huijaukset/';r.appendChild(l);B.appendChild(r);return}
 var q=VISA[i];B.appendChild(el('p','visa-nro','Kysymys '+(i+1)+' / '+VISA.length));
 var k=el('div','kupla');k.appendChild(el('small','',q[0]+' · '+q[1]));k.appendChild(el('p','',q[2]));B.appendChild(k);
 var n=el('div','napit');[['Huijaus',true],['Todennäköisesti aito',false]].forEach(function(v){var b=el('button','btn'+(v[1]?'':' toissij'),v[0]);b.type='button';
  b.onclick=function(){var ok=v[1]===q[3];if(ok)oik++;n.remove();var s=el('div','selitys '+(ok?'oikein':'vaarin'));s.appendChild(el('b','',ok?'Oikein!':'Ei aivan.'));s.appendChild(el('p','',q[4]));
   var x=el('button','btn',i+1<VISA.length?'Seuraava':'Katso tulos');x.type='button';x.onclick=function(){i++;nayta();B.scrollIntoView({block:'start'})};s.appendChild(x);B.appendChild(s);x.focus()};n.appendChild(b)});
 B.appendChild(n)}
nayta()})();</script>"""

JAAJS = r"""<script>(function(){var b=document.getElementById('jaa');if(!b)return;b.onclick=function(){
var u=location.href,t='Muistilista huijauksia vastaan. Tulosta ja laita jääkaapin oveen:';
if(navigator.share){navigator.share({title:document.title,text:t,url:u}).catch(function(){})}
else{location.href='https://wa.me/?text='+encodeURIComponent(t+' '+u)}}})();</script>"""

# ---------- käännökset ----------
SV = dict(
 title="Känn igen bedrägerier | Keräysvahti", meta="De vanligaste bedrägerierna i Finland och vad du ska göra om du redan blivit lurad.",
 h1="Känn igen bedrägerier", lead="Bedragaren skyndar på, spelar på känslor och ber om pengar eller bankkoder. Här är de vanligaste bedrägerierna i Finland och vad du ska göra.",
 kolme=["Stanna upp. Brådska är bedragarens verktyg.", "Ge aldrig ut bankkoder, kortuppgifter eller personbeteckning.", "Kontrollera själv via en officiell källa."],
 apu_h="Om du redan blivit lurad", sulku="Spärrtjänsten: spärra kort och nätbank, dygnet runt", hata="Nödnummer vid akut fara", riku="Brottsofferjouren: stöd och råd",
 askeleet=["<b>Ring genast din bank</b> och spärra kort och nätbankskoder. Bankens nummer finns på kortet och på bankens webbplats.",
           "<b>Gör en brottsanmälan</b> till polisen, även på nätet: <a href=\"https://poliisi.fi/sv\" rel=\"noopener\">poliisi.fi</a>. Spara meddelanden och kvitton.",
           "<b>Byt lösenord</b> som bedragaren kan ha sett, börja med e-posten.",
           "<b>Sök stöd:</b> Brottsofferjouren 116 006. Att bli lurad är ingen skam."],
 tyypit=[("Falsk insamlare", "En insamlare vid dörren eller butiken samlar in pengar, ofta i namn av sjuka barn, men kan inte uppge något insamlingsnummer.",
          ["Fråga efter insamlingstillståndets nummer.", "Kontrollera insamlingen på Keräysvahti och skänk bara till kontot i tillståndet.", "Öppna inte plånboken framför en främling."]),
         ("Falsk polis eller bankanställd ringer", "Den som ringer påstår att ditt konto missbrukas och ber om bankkoder eller att flytta pengar till ett \"säkert konto\".",
          ["Polisen eller banken frågar aldrig efter bankkoder i telefon.", "Avsluta samtalet och ring själv bankens officiella nummer.", "Något \"säkert konto\" finns inte."]),
         ("Bedrägliga meddelanden", "Sms eller e-post om paket, skatt eller bank med brådska och en länk till en falsk sida.",
          ["Öppna inte länken. Gå själv till tjänsten.", "Banker ber aldrig dig logga in via en länk i ett meddelande."]),
         ("\"Hej mamma, det här är mitt nya nummer\"", "Ett meddelande från ett okänt nummer i en anhörigs namn. Snart ber personen dig betala en räkning.",
          ["Ring din anhörigas gamla nummer och fråga.", "Betala inte till ett okänt konto."]),
         ("Investerings- och kryptobedrägeri", "Annonser med kändisar lovar snabba vinster. En \"rådgivare\" får dig att föra över allt mer pengar.",
          ["Kontrollera företaget på Finansinspektionens varningslista.", "Installera aldrig fjärrstyrningsprogram på någons begäran."]),
         ("Romansbedrägeri", "En person du träffat på nätet blir snabbt kär men kan aldrig träffas. Sedan behövs pengar.",
          ["Skicka aldrig pengar till någon du inte träffat.", "Berätta för en närstående."])],
 fi="På finska finns fler verktyg:", lahteet="Källor: polisen, Finansinspektionen och Cybersäkerhetscentret. Keräysvahti är inte en myndighetstjänst.")

EN = dict(
 title="Recognise a scam | Keräysvahti", meta="The most common scams in Finland and what to do if you have already been scammed.",
 h1="Recognise a scam", lead="Scammers rush you, play on your emotions and ask for money or bank credentials. Here are the most common scams in Finland and what to do.",
 kolme=["Stop. Urgency is the scammer's tool.", "Never give out bank credentials, card details or your personal identity code.", "Check for yourself from an official source."],
 apu_h="If you have already been scammed", sulku="Card and online bank blocking service, 24/7", hata="Emergency number when in danger", riku="Victim Support Finland: help and advice",
 askeleet=["<b>Call your bank immediately</b> and block your cards and online banking credentials. Your bank's number is on your card and on the bank's website.",
           "<b>Report the crime</b> to the police, also online: <a href=\"https://poliisi.fi/en\" rel=\"noopener\">poliisi.fi</a>. Keep messages and receipts.",
           "<b>Change passwords</b> the scammer may have seen, starting with your email.",
           "<b>Get support:</b> Victim Support Finland 116 006. Being scammed is nothing to be ashamed of."],
 tyypit=[("Fake fundraiser", "A collector at your door or outside a shop asks for money, often for sick children, but cannot give a fundraising permit number.",
          ["Ask for the fundraising permit number.", "Check the fundraiser on Keräysvahti and donate only to the account in the permit.", "Don't open your wallet in front of a stranger."]),
         ("Fake police officer or bank employee calls", "The caller claims your account is being misused and asks for your credentials or to move money to a \"safe account\".",
          ["The police or your bank will never ask for your credentials over the phone.", "Hang up and call your bank's official number yourself.", "There is no such thing as a \"safe account\"."]),
         ("Scam messages", "Texts or emails about parcels, taxes or your bank, with urgency and a link to a fake website.",
          ["Don't open the link. Go to the service yourself.", "Banks never ask you to log in through a link in a message."]),
         ("\"Hi mum, this is my new number\"", "A message from an unknown number in a family member's name, soon asking you to pay a bill.",
          ["Call your family member's old number and ask.", "Don't pay to an unknown account."]),
         ("Investment and crypto scams", "Ads featuring celebrities promise quick profits. An \"adviser\" gets you to transfer more and more money.",
          ["Check the company on the Finnish Financial Supervisory Authority's warning list.", "Never install remote access software at someone's request."]),
         ("Romance scam", "Someone you met online falls in love quickly but can never meet. Then they need money.",
          ["Never send money to someone you haven't met.", "Tell someone close to you."])],
 fi="More tools are available in Finnish:", lahteet="Sources: the Finnish police, the Financial Supervisory Authority and the National Cyber Security Centre. Keräysvahti is not a government service.")
