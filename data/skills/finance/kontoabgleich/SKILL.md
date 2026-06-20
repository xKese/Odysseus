---
name: kontoabgleich
description: Automatischer Kontoabgleich zwischen internem Family-Office-System (PDF) und Bank-Kontoumsaetzen (CSV/XLSX). Gleicht vorzeichenbehaftete Betraege ab (Soll/Haben) und erstellt einen deutschen Markdown-Bericht mit fehlenden oder ueberzaehligen Buchungen sowie abweichenden Buchungs- und Valutatagen.
version: 1.0.0
category: finance
tags: [reconciliation, family-office, bank, kontoabgleich, m-und-s]
status: published
confidence: 0.9
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Verwende diesen Skill immer, wenn der Nutzer einen Kontoabgleich, eine Kontenabstimmung, einen Umsatzabgleich, eine Account Reconciliation oder einen Buchungsvergleich zwischen Bank und internem System durchfuehren moechte. Trigger-Begriffe: Abgleich, Abstimmung, "stimmt nicht ueberein", "fehlende Buchungen", "Differenzen pruefen", "Kontoumsaetze vergleichen", "Account Check".

## Procedure

1. Identifiziere die beiden Quellen: das interne System liefert eine PDF (Export aus Family-Office-Software), die Bank liefert CSV oder XLSX. Frage gezielt nach, wenn die Zuordnung unklar ist.
2. Stelle sicher, dass beide Dateien im owner-spezifischen Upload-Verzeichnis liegen. Wenn nicht, fordere den Nutzer zum Upload auf.
3. Ermittle das Ausgabeverzeichnis fuer diesen Lauf: `data/uploads/{owner}/reconcile/`. Lege es per `bash mkdir -p` an, falls noch nicht vorhanden. Den Owner-Namen liefert die Sitzung; im Zweifel den vom System bereitgestellten Pfad nutzen, nicht raten.
4. Rufe das Reconciliation-Skript mit dem `bash`-Tool auf: ``` python data/skills/finance/kontoabgleich/scripts/reconcile.py \ --intern <pfad-zur-pdf> \ --bank <pfad-zur-csv-oder-xlsx> \ --output data/uploads/{owner}/reconcile/Kontoabgleich_Ergebnis.md ```
5. Lies den erzeugten Markdown-Bericht und fasse die wichtigsten Befunde im Chat zusammen (Anzahl Uebereinstimmungen, Differenzen, Status).
6. Biete an, den Bericht per `manage_documents create` als Hausdokument abzulegen oder als Anhang zu mailen.
7. Wende den Hausstandard von Meeder & Seifer an (siehe Skill `m-und-s-hausstandard`): Tonalitaet, Datumsformat, Disclaimer.

## Pitfalls

- Matching-Key ist der vorzeichenbehaftete Betrag (Soll negativ, Haben positiv) — keine Toleranz, keine Naeherung. Fehlbuchungen mit falschem Vorzeichen erscheinen sowohl als "fehlend" als auch als "ueberzaehlig".
- PDF-Layout entscheidet ueber das Vorzeichen: x-Position der Betraege bestimmt Soll/Haben (Schwelle x < 600 = Soll). Wenn das Skript die Vorzeichen nicht erkennt, scheint der Abgleich falsch — vor der Naharbeit das Skript-Log lesen.
- CSV/XLSX-Encoding (UTF-8 vs. ISO-8859-1) und Trennzeichen (Komma, Semikolon, Tab) variieren — das Skript probiert mehrere Varianten, kann aber bei ungewoehnlichen Exports scheitern.
- Skript benoetigt die Python-Pakete `pdfplumber`, `openpyxl` und `pandas`. Sind sie im Container nicht installiert, mit dem Admin Ruecksprache halten — niemals `--break-system-packages` im laufenden Betrieb erzwingen.
- Pfadangaben muessen relativ zum Repo-Root sein oder absolut; relative Pfade aus dem Chat ohne Kontext fuehren zu Fehlern.
- Niemals den Originalbericht des Skripts veraendern — er dient als Audit-Beleg. Zusaetzliche Kommentare oder Korrekturen separat im Chat oder als Folge-Dokument.

## Verification

- Der Markdown-Bericht existiert unter `data/uploads/{owner}/reconcile/Kontoabgleich_Ergebnis.md` und enthaelt die Zusammenfassungstabelle, Abweichende Valutatage, Abweichende Buchungstage, Fehlende und Ueberzaehlige Buchungen.
- Die Summe `Buchungen Bank` + `Buchungen Intern` stimmt mit den hochgeladenen Quellen ueberein.
- Wenn keine Differenzen vorhanden sind, zeigt der Bericht "Status: ALLE BUCHUNGEN STIMMEN UEBEREIN".
- Bei Differenzen ist fuer jede gelistete Buchung das Vorzeichen (Soll/Haben) klar markiert.
- Stichtag des Reports steht in der Kopfzeile.

- Match-Key: vorzeichenbehafteter Betrag (Soll = negativ, Haben = positiv).
- PDF: Soll/Haben wird ueber x-Position der Betraege bestimmt (Schwelle x < 600 = Soll).
- CSV: Vorzeichen direkt aus dem Betrag (negativ = Soll, positiv = Haben).
- 1:1-Zuordnung bei Duplikaten, keine Toleranz.
- Abweichende Valutatage und Buchungstage werden separat im Report ausgewiesen.
- Fehlbuchungen mit falschem Vorzeichen erscheinen als fehlend UND ueberzaehlig.

Der erzeugte Markdown-Bericht enthaelt in dieser Reihenfolge:

1. Zusammenfassung mit Anzahlen und Status.
2. Abweichende Valutatage bei gematchten Buchungen.
3. Abweichende Buchungstage bei gematchten Buchungen.
4. Fehlende Buchungen mit Soll/Haben-Kennzeichnung (intern nachzubuchen).
5. Ueberzaehlige Buchungen mit Soll/Haben-Kennzeichnung (intern zu pruefen).
