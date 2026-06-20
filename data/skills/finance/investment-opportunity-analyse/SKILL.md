---
name: investment-opportunity-analyse
description: "Bewertet illiquide Investment-Opportunitaeten aus Pitchdecks fuer das Family Office: Private-Equity-/Venture-Fonds, Immobilien (direkt und Fonds), direkte Unternehmensbeteiligungen sowie Private Debt und Infrastruktur. Klassifiziert die Opportunitaet, wendet das passende Kennzahlen-Modul an, trennt Behauptungen von belegten Fakten, benennt Due-Diligence-Luecken und bewertet Illiquiditaet, Gebuehrenlast und Mandatspassung. KEINE Anlageempfehlung."
version: 1.0.0
category: finance
tags: [alternatives, private-equity, immobilien, beteiligung, private-debt, pitchdeck, due-diligence, vermoegensverwaltung, m-und-s]
status: published
confidence: 0.85
source: imported
shared: true
created: 2026-06-19T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn eine illiquide oder alternative Investment-Opportunitaet bewertet werden soll, die typischerweise als Pitchdeck, Teaser, Exposee oder Private Placement Memorandum hereinkommt und KEINE ISIN/kein Factsheet hat. Trigger-Begriffe: "Pitchdeck bewerten", "Investment-Opportunitaet pruefen", "Beteiligung analysieren", "PE-Fonds bewerten", "Private-Equity-Fonds", "Immobilieninvestment", "Immobilienfonds (geschlossen)", "Direktbeteiligung", "Unternehmensbeteiligung", "Private Debt", "Infrastrukturinvestment", "Club Deal", "Co-Investment", "lohnt sich dieses Investment", "Exposee pruefen". Verwende NICHT fuer liquide Publikumsfonds/ETFs mit ISIN — das ist `fonds-analyse`. NICHT fuer boersennotierte Einzelaktien — das ist `aktien-analyse`. NICHT fuer reine Charttechnik.

## Procedure

1. Klassifiziere die Opportunitaet in eine der vier Asset-Klassen: (a) Private Equity / Venture-Fonds, (b) Immobilien (direkt oder Immobilienfonds), (c) direkte Unternehmensbeteiligung, (d) Private Debt oder Infrastruktur. Bei Hybriden die dominante Klasse waehlen und den Hybridcharakter vermerken. Frage nach gewuenschter Ausfuehrlichkeitsstufe (Kurzbewertung / Detailanalyse / Vergleich mehrerer Opportunitaeten). Falls das Pitchdeck noch fehlt, fordere es zum Upload an.
2. Extrahiere die allgemeinen Stammdaten plus das asset-klassen-spezifische Kennzahlen-Modul (siehe body_extra) aus dem Pitchdeck via `read_file`. Hintergrund zum Anbieter / General Partner / Initiator und zu dessen Track Record ueber `web_fetch` (oeffentliche Quellen) bzw. `trigger_research` mit Quellenpflicht recherchieren. Niemals Zahlen schaetzen.
3. **Trenne Behauptungen von belegten Fakten.** Ein Pitchdeck ist ein Verkaufsdokument. Markiere alles, was nur im Deck behauptet und nicht unabhaengig belegt ist, mit `(laut Anbieter, nicht unabhaengig belegt)`. Track-Record-Angaben besonders kritisch pruefen: Methode der Rendite-Berechnung, Stichtag, Brutto vs. Netto, realisiert vs. unrealisiert, Cherry-Picking einzelner Showcase-Deals, Survivorship Bias.
4. Erstelle den **Due-Diligence-Luecken-Block**: Was fehlt im Deck und muss zwingend angefordert werden, bevor eine Entscheidung moeglich ist (siehe DD-Checklisten je Asset-Klasse im body_extra)? Das ist bei illiquiden Deals oft wichtiger als der vorhandene Inhalt.
5. Erstelle fuer jede Opportunitaet drei Bloecke (Charakteristiken, Chancen, Risiken) mit je 4-5 spezifischen Stichpunkten. Zusaetzlich zwei eigene Dimensionen bewerten: **Illiquiditaet/Lock-up** (Laufzeit, Kuendigungsrechte, Zweitmarkt) und **Gebuehrenlast (all-in)** (alle Ebenen zusammen).
6. Bewerte die **Mandatspassung**: passt die Opportunitaet zu den Anlagerichtlinien, dem Liquiditaetsbedarf und dem Risikoprofil des Family Office? Nutze `hauswissen-suche` fuer die internen Anlagerichtlinien. Gib eine nuechterne Einschaetzung (passt / passt teilweise / passt nicht zu den Richtlinien) — aber KEINE Invest-/Nicht-Invest-Empfehlung. Die Entscheidung trifft der Anlageausschuss.
7. Lege das Ergebnis als Document mit `release_status=draft` ab (`manage_documents action=create`), wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`) und biete an, es ueber `anlageausschuss-vorbereitung` in die naechste Sitzungsmappe einzubinden.

## Pitfalls

- Pitchdeck = Verkaufsdokument. NICHTS ungeprueft uebernehmen; jede beworbene Zahl als "laut Anbieter" kennzeichnen, bis unabhaengig belegt.
- Rendite-Kennzahlen (IRR, TVPI, Multiple) immer mit Methode und Stichtag: **Net-IRR** (nach Gebuehren) ist relevant, **Gross-IRR** schoent. **DPI** (realisiert/ausgezahlt) von **TVPI/RVPI** (inkl. unrealisierter Buchwerte) trennen — unrealisierte Werte sind GP-Schaetzungen.
- Track Record: nur Vorgaengerfonds **gleicher Strategie** zaehlen. Einzelne "Showcase Deals" sind kein Track Record. Pruefen, wie viele Fonds/Deals NICHT gezeigt werden (Survivorship).
- Gebuehren vollstaendig erfassen: Management Fee (auf committed vs. invested capital — grosser Unterschied), Carry/Gewinnbeteiligung, Hurdle Rate, Catch-up, Transaktions-/Monitoring-/Verwaltungs-Fees, Fund Expenses. Die All-in-Kostenlast bei Alternatives liegt oft deutlich ueber liquiden Fonds.
- Illiquiditaet ist eine eigene Risikodimension: Lock-up, Fund Term plus Verlaengerungsoptionen, fehlende ordentliche Kuendigungsrechte, duenner/kein Zweitmarkt. Fuer die Liquiditaetsplanung des Family Office zentral — Capital Calls kommen ueber Jahre verteilt.
- Immobilienbewertung: Ankaufsrendite/Cap Rate und vor allem die **Exit-Yield-Annahme** pruefen; kleine Aenderungen der Exit-Yield haben grosse Wirkung auf die Renditeprognose. Ist ein **unabhaengiges** Wertgutachten vorhanden oder nur die Anbieter-Bewertung?
- Regulatorik klaeren: Ist es ein regulierter AIF nach KAGB? Wer ist KVG/Kapitalverwaltungsgesellschaft und Verwahrstelle? Anleger-Einstufung (semiprofessionell/professionell), Mindestzeichnung, liegt ein gebilligter Verkaufsprospekt vor oder nur ein Pitchdeck?
- Interessenkonflikte: Hoehe des GP-/Initiator-Commitments (Skin in the Game), verbundene Parteien, Related-Party-Transaktionen, Vergaben an GP-nahe Dienstleister.
- Steuerliche und waehrungsseitige Themen (auslaendisches Fondsvehikel, Quellensteuer, Intransparenz, Hinzurechnungsbesteuerung) markieren und an den Steuerberater verweisen — KEINE verbindliche Steuerauskunft.
- Keine Anlageempfehlung — auch nicht impliziert ("aussichtsreich", "attraktiv bewertet", "Top-GP"). Der Skill liefert die Entscheidungsgrundlage; der Anlageausschuss entscheidet.

## Verification

- Asset-Klasse ist klassifiziert und das passende Kennzahlen-Modul angewendet; Hybridcharakter ggf. vermerkt.
- Behauptungen sind klar von belegten Fakten getrennt; alle nur beworbenen Angaben mit `(laut Anbieter, nicht unabhaengig belegt)` markiert.
- Track-Record-Angaben sind methodenkritisch eingeordnet (Net vs. Gross, DPI vs. TVPI, Stichtag, Vollstaendigkeit).
- Due-Diligence-Luecken-Block ist vorhanden und nennt konkret anzufordernde Unterlagen.
- Gebuehren sind all-in erfasst; Illiquiditaet/Lock-up als eigene Dimension bewertet.
- Mandatspassung ist eingeschaetzt (passt / teilweise / passt nicht), OHNE Invest-Empfehlung.
- Hausstandard, Stichtag der Unterlagen, Quellenangabe und Disclaimer sind enthalten.
- Output ist auf Deutsch, professionell-nuechtern, ohne emojis ausser dem Warnhinweis fuer fehlende/unbelegte Werte; Document liegt als `release_status=draft` vor.

## Detail: Asset-Klassen-Klassifikation

Ordne die Opportunitaet zuerst zu — sie bestimmt das anzuwendende Kennzahlen-Modul:

| Indiz im Pitchdeck | Asset-Klasse |
|---|---|
| Blind-Pool-Fonds, GP/General Partner, Fund Vintage, Carry/Hurdle, Capital Calls | Private Equity / Venture-Fonds |
| Konkretes Objekt oder Objektportfolio, Mietflaeche, Cap Rate, LTV, Exit-Yield | Immobilien (direkt oder Fonds) |
| Anteil an einem operativen Unternehmen, Pre-/Post-Money, Cap Table, Stimmrechte | Direkte Unternehmensbeteiligung |
| Kredit-/Darlehensstruktur, Senioritaet, Verzinsung, Besicherung, Covenants | Private Debt |
| Konzession, regulierter/contractierter Cashflow, Versorger/Transport/Digital | Infrastruktur |

Allgemeine Pflichtfelder (alle Klassen): Bezeichnung der Opportunitaet, Anbieter/GP/Initiator, Vehikel und Rechtsform plus Domizil, Asset-Klasse, Strategie, Zielvolumen, Mindestzeichnung, Anleger-Einstufung (semiprofessionell/professionell), Laufzeit/Term und Lock-up, regulatorischer Status (AIF? KVG? Verwahrstelle?), liegt ein gebilligter Prospekt vor?, Stichtag der Unterlagen.

## Detail: Modul Private Equity / Venture-Fonds

| Kennzahl | Hinweis |
|---|---|
| Vintage-Jahr | Auflagejahr des Fonds |
| Fund Size | Target und Hard Cap |
| Strategie | Buyout / Growth / Venture / Secondaries / Fund-of-Funds |
| Track Record Vorgaengerfonds | je Fonds: Vintage, Size, Net-IRR, TVPI, DPI, RVPI |
| Management Fee | Satz und Basis (committed vs. invested capital) |
| Carry / Gewinnbeteiligung | Satz, mit Hurdle Rate und Catch-up |
| GP-Commitment | Eigenanteil des GP (Skin in the Game) |
| Investitionszeitraum | und Gesamt-Fund-Term plus Verlaengerungsoptionen |
| Diversifikation | Zielanzahl Portfoliounternehmen, Sektor-/Regionenfokus |
| Co-Investment-Rechte | falls fuer LPs vorgesehen |

## Detail: Modul Immobilien (direkt und Fonds)

| Kennzahl | Hinweis |
|---|---|
| Objektart | Wohnen / Buero / Logistik / Handel / Mixed-Use |
| Lage / Mikrolage | Standortqualitaet, Markt |
| Mietflaeche / Einheiten | vermietbare Flaeche |
| Vermietungsstand / Leerstand | aktuell, in Prozent |
| WALT | gewichtete Restmietlaufzeit |
| Ankaufsrendite / Cap Rate | und Kaufpreisfaktor |
| Kaufpreis | absolut und je Quadratmeter |
| Finanzierungsstruktur / LTV | Fremdkapitalquote, Zinsbindung |
| Business-Plan-Typ | core / core-plus / value-add / opportunistic |
| CapEx-Bedarf | geplante Investitionen |
| Exit-Strategie | und angenommene Exit-Yield |
| Wertgutachten | Datum, Gutachter, unabhaengig oder Anbieter-intern? |
| (bei Fonds zusaetzlich) | Anzahl Objekte, Diversifikation, KVG/Verwahrstelle, Ausschuettungsprognose |

## Detail: Modul direkte Unternehmensbeteiligung

| Kennzahl | Hinweis |
|---|---|
| Bewertung | Pre- und Post-Money, Bewertungsmethode |
| Umsatz | aktuell plus Wachstum (Historie und Plan) |
| EBITDA / EBIT | und Marge, bereinigt vs. berichtet |
| Verschuldung / Kapitalstruktur | Nettoverschuldung, Gesellschafterstruktur |
| Angebotene Anteilsklasse | Stamm-/Vorzugsanteile, Liquidationspraeferenz |
| Stimmrechte / Minderheitenschutz | Drag-/Tag-along, Veto-Rechte, Informationsrechte |
| Verwaesserungsschutz | Anti-Dilution-Regelungen |
| Governance | Board-Sitz, Beirat, Kontrollrechte |
| Mittelverwendung | wofuer wird das frische Kapital genutzt? |
| Exit-Optionen | Strategie und Zeithorizont, bisherige Exits des Initiators |

## Detail: Modul Private Debt und Infrastruktur

**Private Debt**

| Kennzahl | Hinweis |
|---|---|
| Senioritaet | Senior / Unitranche / Mezzanine / Subordinated |
| Verzinsung | Cash-Zins plus PIK, fix oder variabel plus Spread |
| Besicherung / Covenants | Sicherheiten, Financial Covenants |
| Laufzeit | und Tilgungsprofil |
| Loan-to-Value | Beleihungsquote |
| Ausfall-/Recovery-Annahmen | erwartete Verlustquote |
| Diversifikation / Pipeline | Anzahl Kreditnehmer, Investitionspipeline |

**Infrastruktur**

| Kennzahl | Hinweis |
|---|---|
| Sektor | Energie / Transport / Digital / Versorger / soziale Infrastruktur |
| Cashflow-Profil | contracted / regulated / merchant |
| Konzessions-/Vertragslaufzeit | und Restlaufzeit |
| Regulatorischer Rahmen | Foerderregime, Genehmigungen |
| Inflationsindexierung | Schutz der Cashflows |
| Leverage | Projekt-/Fondsebene |
| ESG / Genehmigungen | offene behoerdliche Auflagen |

## Detail: Ausfuehrlichkeitsstufen

### Stufe 1 — Kurzbewertung (Anlageausschuss-Vorfilter)

Schnelle Einordnung, ob sich eine vertiefte Pruefung lohnt. Enthaelt: Bezeichnung, Anbieter/GP, Asset-Klasse, Strategie, Zielvolumen, Mindestzeichnung, Laufzeit/Lock-up; die wichtigsten klassenspezifischen Kerndaten; die drei Bloecke Charakteristiken/Chancen/Risiken (je 4-5 Stichpunkte); die Top-3 Due-Diligence-Luecken; eine Ampel-Einschaetzung der Mandatspassung (passt / teilweise / passt nicht) OHNE Invest-Empfehlung.

### Stufe 2 — Detailanalyse (intern)

Vollstaendige Pruefung fuer den Anlageausschuss. Enthaelt alles aus Stufe 1, plus: das vollstaendige klassenspezifische Kennzahlen-Modul; methodenkritische Track-Record-/Bewertungsanalyse; vollstaendige Due-Diligence-Luecken-Liste mit anzufordernden Unterlagen; All-in-Gebuehrenrechnung; Illiquiditaets- und einfache Szenariobetrachtung (Basis-/Stress-Fall der Anbieterprognose); Interessenkonflikte und GP-Commitment; regulatorische und steuerliche Hinweise.

### Stufe 3 — Vergleich mehrerer Opportunitaeten

Nur innerhalb der GLEICHEN Asset-Klasse sinnvoll (ein PE-Fonds und eine Direktimmobilie sind nicht 1:1 vergleichbar). Aufbau: Kennzahlen in Zeilen, Opportunitaeten in Spalten. Nach der Tabelle fuer jede Opportunitaet die drei Bloecke anhaengen. Bei DOCX-Output besten Wert je Zeile fett markieren (bei Gebuehren/Lock-up niedriger = besser, bei Track-Record-Renditen hoeher = besser), fehlende Werte mit `(nicht ausgewiesen)`. Wenn der Nutzer Klassen mischen will: explizit darauf hinweisen, dass nur qualitativ und nicht kennzahlenbasiert verglichen werden kann.

## Detail: Due-Diligence-Standard-Checklisten (was anzufordern ist)

**Private Equity / Venture-Fonds**: Limited Partnership Agreement (LPA) bzw. Gesellschaftsvertrag, Private Placement Memorandum, vollstaendige Track-Record-Tabelle aller Vorgaengerfonds (nicht nur Highlights), testierte Fondsabschluesse, Gebuehren-/Kostenuebersicht (LPA-Auszug), GP-Commitment-Nachweis, Referenzen anderer LPs, Side-Letter-Praxis.

**Immobilien**: unabhaengiges Wertgutachten, Mietvertraege/Mieterliste, technisches Gutachten (CapEx/Zustand), Grundbuchauszug, Finanzierungsvertrag/Term Sheet, Standort-/Marktanalyse, Business-Plan mit Annahmen, Versicherungsnachweise.

**Direktbeteiligung**: testierte Jahresabschluesse (3 Jahre), Cap Table, Gesellschaftervertrag/Beteiligungsvertrag, Beteiligungs-/Anteilskaufvertrag-Entwurf, Management-Lebenslaeufe, Kunden-/Auftragspipeline, rechtliche und steuerliche Due-Diligence-Berichte, Wettbewerbsanalyse.

**Private Debt / Infrastruktur**: Kreditvertrag/Term Sheet, Sicherheitendokumentation, Covenants-Definition, Modell mit Ausfall-/Recovery-Annahmen, Konzessions-/Abnahmevertraege (Infra), Genehmigungen/Regulierungsbescheide, technisches Gutachten, ESG-Bewertung.

## Detail: DOCX-Output-Struktur

Falls Word-Dokument gewuenscht, verwende `manage_documents action=create` mit `release_status=draft` und folge dieser Gliederung:

```
Titelseite: Bezeichnung der Opportunitaet, Anbieter/GP, Asset-Klasse, Datum, Ausfuehrlichkeitsstufe
Abschnitt 1: Stammdaten und Struktur (Vehikel, Strategie, Konditionen)
Abschnitt 2: Klassenspezifische Kennzahlen (PE / Immobilie / Beteiligung / Debt-Infra)
Abschnitt 3: Track Record / Bewertung — kritische Einordnung
Abschnitt 4: Gebuehren (all-in) und Illiquiditaet/Lock-up
Abschnitt 5: Chancen und Risiken (Block-Sicht)
Abschnitt 6: Mandatspassung (ohne Invest-Empfehlung)
Abschnitt 7: Due-Diligence-Luecken und anzufordernde Unterlagen
Fusszeile: Disclaimer aus Hausstandard
```

Hinweis "Entwurf — fuer Anlageausschuss, vor Entscheidung pruefen" am Anfang. Farbschema und Schriftarten gemaess Skill `m-und-s-hausstandard`.

## Detail: Beispiel-Workflow

Ein GP sendet ein Pitchdeck zu einem Buyout-Fonds (Vintage 2026, Target 500 Mio. EUR):

1. Klassifizieren: Private Equity / Venture-Fonds.
2. Stammdaten plus PE-Modul extrahieren; Track Record der Vorgaengerfonds aus dem Deck uebernehmen und als "laut Anbieter" markieren, GP-Hintergrund unabhaengig recherchieren.
3. Net-IRR vs. Gross-IRR pruefen, DPI vom TVPI trennen, fragen welche Vorgaengerfonds NICHT gezeigt werden.
4. DD-Luecken: LPA, vollstaendige Track-Record-Tabelle, testierte Abschluesse, GP-Commitment-Nachweis anfordern.
5. Drei Bloecke plus Gebuehren-all-in (2 Prozent auf committed plus 20 Prozent Carry ueber 8 Prozent Hurdle) und Illiquiditaet (10 Jahre Term plus 2x1 Jahr Verlaengerung, keine ordentliche Kuendigung).
6. Mandatspassung gegen Anlagerichtlinien pruefen (Illiquiditaetsbudget, Mindestzeichnung vs. Allokationsgrenze).
7. Als Document `release_status=draft` ablegen, zur Anlageausschuss-Sitzungsmappe anbieten.
