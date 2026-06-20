---
name: anschreiben-entwurf
description: "Erstellt ein Mandanten-Anschreiben nach M&S-Hausvorlage als Entwurf zur Freigabe \u2014 von der Anrede bis zur Disclaimer-Fusszeile."
version: 1.0.0
category: m-und-s
tags: [anschreiben, hausvorlage, schriftverkehr, m-und-s]
status: published
confidence: 0.85
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Triggere diesen Skill, wenn ein Anschreiben, Schreiben, Brief, eine schriftliche Mandantenkommunikation oder ein Begleitschreiben entworfen werden soll. Begriffe: "Anschreiben fuer Mandant X", "Brief verfassen", "schick mir den Entwurf fuer den Brief an...", "Begleitschreiben zum Reporting", "Schreiben aufsetzen".

## Procedure

1. Klaere die Pflichtfelder: Mandantenname und Anschrift, korrekte Anrede (Herr/Frau/Damen-und-Herren), Verfasser (Name plus Funktion), Datum, Betreff, Hauptanliegen in Stichworten. Frage gezielt nach, falls ein Feld fehlt.
2. Formuliere den Haupttext: sachlich-professionell, keine Floskeln, keine Anbiederung; Anliegen klar voranstellen, Hintergrund knapp, naechster Schritt (Rueckmeldung, Termin, Anlage) am Ende.
3. Hole die Anschreiben-Vorlage und renderte sie: `app_api action=call method=POST path=/api/templates/anschreiben/standard-mandant/render body={"mandant": {...}, "anrede": "...", "datum": "...", "betreff": "...", "haupttext": "...", "verfasser": {...}}`. Antworten enthalten das gerenderte Markdown plus `missing_placeholders` — Liste der noch offenen Felder explizit zurueckmelden.
4. Wende den Hausstandard an (siehe `m-und-s-hausstandard`): Begriff "Mandant" statt "Kunde", Datumsformat TT.MM.JJJJ, hoeflich-distanzierte Anrede, Disclaimer-Fusszeile.
5. Lege den Entwurf per `manage_documents action=create` mit Titel `Anschreiben <Mandant> <TT.MM.JJJJ>` ab und uebergib ihn dem Mitarbeiter zur Freigabe.
6. Schreibe explizit "Entwurf — vor Versand pruefen" oben in den Chat-Hinweis, damit der Mitarbeiter nicht versucht, das Schreiben ohne Pruefung weiterzuleiten.

## Pitfalls

- Niemals "wir senden Ihnen bei" suggerieren — der Mitarbeiter versendet selbst.
- Bei Anlagen oder Werten im Brief: ISIN/WKN beifuegen, Stichtag explizit benennen.
- Anrede pruefen: bei mehreren Empfaengern (Familienkonten) "Sehr geehrte Damen und Herren," nur wenn der Mitarbeiter dies ausdruecklich bestaetigt — Familien-Mandate haben oft spezielle hauseigene Anreden.
- Bei vertraulichen Inhalten Vermerk "Vertraulich" auf das Schreiben setzen.
- Kein "wir freuen uns sehr" / "wir wuerden uns freuen wenn" — Hausstil ist direkter.

## Verification

- Anrede, Adresse, Datum, Betreff sind vollstaendig oder explizit als `(noch zu ergaenzen)` markiert.
- Vorlage wurde gerendert, `missing_placeholders` wurden zurueckgemeldet.
- Hausstandard angewendet (Begriffe, Tonalitaet, Datumsformat).
- Disclaimer-Fusszeile ist vorhanden.
- Hinweis "Entwurf — vor Versand pruefen" steht im Chat.
- Dokument liegt im Library/Documents als `draft`.
