"""Maakt de social-afbeeldingen van een bulletin: carrousel (1080x1350) en stories (1080x1920)."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONTS = Path("/home/claude")
INK, GRIJS, WIT = "#141414", "#555555", "#ffffff"
MAANDEN = ["januari","februari","maart","april","mei","juni","juli","augustus","september","oktober","november","december"]
DAGEN = ["Maandag","Dinsdag","Woensdag","Donderdag","Vrijdag","Zaterdag","Zondag"]

def font(soort, px, wght=400):
    if soort == "serif":
        f = ImageFont.truetype(str(FONTS / "newsreader.ttf"), px); f.set_variation_by_axes([wght, 72])
    elif soort == "sans":
        f = ImageFont.truetype(str(FONTS / "AtkinsonHyperlegibleNext[wght].ttf"), px); f.set_variation_by_axes([wght])
    else:
        f = ImageFont.truetype(str(FONTS / "AtkinsonHyperlegibleMono[wght].ttf"), px); f.set_variation_by_axes([400])
    return f

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

def canvas(h): 
    img = Image.new("RGB", (1080, h), WIT); return img, ImageDraw.Draw(img)

def cover(b, h, pad_top):
    img, d = canvas(h); M = 96
    d.text((M, pad_top), "onder/streep", font=font("serif", 56, 500), fill=INK)
    # middenblok: datum, streep, som
    fd = font("serif", 88 if h == 1350 else 92, 400)
    datum = nl_datum(b["datum"]); regels = wrap(d, datum, fd, 888)
    som = [f"{b['beoordeeld']} beoordeeld", f"{b['doorgestreept']} doorgestreept", f"{b['geplaatst']} geplaatst vanaf 11/16"]
    fm = font("mono", 30)
    leeg = not b["berichten"]; fn = font("serif", 72, 400)
    blok = len(regels) * int(fd.size * 1.05) + 32 + 2 + 32 + len(som) * 45 + (int(72 * 1.05) + 28 if leeg else 0)
    y = (h - blok) // 2 - (40 if h == 1350 else 0)
    for r in regels: d.text((M, y), r, font=fd, fill=INK); y += int(fd.size * 1.05)
    y += 32; d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 34
    if leeg: d.text((M, y), "Vandaag niets.", font=fn, fill=INK); y += int(72 * 1.05) + 28
    for s in som: d.text((M, y), s, font=fm, fill=GRIJS); y += 45
    d.text((M, h - (96 if h == 1350 else 320) - 53), "Het nieuws, onderstreept.", font=font("serif", 44, 400), fill=INK)
    return img

def bericht(m, h, pad_top, pad_bottom):
    img, d = canvas(h); M = 96
    d.text((M, pad_top), "onder/streep", font=font("serif", 36 if h == 1350 else 40, 500), fill=GRIJS)
    fl = font("sans", 26 if h == 1350 else 28, 600)
    d.text((1080 - M - d.textlength(m["label"], font=fl), pad_top + 10), m["label"], font=fl, fill=GRIJS)
    y = pad_top + (72 + 43 if h == 1350 else 80 + 48)
    fs = font("serif", 96 if h == 1350 else 104, 500)
    d.text((M, y), f"{m['totaal']}/16", font=fs, fill=INK); y += int(fs.size * 1.1) + 16
    d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 42
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
    blok = len(som) * 42 + 32 + 2 + 32 + int(96 * 1.05)
    y = (h - blok) // 2
    for s in som: d.text((M, y), s, font=fm, fill=GRIJS); y += 42
    y += 32; d.line([(M, y), (1080 - M, y)], fill=INK, width=2); y += 34
    d.text((M, y), "Streep eronder.", font=fs, fill=INK)
    fz = font("sans", 34, 400); fu = font("mono", 28)
    regel = "Het hele bulletin, elke ochtend om zeven." if h == 1350 else "Het hele bulletin, met bron en dossier."
    yb = h - pad_bottom - 42 - 48 - 10
    d.text((M, yb), regel, font=fz, fill=INK); d.text((M, yb + 58), "onderstreep.nl", font=fu, fill=GRIJS)
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
    print("klaar:", sorted(p.name for p in uit.iterdir()))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

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
    n = len(b["berichten"])
    kp = 44 if n <= 3 else 38
    fsc, fk = font("serif", kp, 500), font("serif", kp, 500)
    for m in b["berichten"]:
        d.text((M, y), f"{m['totaal']}/16", font=fsc, fill=GRIJS)
        y = tekst(d, (M + 150, y), m["kop"], fk, breedte=1080 - M - (M + 150), lh=1.18) + 36
    som = f"{b['beoordeeld']} beoordeeld, {b['doorgestreept']} doorgestreept, {b['geplaatst']} geplaatst vanaf 11/16."
    fm, fs = font("mono", 26), font("serif", 56, 400)
    yb = h - M - int(56 * 1.05); d.text((M, yb), "Streep eronder.", font=fs, fill=INK)
    d.text((M, yb - 50), som, font=fm, fill=GRIJS)
    return img

if __name__ == "__main__" and len(sys.argv) > 3 and sys.argv[3] == "overzicht":
    pass

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
    kp = 44 if n <= 2 else (38 if n <= 4 else 34)
    fk = font("serif", kp, 500)
    for m in b["berichten"]:
        d.text((M, y), f"{m['totaal']}/16", font=fk, fill=GRIJS)
        y = tekst(d, (M + 150, y), m["kop"], fk, breedte=S - M - (M + 150), lh=1.18) + 30
    som = f"{b['beoordeeld']} beoordeeld, {b['doorgestreept']} doorgestreept, {b['geplaatst']} geplaatst vanaf 11/16."
    yb = S - M - int(56 * 1.05)
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
    d.text((M, y), "Boven de streep", font=fl, fill=GRIJS); y += 44
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
    return img
