---
name: linkedin-post-entwurf
description: "Verfasst einen LinkedIn-Post-Entwurf fuer Meeder und Seifer nach Hausstandard — fuer das persoenliche Profil (Ich-Perspektive) oder die Unternehmensseite (Wir-Perspektive) — als Entwurf zur Freigabe, ohne direkte Veroeffentlichung."
version: 1.0.0
category: m-und-s
tags: [linkedin, social-media, schriftverkehr, m-und-s]
status: published
confidence: 0.8
source: imported
owner: kese
shared: true
created: "2026-06-20T00:00:00Z"
---

## When to Use

Triggere diesen Skill, wenn ein LinkedIn-Beitrag, Social-Media-Post oder eine oeffentliche Kurzmitteilung entworfen werden soll. Begriffe: "LinkedIn-Post", "Beitrag fuer LinkedIn", "Post fuer die Unternehmensseite", "etwas auf LinkedIn teilen", "Social-Media-Beitrag", "Marktkommentar fuer LinkedIn", "Ankuendigung fuer LinkedIn". Der Skill erstellt ausschliesslich Entwuerfe — das Veroeffentlichen erfolgt manuell durch den Mitarbeiter.

## Procedure

1. Klaere die Pflichtfelder: **Account-Typ** (persoenliches Profil = Ich-Perspektive ODER Meeder-und-Seifer-Unternehmensseite = Wir-Perspektive), Anlass/Thema, Kernbotschaft, gewuenschte Laenge, optionaler Call-to-Action. Frage gezielt nach, falls ein Feld fehlt — insbesondere den Account-Typ niemals raten.
2. Klaere den Recherchemodus (siehe Skill `recherche-modus`): Schnellanalyse (nur vorhandene Angaben, kein Deep Research) oder Tiefenanalyse (mit `trigger_research` und Quellenpflicht). Niemals ungefragt einen Deep-Research-Job starten.
3. Wende den Hausstandard an (siehe `m-und-s-hausstandard`): sachlich-professionelle Tonalitaet, Begriff "Mandant" statt "Kunde", Datumsformat TT.MM.JJJJ, Zahlenformat 1.234.567,89 EUR. Tonalitaet je nach Account-Typ: persoenliches Profil hoeflich-persoenlich in Ich-Form; Unternehmensseite formeller in Wir-Form (Meeder und Seifer).
4. Verfasse den Post LinkedIn-gerecht: praegnanter Hook in der ersten Zeile, kurze Absaetze, klare Struktur, ein konkreter Gedanke pro Post. Hashtags sparsam und nur mit Bezug ans Ende. Sichtbare Laenge vor dem "mehr anzeigen" beachten (ca. 1.300 Zeichen).
5. Lege den Entwurf per `manage_documents action=create` mit Titel `LinkedIn-Post <Account-Typ> <TT.MM.JJJJ>` ab und uebergib ihn dem Mitarbeiter zur Freigabe.
6. Schreibe explizit "Entwurf — vor Veroeffentlichung pruefen" oben in den Chat-Hinweis, damit der Mitarbeiter den Text nicht ungeprueft veroeffentlicht.

## Pitfalls

- Keine konkrete Anlageberatung oder Anlageempfehlung im Post (kein "kaufen Sie X", keine ISIN-/Titel-Tipps) — eine BaFin-regulierte Vermoegensverwaltung darf oeffentlich keine individuelle Empfehlung aussprechen.
- Posts der Unternehmensseite sind Werbemitteilungen im Sinne des WpHG: ausgewogen, nicht irrefuehrend, keine Rendite- oder Erfolgsversprechen; bei Bedarf als Werbung kenntlich machen und einen Standard-Disclaimer bzw. Quellenvermerk beifuegen.
- Keine vertraulichen Mandanten-, Portfolio- oder Performancedaten und keine Namen ohne ausdrueckliche Freigabe verwenden.
- Account-Perspektive nicht vermischen: persoenliches Profil bleibt in Ich-Form, Unternehmensseite in Wir-Form.
- Hashtags nicht inflationaer einsetzen; lieber drei treffende als zehn beliebige.
- Bei Marktaussagen oder Zahlen Stichtag und Quelle benennen; im Tiefenmodus Deep-Research-Befunde als solche markieren (siehe `recherche-modus`).

## Verification

- Account-Typ und Perspektive (Ich/Wir) sind eindeutig geklaert und durchgaengig eingehalten.
- Recherchemodus wurde geklaert (bei fehlender Angabe nachgefragt) und im Output vermerkt.
- Hausstandard angewendet (Begriffe, Tonalitaet, Datums- und Zahlenformat).
- Keine konkrete Anlageempfehlung enthalten; bei der Unternehmensseite ist der Werbe-/Disclaimer-Hinweis vorhanden.
- Entwurf liegt als Dokument (`draft`) im Library/Documents.
- Hinweis "Entwurf — vor Veroeffentlichung pruefen" steht im Chat.
