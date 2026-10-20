#!/usr/bin/env python3
"""Hakee ajankohtaiset huijausvaroitukset ja kirjoittaa huijaukset/varoitukset.json.

Lähteet: Kyberturvallisuuskeskuksen RSS-syötteet ja Nytpuhutaan.fi-uutiskooste
(suomalaiset mediat). Mukaan otetaan vain otsikot, joissa puhutaan huijauksista.
Sivu näyttää otsikon, lähteen ja linkin alkuperäiseen juttuun.
"""
import json, os, re, sys, urllib.request, email.utils
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ULOS = os.path.join(ROOT, "huijaukset", "varoitukset.json")
UA = {"User-Agent": "Keraysvahti-varoitukset/1.0 (+https://keraysvahti.fi)"}
RSS = [
    ("Kyberturvallisuuskeskus", "https://www.kyberturvallisuuskeskus.fi/feed/rss/fi"),
    ("Kyberturvallisuuskeskus", "https://www.kyberturvallisuuskeskus.fi/feed/rss/fi/401"),
    ("Kyberturvallisuuskeskus", "https://www.kyberturvallisuuskeskus.fi/feed/rss/fi/399"),
]
KOOSTE = "https://nytpuhutaan.fi/feed.json"
AVAIN = re.compile(r"huija|huijar|kalastel|valepoliisi|valepankki|petosviest|tekstiviestihuij|bedräg|nettipetos|verkkopetos|sijoituspetos|romanssipetos|identiteettivarkau|tietojenkalastel|väärennetty (?:viesti|sivusto)|varoittaa (?:viest|soitoist|puheluist)", re.I)
POIS = re.compile(r"\b(?:jalkapallo|jääkiekko|veikkausliiga|liiga|nhl|tuomio vanhentunut)\b", re.I)
PAIVAT = 21


def hae(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def aika_rss(s):
    try:
        return email.utils.parsedate_to_datetime(s).astimezone(timezone.utc)
    except Exception:
        return None


def main():
    nyt = datetime.now(timezone.utc)
    raja = nyt - timedelta(days=PAIVAT)
    kohteet, tila = [], []
    for nimi, url in RSS:
        try:
            juuri = ET.fromstring(hae(url))
            n = 0
            for it in juuri.iter("item"):
                o = (it.findtext("title") or "").strip()
                l = (it.findtext("link") or "").strip()
                k = re.sub(r"<[^>]+>", " ", it.findtext("description") or "")
                t = aika_rss(it.findtext("pubDate") or "")
                if o and l and t and t >= raja and AVAIN.search(o + " " + k[:400]):
                    kohteet.append({"o": o, "l": l, "s": nimi, "a": t.isoformat()}); n += 1
            tila.append(f"{url}: ok ({n})")
        except Exception as e:
            tila.append(f"{url}: {type(e).__name__} {str(e)[:80]}")
    try:
        d = json.loads(hae(KOOSTE, 40))
        n = 0
        for u in d.get("u", []):
            o = u.get("o", "")
            try:
                t = datetime.fromisoformat(u["a"].replace("Z", "+00:00"))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=timezone.utc)
            except Exception:
                continue
            if t >= raja and AVAIN.search(o) and not POIS.search(o):
                kohteet.append({"o": o, "l": u["l"], "s": u.get("s", ""), "a": t.astimezone(timezone.utc).isoformat()}); n += 1
        tila.append(f"nytpuhutaan: ok ({n})")
    except Exception as e:
        tila.append(f"nytpuhutaan: {type(e).__name__} {str(e)[:80]}")

    # Poista tuplat (sama linkki tai lähes sama otsikko), uusin ensin
    nahty, uniq = set(), []
    for k in sorted(kohteet, key=lambda x: x["a"], reverse=True):
        avain = re.sub(r"\W+", "", k["o"].lower())[:60]
        if k["l"] in nahty or avain in nahty:
            continue
        nahty.update([k["l"], avain]); uniq.append(k)
    uniq = uniq[:30]

    vanha = None
    if os.path.exists(ULOS):
        try:
            vanha = json.load(open(ULOS, encoding="utf-8"))
        except Exception:
            pass
    # Jos kaikki lähteet epäonnistuivat, älä tyhjennä vanhaa listaa
    if not uniq and vanha and all(": ok" not in x for x in tila):
        print("::warning::Kaikki lähteet epäonnistuivat, vanha lista säilytetään"); print("\n".join(tila)); return
    if vanha and vanha.get("u") == uniq:
        print("Ei muutoksia"); print(" | ".join(tila)); return
    os.makedirs(os.path.dirname(ULOS), exist_ok=True)
    json.dump({"p": nyt.isoformat(timespec="minutes"), "u": uniq}, open(ULOS, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"::notice title=Varoitukset::{len(uniq)} kpl. " + " | ".join(tila))


if __name__ == "__main__":
    main()
