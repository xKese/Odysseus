---
name: fonds-analyse
description: "Vergleich und Analyse von Investmentfonds (aktive Fonds und ETFs) auf Basis von Factsheets, PDFs oder manuell eingegebenen Daten. Erstellt professionelle Auswertungen auf Deutsch in drei Detailstufen: Kurzuebersicht (Kundenkommunikation), Detailanalyse (intern) und Vergleichstabelle (mehrere Fonds nebeneinander). Wahlweise als Schnellanalyse oder Tiefenanalyse mit Deep Research."
version: 1.0.0
category: finance
tags: [fonds, factsheet, vermoegensverwaltung, m-und-s]
status: published
confidence: 0.95
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Verwende diesen Skill immer, wenn der Nutzer Fonds analysieren, vergleichen, gegenuebersteleln oder bewerten moechte. Trigger-Begriffe: "Fondsvergleich", "Fondsanalyse", "Factsheet auswerten", "Rendite vergleichen", "welcher Fonds ist besser", "Fondssteckbrief". Auch dann triggern, wenn Factsheet-PDFs hochgeladen werden, ohne dass der Nutzer den Skill namentlich nennt.

## Procedure

1. Frage nach gewuenschter Ausfuehrlichkeitsstufe UND Recherchemodus: Ausfuehrlichkeit (1) Kurzuebersicht fuer Kundenkommunikation, (2) Detailanalyse intern, (3) Vergleichstabelle fuer mehrere Fonds; Recherchemodus (siehe Skill `recherche-modus`) Schnellanalyse (nur Upload-Dokumente + gezielter `web_fetch`) oder Tiefenanalyse (zusaetzlich `trigger_research`). Wenn der Nutzer den Modus nicht nennt, nachfragen — niemals ungefragt einen Deep-Research-Lauf starten. In dieser Domaene validiert Deep Research vor allem: Max Drawdown / Sharpe Ratio / 3-Jahres-Volatilitaet (fehlen meist im Factsheet), Anbieter-Reputation und den Vergleich mit Kategorie-Peers. Falls die Quellen-PDFs noch fehlen, frage nach Upload oder ISIN.
2. Lies alle bereitgestellten Factsheets/Dokumente und extrahiere die Pflichtfelder gemaess Kennzahlentabelle im body_extra (Stammdaten, Performance, Risiko, Portfolio). Verwende `read_file` fuer hochgeladene Dateien und `web_fetch` fuer gezielt benannte oeffentliche Anbieter-Seiten. NUR im Tiefenmodus zusaetzlich `trigger_research` mit enger Forschungsfrage; den fertigen Bericht ueber `manage_research` lesen und einarbeiten. Deep-Research-Befunde mit Marker `(Deep Research: <Quelle>, <Stichtag>)` kennzeichnen und von den Factsheet-Daten trennen. Im Schnellmodus KEIN `trigger_research`.
3. Markiere jeden nicht direkt im Dokument ausgewiesenen Wert mit `(nicht ausgewiesen)` oder `(berechnet aus: ...)`. Niemals Werte schaetzen.
4. Erstelle fuer jeden Fonds drei Bloecke (Charakteristiken, Chancen, Risiken) mit je 4-5 prägnanten, fondsspezifischen Stichpunkten. Keine Platituden, keine generischen Risikohinweise.
5. Baue die Auswertung gemaess der gewaehlten Stufe (siehe body_extra) und formatiere als Markdown (im Chat) oder erzeuge ein DOCX ueber `manage_documents create` mit Hausstandard-Layout.
6. Haenge am Ende einen Block "Fehlende Kennzahlen" mit konkreten Empfehlungen zur Ergaenzungsquelle (Morningstar, fondsweb.de, Bloomberg) an.
7. Wende den Hausstandard von Meeder & Seifer an (siehe Skill `m-und-s-hausstandard`): Tonalitaet, Datumsformat, Disclaimer, Tabellen-Farbschema, Quellenangabe.

## Pitfalls

- Niemals Renditen, Volatilitaet oder TER berechnen oder schaetzen, wenn sie nicht explizit ausgewiesen sind — auch nicht "ueberschlagen".
- Annualisierte vs. kumulierte Performance nicht verwechseln; bei jeder Zahl Zeitraum (1J/3J/5J/10J/YTD/seit Auflage) und Brutto-/Netto-Charakter ausweisen.
- Max. Drawdown und Sharpe Ratio fehlen in den meisten Factsheets — als "(zusaetzliche Quelle erforderlich)" markieren, nicht aus Volatilitaet ableiten.
- Simulierte Wertentwicklung vor Auflagedatum klar als solche kennzeichnen.
- Stichtag der Daten immer mit angeben, auch wenn der Nutzer nicht danach fragt.
- Bei DOCX-Output das Farbschema des `m-und-s-hausstandard`-Skills nutzen, keinen eigenen Stil erfinden.
- Kein Anlageberatungs-Disclaimer fehlen lassen — Pflichttext aus dem Hausstandard-Skill am Ende einfuegen.

## Verification

- Alle Zahlen sind direkt aus dem Quelldokument entnommen, jede Zahl hat einen klaren Zeitraum und Charakter (annualisiert/kumuliert, brutto/netto).
- Fuer jeden Fonds existieren die drei Bloecke Charakteristiken / Chancen / Risiken mit je 4-5 fondsspezifischen Stichpunkten.
- Fehlende-Kennzahlen-Block ist vorhanden und nennt Ergaenzungsquellen.
- Stichtag der Daten und Disclaimer "Alle Angaben ohne Gewaehr. Historische Wertentwicklung ist kein Indikator fuer zukuenftige Renditen." sind enthalten.
- Output ist auf Deutsch, professioneller Ton, ohne emojis ausser dem Warnhinweis fuer fehlende Werte.
- Recherchemodus ist geklaert (bei fehlender Angabe wurde nachgefragt) und im Kopf des Outputs vermerkt; bei Tiefenanalyse sind Deep-Research-Befunde als solche markiert, mit Quelle und Stichtag belegt und von den Factsheet-Daten getrennt. ### Pflichtfelder (Stammdaten) | Kennzahl | Quelle / Hinweis | |---|---| | Fondsname | Vollstaendiger Name inkl. Anteilklasse | | ISIN / WKN | Direkt aus Factsheet | | Fondswaehrung | z.B. EUR, USD | | Ertragsverwendung | Thesaurierend oder Ausschuettend | | Fondsvolumen | In Mio./Mrd. der jeweiligen Waehrung | | Ruecknahmepreis / NAV | Aktueller Kurs | | Mindestanlage | Erstanlage und Folgeanlage | | Gesamtkostenquote (TER/OGC) | In Prozent p.a. — nur explizit ausgewiesene Werte | | Ausgabeaufschlag | In Prozent | | SFDR-Kategorie | Artikel 6, 8 oder 9 | | Risikoklasse (SRI) | 1-7 Skala | | Anlagehorizont | Empfehlung in Jahren | | Verwaltungsgesellschaft | Vollstaendiger Name | | Sitzland | Land des Fonds | | Auflagedatum | Des Fonds oder der Anteilklasse | ### Performance-Daten | Kennzahl | Zeitraum | |---|---| | Rendite p.a. (annualisiert) | 1J, 3J, 5J, 10J, seit Auflage | | Rendite kumuliert | 3J, 5J, 10J | | YTD-Performance | Laufendes Jahr | | Jahresrenditen | Einzeljahre sofern ausgewiesen | ### Risikokennzahlen | Kennzahl | Hinweis | |---|---| | Standardabweichung / Volatilitaet p.a. | Zeitraum beachten (meist 1J oder 3J) | | VaR (Value at Risk) | Konfidenzintervall und Haltedauer notieren | | Max. Drawdown (5J) | Oft nicht in Factsheets — externe Quelle noetig | | Sharpe Ratio | Falls ausgewiesen | ### Portfolio-Daten | Kennzahl | Hinweis | |---|---| | Asset-Allokation | Aktien, Renten, Cash, Rohstoffe, etc. in Prozent | | Aktienquote (aktuell und Bandbreite) | Falls ausgewiesen | | Regionale Allokation | Wichtigste Regionen in Prozent | | Top-Sektoren | Bei Aktienfonds | | Duration | Bei Rentenfonds / Multi-Asset | | Laufende Rendite (Yield) | Bei Rentenfonds | ### Stufe 1 — Kurzuebersicht (Kundenkommunikation) Prägnante Zusammenfassung fuer Endkunden oder Beratungsgespraeche. Enthaelt: Fondsname, ISIN, Fondswaehrung, Ertragsverwendung; Kurzbeschreibung der Strategie (2-3 Saetze); Hauptkennzahlen (Volumen, TER, Mindestanlage, SFDR); Performance 1J/3J/5J p.a.; Risikoprofil (Risikoklasse, Volatilitaet, Anlagehorizont); Charakteristiken/Chancen/Risiken (je 4-5 Stichpunkte); Fehlende-Kennzahlen-Hinweis. Ton: verstaendlich, ohne uebermaeßige Fachbegriffe, professionell. ### Stufe 2 — Detailanalyse (intern) Vollstaendige Analyse fuer interne Entscheidungsprozesse. Enthaelt alles aus Stufe 1 plus: alle verfuegbaren Performance-Daten (Jahresrenditen, kumuliert, annualisiert); vollstaendige Risikokennzahlen; Asset-Allokation inkl. Bandbreiten; Portfolio-Details (Sektoren, Regionen, Waehrungen, Top-Holdings); Kostenstruktur (TER, Ausgabeaufschlag, Performance Fee, Transaktionskosten); Verwaltungsgesellschaft, Verwahrstelle; steuerliche Hinweise (z.B. Teilfreistellung); Fondsmanagement; Auszeichnungen / Ratings. ### Stufe 3 — Vergleichstabelle (mehrere Fonds) Aufbau: Kennzahlen in Zeilen, Fonds in Spalten. Reihenfolge: (1) Stammdaten, (2) Kosten, (3) Performance, (4) Risiko, (5) Strategie, (6) Sonstiges. Nach der Tabelle fuer jeden Fonds separaten Abschnitt mit den drei Bloecken anhaengen. Bei DOCX-Output: besten Wert je Zeile fett markieren (Performance hoechster Wert; Kosten niedrigster Wert), fehlende Werte mit `(nicht ausgewiesen)` markieren. Falls Word-Dokument gewuenscht, verwende `manage_documents action=create` und folge dieser Gliederung: ``` Titelseite: Fondsname(n), Datum der Analyse, Ausfuehrlichkeitsstufe Abschnitt 1: Stammdaten und Strategie Abschnitt 2: Kosten Abschnitt 3: Performance Abschnitt 4: Risiko Abschnitt 5: Portfolio-Zusammensetzung (nur Stufe 2) Abschnitt 6: Chancen und Risiken Abschnitt 7: Fehlende Kennzahlen und Hinweise Fusszeile: Disclaimer aus Hausstandard ``` Farbschema und Schriftarten gemaess Skill `m-und-s-hausstandard`. Nutzer laedt 3 Factsheet-PDFs hoch und schreibt "Bitte vergleiche diese Fonds":
- Alle drei PDFs lesen, Kennzahlen nach obiger Tabelle extrahieren.
- Fehlende Werte identifizieren und dokumentieren.
- Fragen: "Soll ich eine Kurzuebersicht, Detailanalyse oder Vergleichstabelle erstellen? Markdown im Chat oder Word-Dokument?"
- Auswertung in gewaehltem Format erstellen, Hausstandard anwenden.
- Fehlende-Kennzahlen-Block mit Ergaenzungsquellen anhaengen, zur Freigabe stellen.
