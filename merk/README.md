# merk

Huisstijlbestanden van onder/streep. Niet door `build.py` gebruikt; de site heeft haar eigen kopieën in `static/`.

- `profiel-1024.png`: profielbeeld, zwart op wit (overal gebruiken)
- `profiel-1024-donker.png`: wit op zwart, alleen voor donkere achtergronden
- `teken.svg`: de schuine streep als vector (favicon, drukwerk)
- `linkedin-omslag.png`: omslag LinkedIn, 1584 × 396
- `handtekening.html`: mailhandtekening; openen in Safari, alles kopiëren, plakken in Mail
- `maak_kaarten.py`: maakt uit een bulletin de social-afbeeldingen (carrousel, stories, overzichtskaarten, weekkaart); `pip install pillow`, dan `python maak_kaarten.py bulletins/2026-10-18.json uit/`
- `lettertypes/`: Newsreader, Atkinson Hyperlegible Next en Mono (OFL-licentie), gebruikt door de generator

Typografie: koppen en getallen Newsreader 500 (optische maat 72), tekst Atkinson Hyperlegible Next 400 (labels 600), bron en som Atkinson Hyperlegible Mono 400. Zwart #141414 op wit; donker: #f0f0f0 op zwart. Eén streep per pagina of kaart, 1 px op de site, 2 px op kaarten.
