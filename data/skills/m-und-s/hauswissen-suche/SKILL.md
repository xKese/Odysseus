---
name: hauswissen-suche
description: "Sucht im kuratierten Hauswissen (Anlagerichtlinien, Vorlagen, Prozessbeschreibungen, historische Auswertungen) von Meeder und Seifer. Liefert Antworten mit konkreter Quellenangabe je Sammlung."
version: 1.0.0
category: m-und-s
tags: [hauswissen, rag, m-und-s, knowledge]
status: published
confidence: 0.9
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Triggere diesen Skill, wenn der Nutzer eine Frage zum internen Hauswissen stellt: Anlagerichtlinien, Vorlagen, Prozesse, Compliance-Vorgaben, historische Memos, Hausstandard-Texte. Begriffe: "was sagt unsere Richtlinie zu...", "haben wir intern Material zu...", "wo finde ich die Vorlage fuer...", "wie machen wir das normalerweise mit...", "Hauswissen", "wissensbasis". Bei Externer-Markt-Recherche stattdessen `research-assistent` triggern.

## Procedure

1. Klaere das gesuchte Themenfeld und ob eine bestimmte Sammlung relevant ist (z.B. Anlagerichtlinien, Compliance, Reportingvorlagen). Frage gezielt nach, wenn die Sammlungsangabe fehlt.
2. Liste die verfuegbaren Sammlungen ueber `app_api action=call method=GET path=/api/knowledge/collections`. Zeige Slug, Name und Dokumentanzahl im Chat, wenn der Nutzer unsicher ist.
3. Falls eine Sammlung bekannt ist, suche gezielt: `app_api action=call method=POST path=/api/knowledge/collections/<id>/search body={"query": "<frage>", "k": 5}`. Andernfalls Org-weit ueber `app_api action=call method=POST path=/api/knowledge/search body={"query": "<frage>", "k": 5}` — beide respektieren die Rollen-ACL des aktuellen Nutzers.
4. Analysiere die Treffer: jede Ergebnis-Zeile enthaelt `document` (Text-Chunk) und `metadata.filename` (Quelldokument). Konsolidiere die relevantesten Stellen auf eine knappe Antwort, niemals einfach den Roh-Chunk durchreichen.
5. Antworte mit (a) Kernaussage in 2-4 Saetzen, (b) konkrete Quellenangabe je Aussage (Dateiname plus Sammlung), (c) Hinweis falls die Antwort nicht eindeutig oder zu duenn belegt ist.
6. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Tonalitaet, Datumsformat, Quellen-Block. Bei anlagerelevanten Inhalten den Disclaimer anfuegen.
7. Bei wiederholten Fragen zum gleichen Thema die Sammlung explizit nennen, damit der Nutzer weiss, wo das Wissen kuratiert ist.

## Pitfalls

- Niemals raten oder ergaenzen, wenn die Treffer nichts Brauchbares liefern — explizit sagen, dass das Hauswissen dazu nichts enthaelt, und gegebenenfalls auf `research-assistent` verweisen.
- Bei `403 Keine Berechtigung` keine Workarounds — dem Nutzer mitteilen, dass die Sammlung fuer seine Rolle nicht freigegeben ist; Admin soll ACL pruefen.
- Bei Org-weiter Suche kann es Treffer aus mehreren Sammlungen geben — die Sammlung MUSS in der Quellenangabe genannt werden, damit der Nutzer den Kontext versteht.
- Treffer-Texte sind Chunks (1-2 KB) — keine vollstaendigen Dokumente; bei Bedarf nach dem konkreten Dokument verlangen (per `manage_documents` oder gezielten Folgefragen).
- Antworten zu personenbezogenen Mandantendaten sind streng vertraulich — kein "wir hatten Mandant X mit dem Wertpapier Y" ohne explizite Aufforderung zur Mandanten-Detailansicht und Pruefung der Berechtigung.

## Verification

- Die Antwort enthaelt mindestens eine konkrete Quellenangabe (Dateiname plus Sammlungsname).
- Bei mehreren Treffern aus unterschiedlichen Sammlungen ist die Sammlungszuordnung je Aussage nachvollziehbar.
- Bei leerem Ergebnis ist der Hinweis "Im Hauswissen nichts dazu gefunden" enthalten, plus optional Vorschlag zur externen Recherche.
- Hausstandard angewendet (Datumsformat, ggf. Disclaimer).

```

<Kernaussage in 2-4 Saetzen, mit Quellen-Markern>

**Belege**
- *<Sammlungsname> · <Dateiname>* — kurze Wiedergabe der relevanten Stelle.
- *<Sammlungsname> · <Dateiname>* — ...

<Disclaimer aus Hausstandard, falls anlagerelevant>
```
