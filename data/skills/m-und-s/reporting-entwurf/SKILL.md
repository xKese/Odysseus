---
name: reporting-entwurf
description: "Erstellt einen Reporting-Entwurf nach M&S-Hausvorlage (Quartals- oder Monatsbericht) auf Basis von Portfolio- und Performancedaten. Liefert Markdown oder DOCX zur Freigabe."
version: 1.0.0
category: m-und-s
tags: [reporting, hausvorlage, m-und-s]
status: published
confidence: 0.85
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Triggere diesen Skill, wenn ein Mandantenreporting, Quartalsbericht, Monatsbericht oder eine Vermoegensuebersicht als Entwurf erstellt werden soll. Begriffe: "Quartalsreporting", "Monatsbericht", "Mandantenbericht", "Reporting fuer Mandant X", "erstell den Bericht fuer Q3".

## Procedure

1. Klaere die Berichtsparameter: Mandantenname, Quartal/Monat, Stichtag, Berichtswaehrung. Klaere zusaetzlich den Recherchemodus (siehe Skill `recherche-modus`): Schnellanalyse (nur interne Daten + Upload) oder Tiefenanalyse (zusaetzlich `trigger_research` fuer Marktkontext und Benchmark-Daten des Berichtszeitraums). Wenn der Nutzer den Modus nicht nennt, nachfragen — niemals ungefragt einen Deep-Research-Lauf starten. Wenn Daten fehlen, gezielt nachfragen.
2. Sammle die Inhaltsbausteine: Performance-Tabelle (YTD / 1J / 3J p.a. mit Benchmark), Asset-Allokation, Top-Positionen, Risikokennzahlen (Volatilitaet, Max. Drawdown, Sharpe), Markt-/Strategieausblick. Daten kommen entweder aus dem Hauswissen (`hauswissen-suche`), aus hochgeladenen Auswertungen oder ueber explizite Mandanten-Inputs des Mitarbeiters. NUR im Tiefenmodus den Markt-/Strategieausblick mit `trigger_research` (Marktkontext, Benchmark-Daten) unterfuettern; den fertigen Bericht ueber `manage_research` lesen und Deep-Research-Befunde mit Marker `(Deep Research: <Quelle>, <Stichtag>)` einarbeiten, getrennt von den Portfoliodaten. Im Schnellmodus KEIN `trigger_research`.
3. Markiere fehlende Daten als `(noch zu ergaenzen)`. Niemals Zahlen erfinden oder aus dem Modellwissen extrapolieren.
4. Lade die Hausvorlage ueber `app_api action=call method=GET path=/api/templates/reporting/quartalsreporting-skelett` und rufe `app_api action=call method=POST path=/api/templates/reporting/quartalsreporting-skelett/render body={"mandant": {...}, "stichtag": "...", "perf": {...}, "alloc": {...}, ...}` mit dem zusammengestellten Datenobjekt auf. Antworten enthalten das gerenderte Markdown plus eine Liste `missing_placeholders` — diese Liste explizit im Chat ausweisen.
5. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Tonalitaet, Datums- und Zahlenformat, Tabellenformat, Disclaimer.
6. Lege den Entwurf per `manage_documents action=create` mit Titel `Reporting <Mandant> <Quartal> <Jahr>` ab und uebergebe ihn dem Mitarbeiter zur Freigabe. Bei Stufe 2 (Freigabe noetig) explizit kennzeichnen: "Entwurf — vor Versand pruefen".

## Pitfalls

- Niemals Performance- oder Risikozahlen schaetzen oder aus aelteren Quartalen fortschreiben. Lieber `(noch zu ergaenzen)` stehen lassen und das Pilotteam darauf hinweisen.
- Benchmark-Auswahl muss zum Mandantenmandat passen; im Zweifel mit der Hauswissen-Sammlung "Anlagerichtlinien" abgleichen.
- Bei Vermoegensanlagen, die regulatorisch besonders zu kennzeichnen sind (z.B. SFDR-Artikel-9-Fonds, Sonderverwahrung), den Hinweis explizit aufnehmen.
- Im DOCX-Output das Farbschema des Hausstandards verwenden; eigene Akzentfarben sind nicht zulaessig.
- Reporting-Entwuerfe sind NIEMALS versandfertig — Skill liefert Stufe-2-Output (Vorschlag mit Freigabe).

## Verification

- Vorlage wurde gerendert, `missing_placeholders` (falls vorhanden) wurden im Chat genannt.
- Performance, Allokation, Risiko sind entweder mit konkreten Werten plus Stichtag belegt oder als `(noch zu ergaenzen)` markiert.
- Hausstandard angewendet (Datumsformat, Disclaimer, Tabellenformat).
- Entwurfs-Vermerk "Entwurf — vor Versand pruefen" ist enthalten.
- Dokument liegt im Library/Documents als `draft`, nicht als `released`.
- Recherchemodus ist geklaert (bei fehlender Angabe wurde nachgefragt); bei Tiefenanalyse sind Deep-Research-Befunde markiert, mit Quelle und Stichtag belegt und von den Portfoliodaten getrennt.
