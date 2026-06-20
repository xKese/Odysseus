---
name: standardanfrage
description: "Beantwortet wiederkehrende Mandantenanfragen (Kosten, Steuern, Risikoeinstufung, Kuendigung, Auszahlung) aus der M&S-Standardanfragen-Bibliothek. Matched die Frage gegen Stichworte, rendert das Antwort-Template und bereitet einen Anschreiben-Entwurf zur Freigabe vor."
version: 1.0.0
category: m-und-s
tags: [standardanfrage, kundenkommunikation, faq, m-und-s]
status: published
confidence: 0.85
source: imported
shared: true
created: 2026-06-19T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn eine konkrete Mandantenanfrage vorliegt und der Mitarbeiter einen Antwort-Entwurf braucht. Trigger-Begriffe: "wie beantworte ich ...", "Standardanfrage", "Antwort auf Mandantenfrage", "FAQ", "Kostenanfrage Mandant", "Steuerfrage", "Kuendigungsanfrage". Auch automatisch, wenn die Posteingang-Triage (`email`-MCP) eine Mandantenanfrage zu Standardthemen erkennt.

## Procedure

1. Klaere die konkrete Frage des Mandanten — am besten als woertliches Zitat oder zusammengefasster Kern. Mandantenkontext (Name, Mandatsart) festhalten, ohne Mandantendetails ausserhalb des Owner-Scopes preiszugeben.
2. Match die Frage gegen die Bibliothek: `app_api action=call method=POST path=/api/standardanfragen/match body={"frage": "<frage-text>"}`. Die Antwort enthaelt `best_match` (oder null) und `candidates` mit Scores.
3. Bei `best_match` mit Score >= 0.18: zur passenden Standardanfrage uebergehen. Bei niedrigerem Score oder ohne Treffer: KEIN Workaround mit der naechstbesten Vorlage — stattdessen den Mitarbeiter darauf hinweisen, dass das Thema noch nicht in der Bibliothek ist, und auf `hauswissen-suche` verweisen.
4. Hole das Antwort-Template: `app_api action=call method=GET path=/api/standardanfragen/<slug>` und sieh die Stichworte sowie das Template-Skelett.
5. Fuelle die Platzhalter: `app_api action=call method=POST path=/api/standardanfragen/<slug>/render body={"anrede": "Sehr geehrter Herr Mustermann,", "verfasser": {"name": "K. Seifer", "funktion": "Vermoegensverwalter"}, ...}`. Bei mandantenspezifischen Variablen (z.B. Risikoklasse, Betrag, Valuta, Empfaengerkonto) das Hauswissen oder die Mandantenakte konsultieren — niemals raten.
6. Passe den Antworttext bei Bedarf an Tonalitaet und Mandantenkontext an (z.B. bestehende Geschaeftsbeziehung, persoenlicher Bekanntheitsgrad), ohne den Pflichttext oder die Disclaimer zu veraendern.
7. Lege den Entwurf per `manage_documents action=create` mit Titel `Antwort <Mandant> <Thema> <TT.MM.JJJJ>` ab, `release_status=draft`, Hinweis "Entwurf — vor Versand pruefen" am Anfang.
8. Wende den Hausstandard an (siehe Skill `m-und-s-hausstandard`): Anrede, Datumsformat, Disclaimer, Tonalitaet.

## Pitfalls

- Niemals eine Standardanfrage zwangsweise zuordnen, wenn der Score unter 0.18 liegt — sonst bekommt der Mandant die falsche Antwort. Bei niedrigem Score klar sagen, dass das Thema individuell beantwortet werden muss.
- Steuerliche Fragen NIE als verbindliche Steuerauskunft beantworten — die Templates enthalten den Hinweis auf den Steuerberater; den NIE entfernen.
- Auszahlungsanfragen ueber 50.000 EUR oder bei ungewoehnlichen Empfaengerkonten als "Sonderfall" markieren und persoenliche Pruefung anregen. Geldwaesche-/KYC-Pflichten respektieren.
- Bei Kuendigungs-Anfragen den Tonfall sachlich-respektvoll halten; weder relativieren noch dramatisieren. Vertragliche Bestimmungen ueberpruefen, nicht aus dem Standard-Template ableiten.
- Standardanfragen sind Stufe 2 (Vorschlag mit Freigabe). Niemals Versandbereitschaft suggerieren — der Mitarbeiter prueft und versendet selbst.
- Wenn der Mandant in seiner Anfrage mehrere Themen vermischt (z.B. Kuendigung + Auszahlung), getrennte Antwortbloecke je Thema erstellen.

## Verification

- Match wurde durchgefuehrt; bei niedrigem Score (<0.18) wurde dem Mitarbeiter mitgeteilt, dass keine Standardvorlage passt.
- Template wurde mit Platzhaltern befuellt; `missing_placeholders` (falls vorhanden) wurden im Chat genannt.
- Bei steuerlichen Fragen ist der Hinweis auf den Steuerberater enthalten.
- Bei Auszahlungs-Anfragen ueber 50.000 EUR oder ungewoehnlichen Empfaengerkonten ist der "Sonderfall"-Vermerk gesetzt.
- Document liegt als `release_status=draft` vor, Hinweis "Entwurf — vor Versand pruefen" am Anfang.
- Disclaimer und Hausstandard sind angewendet.

## Detail: Bibliothek (Stand 19.06.2026)

- `kosten-und-gebuehren`: Konditionen, Performance Fee, All-in-Fee
- `steuerliche-aspekte`: Abgeltungssteuer, Quellensteuer, Teilfreistellung
- `risikoeinstufung`: WpHG-Anlegerprofil, Anpassung der Risikoklasse
- `kuendigung-mandat`: Kuendigungsfristen, Ablauf, Vermoegensueberleitung
- `auszahlung-anfordern`: Beleg-Pflichtangaben, Bearbeitungszeit, Sonderfaelle

Erweiterung der Bibliothek erfolgt im Repo unter `data/standardanfragen/<neuer-slug>/` mit `frage.md` (Stichworte) und `antwort-template.md` (Vorlage mit `{{ platzhaltern }}`).
