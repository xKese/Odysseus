---
name: aktien-analyse
description: "Vergleich und Analyse von Einzelaktien auf Basis von Geschaeftsberichten, Quartalsmitteilungen, Anbieter-Seiten oder manuell eingegebenen Daten. Erstellt professionelle Auswertungen auf Deutsch in drei Detailstufen: Kurzuebersicht (Kundenkommunikation), Detailanalyse (intern) und Peer-Vergleich (mehrere Aktien). Ausgabe als Word-Dokument (.docx) oder Fliesstext im Chat."
version: 1.0.0
category: finance
tags: [aktien, einzelaktie, fundamentalanalyse, vermoegensverwaltung, m-und-s]
status: published
confidence: 0.85
source: imported
owner: kese
shared: true
created: "2026-06-19T00:00:00Z"
---

## When to Use

Triggere diesen Skill, wenn der Nutzer eine Aktie, ein boersennotiertes Unternehmen oder einen Einzeltitel analysieren, vergleichen, gegenuebersteleln oder bewerten moechte. Trigger-Begriffe: "Aktienanalyse", "Aktienvergleich", "Steckbrief Aktie", "wie ist die Aktie XY zu bewerten", "Fundamentalanalyse", "Bewertung Unternehmen", "Quartalszahlen auswerten", "Geschaeftsbericht analysieren". Auch dann triggern, wenn Geschaeftsbericht-PDFs oder Quartalsmitteilungen hochgeladen werden, ohne dass der Nutzer den Skill namentlich nennt. NICHT verwenden fuer Investmentfonds/ETFs — das ist `fonds-analyse`. NICHT fuer reine Charttechnik/Trading-Setups.

## Procedure

1. Frage nach gewuenschter Ausfuehrlichkeitsstufe und Anlagezweck: (1) Kurzuebersicht fuer Kundenkommunikation, (2) Detailanalyse intern, (3) Peer-Vergleich fuer mehrere Aktien. Klaere bei Family-Office-Mandanten den Charakter (Buy-and-Hold, Dividendenfokus, opportunistisch). Falls Quellen-PDFs noch fehlen, frage nach Upload oder ISIN/WKN.
2. Lies alle bereitgestellten Geschaeftsberichte/Quartalsmitteilungen und extrahiere die Pflichtfelder gemaess Kennzahlentabellen im body_extra (Stammdaten, Bewertung, Fundamentaldaten, Dividenden, Risiko). Verwende `read_file` fuer hochgeladene Dateien, `web_fetch` nur fuer oeffentliche Anbieter-Seiten (Yahoo Finance, Comdirect, Onvista, Investor Relations). Fuer tiefere Recherche `trigger_research` mit konkreter Frage und Quellenpflicht — nie unbelegte Aussagen uebernehmen.
3. Markiere jeden nicht direkt im Dokument ausgewiesenen Wert mit `(nicht ausgewiesen)` oder `(berechnet aus: ...)`. Niemals Zahlen schaetzen.
4. Erstelle fuer jede Aktie drei Bloecke (Charakteristiken, Chancen, Risiken) mit je 4-5 unternehmensspezifischen Stichpunkten. Keine Platituden, keine generischen Risikohinweise (Inflation und Geopolitik gelten fuer alle Aktien — bringen nur dann Mehrwert, wenn das Unternehmen besonders davon betroffen ist).
5. Baue die Auswertung gemaess der gewaehlten Stufe (siehe body_extra) und formatiere als Markdown (im Chat) oder erzeuge ein DOCX ueber `manage_documents action=create` mit dem Hausstandard-Layout. Bei DOCX `release_status=draft`.
6. Haenge am Ende einen Block "Fehlende Kennzahlen" mit konkreten Ergaenzungsquellen an (Bloomberg, Refinitiv, Onvista, Yahoo Finance, IR-Seite, fondsweb fuer ETF-Tracker auf den Titel).
7. Wende den Hausstandard von Meeder & Seifer an (siehe Skill `m-und-s-hausstandard`): Tonalitaet, Datumsformat, Disclaimer, Tabellen-Farbschema, Quellenangabe.

## Pitfalls

- TTM (Trailing Twelve Months) vs. LFY (Last Fiscal Year) bei Bewertungskennzahlen niemals vermischen — IMMER Zeitraum (TTM, FY2025, Q1/2026 etc.) angeben.
- Adjusted Earnings (bereinigt) vs. Reported Earnings explizit ausweisen. "Adjusted" ist die Sicht des Managements und sollte mit der reported-Zahl gegengeprueft werden.
- IFRS- vs. US-GAAP-Abschluesse bei Peer-Vergleichen kennzeichnen, weil Margen und Eigenkapitalquoten zwischen Standards nicht 1:1 vergleichbar sind.
- Dividendenrenditen muessen auf Brutto-/Nettoausweis geprueft werden; Quellensteuer-Saetze fuer auslaendische Aktien (z.B. CH 35 Prozent, US 30 Prozent reduzierbar via DBA) erwaehnen, wenn Mandantenkontext eine deutsche Steuerpflicht hat.
- Aktiensplits und Sonderdividenden bei historischen Kursen pruefen — viele Anbieter-Charts sind unbereinigt. Quelle angeben, ob "adjusted close" oder "raw".
- Bei Small- und Mid-Caps Liquiditaet (durchschnittliches Tagesvolumen) und Bid/Ask-Spread mit angeben — relevant fuer die Family-Office-Disposition (Order-Groesse vs. Marktimpact).
- Keine Anlageempfehlung — auch nicht impliziert ("vielversprechend", "unterbewertet", "starkes Investment"). Der Skill liefert Befunde, der Anlageausschuss entscheidet (siehe Skill `anlageausschuss-vorbereitung`).
- Wenn die Aktie bereits in einem Mandantenportfolio enthalten ist (siehe Skill `portfolio-aufbereitung`), Hinweis in der Auswertung aufnehmen, ohne Mandantennamen ausserhalb des Owner-Scopes preiszugeben.

## Verification

- Alle Zahlen sind direkt aus Quelldokument oder benannter Anbieter-Seite entnommen, jede Zahl hat Stichtag und Zeitraumbezug (TTM, FY2025, Q1/2026).
- Fuer jede Aktie existieren die drei Bloecke Charakteristiken / Chancen / Risiken mit je 4-5 unternehmensspezifischen Stichpunkten.
- Fehlende-Kennzahlen-Block ist vorhanden und nennt mindestens zwei konkrete Ergaenzungsquellen.
- Bei Peer-Vergleichen sind unterschiedliche Bilanzierungsstandards (IFRS/US-GAAP) als Fussnote gekennzeichnet.
- Disclaimer aus Hausstandard, Stichtag der Daten und vollstaendige Quellenangabe sind enthalten.
- Output ist auf Deutsch, professioneller Ton, ohne emojis ausser dem Warnhinweis fuer fehlende Werte.

### Pflichtfelder (Stammdaten)

| Kennzahl | Quelle / Hinweis |
|---|---|
| Unternehmensname | Vollstaendiger Firmenname inkl. Rechtsform |
| ISIN / WKN | Geschaeftsbericht oder IR-Seite |
| Heimatboerse plus Listings | z.B. XETRA primaer, NYSE secondary |
| Sektor / Branche | GICS-Klassifikation oder Hausordnung |
| Aktienart | Stammaktie, Vorzugsaktie, Namens-/Inhaberaktie |
| Indexzugehoerigkeit | DAX, MDAX, SDAX, S&P 500, Nikkei etc. |
| Marktkapitalisierung | Kurs mal Aktienanzahl, mit Stichtag |
| Ausstehende Aktien | Gesamtzahl laut letztem Geschaeftsbericht |
| Streubesitz | Float in Prozent |
| Stimmrechtsverteilung | Hauptaktionaere, Familien-/Stiftungsanteile |
| Geschaeftsmodell | 2-3 Saetze Kurzbeschreibung |
| Hauptmaerkte / Regionen | Umsatzaufteilung in Prozent |
| Mitarbeiterzahl | aktuellster Stand |
| Hauptsitz / Land | Sitzgesellschaft, ggf. Steuerdomizil |
| Gruendungsjahr | Geschaeftsbericht |

### Bewertungskennzahlen

| Kennzahl | Hinweis |
|---|---|
| Aktueller Kurs | Stichtag explizit |
| 52-Wochen-Hoch / -Tief | Anbieterquelle |
| KGV (P/E) | TTM und Forward, getrennt ausweisen |
| KBV (P/B) | letztes berichtetes Eigenkapital |
| KUV (P/S) | TTM-Umsatz |
| EV/EBITDA | TTM, mit Net-Debt-Berechnung |
| PEG Ratio | Bei vorhandener Wachstumsprognose, Quelle angeben |
| Dividendenrendite | aktuell, brutto, Stichtag |
| Ausschuettungsquote | Dividende / Gewinn, letzte 12 Monate |

### Fundamentalkennzahlen (5-Jahres-Historie plus TTM)

| Kennzahl | Hinweis |
|---|---|
| Umsatz | letzte 5 Geschaeftsjahre plus TTM |
| Umsatzwachstum p.a. | CAGR 3J und 5J |
| EBIT / Operatives Ergebnis | letzte 5 Geschaeftsjahre |
| EBIT-Marge | letzte 5 Jahre, Trend ausweisen |
| Nettogewinn | letzte 5 Jahre |
| EPS | unverwaessert und verwaessert, falls relevant |
| Free Cashflow | letzte 5 Jahre, ggf. Bereinigung dokumentieren |
| Eigenkapital | aktueller Stand |
| Eigenkapitalquote | aktueller Stand |
| Nettoverschuldung | aktueller Stand |
| Net Debt / EBITDA | aktueller Stand |
| ROE | letzte 3 Jahre |
| ROCE / ROIC | letzte 3 Jahre |

### Dividendenfokus (Family-Office relevant)

| Kennzahl | Hinweis |
|---|---|
| Dividenden-Historie | letzte 5 Jahre, je Geschaeftsjahr |
| Geplante / angekuendigte Dividende | naechste Hauptversammlung |
| Dividendenkontinuitaet | Anzahl Jahre ohne Senkung / Aussetzung |
| Dividenden-CAGR | 5-Jahres-Wachstumsrate |
| Ex-Tag und Zahltag | letzte Periode plus naechste |

### Risikokennzahlen

| Kennzahl | Hinweis |
|---|---|
| Beta | 5-Jahres-Beta gegen lokalen Index |
| Volatilitaet | annualisiert, taegliche Renditen |
| Max. Drawdown (5J) | aus historischen Kursen, "adjusted close" |
| Sharpe Ratio | falls verfuegbar |
| Durchschnittliches Tagesvolumen | Liquiditaetssignal |
| Bid/Ask-Spread | bei Small- und Mid-Caps zwingend |

### Stufe 1 — Kurzuebersicht (Kundenkommunikation)

Praegnante Zusammenfassung fuer Endkunden oder Beratungsgespraeche. Enthaelt: Unternehmen, ISIN, Sektor, Indexzugehoerigkeit; Geschaeftsmodell-Kurzbeschreibung (2-3 Saetze); Hauptkennzahlen (Marktkap, KGV TTM, KBV, Dividendenrendite); Performance 1J/3J/5J sofern verfuegbar; Risikoprofil (Beta, Volatilitaet); Charakteristiken/Chancen/Risiken (je 4-5 Stichpunkte); Fehlende-Kennzahlen-Hinweis. Ton: verstaendlich, ohne uebermaeßige Fachbegriffe, professionell.

### Stufe 2 — Detailanalyse (intern)

Vollstaendige Analyse fuer interne Entscheidungsprozesse und Anlageausschuss-Vorbereitung. Enthaelt alles aus Stufe 1, plus: alle Bewertungs- und Fundamentalkennzahlen, 5-Jahres-Historie der Fundamentaldaten, Dividendenfokus mit Historie und Ausschuettungspolitik, Kapitalstruktur (Eigen-/Fremdkapital, Liquiditaet), Hauptaktionaere mit Beteiligungshoehen, Management (Vorstand, Aufsichtsrat, Vorstandsverguetung), Strategie und Ausblick aus dem letzten Geschaeftsbericht, ESG-Einstufung (falls vorhanden, z.B. MSCI ESG Rating), Analysten-Konsens (Kursziele plus Anzahl Analysten, nur wenn Quelle nennbar). Bei Aktien im Familienbesitz oder mit Stiftungsstruktur explizit dokumentieren.

### Stufe 3 — Peer-Vergleich (mehrere Aktien)

Aufbau: Kennzahlen in Zeilen, Aktien in Spalten. Reihenfolge: (1) Stammdaten, (2) Bewertung, (3) Fundamental, (4) Dividenden, (5) Risiko, (6) Sonstiges. Nach der Tabelle fuer jede Aktie separaten Abschnitt mit den drei Bloecken (Charakteristiken, Chancen, Risiken) anhaengen. Bei DOCX-Output: besten Wert je Zeile fett markieren (bei Bewertung niedrigster Wert "guenstig", bei Marge/ROE hoechster Wert), fehlende Werte mit `(nicht ausgewiesen)`. Bilanzierungsstandard-Unterschiede (IFRS/US-GAAP) als Fussnote zur betroffenen Zeile.

Falls Word-Dokument gewuenscht, verwende `manage_documents action=create` mit `release_status=draft` und folge dieser Gliederung:

```
Titelseite: Unternehmensname(n), Datum der Analyse, Ausfuehrlichkeitsstufe
Abschnitt 1: Stammdaten und Geschaeftsmodell
Abschnitt 2: Bewertung (Multiples, Kurs)
Abschnitt 3: Fundamentaldaten (5J-Historie)
Abschnitt 4: Dividenden (nur Stufe 2)
Abschnitt 5: Risiko und Liquiditaet
Abschnitt 6: Chancen und Risiken (Block-Sicht je Titel)
Abschnitt 7: Fehlende Kennzahlen und Ergaenzungsquellen
Fusszeile: Disclaimer aus Hausstandard
```

Farbschema und Schriftarten gemaess Skill `m-und-s-hausstandard`. Hinweis "Entwurf — vor Versand pruefen" am Anfang einfuegen.

Nutzer laedt einen Geschaeftsbericht der Allianz SE hoch und schreibt "Bitte analysiere diese Aktie":

1. Geschaeftsbericht lesen, Pflichtfelder extrahieren (Stammdaten, Bewertung, Fundamentaldaten, Dividenden, Risiko).
2. Fehlende Werte identifizieren — typisch fehlen Live-Kurs, Marktkap (Stichtag), Beta, Volatilitaet, Liquiditaet. Diese ggf. ueber `web_fetch` auf Anbieter-Seite ergaenzen.
3. Fragen: "Soll ich eine Kurzuebersicht (Stufe 1), Detailanalyse (Stufe 2) oder Peer-Vergleich (Stufe 3) erstellen? Markdown im Chat oder Word-Dokument?"
4. Auswertung in gewaehltem Format erstellen, Hausstandard anwenden.
5. Fehlende-Kennzahlen-Block mit Ergaenzungsquellen anhaengen, als Document mit `release_status=draft` ablegen und zur Freigabe stellen.

Wenn der Mandant bereits Allianz-Aktien im Portfolio hat (siehe Skill `portfolio-aufbereitung`), Hinweis aufnehmen, ohne Mandantendetails offenzulegen.
