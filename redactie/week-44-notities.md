# Week 44: notities voor de zondag

## Te laat verschenen en achteraf gedaan
- De bulletins van 26 tot en met 29 oktober 2026 verschenen te laat. Het bulletin van 26 oktober verscheen om 11:39 (de handmatige run; zie de noot in bulletins/2026-10-26.json). De tijden van 27, 28 en 29 oktober worden bij het pushen ingevuld; in de noten staat nu HH:MM.
- De sweeps voor 27, 28 en 29 oktober (over respectievelijk maandag 26, dinsdag 27 en woensdag 28 oktober) zijn niet op de avond zelf gedaan, maar achteraf op donderdag 29 oktober, een voor een. Elke dag is beoordeeld alsof het die avond 22:00 was; wat daarna veranderde hoort in Verloop, met datum. Het venster per sweep staat bovenin elk concept- en netniet-bestand.

## Zoekdienst Staatsblad en Staatscourant (SRU van KOOP)
- Op 25 oktober gaf de reguliere zoekdienst (zoek.officielebekendmakingen.nl) nul resultaten, ook voor eerdere data.
- Op 29 oktober de open SRU-dienst van KOOP geprobeerd (repository.overheid.nl/sru). Bevindingen:
  - Vrije tekst werkt: `query=vogelgriep` gaf 2.496 records.
  - De collectie werkt: `c.product-area==officielepublicaties` gaf 6.743.624 records.
  - Filteren op datum werkt: `c.product-area==officielepublicaties and dt.date==2026-10-28` gaf 3.286 records; maar dat zijn vrijwel allemaal lokale omgevingsvergunningen (Gemeenteblad en dergelijke).
  - De index die de nationale bladen afbakent werkt niet zoals geprobeerd: `dt.type==Staatsblad` en `dt.type==Staatscourant` gaven nul records, zonder foutmelding, ook zonder datum en voor oudere data. De indexnaam of de waarde voor het publicatieblad klopt niet.
  - Gevolg: de SRU is bereikbaar en levert data, maar de nationale Staatsblad- en Staatscourant-publicaties van 26 tot en met 28 oktober zijn via deze route niet schoon te isoleren. Voor die drie dagen staat de officiele sweep op de nationale bekendmakingen als "niet gecontroleerd".
  - Nog uit te zoeken (zondag): de juiste index of waarde voor het publicatieblad (waarschijnlijk `w.publicatienaam` of een KOOP-specifieke index), zodat Staatsblad en Staatscourant per publicatiedatum zijn uit te lezen. bronnen.json is nu niet aangepast (op verzoek).

## Uitkomst van de drie sweeps (kort)
- 26-10 (maandag): 11 beoordeeld, 0 geplaatst. Hoogste: KLM schrapt wintervluchten op Dubai, Riyad en Dammam (9, met haak). Vandaag niets.
- 27-10 (dinsdag): 15 beoordeeld (12 in de sweep plus 3 gemiste items uit de vergelijkingssweep), 0 geplaatst. Net niet: NHG-funderingsregel (10), ACM weigert overname Unox/Zwanenberg (10), Luchthavenverkeerbesluit Schiphol (10, gemist), vogelgriep Lutjegast (9), Eerste Kamer lokale publieke omroep (9, gemist), Wlz-aanvraag door familie (9, gemist). Vandaag niets.
- 28-10 (woensdag): 11 beoordeeld, 1 geplaatst: landelijke ophok- en afschermplicht voor pluimvee (11). De primaire bron (rijksoverheid.nl) is direct gelezen.

## Voor de kalibratie van zondag 1 november
- NHG-funderingsregel: Robbert-Jan houdt het op 10 (net niet). Scores herzien naar 3-1-3-3: reikwijdte 1 (kopers met een NHG-hypotheek van een woning met funderingsrisico, ruim onder 100.000 per jaar), houdbaarheid 3 (norm zonder einddatum). Vastgelegd in het log met oordeel 'Robbert-Jan: blijft 10'. Concept 2026-10-28 blijft ongewijzigd (3-2-2-3); de correctie staat in het log.
- Overweeg een dossier 'vogelgriep': ruiming Lutjegast (27-10), uitbraken Middelie en Grootegast (28-10) en de landelijke ophokplicht (28-10). Er is nog geen dossierbestand aangemaakt; dat is een besluit.
- Drie dagen op rij 'Vandaag niets' (25, 26, 27 oktober), daarna een plaatsing op 28. Het aandeel lege dagen is hoog, maar het nieuws gaf niet meer; de lat is niet verlaagd.
- Buitenland zonder haak bleef onder de 9 (Israel-verkiezingen 8, Spaanse treinramp 8, Fed-rente 6, Microsoft-vertrekregeling 7).
- Permanente controle: dit zijn achteraf-sweeps. Het onderscheid officieel/vangnet is deels kunstmatig, omdat de officiele zoekdiensten niet schoon uit te lezen waren; de vangnet-sweep (NOS en de rubrieken binnenland, politiek, economie, buitenland) droeg de drie dagen. Dat is precies het soort vangnet-only vondst dat de dubbele sweep moet signaleren: de ophokplicht is wel via de officiele route (rijksoverheid.nl) bevestigd.
- Nog te volgen: het plan om vaccinatie van legpluimvee verplicht te maken (eind 2026 naar de Tweede Kamer) en het stoppen van het 2G-netwerk (KPN eind 2027, gevolgen voor noodknoppen van ouderen).

## Aanvulling 29 oktober: vergelijkingssweep, correcties en uitkomst
- De sweeps van 27-10 tot en met 29-10 draaiden op Opus 4.8, niet op Sonnet (het standaardmodel in de projectinstellingen).
- Drie gemiste items op 27-10. Oorzaak: de nieuwslijst van rijksoverheid.nl op /actueel/nieuws laadt dynamisch en kwam leeg binnen, dus de officiele route werd niet uitgelezen. Nieuwe uitleesroute: https://www.rijksoverheid.nl/actueel geeft wel een leesbare lijst met datum en tijd (gecontroleerd 29-10-2026); bronnen.json is daarop bijgewerkt. De drie items (Luchthavenverkeerbesluit Schiphol 10, Eerste Kamer lokale publieke omroep 9, Wlz-aanvraag door familie 9) staan in het log met sweep 'officieel', uitkomst 'net niet' en de reden 'alleen gevonden in de vergelijkingssweep; oorzaak: bron niet uitgelezen'. Schiphol staat ook als 'gemist' (9 of hoger).
- Schiphol is een tweede geval dat alleen via het Staatsblad of de officiele route te vinden was (na eerdere officiele-sweep-only vondsten in week 43). De officiele zoekdienst krijgt voorrang bij de kalibratie van zondag, samen met het uitzoeken van de juiste SRU-index voor Staatsblad en Staatscourant.
- Uitkomst punt 1 (ophokplicht): de landelijke ophok- en afschermplicht geldt 'sinds 28 oktober 2026' (rijksoverheid.nl), aangekondigd op 28-10 om 17:46. Ingegaan op 28-10 voor 22:00, dus hardheid 4, totaal 11: geplaatst in bulletin 2026-10-29. Dossier 'vogelgriep' aangemaakt (Lutjegast 26-10, Middelie 27-10, Grootegast 28-10, ophokplicht 28-10) en aan het bericht gekoppeld. De regel 'opgeheven in juni' is uit het bericht gehaald; de vorige landelijke plicht werd op 21 april 2026 grotendeels ingetrokken (rijksoverheid.nl 21-04-2026). Het exacte uur van inwerkingtreding staat niet in het nieuwsbericht; de Staatscourant-regeling 'Regeling ophok- en afschermplicht oktober 2026' en de Kamerbrief 'Vogelgriepsituatie en aanscherpen maatregelen' staan op open.overheid.nl maar waren niet rechtstreeks uit te lezen.
- Oekraine-steun 28-10 gecorrigeerd in het log: het primaire bericht (Rijksoverheid, minister Sjoerdsma in Kyiv, 09:15) noemt 1,2 miljard euro niet-militaire steun over drie jaar; de 500 miljoen euro voor luchtafweer (NOS, premier Jetten, 16:48) is een los militair deel dat dezelfde dag is aangekondigd. Score ongewijzigd (8).

## Tegenproef (officiele route, 1 november)
Met de nieuwe officiele route (SRU op w.publicatienaam + zoek.officielebekendmakingen.nl, en de Douane) zijn drie items teruggevonden die de sweeps misten. Alle drie als "gemist" gelogd:
- Afhandelingsvergoeding e-commerce, 2 euro per productcategorie (douane.nl), 1-11, 4-2-3-2 = 11. Oorzaak: bron ontbreekt (Douane niet in bronnen.json). Alsnog geplaatst in bulletin 2026-11-02; Douane is nu aan bronnen.json toegevoegd.
- Thuiskopievergoeding 2027-2028 (Stcrt. 2026, 36929), 28-10, 3-2-2-3 = 10. Oorzaak: bron niet uitgelezen (zoekdienst defect).
- Kadaster, verstrekkingsbeperking op naam (Stb. 2026, 338), 28-10, 3-1-3-3 = 10. Oorzaak: bron niet uitgelezen (zoekdienst defect).
Les: tarief- en heffingsbesluiten zonder nette datafeed (thuiskopievergoeding, afhandelingsvergoeding) zijn de grootste blinde vlek. De officiele SRU-route en de Douane dekken die nu af; de inwerkingtredingen staan op de agenda.
