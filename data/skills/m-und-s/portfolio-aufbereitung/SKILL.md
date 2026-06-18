---
name: portfolio-aufbereitung
description: "Bereitet einen Portfolio-Snapshot fuer Reporting, Anlageausschuss-Vorlagen oder Mandantenkommunikation auf: Allokation, Top-Positionen, Gesamtwert nach Hausstandard."
version: 1.0.0
category: m-und-s
tags: [portfolio, vermoegensverwaltung, reporting, m-und-s]
status: published
confidence: 0.85
source: imported
shared: true
created: 2026-06-18T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn der Nutzer eine Auswertung, Aufbereitung oder Uebersicht zu einem Mandantenportfolio anfordert. Begriffe: "Portfolio aufbereiten", "Allokation zeigen", "Positionsliste", "Vermoegensuebersicht", "Top-Positionen", "wieviel Aktien hat Mandant X", "Asset-Mix Mandant Y". Falls der Mandant in einem laufenden Reporting/Anschreiben-Workflow steckt, verbindet sich dieser Skill mit `reporting-entwurf` bzw. `anschreiben-entwurf`.

## Procedure

1. Klaere den Mandanten und den Stichtag (Mandantenname oder Portfolio-ID). Wenn unklar: liste Portfolios per `app_api action=call method=GET path=/api/portfolios` und biete dem Nutzer eine Auswahl.
2. Hole die Snapshots zum Portfolio: `app_api action=call method=GET path=/api/portfolios/{id}/snapshots`. Wenn der Nutzer keinen Stichtag nennt, nimm den juengsten Snapshot.
3. Wenn der gewuenschte Snapshot fehlt, fordere den Mitarbeiter zum Upload via Portfolio-Panel auf (das aktuelle Snapshot-Upload-Endpunkt ist `POST /api/portfolios/{id}/snapshots` mit `file` und `stichtag`).
4. Aggregiere die Daten ueber `app_api action=call method=GET path=/api/portfolios/{id}/snapshots/{snapshot_id}/summary`. Antwort enthaelt `allocation` (je Asset-Klasse) und `top_positions` (Top 5).
5. Formuliere eine strukturierte Antwort: Kopfzeile (Mandant, Stichtag, Gesamtwert), Allokations-Tabelle, Top-Positionen-Tabelle, Hinweis auf Auffaelligkeiten (Klumpenrisiken, Cash-Quote, Fremdwaehrung). Niemals Performance-Zahlen erfinden — der Snapshot enthaelt nur den Bestand, keine Zeitreihe.
6. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Datums- und Zahlenformat, Tabellenformat, Disclaimer.
7. Lege das Ergebnis bei Bedarf als Document mit `release_status=draft` ab (`manage_documents action=create`), damit es spaeter in eine Anlageausschuss-Sitzungsmappe einfliessen kann.

## Pitfalls

- Niemals Performance- oder Renditezahlen berechnen oder schaetzen — der Snapshot ist eine Bestandsaufnahme, keine Performance-Quelle. Wenn der Nutzer "Performance" fragt, klar sagen, dass dafuer ein Vergleich mit einem zweiten Snapshot oder externe Daten noetig sind.
- Asset-Klassen-Heuristik des Importers ist grob (ISIN-Praefix + Name-Keywords). Wenn dem Nutzer eine Position ueberraschend zugeordnet erscheint, vor weiterer Auswertung manuelle Korrektur im Snapshot anregen — keine eigenen Klassifikations-Annahmen treffen.
- Fremdwaehrungs-Positionen werden im Wert NICHT in Basiswaehrung umgerechnet — der Importer haelt Marktwerte so, wie sie im Quelldokument stehen. Bei Mischportfolios den Hinweis "Werte teils in Fremdwaehrung" mit anhaengen.
- Cash-Quote bei >25 Prozent zwingend kommentieren — Klumpensignal, gehoert in jeden Anlageausschuss-Hinweis.
- Mandantendaten sind streng vertraulich; keine Mandantennamen oder Positionsdetails in Antworten ausserhalb des owner-Scopes ausgeben.

## Verification

- Antwort enthaelt Mandant, Stichtag, Gesamtwert, Basiswaehrung.
- Allokations-Tabelle ist vorhanden, Summe der Prozentwerte rund 100 (Abweichung wegen Rundung erlaubt).
- Top-Positionen-Tabelle zeigt Name, ISIN/WKN, Marktwert, ggf. Anteil.
- Auffaelligkeiten (Cash-Quote, Klumpenrisiken, Fremdwaehrung) sind benannt oder explizit als "keine" markiert.
- Hausstandard angewendet (Datumsformat, Tabellenformat, Disclaimer).
- Bei Persistierung als Document: `release_status=draft` und Hinweis "Entwurf — vor Versand pruefen".

## Detail: Erwartete Eingangs-Daten

Der Snapshot wird per CSV/XLSX aus der Family-Office-Software exportiert. Akzeptierte Spalten (Header-Aliase werden automatisch erkannt):

- `ISIN`, `WKN` (mindestens eines empfohlen)
- `Name` / `Bezeichnung` / `Wertpapier` (Pflicht)
- `Anlageklasse` / `Asset Class` / `Kategorie` (optional — Heuristik faellt sonst zurueck)
- `Menge` / `Stueck` / `Nominal`
- `Waehrung` / `Currency`
- `Kurswert` / `Marktwert` / `Wert`
- `Anteil` / `Gewichtung` (in Prozent)

Der Importer toleriert deutsche Zahlenformate (1.234,56) und CSV-Encoding (UTF-8, ISO-8859-1, CP1252).
