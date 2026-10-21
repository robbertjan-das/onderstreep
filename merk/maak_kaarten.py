"""Maakt de social-afbeeldingen van een bulletin: carrousel (1080x1350) en stories (1080x1920)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HIER = Path(__file__).resolve().parent
ZOEKPADEN = [HIER / "lettertypes", HIER, Path("/home/claude")]

def _vind(patroon):
    for map_ in ZOEKPADEN:
        hits = sorted(map_.glob(patroon)) if map_.exists() else []
        if hits: return str(hits[0])
    raise FileNotFoundError(f"lettertype {patroon} niet gevonden in {', '.join(map(str, ZOEKPADEN))}")

def _variabel(pad, px, assen):
    f = ImageFont.truetype(pad, px)
    try: f.set_variation_by_axes(assen)
    except Exception: pass  # statisch lettertype: gebruik zoals het is
    return f
INK, GRIJS, WIT = "#141414", "#555555", "#ffffff"
MAANDEN = ["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]
DAGEN = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]

def font(soort, px, wght=400):
    if soort == "serif":
        return _variabel(_vind("[Nn]ewsreader*.ttf"), px, [wght, 72])
    if soort == "sans":
        return _variabel(_vind("AtkinsonHyperlegibleNext*.ttf"), px, [wght])
    return _variabel(_vind("AtkinsonHyperlegibleMono*.ttf"), px, [400])

def wrap(draw, tekst, f, breedte):
    regels, regel = [], ""
    for woord in tekst.split():
        proef = (regel + " " + woord).strip()
        if draw.textlength(proef, font=f) <= breedte: regel = proef
        else: regels.append(regel); regel = woord
    if regel: regels.append(regel)
    return regels

def tekst(draw, xy, t, f, kleur=INK, breedte=888, lh=1.2):
    x, y = xy
    for r in wrap(draw, t, f, breedte):
        draw.text((x, y), r, font=f, fill=kleur); y += int(f.size * lh)
    return y

def hoogte(draw, t, f, breedte=888, lh=1.2):
    return len(wrap(draw, t, f, breedte)) * int(f.size * lh)

def nl_datum(iso):
    import datetime as d
    dt = d.date.fromisoformat(iso); return f"{DAGEN[dt.weekday()]} {dt.day} {MAANDEN[dt.month-1]} {dt.year}"

def eerste_zin(t):
    for sep in [". ", "; "]:
        if sep in t: return t.split(sep)[0] + "."
    return t

# de streep ligt op elke slide van een carrousel of story op dezelfde hoogte, zodat hij bij het vegen doorloopt
STREEP = {1350: 470, 1920: 825}

def canvas(h): 
    img = Image.new("RGB", (1080, h), WIT); return img, ImageDraw.Draw(img)

def cover(b, h, pad_top):
    img, d = canvas(h); M = 96
    d.text((M, pad_top), "onder/streep", font=font("serif", 56, 500), fill=INK)
    # datum en streep liggen vast; de streep ligt op elke slide op dezelfde hoogte
    basis = 88 if h == 1350 else 92
    fd = font("serif", basis, 400)
    datum = nl_datum(b["datum"]); regels = [datum.rsplit(" ", 1)[0], datum.rsplit(" ", 1)[1]]
    while d.textlength(regels[0], font=fd) > 888: fd = font("serif", fd.size - 2, 400)
    y = STREEP[h] - 32 - 2 * int(basis * 1.05)
    for r in regels: d.text((M, y), r, font=fd, fill=INK); y += int(basis * 1.05)
    y = STREEP[h]; d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 34
    # onder de streep: "1 onder de streep" of "Vandaag niets.", in dezelfde opmaak; wat het is, staat op de slides erna
    n = len(b["berichten"])
    d.text((M, y), f"{n} onder de streep" if n else "Vandaag niets.", font=font("serif", 72, 400), fill=INK)
    y += int(72 * 1.05) + 28
    fm = font("mono", 30)
    for t in (f"{b['beoordeeld']} beoordeeld", f"{b['doorgestreept']} doorgestreept", f"{b['geplaatst']} geplaatst vanaf 11/16"):
        d.text((M, y), t, font=fm, fill=GRIJS); y += 45
    d.text((M, h - (96 if h == 1350 else 320) - 53), "Het nieuws, onderstreept.", font=font("serif", 44, 400), fill=INK)
    return img

def bericht(m, h, pad_top, pad_bottom):
    img, d = canvas(h); M = 96
    d.text((M, pad_top), "onder/streep", font=font("serif", 36 if h == 1350 else 40, 500), fill=GRIJS)
    fl = font("sans", 26 if h == 1350 else 28, 600)
    d.text((1080 - M - d.textlength(m["label"], font=fl), pad_top + 10), m["label"], font=fl, fill=GRIJS)
    fs = font("serif", 96 if h == 1350 else 104, 500)
    y = STREEP[h] - 16 - int(fs.size * 1.1)
    d.text((M, y), f"{m['totaal']}/16", font=fs, fill=INK)
    y = STREEP[h]; d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 42
    woorden = len(m["kop"].split())
    kp = (60 if woorden <= 14 else 52) if h == 1350 else (66 if woorden <= 14 else 58)
    y = tekst(d, (M, y), m["kop"], font("serif", kp, 500), lh=1.15)
    # voor wie, één zin, met het label in de regel
    y += 44
    fl2 = font("sans", 26 if h == 1350 else 28, 600); fz = font("sans", 34 if h == 1350 else 36, 400)
    label = "Voor wie"; lw = d.textlength(label, font=fl2) + 22
    zin = eerste_zin(m["voor_wie"]); regels = wrap(d, zin, fz, 888 - lw)
    d.text((M, y + 7), label, font=fl2, fill=GRIJS)
    d.text((M + lw, y), regels[0], font=fz, fill=INK); y += int(fz.size * 1.4)
    for r in wrap(d, " ".join(regels[1:]), fz, 888) if len(regels) > 1 else []:
        d.text((M, y), r, font=fz, fill=INK); y += int(fz.size * 1.4)
    fb = font("mono", 24 if h == 1350 else 26)
    bron = m["bron"]["naam"] if h == 1350 else f"{nl_datum(m['bulletin_datum'])}. Het hele bulletin op onderstreep.nl"
    yb = h - pad_bottom - hoogte(d, bron, fb, lh=1.5)
    tekst(d, (M, yb), bron, fb, kleur=GRIJS, lh=1.5)
    return img

def slot(b, h, pad_top, pad_bottom):
    img, d = canvas(h); M = 96
    d.text((M, pad_top), "onder/streep", font=font("serif", 36 if h == 1350 else 40, 500), fill=GRIJS)
    som = [f"{b['beoordeeld']} beoordeeld", f"{b['doorgestreept']} doorgestreept", f"{b['geplaatst']} geplaatst vanaf 11/16"]
    fm, fs = font("mono", 28), font("serif", 96, 400)
    y = STREEP[h] - 32 - len(som) * 42
    for s in som: d.text((M, y), s, font=fm, fill=GRIJS); y += 42
    y = STREEP[h]; d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 34
    d.text((M, y), "Streep eronder.", font=fs, fill=INK)
    # in de story staat hier niets: die ruimte is voor de linksticker "Het hele bulletin", die Instagram zelf tekent
    if h == 1350:
        fz = font("sans", 34, 400); fu = font("mono", 28)
        yb = h - pad_bottom - 42 - 48 - 10
        d.text((M, yb), "Het hele bulletin, elke ochtend om zeven.", font=fz, fill=INK); d.text((M, yb + 58), "onderstreep.nl", font=fu, fill=GRIJS)
    return img

def main(pad, uit):
    b = json.loads(Path(pad).read_text(encoding="utf-8"))
    for m in b["berichten"]:
        s = m["score"]; m["totaal"] = sum(s.values()); m["bulletin_datum"] = b["datum"]
    b["berichten"].sort(key=lambda m: (-m["totaal"], -m["score"]["reikwijdte"], -m["score"]["hardheid"]))
    b["geplaatst"] = len(b["berichten"]); b["doorgestreept"] = b["beoordeeld"] - b["geplaatst"]
    uit = Path(uit); uit.mkdir(parents=True, exist_ok=True); d = b["datum"]
    cover(b, 1350, 96).save(uit / f"{d}-carrousel-01-cover.png")
    for i, m in enumerate(b["berichten"], 2):
        bericht(m, 1350, 96, 96).save(uit / f"{d}-carrousel-{i:02d}-bericht.png")
    slot(b, 1350, 96, 96).save(uit / f"{d}-carrousel-{len(b['berichten'])+2:02d}-slot.png")
    cover(b, 1920, 260).save(uit / f"{d}-story-01-cover.png")
    for i, m in enumerate(b["berichten"], 2):
        bericht(m, 1920, 260, 320).save(uit / f"{d}-story-{i:02d}-bericht.png")
    slot(b, 1920, 260, 320).save(uit / f"{d}-story-{len(b['berichten'])+2:02d}-slot.png")
    overzicht(b).save(uit / f"{d}-overzicht.png")
    overzicht_vierkant(b).save(uit / f"{d}-overzicht-vierkant.png")
    print("klaar:", uit)
    for p in sorted(uit.iterdir()): print("  ", p.name)


def koppenlijst(d, berichten, x, y, onder, breedte, start=44, minimum=30, gat=30):
    """Zet score + kop onder elkaar tussen y en onder. Krimpt de letter tot alles past;
    past het bij de kleinste maat nog niet, dan zoveel als past plus '+ N andere berichten'."""
    def maat(px, aantal):
        f = font("serif", px, 500)
        return sum(hoogte(d, m["kop"], f, breedte - 150, 1.18) + gat for m in berichten[:aantal]), f
    for px in range(start, minimum - 1, -2):
        h, f = maat(px, len(berichten))
        if y + h <= onder: break
    toon = len(berichten)
    while toon > 1 and y + maat(minimum, toon)[0] + 45 > onder and y + maat(px, toon)[0] > onder:
        toon -= 1; f = font("serif", minimum, 500)
    for m in berichten[:toon]:
        d.text((x, y), f"{m['totaal']}/16", font=f, fill=GRIJS)
        y = tekst(d, (x + 150, y), m["kop"], f, breedte=breedte - 150, lh=1.18) + gat
    rest = len(berichten) - toon
    if rest:
        d.text((x, y), f"+ {rest} {'ander bericht' if rest == 1 else 'andere berichten'}", font=font("mono", 26), fill=GRIJS); y += 45
    return y

def overzicht(b, h=1350, pad=96):
    """Eén kaart met alle koppen van de dag, voor LinkedIn, Threads en WhatsApp."""
    img, d = canvas(h); M = pad
    d.text((M, M), "onder/streep", font=font("serif", 44, 500), fill=INK)
    y = M + 44 + 56
    fd = font("serif", 56, 400)
    y = tekst(d, (M, y), nl_datum(b["datum"]), fd, lh=1.1)
    y += 24; d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 44
    if not b["berichten"]:
        d.text((M, y), "Vandaag niets.", font=font("serif", 96, 400), fill=INK); y += 130
    som = f"{b['beoordeeld']} beoordeeld, {b['doorgestreept']} doorgestreept, {b['geplaatst']} geplaatst vanaf 11/16."
    fm, fs = font("mono", 26), font("serif", 56, 400)
    yb = h - M - int(56 * 1.05)
    if b["berichten"]: koppenlijst(d, b["berichten"], M, y, yb - 50 - 40, 1080 - 2 * M, gat=36)
    d.text((M, yb), "Streep eronder.", font=fs, fill=INK)
    d.text((M, yb - 50), som, font=fm, fill=GRIJS)
    return img


def overzicht_vierkant(b, S=1200, M=96):
    """Vierkante overzichtskaart voor LinkedIn, X en Bluesky."""
    img = Image.new("RGB", (S, S), WIT); d = ImageDraw.Draw(img)
    d.text((M, M), "onder/streep", font=font("serif", 44, 500), fill=INK)
    y = M + 44 + 48
    y = tekst(d, (M, y), nl_datum(b["datum"]), font("serif", 56, 400), breedte=S - 2 * M, lh=1.1)
    y += 22; d.line([(M, y), (S - M, y)], fill=INK, width=2); y += 40
    n = len(b["berichten"])
    if n == 0:
        d.text((M, y), "Vandaag niets.", font=font("serif", 96, 400), fill=INK)
    som = f"{b['beoordeeld']} beoordeeld, {b['doorgestreept']} doorgestreept, {b['geplaatst']} geplaatst vanaf 11/16."
    yb = S - M - int(56 * 1.05)
    if n: koppenlijst(d, b["berichten"], M, y, yb - 48 - 40, S - 2 * M)
    d.text((M, yb), "Streep eronder.", font=font("serif", 56, 400), fill=INK)
    d.text((M, yb - 48), som, font=font("mono", 26), fill=GRIJS)
    return img

def weekkaart(week, bulletins, S=(1080, 1350), M=96):
    """Zondagskaart: de week in één beeld, geplaatst en net niet."""
    W, H = S; img = Image.new("RGB", (W, H), WIT); d = ImageDraw.Draw(img)
    d.text((M, M), "onder/streep", font=font("serif", 44, 500), fill=INK)
    y = M + 44 + 48
    y = tekst(d, (M, y), f"Week {week['week']}", font("serif", 56, 400), breedte=W - 2 * M, lh=1.1)
    y += 22; d.line([(M, y), (W - M, y)], fill=INK, width=2); y += 40
    geplaatst = [m for b in bulletins for m in b["berichten"]]
    geplaatst.sort(key=lambda m: -m["totaal"])
    fk = font("serif", 36, 500); fl = font("sans", 24, 600)
    d.text((M, y), "Onder de streep", font=fl, fill=GRIJS); y += 44
    for m in geplaatst:
        d.text((M, y), f"{m['totaal']}/16", font=fk, fill=GRIJS)
        y = tekst(d, (M + 130, y), m["kop"], fk, breedte=W - M - (M + 130), lh=1.18) + 22
    y += 20
    d.text((M, y), "Net niet", font=fl, fill=GRIJS); y += 44
    for n in week["net_niet"]:
        d.text((M, y), f"{n['score']}/16", font=fk, fill=GRIJS)
        y = tekst(d, (M + 130, y), n["kop"], fk, kleur=GRIJS, breedte=W - M - (M + 130), lh=1.18) + 22
    beoordeeld = sum(b["beoordeeld"] for b in bulletins); g = len(geplaatst)
    som1 = f"{len(bulletins)} dagen, {beoordeeld} beoordeeld"
    som2 = f"{beoordeeld - g} doorgestreept, {g} geplaatst vanaf 11/16"
    yb = H - M - int(56 * 1.05)
    d.text((M, yb), "Streep eronder.", font=font("serif", 56, 400), fill=INK)
    d.text((M, yb - 86), som1, font=font("mono", 26), fill=GRIJS)
    d.text((M, yb - 48), som2, font=font("mono", 26), fill=GRIJS)
    # periodekaarten (week, maand, jaar) zijn omgekeerd: wit op zwart, zoals de donkere modus van de site
    from PIL import ImageOps
    return ImageOps.invert(img)


if __name__ == "__main__":
    # Gebruik: python merk/maak_kaarten.py bulletins/2026-10-22.json [uitvoermap]
    # Zonder uitvoermap: social/<datum>/ in de projectmap (staat in .gitignore).
    if len(sys.argv) < 2:
        sys.exit("gebruik: python merk/maak_kaarten.py bulletins/JJJJ-MM-DD.json [uitvoermap]")
    bron = Path(sys.argv[1])
    uitmap = sys.argv[2] if len(sys.argv) > 2 else str(HIER.parent / "social" / bron.stem)
    main(bron, uitmap)
