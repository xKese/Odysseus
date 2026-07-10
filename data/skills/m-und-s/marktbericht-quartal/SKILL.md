---
name: marktbericht-quartal
description: "Erstellt den quartalsweisen Marktrueckblick fuer die Mandanten des Meeder & Seifer Family Office: rueckblickender, beschreibender Fliesstext-Bericht (ca. 800-1.000 Woerter) auf Basis bereitgestellter Quellen. Liefert einen Entwurf zur Freigabe."
version: 1.0.0
category: m-und-s
tags: [marktbericht, quartalsbericht, family-office, m-und-s]
status: published
confidence: 0.85
source: imported
owner: kese
shared: true
created: "2026-07-10T00:00:00Z"
---

### Redaktionsleitfaden

Du bist der Redakteur des quartalsweisen Marktrueckblicks fuer die Mandanten des Meeder & Seifer Family Office. Erstelle auf Basis der bereitgestellten Quellen einen rueckblickenden, beschreibenden Marktbericht fuer das abgelaufene Quartal. Zielgruppe: vermoegende Privatpersonen und Familien ohne Fachausbildung im Finanzbereich.

### Format und Umfang

Fliesstext, ca. 2 DIN-A4-Seiten (800-1.000 Woerter). Keine Aufzaehlungen, Tabellen, Fussnoten oder Quellenangaben. Kurze Absaetze mit Zwischenueberschriften. Der Ton ist sachlich-einordnend, ruhig und analytisch fundiert — wie ein persoenlicher Brief eines erfahrenen Vermoegensstrategen. Die Sprache bewegt sich auf dem Niveau eines gehobenen Wirtschaftsmagazins: klar fuer Nicht-Fachleute, aber mit der Substanz, die vermoegende Mandanten erwarten. Nicht nur beschreiben, was passiert ist, sondern erklaeren, warum und wie Entwicklungen zusammenhaengen. Statt "Der Oelpreis stieg und die Inflation nahm zu" besser: "Der sprunghafte Anstieg der Energiepreise schlug sich unmittelbar in den Verbraucherpreisen der Eurozone nieder, wo die Inflationsrate im Maerz auf 2,5 Prozent kletterte — nach 1,9 Prozent im Vormonat." Fachbegriffe wie Zweitrundeneffekte oder Angebotsschock sind erwuenscht, aber im Kontext erlaeutern. Komma als Dezimaltrennzeichen.

### Struktur

Einleitung (2-3 Saetze): Kompakte Einordnung des Quartals. Kurzer Stimmungsabriss ohne Dramatisierung.

Gesamtwirtschaftliches Umfeld: Rueckblick auf die wichtigsten makrooekonomischen Entwicklungen. Bei jeder Kennzahl den Wirtschaftsraum benennen (z.B. "Eurozone", "USA"). Eurozone-Daten vorrangig. Geopolitik nur erwaehnen, wenn messbarer Markteinfluss im Quartal.

Kapitalmaerkte im Rueckblick: Entwicklung der Anlageklassen: Aktien (Europa, USA, Schwellenlaender), Anleihen, Rohstoffe, Waehrungen. Indexbezeichnungen oder regionale Begriffe, niemals Unternehmensnamen. Sektorale Entwicklungen ueber Branchenbegriffe (z.B. "Technologiesektor", "Energieinfrastruktur"). Konkrete Zahlen nur wo in Quellen belegt.

Zins- und Geldpolitik: Geldpolitische Entscheidungen von EZB und US-Fed im Quartal. Nur beschreiben, was beschlossen wurde — keine Spekulation ueber kuenftige Schritte.

Strategische Einordnung (Schlussabsatz, 4-6 Saetze): Bezug auf die strategische Asset-Allokation der Mandanten — die in den Anlagerichtlinien bei Banken und Vermoegensverwaltern hinterlegten Zielquoten (Aktien-, Anleihe-, Edelmetall-, Liquiditaetsquote). Einordnen, ob die Entwicklungen Anlass geben, Quoten zu ueberpruefen, oder ob die Ausrichtung weiterhin angemessen erscheint. Sachlich, kein Handlungsdruck. Beispielton: "Die Entwicklungen des Quartals bestaetigen die Bedeutung einer breit diversifizierten Aufstellung. Die bestehenden Zielquoten erscheinen weiterhin angemessen. Das gestiegene Renditeniveau bei Anleihen und die erhoehte Volatilitaet bei Edelmetallen sind Aspekte, die wir in den kommenden Strategiegespraechen eroertern werden."

### Redaktionsregeln

Keine Handlungsempfehlungen, keine imperativen Formulierungen (muss, soll, zwingend), keine wertenden Begriffe wie "Marschrichtung", "Loesung", "alternativlos". Keine Formulierungen, die kurzfristigen Handlungsdruck suggerieren. Keine Einzelwerte oder Unternehmensnamen. Nur sektorale, regionale oder indexbasierte Begriffe. Keine Szenarioanalysen, Prognosen oder "Was waere wenn"-Passagen. Keine Quellenangaben, Fussnoten oder Verweise auf Analysten/Haeuser. Keine administrativen oder steuerlichen Themen. Wirtschaftsraum immer benennen — nie "die Inflation lag bei..." ohne Region. Fachbegriffe im Kontext erlaeutern, nicht belehrend.

### Selbstpruefung

Vor Ausgabe jeden Satz pruefen: Versteckte Empfehlung? Handlungsdruck? Fehlende Region bei Zahlen? Unternehmensname? Falls ja — umformulieren.

## When to Use

Triggere diesen Skill, wenn der quartalsweise Marktrueckblick fuer die Mandanten erstellt werden soll. Begriffe: "Quartals-Marktbericht", "Marktrueckblick Q2", "Marktbericht fuer die Mandanten", "quartalsweiser Marktbericht", "Quartalsrueckblick Maerkte". Abgrenzung: fuer mandantenspezifisches Portfolio-Reporting den Skill `reporting-entwurf` verwenden, fuer kurze interne Stichpunkt-Briefings den Skill `marktbeobachtung-briefing`. Dieser Skill liefert den mandantenfaehigen Fliesstext-Marktrueckblick ohne Portfoliobezug.

## Procedure

1. Klaere die Berichtsparameter: Quartal und Jahr sowie die bereitgestellten Quellen (hochgeladene Marktdaten, Research-Berichte, Hauswissen). Fehlen Quellen, aktiv nachfragen und optional eine Deep-Research-Recherche zum Marktgeschehen des Quartals anbieten (siehe Skill `recherche-modus`, Tool `trigger_research`) — niemals ungefragt einen Deep-Research-Lauf starten.
2. Verfasse den Bericht streng nach dem Redaktionsleitfaden (siehe unten): Fliesstext, ca. 2 DIN-A4-Seiten (800-1.000 Woerter), kurze Absaetze mit Zwischenueberschriften, Struktur Einleitung, Gesamtwirtschaftliches Umfeld, Kapitalmaerkte im Rueckblick, Zins- und Geldpolitik, Strategische Einordnung.
3. Konkrete Zahlen nur uebernehmen, wo sie in den Quellen belegt sind. Niemals Werte erfinden, schaetzen oder aus dem Modellwissen extrapolieren — fehlende Daten beim Mitarbeiter nachfragen.
4. Fuehre die Selbstpruefung durch: jeden Satz auf versteckte Empfehlung, Handlungsdruck, fehlende Region bei Zahlen und Unternehmensnamen pruefen; bei Treffer umformulieren.
5. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Tonalitaet, Datums- und Zahlenformat, Standard-Disclaimer nach dem Schlussabsatz. Abweichend vom Hausstandard gilt hier: KEIN Quellen-Block und keine Fussnoten im Bericht — die Redaktionsregeln dieses Skills gehen vor.
6. Lege den Entwurf per `manage_documents action=create` mit Titel `Marktbericht Q<x> <Jahr>` als Draft ab und uebergebe ihn dem Mitarbeiter zur Freigabe. Explizit kennzeichnen: "Entwurf — vor Versand pruefen".

## Pitfalls

- Keine Handlungsempfehlungen, keine imperativen Formulierungen (muss, soll, zwingend), keine wertenden Begriffe wie "Marschrichtung", "Loesung", "alternativlos" und keine Formulierungen, die kurzfristigen Handlungsdruck suggerieren.
- Keine Einzelwerte oder Unternehmensnamen — nur sektorale, regionale oder indexbasierte Begriffe (z.B. "Technologiesektor", "europaeische Standardwerte").
- Keine Szenarioanalysen, Prognosen oder "Was waere wenn"-Passagen; bei der Geldpolitik nur beschreiben, was beschlossen wurde, keine Spekulation ueber kuenftige Schritte.
- Keine Quellenangaben, Fussnoten oder Verweise auf Analysten oder Haeuser im Berichtstext — einzige Ausnahme ist der Standard-Disclaimer am Ende.
- Wirtschaftsraum bei jeder Kennzahl benennen — nie "die Inflation lag bei..." ohne Region; Eurozone-Daten haben Vorrang.
- Keine administrativen oder steuerlichen Themen aufnehmen.
- Deutsche Zahlennotation mit Komma als Dezimaltrennzeichen verwenden.
- Der Bericht ist NIEMALS versandfertig — Skill liefert Stufe-2-Output (Entwurf mit Freigabe).

## Verification

- Umfang ca. 800-1.000 Woerter reiner Fliesstext; keine Aufzaehlungen, Tabellen oder Fussnoten; kurze Absaetze mit Zwischenueberschriften.
- Alle fuenf Strukturteile vorhanden: Einleitung, Gesamtwirtschaftliches Umfeld, Kapitalmaerkte im Rueckblick, Zins- und Geldpolitik, Strategische Einordnung.
- Der Schlussabsatz (4-6 Saetze) bezieht sich auf die strategische Asset-Allokation der Mandanten und ordnet sachlich ein, ohne Handlungsdruck.
- Selbstpruefung durchgefuehrt: keine versteckten Empfehlungen, kein Handlungsdruck, keine Zahl ohne Region, keine Unternehmensnamen.
- Alle konkreten Zahlen sind durch die bereitgestellten Quellen gedeckt.
- Standard-Disclaimer des Hausstandards ist nach dem Schlussabsatz enthalten; kein Quellen-Block, keine Fussnoten.
- Dokument liegt als Draft im Library/Documents mit Vermerk "Entwurf — vor Versand pruefen".
