# onder/streep

Statische site van Onderstreep, een Nederlands nieuwsbulletin dat elke ochtend om 07:00 alleen brengt wat echt is veranderd (een besluit, een uitspraak, een gebeurtenis) en gevolgen heeft voor mensen in Nederland. Slogan: "Het nieuws, onderstreept." Regel: "Elke ochtend om zeven: alleen wat echt is veranderd." Nooit "gisteren" of "besloten" in slogan of bio. Elk bericht wordt gescoord op vier criteria (hardheid, reikwijdte, houdbaarheid, nieuwheid, elk 0–4) en verschijnt alleen vanaf 11 van 16, met hardheid minimaal 2. De eigenaar is Robbert-Jan Das; het project is persoonlijk, zonder advertenties en zonder politieke kleur.

## Hoe de site werkt

- `bulletins/JJJJ-MM-DD.json`: één bestand per publicatiedag. `build.py` maakt daar de hele site van (voorpagina, bulletinpagina's, Kroniek met jaar- en maandpagina's, dossiers, feeds). Zie `README.md` voor het formaat.
- `dossiers/<slug>.json`: onderwerpen die vaker terugkomen, met een gedateerd verloop.
- `templates/`: de sjablonen. `static/`: stijl, favicon, profielbeeld. `rubriek.json`: de criteria en labels.
- GitHub Actions bouwt en publiceert bij elke push naar `main` én elke ochtend om 07:00 Nederlandse tijd; de site staat op https://onderstreep.nl.
- Een bulletin wordt 's avonds (sweep om 22:00) gepusht met de datum van morgen; `build.py` toont het pas vanaf 07:00 op die datum. Een bulletin van morgen in de map is dus normaal, niet een fout.

## Werkwijze

- Begin elk gesprek met `git pull`, zodat de map gelijkloopt met GitHub (er wordt ook via de browser geüpload).
- Controleer na elke wijziging met `pip install jinja2` (eenmalig) en `python build.py`; de bouw weigert berichten onder de drempel.
- Commit-berichten in het Nederlands, kort: "Bulletin 2026-10-18", "Introregel in Atkinson".
- Push pas na een geslaagde lokale bouw, en zeg bij elke push kort wat er is veranderd.
- `dist/` is bouwuitvoer en staat in `.gitignore`; nooit committen.

## Redactionele regels voor berichten

- Kop: één zin, wat er is veranderd, geen vraag, geen citaat, geen bijvoeglijk naamwoord.
- Vier labels: Wat, Voor wie, optioneel Verloop (wat eraan voorafging en wat erna komt, alleen wat vaststaat), Onbekend. Ze staan in de regel en de alinea's worden als één doorlopend stuk geschreven, niet als vier losse antwoorden. Getallen en data in plaats van bijwoorden.
- Lengte: zo lang als de feiten vragen, bovengrens 210 woorden per bericht; Wat boven de 120 woorden wordt geknipt in twee alinea's (lege regel in de JSON).
- Geen citaten, geen reacties, geen speculatie, geen waardende woorden (omstreden, eindelijk, hard, drastisch, historisch).
- Bron is altijd de primaire bron: het besluit, het vonnis, de publicatie. Zonder primaire bron geen bericht.
- Geen uitroeptekens, geen emoji, geen hashtags. Typografische apostrof en aanhalingstekens.
- Volgorde en scores berekent `build.py`; niet handmatig sorteren.

## Niet doen zonder expliciete opdracht

- De drempel (11), de schaal (0–4) of `rubriek.json` veranderen.
- Bestaande bulletins herschrijven; een fout wordt gecorrigeerd met een zichtbare, gedateerde correctie in het bericht.
- Het beeld is een som: al het nieuws onder elkaar, wat niet telt wordt doorgestreept, wat echt is veranderd staat "onder de streep". Nooit "boven de streep". Uitleg: "Elke dag zetten we het nieuws onder elkaar, als een som. Wat niet telt, strepen we door. Wat echt is veranderd, staat onder de streep."
- De drie lettertypes, de zwart-witopmaak of de vaste regels ("Vandaag niets.", "Streep eronder.") aanpassen.
- Iets plaatsen op sociale media of een nieuwsbrief versturen; dat loopt via andere systemen.
- Bestanden buiten deze map aanraken.

## Kaarten maken

Opdracht: "maak kaarten" (of "bouw, maak kaarten en push").
- `python merk/maak_kaarten.py bulletins/JJJJ-MM-DD.json` maakt alle beelden van dat bulletin in `social/JJJJ-MM-DD/`: carrousel (Instagram, Facebook, Threads), stories (Instagram, Facebook), `-overzicht.png` (WhatsApp) en `-overzicht-vierkant.png` (LinkedIn).
- Lettertypes komen uit `merk/lettertypes/`. Nodig: Pillow (`pip install pillow` in de venv).
- `social/` staat in `.gitignore`: beelden worden nooit gecommit.
- Open na afloop de map in de Finder (`open social/JJJJ-MM-DD`).
