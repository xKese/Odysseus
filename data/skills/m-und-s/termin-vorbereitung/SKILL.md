---
name: termin-vorbereitung
description: "Bereitet einen Mandantentermin vor: sammelt Mandantenakte (Portfolio, letzte Reports, freigegebene Anschreiben), identifiziert offene Punkte und baut eine Briefing-Mappe mit Gespraechsleitfaden. Verbindet sie als Vorbereitungs-Dokument mit der Sitzung."
version: 1.0.0
category: m-und-s
tags: [termin, mandantentermin, vorbereitung, briefing, m-und-s]
status: published
confidence: 0.85
source: imported
shared: true
created: 2026-06-19T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn ein Mandantengespraech oder Termin vorbereitet werden soll. Trigger-Begriffe: "Termin vorbereiten", "Briefing fuer Mandant X", "Gespraechsleitfaden", "was bespreche ich morgen mit ...", "Termin-Mappe", "Erstgespraech Mandant". Verwende NICHT fuer Anlageausschuss-Sitzungen — dafuer ist `anlageausschuss-vorbereitung`.

## Procedure

1. Klaere den Termin: Mandantenname, Datum/Uhrzeit, Ort, Anlass. Wenn die Sitzung noch nicht angelegt ist, lege sie an via `app_api action=call method=POST path=/api/meetings body={"title": "Termin <Mandantenname> <TT.MM.JJJJ>", "meeting_date": "YYYY-MM-DDTHH:MM:00", "location": "...", "attendees": [...], "meeting_type": "mandant", "mandant_name": "<Mandantenname>"}`.
2. Sammle die Mandantenakte:
   - Aktuellste Portfolio-Aufbereitung des Mandanten (`portfolio-aufbereitung`-Skill bzw. `app_api method=GET path=/api/portfolios` zur Mandantensuche).
   - Letzte freigegebene Reportings und Anschreiben aus `/api/documents/library?release_status=released` mit Mandantenbezug.
   - Marktbeobachtungs-Briefings des relevanten Zeitraums.
   - Bei Bedarf Hauswissen-Suche zu Mandantenrichtlinien.
3. Identifiziere offene Punkte: Welche Themen sind seit dem letzten Kontakt aufgekommen? Was steht in der Mandanten-Korrespondenz noch ungeklaert? Nutze ggf. `hauswissen-suche` fuer den Hausstandard zu Vorgehensweisen.
4. Erstelle die Briefing-Mappe als Markdown-Dokument mit den Abschnitten:
   - Kopf: Mandant, Termin (Datum, Uhrzeit, Ort), Teilnehmer, Anlass.
   - Kurzprofil: Mandantenuebersicht, Anlagestrategie, Risikoprofil.
   - Portfolio-Stand: Gesamtwert, Allokation, wesentliche Veraenderungen seit letztem Kontakt.
   - Performance & Markt: Kurze Erlaeuterung der Performance seit letztem Termin, Markteinordnung.
   - Offene Punkte: Liste der zu besprechenden Themen mit Hintergrund je Punkt.
   - Gespraechsleitfaden: Vorgeschlagene Reihenfolge der Themen, Schluesselfragen.
   - Naechste Schritte: Was sollte aus dem Termin folgen?
5. Lege die Mappe per `manage_documents action=create` mit Titel `Briefing Mandant <Name> <TT.MM.JJJJ>` an, `release_status=draft`.
6. Verknuepfe das Document mit der Sitzung als Vorbereitungs-Dokument: `app_api action=call method=POST path=/api/meetings/{meeting_id}/prepare body={"document_id": "<doc_id>"}`.
7. Wende den Hausstandard an (siehe `m-und-s-hausstandard`): Tonalitaet, Datums- und Zahlenformat, Quellenangabe bei Marktaussagen.

## Pitfalls

- Niemals Anlageempfehlungen vorwegnehmen — die Briefing-Mappe ist Vorbereitung, kein Beratungsprotokoll. Der Mitarbeiter spricht im Termin mit dem Mandanten und entscheidet gemeinsam mit ihm.
- Mandantendaten sind streng vertraulich. Vor Aufruf pruefen, dass der Aufrufer das Mandat betreut (Owner-Filter respektieren).
- Performance-Veraenderungen seit letztem Kontakt klar mit Stichtag belegen; keine "ueberschlaegigen" Zahlen.
- Offene Punkte aus Mandanten-Korrespondenz koennen sensibel sein (z.B. Lebensereignisse, Liquiditaetsbedarf). Direkt benennen, aber Diskretion wahren — keine Spekulation.
- Bei Erstgespraechen (Onboarding) Mandantenkenntnisse koennen luekenhaft sein — `onboarding-unterstuetzung` als Begleit-Skill triggern.
- Termin-Vorbereitungen sind Stufe-1-Output (Assistenz, nicht Vorschlag mit Freigabe) — der Mitarbeiter nutzt sie als Arbeitsgrundlage, nicht als Freigabe-Entwurf.

## Verification

- Briefing-Mappe enthaelt Kopf (Mandant, Termin, Teilnehmer, Anlass), Kurzprofil, Portfolio-Stand, Performance & Markt, offene Punkte, Gespraechsleitfaden, naechste Schritte.
- Portfolio-Zahlen sind mit Stichtag belegt.
- Offene Punkte sind aus konkreten Quellen (letzte Anschreiben, Mandanten-Korrespondenz, Hauswissen) abgeleitet, nicht erfunden.
- Sitzung im `meetings`-Modell mit `meeting_type=mandant` und korrekt gesetztem `mandant_name`.
- Mappe ist als `preparation_document_id` an der Sitzung verknuepft.
- Hausstandard angewendet (Datumsformat, Tonalitaet).
- Hinweis "Vorbereitung — interner Gebrauch" am Anfang.
