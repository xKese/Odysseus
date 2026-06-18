---
name: m-und-s-hausstandard
description: "Hausstandard von Meeder und Seifer fuer alle KI-erzeugten Texte, Reports, Anschreiben und Dokumente. Definiert Tonalitaet, Begriffe, Disclaimer, Datums- und Adressformate sowie das Tabellen-Farbschema. Wird von jedem Fach-Skill referenziert."
version: 1.0.0
category: m-und-s
tags: [hausstandard, stil, branding, m-und-s]
status: published
confidence: 0.95
source: imported
owner: kese
shared: true
created: "2026-06-17T00:00:00Z"
---

## When to Use

Verwende diesen Skill immer als Output-Layer, wenn Texte, Reports, Anschreiben, Reportings oder Word-/PDF-Dokumente fuer Meeder und Seifer erzeugt werden. Wird typischerweise nicht direkt vom Nutzer aufgerufen, sondern von Fach-Skills (Fondsanalyse, Kontoabgleich, Reporting-Entwurf, Anschreiben-Entwurf, Marktbeobachtung-Briefing) im Schritt "Hausstandard anwenden" eingebunden.

## Procedure

1. Pruefe die Tonalitaet: sachlich, professionell, ohne uebertriebenes Marketingvokabular, ohne Anbiederung. Kein Floskel-Deutsch ("wir freuen uns sehr, Ihnen mitteilen zu duerfen"), stattdessen direkter und respektvoller Stil.
2. Verwende die hauseigenen Begriffe: "Mandant" statt "Kunde" oder "Klient"; "Vermoegensverwaltung" statt "Asset Management" oder "VV-Service"; "Anlagerichtlinien" statt "Investment Policy"; "Family Office" stets mit Bindestrich-Kompositum nur dann, wenn als Adjektiv (z.B. "Family-Office-Software").
3. Datumsformat: `TT.MM.JJJJ` (z.B. `17.06.2026`). Uhrzeit nur wenn relevant, dann `HH:MM Uhr`.
4. Zahlenformat: deutsche Notation mit Tausenderpunkt und Dezimalkomma (z.B. `1.234.567,89 EUR`). Waehrungskuerzel nach der Zahl mit Leerzeichen.
5. Adressformat (Anschreiben): Anrede `Sehr geehrte Frau Mustermann,` / `Sehr geehrter Herr Mustermann,`. Bei Personenmehrzahl `Sehr geehrte Damen und Herren,`. Briefkopf links oben mit Mandantenname, Adresse, daneben rechts Datum (`Frankfurt am Main, 17.06.2026`).
6. Tabellenformat (Markdown und DOCX): Kopfzeile in Dunkelblau `#1F3864` mit weisser Schrift, abwechselnde Zeilenfarben Weiss und Hellgrau `#F2F2F2`, Standard-Schriftart Calibri 11pt fuer DOCX. Bei besten/schlechtesten Werten in Vergleichstabellen jeweils fett.
7. Quellenanzeige: Bei recherche- oder factsheet-basierten Inhalten am Ende einen Block `## Quellen` mit nummerierter Liste der verwendeten Dokumente, URLs und Stichtagen.
8. Disclaimer am Ende jedes externen oder anlagerelevanten Dokuments einfuegen (siehe body_extra unten). Bei internen Memos den Vermerk "Vertraulich, nur zur internen Verwendung" in der Fusszeile.
9. Pruefe abschliessend, dass keine emojis, ASCII-Sterne als Hervorhebung oder typografischen Sonderzeichen ausser Halbgeviertstrich `–` und Anfuehrungszeichen `„"` enthalten sind.

## Pitfalls

- Niemals "wir" und "uns" verwenden, wenn nicht klar ist, ob die KI fuer das Haus spricht oder fuer den Autor. Bei Unklarheit neutrale Formulierung waehlen ("die Vermoegensverwaltung empfiehlt...").
- Bei Anlageempfehlungen oder Performance-Aussagen IMMER den vollstaendigen Disclaimer (siehe unten) anfuegen — auch bei Kurzuebersichten.
- Bei E-Mail-Entwuerfen niemals Versandbereitschaft suggerieren — der Mitarbeiter gibt frei und versendet selbst.
- Bei Wertpapier- oder Fondsnamen die ISIN oder WKN zur Eindeutigkeit hinzufuegen, auch wenn der Markenname gelaeufig ist.
- Bei englischen Fachbegriffen (z.B. "Drawdown", "Sharpe Ratio") in Klammern eine deutsche Kurzerklaerung bei der ersten Verwendung, danach unbedenklich weiterverwenden.
- Keine ASCII-Tabellen-Pseudokunst (`+---+---+`); Markdown-Tabellen mit Pipe-Trennzeichen sind Standard.

## Verification

- Tonalitaet ist sachlich-professionell, keine Floskeln, keine Anbiederung.
- Begriffe "Mandant", "Vermoegensverwaltung", "Anlagerichtlinien" sind durchgaengig verwendet.
- Datums- und Zahlenformate sind durchgaengig deutsch.
- Tabellen folgen dem Farbschema (Markdown: Header-Zeile, DOCX: Dunkelblau Kopfzeile, alternierende Zeilen).
- Bei recherche- oder factsheet-basierten Inhalten ist der Quellen-Block am Ende vorhanden.
- Bei anlagerelevanten oder externen Dokumenten ist der vollstaendige Disclaimer enthalten.
- Keine emojis, keine Marketingfloskeln, keine Versandbereitschaft suggeriert.

Standard-Disclaimer (Performance- und Anlageinhalte):

```
Alle Angaben ohne Gewaehr. Historische Wertentwicklung ist kein verlaesslicher
Indikator fuer zukuenftige Renditen. Diese Darstellung dient ausschliesslich
Informationszwecken und stellt keine Anlageberatung oder Anlagevermittlung dar.
Stichtag der Daten: <TT.MM.JJJJ>.

Meeder und Seifer Vermoegensverwaltung GmbH
```

Bei internen Memos zusaetzlich: `Vertraulich, nur zur internen Verwendung.`

- Kopfzeile Tabelle: Hintergrund `#1F3864` (Dunkelblau), Schrift `#FFFFFF` (Weiss), Calibri 11pt bold.
- Zeilen alternierend: `#FFFFFF` (Weiss) und `#F2F2F2` (Hellgrau), Calibri 11pt regular.
- Ueberschriften H1: Calibri 18pt bold, Farbe `#1F3864`.
- Ueberschriften H2: Calibri 14pt bold, Farbe `#1F3864`.
- Fliesstext: Calibri 11pt, Schwarz `#000000`, Zeilenabstand 1.15.
- Akzentfarbe (Hervorhebungen, Marker): `#C00000` (Dunkelrot), sparsam einsetzen.
- Logo-Pfad (DOCX-Briefkopf, sofern vorhanden): `data/templates/assets/logo-m-und-s.png`.

| Bevorzugt | Vermeiden |
|---|---|
| Mandant | Kunde, Klient |
| Vermoegensverwaltung | Asset Management, VV-Service |
| Family-Office-Betrieb | Family Office (alleinstehend in deutschen Texten) |
| Anlagerichtlinien | Investment Policy |
| Anlageausschuss | Investment Committee |
| Anlagehorizont | Investment Horizon |
| Risikoprofil | Risk Profile |
| Vermoegensuebersicht | Portfolio Overview |
| Reporting (etabliert, beibehalten) | "Berichtswesen" wirkt veraltet |
| Schriftverkehr | Correspondence |

Format am Ende von recherche- oder factsheet-basierten Texten:

```

1. <Anbieter>: <Dokumenttitel>, Stand <TT.MM.JJJJ>, <URL oder Dateiname>.
2. <...>
```

Bei mehreren Quellen zur selben Aussage in eckigen Klammern referenzieren: `Die Aktienquote betraegt 78 Prozent [1, 3].`
