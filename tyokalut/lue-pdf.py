import pdfplumber, re, json
from collections import Counter
COLS = ["Keräysnumero", "Voimassa", "Julkaisu", "Viran-", "Pankkiyhteys", "Y-tunnus", "Yhteisö", "Kotipaikka"]
KEY = ["nro", "voimassa", "kayttotarkoitus", "viranomainen", "pankki", "ytunnus", "yhteiso", "kotipaikka"]
recs = []; cur = None
with pdfplumber.open("lista.pdf") as pdf:
    for page in pdf.pages:
        words = page.extract_words(keep_blank_chars=False, use_text_flow=False, x_tolerance=1.5)
        hdr = {w["text"]: w for w in words if w["text"] in COLS}
        if len(hdr) < 8: continue
        htop = max(hdr[c]["bottom"] for c in COLS)
        xs = [hdr[c]["x0"] - 2 for c in COLS]
        xe = xs[1:] + [page.width - 15]
        # rivit
        rows = {}
        for w in words:
            if w["top"] <= htop + 8: continue
            if re.fullmatch(r"\d+ / \d+|\d+/\d+", w["text"]): continue
            k = round(w["top"] / 3)
            rows.setdefault(k, []).append(w)
        for k in sorted(rows):
            ws = sorted(rows[k], key=lambda w: w["x0"])
            if ws[-1]["top"] > page.height - 30 and len(ws) <= 3: continue  # sivunumero
            cells = [[] for _ in COLS]; ends = [0] * len(COLS)
            for w in ws:
                i = max(j for j in range(len(xs)) if w["x0"] >= xs[j] - 1) if w["x0"] >= xs[0] - 1 else 0
                cells[i].append(w["text"]); ends[i] = max(ends[i], w["x1"])
            c = [" ".join(x) for x in cells]
            gaps = [xe[j] - ends[j] for j in range(len(COLS))]
            if re.fullmatch(r"RA/\d{4}/\d+", c[0]):
                cur = {kk: [] for kk in KEY}; recs.append(cur)
            if cur is None: continue
            for kk, v, g in zip(KEY, c, gaps):
                if v: cur[kk].append((v, g))
ERILLISET = set("ry rf sr r.y. ry. rf. r.f. s.r. ja tai sekä och i av för på till med the of and for in e.v. ry., ab oy ei on ovat sen eri".split())
def join(parts, tiukka=False):
    """Yhdistää solun rivit. PDF katkaisee kapeassa sarakkeessa pitkät sanat kesken (esim. 'Lastensuojelujärjest' + 'öt'):
    silloin rivit liitetään ilman välilyöntiä."""
    s, prev_gap = "", 99
    for item in parts:
        p, g = item if isinstance(item, tuple) else (item, 99)
        eka = p.split(" ")[0]; edellinen = s.split(" ")[-1] if s else ""
        katkennut = (s and eka[:1].islower() and eka.strip(".,") not in ERILLISET and edellinen[-1:].isalpha() and
                     ((not tiukka and len(eka) <= 4) or prev_gap < (2.5 if tiukka else 4)))
        if s.endswith("-") and not s.endswith(" -") and p[:1].islower(): s = s + p
        elif katkennut: s = s + p
        else: s = s + " " + p if s else p
        prev_gap = g
    return re.sub(r"\s+", " ", s).strip()
out = []
for r in recs:
    pank = " ".join(x[0] for x in r["pankki"]); ib = re.search(r"FI\d{2}\s?(?:\d\s?){14}", pank)
    v = join(r["voimassa"]); d = re.findall(r"\d\d\.\d\d\.\d{4}", v)
    out.append({"nro": join(r["nro"]), "alku": d[0] if d else "", "loppu": d[1] if len(d) > 1 else "",
                "kayttotarkoitus": join(r["kayttotarkoitus"], tiukka=True), "viranomainen": join(r["viranomainen"]).replace("Poliisihallitu s", "Poliisihallitus"),
                "iban": ib.group(0).replace(" ", "") if ib else "", "ytunnus": join(r["ytunnus"]).replace(" ", ""),
                "yhteiso": join(r["yhteiso"]), "kotipaikka": join(r["kotipaikka"])})
print(len(out), "lupaa;", len({o["nro"] for o in out}), "uniikkia")
print(Counter(o["viranomainen"] for o in out).most_common(4))
print("ilman ibania", sum(not o["iban"] for o in out), "ilman ytunnusta", sum(not re.fullmatch(r"\d{7}-\d", o["ytunnus"]) for o in out), "loppupv", sum(bool(o["loppu"]) for o in out))
for o in out[:3] + [x for x in out if x["nro"] in ("RA/2020/585", "RA/2020/469", "RA/2020/425", "RA/2026/1048")]:
    print(o["nro"], "|", o["yhteiso"], "|", o["kotipaikka"], "|", o["ytunnus"], "|", o["iban"], "|", o["kayttotarkoitus"][:70])
bad = [o for o in out if not re.fullmatch(r"\d{7}-\d", o["ytunnus"])][:5]
for o in bad: print("HUONO", o["nro"], o["ytunnus"], o["yhteiso"])
json.dump({"paivays": "25.8.2026", "luvat": out}, open("luvat.json", "w"), ensure_ascii=False)
