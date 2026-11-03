"""Lataa Poliisihallituksen lupalistan (lista.pdf on jo ladattu), lukee sen ja päivittää data/luvat.json.
Ei päivitä, jos lupia tulee selvästi vähemmän kuin ennen (PDF:n rakenne muuttunut)."""
import json, os, re, subprocess, sys, datetime
import pdfplumber
t = pdfplumber.open("lista.pdf").pages[0].extract_text() or ""
m = re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(20\d\d)\b", t)
p = f"{int(m[0][0])}.{int(m[0][1])}.{m[0][2]}" if m else datetime.date.today().strftime("%-d.%-m.%Y")
print(f"::notice title=Listan päiväys::{p} (ensimmäisen sivun alku: {t[:150]!r})")
subprocess.run([sys.executable, "tyokalut/lue-pdf.py"], check=True, env={**os.environ, "PAIVAYS": p})
u = json.load(open("luvat.json")); v = json.load(open("data/luvat.json"))
n, o = len(u["luvat"]), len(v["luvat"])
print(f"::notice title=Luvat::uusi {n}, vanha {o}, päiväys {v['paivays']} -> {u['paivays']}")
if n < 0.8 * o:
    print(f"::error::Liian vähän lupia ({n} / {o}), ei päivitetä"); sys.exit(1)
os.replace("luvat.json", "data/luvat.json")
