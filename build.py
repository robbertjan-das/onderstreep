"""Bouwt de statische site van onder/streep uit bulletins/*.json en dossiers/*.json.

Gebruik: python build.py  ->  dist/
"""
import json
import shutil
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SITE = "https://onderstreep.nl"
DREMPEL = 11
PUBLICATIE_UUR = 7  # 07:00 Nederlandse tijd

MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]
DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]


def nl_datum(iso: str, met_dag: bool = True) -> str:
    d = date.fromisoformat(iso)
    tekst = f"{d.day} {MAANDEN[d.month - 1]} {d.year}"
    return f"{DAGEN[d.weekday()].capitalize()} {tekst}" if met_dag else tekst


def nl_datum_kort(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{DAGEN[d.weekday()]} {d.day} {MAANDEN[d.month - 1]}"


def slug(tekst: str) -> str:
    return (tekst.lower().replace("&", "en").replace(" ", "-")
            .replace("--", "-"))


def laad(map_naam: str) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((ROOT / map_naam).glob("*.json"))]


def verwerk_bulletin(b: dict, dossiers: dict) -> dict:
    for volgorde, m in enumerate(b["berichten"]):
        s = m["score"]
        m["totaal"] = s["hardheid"] + s["reikwijdte"] + s["houdbaarheid"] + s["nieuwheid"]
        m["volgorde"] = volgorde
        if m["totaal"] < DREMPEL or s["hardheid"] < 2:
            raise SystemExit(f"{b['datum']}: '{m['kop']}' haalt de drempel niet "
                             f"({m['totaal']}/16, hardheid {s['hardheid']}).")
        m["dossier_obj"] = dossiers.get(m.get("dossier"))
        m["bulletin_datum"] = b["datum"]
        m["bulletin_datum_nl"] = nl_datum(b["datum"])
    b["berichten"].sort(key=lambda m: (-m["totaal"], -m["score"]["reikwijdte"],
                                       -m["score"]["hardheid"], m["volgorde"]))
    b["geplaatst"] = len(b["berichten"])
    b["updates"] = sum(1 for m in b["berichten"] if m.get("update"))
    b["nieuw"] = b["geplaatst"] - b["updates"]
    b["doorgestreept"] = b["beoordeeld"] - b["geplaatst"]
    b["datum_nl"] = nl_datum(b["datum"])
    b["over_nl_kort"] = nl_datum_kort(b["over"])
    return b


def verwerk_dossier(d: dict) -> dict:
    d["gestart_nl"] = nl_datum(d["gestart"], met_dag=False)
    for v in d["verloop"]:
        v["datum_nl"] = nl_datum(v["datum"], met_dag=False)
    d["laatste_nl"] = nl_datum(d["verloop"][-1]["datum"], met_dag=False)
    d["berichten"] = []
    d["hoogste"] = 0
    return d


def pubdate(iso: str) -> str:
    d = date.fromisoformat(iso)
    tz = timezone(timedelta(hours=2))  # CEST; zomertijd volstaat voor de feed
    return format_datetime(datetime(d.year, d.month, d.day, PUBLICATIE_UUR, 0, tzinfo=tz))


def feed_items(bulletins: list[dict], label: str | None = None) -> list[dict]:
    items = []
    for b in bulletins:
        berichten = [m for m in b["berichten"] if label is None or m["label"] == label]
        if not berichten and label is None:
            items.append({"titel": "Vandaag niets.",
                          "link": f"{SITE}/bulletin/{b['datum']}/",
                          "pubdate": pubdate(b["datum"]),
                          "tekst": f"{b['beoordeeld']} beoordeeld, {b['doorgestreept']} "
                                   f"doorgestreept, 0 geplaatst vanaf 11/16."})
        for m in berichten:
            items.append({"titel": ("Update: " if m.get("update") else "") + m["kop"],
                          "link": f"{SITE}/bulletin/{b['datum']}/#{m['id']}",
                          "pubdate": pubdate(b["datum"]),
                          "tekst": f"{m['totaal']}/16. {m['wat']} Voor wie: {m['voor_wie']}"})
    return items


def main() -> None:
    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      autoescape=select_autoescape(["html"]))
    rubriek = json.loads((ROOT / "rubriek.json").read_text(encoding="utf-8"))
    dossiers = {d["slug"]: verwerk_dossier(d) for d in laad("dossiers")}
    bulletins = [verwerk_bulletin(b, dossiers) for b in laad("bulletins")]
    bulletins.sort(key=lambda b: b["datum"], reverse=True)
    for b in bulletins:
        for m in b["berichten"]:
            if m["dossier_obj"]:
                m["dossier_obj"]["berichten"].append(m)
                m["dossier_obj"]["hoogste"] = max(m["dossier_obj"]["hoogste"], m["totaal"])
    dossier_lijst = sorted(dossiers.values(), key=lambda d: d["verloop"][-1]["datum"], reverse=True)

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    shutil.copytree(ROOT / "static", DIST / "static")
    (DIST / "CNAME").write_text("onderstreep.nl\n")
    (DIST / ".nojekyll").write_text("")

    def schrijf(pad: str, sjabloon: str, **ctx) -> None:
        doel = DIST / pad
        doel.parent.mkdir(parents=True, exist_ok=True)
        doel.write_text(env.get_template(sjabloon).render(site=SITE, rubriek=rubriek, **ctx),
                        encoding="utf-8")

    if bulletins:
        schrijf("index.html", "bulletin.html", b=bulletins[0], pagina="vandaag")
    for b in bulletins:
        schrijf(f"bulletin/{b['datum']}/index.html", "bulletin.html", b=b, pagina="vandaag")
    schrijf("kroniek/index.html", "kroniek.html", dossiers=dossier_lijst, bulletins=bulletins, pagina="kroniek")
    for d in dossier_lijst:
        schrijf(f"kroniek/{d['slug']}/index.html", "dossier.html", d=d, pagina="kroniek")
    schrijf("rubriek/index.html", "rubriek.html", pagina="rubriek")
    schrijf("over/index.html", "over.html", pagina="over")

    recent = bulletins[:30]
    schrijf("feed.xml", "feed.xml", items=feed_items(recent), label=None, bestand="feed.xml")
    for label in rubriek["labels"]:
        bestand = f"feed-{slug(label)}.xml"
        schrijf(bestand, "feed.xml", items=feed_items(recent, label), label=label, bestand=bestand)

    print(f"Gebouwd: {len(bulletins)} bulletins, {len(dossier_lijst)} dossiers -> {DIST}")


if __name__ == "__main__":
    main()
