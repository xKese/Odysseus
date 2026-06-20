---
name: recherche-modus
description: "Definiert den Recherchemodus fuer alle Analyse- und Reporting-Skills von Meeder und Seifer: Schnellanalyse (ohne Deep Research, nur Upload-Dokumente) oder Tiefenanalyse (mit Deep Research, externe Validierung). Wird von fonds-analyse, aktien-analyse, investment-opportunity-analyse, reporting-entwurf, reporting-begleittext, termin-vorbereitung und anlageausschuss-vorbereitung referenziert."
version: 1.0.0
category: m-und-s
tags: [recherche, deep-research, modus, analyse, m-und-s]
status: published
confidence: 0.9
source: imported
owner: kese
shared: true
created: "2026-06-19T00:00:00Z"
---

## When to Use

Dieser Skill ist die gemeinsame Definition des Recherchemodus. Er wird von den Analyse- und Reporting-Skills im Procedure-Schritt "Recherchemodus klaeren" referenziert und legt fest, wie tief eine Analyse extern recherchiert. Direkt aufrufbar, wird aber normalerweise nicht eigenstaendig getriggert, sondern aus einem Fach-Skill heraus angewendet.

## Procedure

1. Zu Beginn jeder Analyse den Recherchemodus klaeren: **Schnellanalyse** (ohne Deep Research) oder **Tiefenanalyse** (mit Deep Research). Wenn der Nutzer den Modus nicht ausdruecklich nennt, NACHFRAGEN — niemals ungefragt einen Deep-Research-Job starten.
2. Den gewaehlten Modus im Kopf des Outputs vermerken (z.B. "Recherchemodus: Tiefenanalyse mit Deep Research, Stichtag TT.MM.JJJJ").
3. Die Datenbasis gemaess dem gewaehlten Modus zusammenstellen (siehe body_extra).
4. Bei Tiefenanalyse jede extern recherchierte Aussage klar als Deep-Research-Befund markieren und von den Upload-Daten trennen.

## Pitfalls

- Niemals ungefragt in den Tiefenanalyse-Modus wechseln — Deep Research ist ein asynchroner, laengerer und ressourcenintensiver Lauf. Erst nachfragen.
- Im Schnellmodus KEIN `trigger_research` verwenden — nicht belegte Werte bleiben `(nicht ausgewiesen)`, statt sie extern zu ergaenzen.
- Bei Tiefenanalyse niemals Upload-Daten und Deep-Research-Befunde vermischen, ohne die Quelle zu kennzeichnen — der Pruefer muss sehen, was aus dem Originaldokument stammt und was extern ergaenzt wurde.
- Deep-Research-Befunde unterliegen der Quellenpflicht: jede Aussage mit Quelle und Stichtag. Ohne Quelle nicht uebernehmen.
- Der Recherchemodus ist unabhaengig von der Ausfuehrlichkeitsstufe (Kurzuebersicht/Detailanalyse/Vergleich). Beide Achsen getrennt erheben, nicht verwechseln.

## Verification

- Der Recherchemodus wurde geklaert (bei fehlender Angabe wurde nachgefragt) und im Output vermerkt.
- Im Schnellmodus wurde kein Deep-Research-Job gestartet.
- Im Tiefenmodus sind Deep-Research-Befunde als solche markiert, mit Quelle und Stichtag belegt und von den Upload-Daten getrennt.

### Modus A — Schnellanalyse (ohne Deep Research)

- **Datenbasis**: ausschliesslich hochgeladene Dokumente (Factsheet, Geschaeftsbericht, Pitchdeck, Reporting) plus optional einzelne gezielte `web_fetch`-Abrufe auf eine konkret benannte Quelle (z.B. Investor-Relations-Seite, Anbieter-Seite).
- **Kein** `trigger_research`.
- Nicht im Dokument belegte Werte bleiben `(nicht ausgewiesen)` — sie werden NICHT extern ergaenzt.
- Schnell (Sekunden bis Minute). Geeignet als Vorfilter, fuer den schnellen Ueberblick oder wenn die Unterlagen vollstaendig sind.

### Modus B — Tiefenanalyse (mit Deep Research)

- Zusaetzlich zu den Upload-Dokumenten ein `trigger_research`-Lauf mit eng gefasster, konkreter Forschungsfrage. Nach Abschluss den Bericht ueber `manage_research action=read` lesen und einarbeiten.
- **Zweck** (je nach Fach-Skill unterschiedlich): unabhaengige Validierung der im Dokument genannten Kennzahlen, Track-Record-/Reputations-/Negativ-Recherche, Markt-/Peer-/Wettbewerbskontext, Ergaenzung typisch fehlender Kennzahlen aus unabhaengigen Quellen.
- **Quellenpflicht**: jede ergaenzte Aussage mit Quelle und Stichtag. Im Output klar trennen, was aus den Upload-Unterlagen stammt und was aus der Deep Research — Marker `(Deep Research: <Quelle>, <Stichtag>)`.
- Dem Nutzer mitteilen, dass Deep Research ein asynchroner Job ist und laenger dauert.
- Geeignet fuer Anlageausschuss-Vorlagen, groessere Tickets, illiquide Deals mit hohem Pruefbedarf.

### Grundsatz

Der Recherchemodus ist **orthogonal** zur Ausfuehrlichkeitsstufe — frei kombinierbar (z.B. Detailanalyse Stufe 2 mit Tiefenanalyse, oder Kurzuebersicht Stufe 1 mit Schnellanalyse). Wenn der Nutzer nur eine der beiden Achsen nennt, die andere erfragen.

Die Skills `marktbeobachtung-briefing` und `research-assistent` sind per Definition immer Tiefenanalyse (sie basieren auf Deep Research) und brauchen daher keine Modus-Wahl.
