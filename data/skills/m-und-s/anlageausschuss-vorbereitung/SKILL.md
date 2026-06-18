---
name: anlageausschuss-vorbereitung
description: "Stellt die Sitzungsmappe fuer den Anlageausschuss zusammen: Tagesordnung, freigegebene Reports und Briefings, Beschlussvorschlaege \u2014 als Document zur Freigabe und an die Sitzung gebunden."
version: 1.0.0
category: m-und-s
tags: [anlageausschuss, sitzung, vermoegensverwaltung, m-und-s]
status: published
confidence: 0.85
source: imported
owner: kese
shared: true
created: "2026-06-18T00:00:00Z"
---

## When to Use

Triggere diesen Skill, wenn eine Anlageausschuss-Sitzung vorbereitet werden soll. Begriffe: "Anlageausschuss vorbereiten", "Sitzungsmappe", "Tagesordnung", "Sitzung am ... vorbereiten", "Unterlagen fuer Anlageausschuss", "Beschlussvorlage". Auch nach Anlage einer neuen Sitzung im Sitzungs-Panel verwendbar.

## Procedure

1. Klaere die Sitzung: Datum, Titel, Teilnehmer. Wenn die Sitzung noch nicht existiert, lege sie an via `app_api action=call method=POST path=/api/meetings body={"title": "Anlageausschuss <TT.MM.JJJJ>", "meeting_date": "YYYY-MM-DDTHH:MM:00", "location": "...", "attendees": [...]}`.
2. Sammle die fuer die Sitzung relevanten Reports und Briefings:
3. Marktbeobachtungs-Briefings der letzten Woche (`app_api action=call method=GET path=/api/documents/library?release_status=draft` und nach Titel filtern)
4. Aktuelle Reporting-Entwuerfe und Portfolio-Aufbereitungen
5. Freigegebene Hauswissen-Dokumente zur Anlagepolitik (`hauswissen-suche` ggf. nutzen)
6. Identifiziere Beschlussbedarf: Welche Allokations-, Mandanten- oder Strategiethemen brauchen eine Entscheidung? Formuliere je Punkt einen kurzen Tagesordnungs-Eintrag.
7. Erstelle die Sitzungsmappe als Markdown-Dokument mit Abschnitten:
8. Kopf: Sitzungstitel, Datum, Ort, Teilnehmer
9. Tagesordnung (nummerierte Liste)
10. Vorab-Berichte (Liste der angehaengten Dokumente, mit Status und Freigeber)
11. Beschlussvorlagen (je Punkt: Sachverhalt, Optionen, Empfehlung)
12. Naechste Sitzung (Datum-Vorschlag)
13. Lege die Sitzungsmappe per `manage_documents action=create` mit Titel `Sitzungsmappe Anlageausschuss <TT.MM.JJJJ>` an. ``release_status=draft``.
14. Haenge das Document an die Sitzung als Protokollvorbereitung: `app_api action=call method=POST path=/api/meetings/{meeting_id}/documents body={"document_id": "<doc_id>", "role": "protocol"}`. Weitere Vorab-Berichte mit `role="decision"` ebenfalls verknuepfen.
15. Wende den Hausstandard an (siehe `m-und-s-hausstandard`): Tonalitaet, Datum-/Zahlenformat, Disclaimer.

## Pitfalls

- Nur freigegebene oder im Entwurfsstatus klar markierte Dokumente in die Sitzungsmappe aufnehmen. Wenn eine zentrale Vorlage fehlt, das im Mappen-Kapitel "Ungeklaerte Punkte" festhalten — kein stillschweigendes Auslassen.
- Beschlussvorlagen muessen Optionen explizit aufzeigen, keine versteckte Empfehlung. Eine Empfehlung am Ende des Punkts ist erlaubt, aber sie muss als Empfehlung gekennzeichnet sein, nicht als Tatsache.
- Anlageentscheidungen verbleiben in menschlicher Verantwortung. Der Skill erstellt die Vorbereitungs-Unterlagen; die Entscheidung trifft der Ausschuss.
- Mandantenbezogene Beschluesse niemals ohne explizite Mandanten-Berechtigung des Aufrufers ausgeben — Owner-Filter respektieren.
- Wenn die Sitzung bereits den Status `held` oder `protocol` hat, vor dem Anlegen einer neuen Sitzungsmappe pruefen, ob das gewuenscht ist (sonst Protokoll-Workflow waehlen).

## Verification

- Sitzungsmappe enthaelt Kopf (Titel, Datum, Ort, Teilnehmer), Tagesordnung, Vorab-Berichte, Beschlussvorlagen, naechste Sitzung.
- Jeder Tagesordnungs-Punkt hat eine Sachverhaltskurzbeschreibung plus Beschlussvorschlag oder Diskussionspunkt.
- Vorab-Berichte sind als Document-Liste mit Status und Freigeber gefuehrt.
- Sitzungsmappe ist an die Sitzung via Meeting-Endpoint gebunden (`role=protocol`).
- Hausstandard angewendet (Datumsformat, Disclaimer).
- Status `release_status=draft` und Hinweis "Entwurf — vor Sitzung pruefen" am Anfang.
