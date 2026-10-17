# onder/streep

Statische site van Onderstreep. Elke bulletin is één JSON-bestand; `build.py` maakt daar de site, de dossierpagina's en de feeds van. GitHub Actions bouwt en publiceert bij elke push naar `main`.

## Eenmalig instellen

1. Maak op GitHub een repository `onderstreep` (privé mag) en zet deze map erin:
   `git init && git add . && git commit -m "Startpakket" && git branch -M main && git remote add origin <url> && git push -u origin main`
2. Repository, Settings, Pages: bij Source kies **GitHub Actions**. De workflow `Bouw en publiceer` draait dan vanzelf; na een minuut staat de site op `https://<gebruiker>.github.io/onderstreep/`.
3. Settings, Pages, Custom domain: `onderstreep.nl`. Vink **Enforce HTTPS** aan zodra het certificaat er is (kan een uur duren).
4. DNS bij Hostnet (Domeinbeheer, DNS-instellingen):
   - vier A-records voor `@` (het kale domein): `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - een CNAME voor `www` naar `<gebruiker>.github.io`
   - de bestaande Hostnet-parkeerrecords voor `@` en `www` weghalen
   Doorlooptijd: meestal binnen een uur, soms langer.

Het bestand `dist/CNAME` wordt bij elke bouw aangemaakt, zodat het domein gekoppeld blijft.

## Een bulletin plaatsen

Maak `bulletins/JJJJ-MM-DD.json` (de publicatiedatum) naar het voorbeeld van `bulletins/2026-10-16.json`:

- `datum`: publicatiedag, `over`: de dag waar het bulletin over gaat
- `beoordeeld`: aantal beoordeelde berichten; `doorgestreept` wordt berekend
- `berichten`: nul of meer berichten met `score` (hardheid, reikwijdte, houdbaarheid, nieuwheid, elk 0–4), `label`, `kop`, `wat`, `voor_wie`, `onbekend`, optioneel `eerder`, `bron` (naam en url), optioneel `dossier` (slug) en `update: true`

De bouw weigert een bericht onder 11/16 of met hardheid onder 2, en sorteert zelf: hoogste score eerst, dan reikwijdte, dan hardheid, dan de volgorde in het bestand. Een leeg bulletin (`"berichten": []`) wordt "Vandaag niets."

Push het bestand; de site is binnen een minuut bijgewerkt. Het nieuwste bulletin is de voorpagina.

## Dossiers

Elk onderwerp dat ooit de drempel haalde, krijgt `dossiers/<slug>.json` met `titel`, `label`, `gestart` en `verloop` (gedateerde regels). Berichten met `"dossier": "<slug>"` worden automatisch aan het dossier gekoppeld en in Kroniek getoond.

## Feeds

- `/feed.xml`: alles, één item per bericht, en "Vandaag niets." op lege dagen (zodat de cross-poster ook dan iets plaatst)
- `/feed-<label>.xml`: per label, voor nieuwsbrief en cross-poster

## Werken met Claude Code

Open de map in het tabblad Code van de Claude-app. `CLAUDE.md` bevat de afspraken (eerst `git pull`, lokaal bouwen, dan pushen) en de redactionele regels. Een bulletin plaatsen is dan één opdracht: het JSON-bestand of de tekst geven, Claude bouwt, controleert en pusht.

## Lokaal bouwen

`pip install jinja2` en `python build.py`; de site staat in `dist/`. Open `dist/index.html` via een lokale server (`python -m http.server -d dist`), want de paden zijn absoluut.

## Volgende stappen (niet in dit pakket)

- Nieuwsbrief: dienst met RSS-naar-e-mail koppelen aan `/feed.xml`, verzenden vanaf `mail.onderstreep.nl` met SPF, DKIM en DMARC.
- Cross-poster koppelen aan `/feed.xml` voor Threads, Bluesky, X en Facebook.
- De pijplijn (bronnen ophalen, scoren, Telegram-concept om 06:00) schrijft straks zelf de JSON-bestanden en pusht ze; de site hoeft daarvoor niet te veranderen.
