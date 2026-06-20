---
name: onboarding-unterstuetzung
description: "Unterstuetzt das Onboarding eines Neumandats: legt den Prozess an, leitet die Standard-Checkliste je Onboarding-Typ ab, erstellt das Willkommensschreiben und sammelt die noetigen Unterlagen mit Quellenhinweisen."
version: 1.0.0
category: m-und-s
tags: [onboarding, neumandat, checklist, kundenkommunikation, m-und-s]
status: published
confidence: 0.85
source: imported
shared: true
created: 2026-06-19T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn ein Neumandat angenommen wird und der Onboarding-Prozess begleitet werden soll. Trigger-Begriffe: "Onboarding fuer ...", "Neukunde aufnehmen", "Welcome-Mappe", "Neumandat", "Onboarding starten", "Mandat einrichten", "Checkliste Onboarding". Auch nach einem Erstgespraech automatisch nutzbar.

## Procedure

1. Klaere Mandantenname und Onboarding-Typ: `vermoegensverwaltung` (Standard), `family_office` (mit Familienstrukturen, Stiftungen) oder `beratung` (loseres Beratungsmandat ohne Verwaltungsvertrag).
2. Lege den Onboarding-Prozess an: `app_api action=call method=POST path=/api/onboarding body={"mandant_name": "<Name>", "onboarding_type": "vermoegensverwaltung", "target_completion_date": "YYYY-MM-DD"}`. Der Endpoint setzt automatisch eine Default-Checkliste je Typ.
3. Verfeinere die Checkliste falls noetig: `PUT /api/onboarding/{id}` mit `checklist`-Array. Mandantenspezifische Pflichten (z.B. zusaetzliche KYC-Dokumentation, Sondervollmachten) ergaenzen.
4. Ermittle den genauen Unterlagenbedarf je Schritt:
   - Aus Hauswissen-Sammlung "Onboarding-Richtlinien" via `hauswissen-suche` (falls vorhanden) — speziell zu Identifikation, Vertragsmustern, Reportingfrequenz.
   - Bei Family-Office-Onboarding: Familienstruktur und Stiftungen erfragen, konsolidierte Vermoegensuebersicht skizzieren.
5. Erstelle das Willkommensschreiben via `anschreiben-entwurf`-Skill mit Hausvorlage und folgenden Eckdaten: Begruessung, Bestaetigung des Mandates, Ansprechpartner, naechste Schritte (drei bis fuenf konkrete Punkte), Anlagen-Hinweis fuer mitgesandte Dokumente. `release_status=draft`.
6. Verknuepfe das Willkommensschreiben mit dem Onboarding-Prozess: `PUT /api/onboarding/{id}` mit `welcome_document_id: <doc-id>`.
7. Stelle eine Unterlagenliste fuer den Mandanten zusammen (welche Dokumente werden vom Mandanten benoetigt: Ausweis-Kopie, steuerliche Identifikationsnummer, Vorlieben zur Anlagestrategie, etc.) und lege sie als separates Document ab.
8. Lege optional ein Initial-Briefing fuer das Erstgespraech via `termin-vorbereitung`-Skill an, sofern ein Termin schon angesetzt ist.
9. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Anrede, Datumsformat, Disclaimer.

## Pitfalls

- **KYC- und Geldwaesche-Pflichten** sind nicht delegierbar — der Mitarbeiter prueft die Identifikation persoenlich. Der Skill listet nur die Anforderungen.
- Bei Mandanten mit politisch exponierter Position (PEP), in Sanktionslisten oder mit ungewoehnlichem Vermoegenshintergrund: KEIN Standard-Onboarding starten, sondern Compliance-Pruefung erst abwarten.
- Family-Office-Onboardings haben staerker variierende Anforderungen als Standard-Vermoegensverwaltung — die Checkliste ist nur eine Basis, nicht abschliessend.
- Bei minderjaehrigen Mandanten oder Mandanten unter Betreuung zusaetzliche rechtliche Vertretungs-Dokumentation einplanen.
- Willkommensschreiben darf KEINE Versandbereitschaft suggerieren — Stufe 2 (Vorschlag mit Freigabe). Der Mitarbeiter prueft persoenlich.
- Mandantenspezifische sensitive Daten (Lebenssituation, Vermoegenshintergrund) immer im Owner-Scope halten. KEINE Detailweitergabe an andere Mitarbeiter, ausser deren Rolle das explizit zulaesst.
- Onboarding-Prozess als "completed" zu markieren ist nur zulaessig, wenn die formellen Schritte (Identifikation, Verwaltungsvertrag, Depot-Eroeffnung) verifizierbar abgeschlossen sind. KYC-Schritte NIE als "skipped" markieren.

## Verification

- Onboarding-Prozess existiert in der DB mit Mandantenname, Typ und initialer Checkliste.
- Default-Checkliste enthaelt mindestens die KYC-/Identifikations-, Vertrags- und Depot-Schritte fuer den gewaehlten Typ.
- Willkommensschreiben ist als Document mit `release_status=draft` angelegt und mit dem Prozess verknuepft.
- Unterlagenliste fuer den Mandanten ist erstellt und beinhaltet rechtliche und steuerliche Pflichtangaben.
- Hausstandard angewendet (Anrede, Datum, Disclaimer).
- Hinweis "Onboarding gestartet — KYC-Pruefung steht aus" steht in den Notizen, bis die Identifikation bestaetigt ist.

## Detail: Default-Checklisten

Der Endpoint `POST /api/onboarding` setzt automatisch die folgenden Default-Schritte:

**Vermoegensverwaltung (Standard)**
1. Anlegerprofil (WpHG) ausfuellen
2. Identifikation (PostIdent/VideoIdent)
3. Verwaltungsvertrag unterschrieben
4. Depot-/Konto-Eroeffnung bei depotfuehrender Bank
5. Vermoegensueberleitung beauftragt
6. Willkommensschreiben versandt

**Family-Office** (zusaetzlich zu Standard)
- Familienstruktur und Stiftungen erfasst
- Vermoegensuebersicht (Konsolidierung) konsolidiert
- Reportingfrequenz vereinbart

**Beratung** (zusaetzlich zu Standard)
- Beratungsumfang abgegrenzt
- Erstberatungstermin durchgefuehrt

Mandantenspezifische Schritte koennen jederzeit via `PUT /api/onboarding/{id}` (Feld `checklist`) ergaenzt werden.
