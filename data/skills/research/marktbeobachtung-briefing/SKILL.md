---
name: marktbeobachtung-briefing
description: "Erstellt ein taegliches oder woechentliches Markt- und Nachrichten-Briefing fuer das Team von Meeder und Seifer. Kombiniert Deep-Research-Recherche mit der M&S-Briefing-Vorlage. Kann manuell ausgeloest oder zeitgesteuert als geplante Aufgabe laufen."
version: 1.0.0
category: research
tags: [briefing, marktbeobachtung, deep-research, m-und-s]
status: published
confidence: 0.85
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Verwende diesen Skill, wenn ein zusammenfassendes Markt- oder Themen-Briefing erstellt werden soll — entweder ad hoc auf Zuruf ("erstell mir das taegliche Briefing zu europaeischen Anleihen") oder als geplante Aufgabe (taeglich morgens, wochenend-Wrap-up). Der Skill liefert immer ein strukturiertes Markdown-Briefing nach M&S-Vorlage mit Quellen.

## Procedure

1. Klaere die Briefing-Parameter: Themenfeld (z.B. "europaeische Anleihen", "Tech-Aktien USA", "Gold und Edelmetalle"), Zeitraum (gestern, letzte Woche, letzter Monat), Zielgruppe (intern / Mandanten-Briefing). Bei wiederkehrenden Briefings die im Skill-Body genannte Standard-Konfiguration verwenden.
2. Starte ueber das Tool `trigger_research` eine Recherche mit der konsolidierten Frage, z.B. "Was war in der vergangenen Woche relevant fuer europaeische Anleihen? Marktdaten, Notenbank-Aussagen, Emittenten-Nachrichten, regulatorische Aenderungen — mit Quellen."
3. Lies den fertigen Recherchebericht aus dem Research-Verlauf und destilliere ihn auf die fuenf wichtigsten Befunde plus Stimmungsbild.
4. Fuelle die M&S-Briefing-Vorlage aus `data/templates/briefings/markt-briefing.md` (oder verwende das Skelett aus dem body_extra). Achte auf Kuerze: maximal eine Seite, Stichpunkte vor Fliesstext.
5. Haenge den vollstaendigen Quellen-Block an und wende den Hausstandard an (siehe `m-und-s-hausstandard`).
6. Speichere das Briefing per `manage_documents action=create` mit Titel `Markt-Briefing <Themenfeld> <TT.MM.JJJJ>` zur Freigabe. Wenn der Aufruf aus einer geplanten Aufgabe (ScheduledTask, `task_type=llm`) kommt, das Document IMMER mit `release_status=draft` anlegen — der Mitarbeiter prueft am naechsten Werktag.

Hinweis fuer den Admin: Wiederkehrendes Briefing einplanen via `app_api action=call method=POST path=/api/tasks/schedule-skill body={"skill_slug": "marktbeobachtung-briefing", "arguments": "Themenfeld: europaeische Anleihen", "schedule": "daily", "scheduled_time": "08:00"}`. Der Endpoint baut einen ScheduledTask mit dem passenden Slash-Befehl.

## Pitfalls

- Briefings duerfen nicht spekulieren — nur Befunde mit Quelle. Bei "der Markt erwartet..." immer die Quelle des Marktkonsens nennen (z.B. "laut Bloomberg-Konsens", "laut Reuters-Umfrage").
- Bei Marktdaten Stichzeit und Quelle ausweisen (z.B. "10-Jahres-Bund Rendite 2,34 Prozent, Stand 16.06.2026 17:30 Uhr, Reuters").
- Geplante Aufgaben: Wenn die Recherche keine relevanten neuen Befunde liefert (Wochenende, Feiertag), das Briefing trotzdem mit kurzer Notiz "keine wesentlichen Bewegungen" und Stichzeit ausgeben — nicht stillschweigend auslassen.
- Mandantenbriefings benoetigen zusaetzlich Freigabe — Skill liefert nur Entwurf.

## Verification

- Briefing-Laenge: maximal eine Bildschirmseite (ca. 30 Zeilen Markdown).
- Fuenf bis sieben Stichpunkte als Hauptbefunde, danach optional kurze Detail-Erlaeuterung.
- Quellen-Block am Ende mit nummerierten Eintraegen und Stichzeit.
- Hausstandard angewendet (Datumsformat, Disclaimer bei anlagerelevanten Inhalten).
- Bei Mandanten-Briefings explizit Vermerk "Entwurf — vor Versand pruefen".

```
# Markt-Briefing: <Themenfeld>
*Stichtag: <TT.MM.JJJJ>, <HH:MM Uhr>*
*Zielgruppe: intern / Mandanten-Entwurf*

- <Befund 1> [1]
- <Befund 2> [2]
- <Befund 3> [3]
- <Befund 4> [4]
- <Befund 5> [5]

<Kurzer Absatz, 3-5 Saetze>

| Indikator | Wert | Veraenderung | Stichzeit |
|---|---|---|---|
| ... | ... | ... | ... |

1. ...
2. ...

<Disclaimer aus Hausstandard, falls anlagerelevant>
```
