---
name: reporting-begleittext
description: "Erstellt einen verstaendlichen Begleittext zu einem freigegebenen Mandanten-Reporting: Performance-Erklaerung in einfacher Sprache, wesentliche Portfolio-Veraenderungen, Marktkommentar und Ausblick. Output als Document zur Freigabe."
version: 1.0.0
category: m-und-s
tags: [reporting, begleittext, kundenkommunikation, m-und-s]
status: published
confidence: 0.85
source: imported
shared: true
created: 2026-06-19T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn ein Begleittext zu einem Mandanten-Reporting (Quartals-, Monats- oder Jahresbericht) erstellt werden soll. Trigger-Begriffe: "Reporting-Begleittext", "Begleittext zum Bericht", "erklaer dem Mandanten das Reporting", "verstaendliche Erlaeuterung Quartalsbericht", "Begleitschreiben zum Reporting", "kommentar zum Reporting". Verwende NICHT, um den Bericht selbst zu erzeugen — dafuer ist `reporting-entwurf`.

## Procedure

1. Identifiziere das Quell-Reporting: der jueengste `reporting-entwurf`-Output mit `release_status=released` (oder vom Nutzer benannt). Hole es per `app_api action=call method=GET path=/api/documents/library?release_status=released` und filtere nach Titel und Mandant. Wenn unklar welche Mandantenbeziehung: nachfragen.
2. Hole den passenden Portfolio-Snapshot zur gleichen Stichtag (`portfolio-aufbereitung`-Skill oder direkt `app_api action=call method=GET path=/api/portfolios/{id}/snapshots`). Stelle sicher, dass Stichtag und Berichtsperiode uebereinstimmen.
3. Sammle die Marktbeobachtungs-Briefings des Berichtszeitraums via `app_api action=call method=GET path=/api/documents/library?release_status=released` mit Filter auf "Markt-Briefing". Wenn keine Briefings vorhanden: kurzer eigener Marktrueckblick auf Basis Hauswissen, ohne Spekulation.
4. Formuliere den Begleittext in drei Abschnitten:
   - **Performance-Erlaeuterung**: Wertentwicklung in der Berichtsperiode in einfacher Sprache (keine Fachbegriffe ohne Erklaerung), mit Zahlen aus dem Reporting belegt.
   - **Portfolio-Veraenderungen**: Wesentliche Allokations-Aenderungen, Zu-/Verkaeufe, Dividenden, Zinseinnahmen — kurz und konkret, nicht jede Buchung.
   - **Marktkommentar und Ausblick**: 3-5 Saetze zur Markteinordnung, mit Quellen aus Marktbeobachtungs-Briefings. Bewusst nuechtern; kein Werbeton.
5. Tonalitaet: kundenfreundlich, hoeflich-distanzierte Anrede (Sie), kurze Saetze. Fachbegriffe nur, wenn sie im Mandantenstandard etabliert sind ("Allokation", "Volatilitaet") — sonst umschreiben.
6. Lege den Begleittext per `manage_documents action=create` mit Titel `Begleittext <Mandant> <Quartal/Monat> <Jahr>` als Document mit `release_status=draft` an. Hinweis "Entwurf — vor Versand pruefen" am Anfang.
7. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Anrede, Datumsformat, Disclaimer als Fusszeile, Quellenangabe.

## Pitfalls

- Performance-Zahlen NIE schaetzen oder runden — aus dem Quell-Reporting wortwoertlich uebernehmen mit Stichtag.
- Keine impliziten Anlageempfehlungen ("aussichtsreich", "vielversprechend") — der Skill liefert Befund und Erklaerung, keine Beratung.
- Negative Performance offen ansprechen, nicht beschoenigen. Sachlich erklaeren, ohne Schuldzuweisungen oder Schwarzmalerei.
- Marktkommentar braucht Quelle (Marktbeobachtungs-Briefing, Bloomberg, Reuters). Ohne Quelle keine Marktaussagen — lieber den Block schlanker halten.
- Bei Mandanten mit besonderem Kontext (Lebensereignisse, Liquiditaetsbedarf) den Ton entsprechend anpassen — vorab mit dem betreuenden Mitarbeiter abklaeren, wenn unklar.
- Disclaimer aus Hausstandard NIE weglassen — auch bei kurzen Begleittexten.
- Skill ist Stufe 2 (Vorschlag mit Freigabe). Niemals Versandbereitschaft suggerieren — der Mitarbeiter gibt frei und versendet selbst.

## Verification

- Begleittext enthaelt die drei Abschnitte Performance-Erlaeuterung, Portfolio-Veraenderungen, Marktkommentar und Ausblick.
- Alle Performance-Zahlen sind aus dem Quell-Reporting wortwoertlich uebernommen und mit Stichtag belegt.
- Marktaussagen haben mindestens eine konkrete Quelle (Briefing oder externer Anbieter).
- Anrede, Datumsformat, Tonalitaet folgen dem Hausstandard.
- Disclaimer als Fusszeile vorhanden.
- Document liegt als `release_status=draft` vor, Hinweis "Entwurf — vor Versand pruefen" am Anfang.
- Negative Performance, falls vorhanden, sachlich und ohne Beschoenigung dargestellt.
