---
name: linkedin-post-entwurf
description: "Verfasst einen LinkedIn-Post-Entwurf fuer Meeder und Seifer nach Hausstandard — fuer das persoenliche Profil (Ich-Perspektive) oder die Unternehmensseite (Wir-Perspektive) — als Entwurf zur Freigabe. Veroeffentlichung erfolgt manuell per Copy-Paste."
version: 1.0.0
category: m-und-s
tags: [linkedin, social-media, schriftverkehr, m-und-s]
status: published
confidence: 0.8
source: imported
shared: true
created: 2026-06-20T00:00:00Z
---

## When to Use

Triggere diesen Skill, wenn ein LinkedIn-Beitrag entworfen werden soll. Trigger-Begriffe: "LinkedIn-Post", "Beitrag fuer LinkedIn", "Post fuer die Unternehmensseite", "etwas auf LinkedIn teilen", "Social-Media-Beitrag", "LinkedIn-Beitrag zu ...", Marktkommentar oder Ankuendigung fuer Social Media. Der Skill erstellt nur den Entwurf; das Veroeffentlichen macht der Mitarbeiter selbst per Copy-Paste (keine LinkedIn-Anbindung).

## Procedure

1. Pflichtfelder klaeren: Account-Typ (persoenliches Profil = Ich-Perspektive ODER M&S-Unternehmensseite = Wir-Perspektive), Anlass/Thema, Kernbotschaft, gewuenschte Laenge, Call-to-Action (optional). Fehlende Felder gezielt erfragen — besonders den Account-Typ, da er Perspektive und Tonalitaet bestimmt.
2. Recherchemodus klaeren (siehe Skill `recherche-modus`): Schnellanalyse (nur gegebene Infos + Hauswissen) oder Tiefenanalyse (zusaetzlich `trigger_research` fuer Marktfakten/aktuelle Zahlen). Wenn der Nutzer den Modus nicht nennt, nachfragen — niemals ungefragt einen Deep-Research-Lauf starten. Bei Posts mit Markt-/Themenbezug eignet sich die Tiefenanalyse, mit Quellenpflicht: jede konkrete Zahl belegt, Deep-Research-Befunde mit Marker `(Deep Research: <Quelle>, <Stichtag>)`.
3. Hausstandard anwenden (siehe Skill `m-und-s-hausstandard`): Tonalitaet sachlich-professionell, Begriff "Mandant" statt "Kunde", Datumsformat TT.MM.JJJJ, deutsches Zahlenformat. Tonalitaet je nach Account: persoenliches Profil = Ich, etwas persoenlicher; Unternehmensseite = Wir, etwas formeller.
4. Post verfassen: Hook in Zeile 1 (greift sofort, kein Floskel-Einstieg), danach knapper Fliesstext in kurzen Absaetzen, klare Struktur, optional eine kurze Aufzaehlung. LinkedIn-gerecht: sinnvolle Laenge (rund 1.300 Zeichen bis zur "mehr anzeigen"-Sichtbarkeitsgrenze), sparsame Hashtags (3-5) am Ende, optional ein klarer Call-to-Action.
5. Entwurf ablegen: `manage_documents action=create` mit Titel `LinkedIn-Post <Account-Typ> <TT.MM.JJJJ>`, `release_status=draft`, und dem Mitarbeiter zur Freigabe uebergeben.
6. Chat-Hinweis "Entwurf — vor Veroeffentlichung pruefen" oben setzen. Bei Posts der Unternehmensseite zusaetzlich darauf hinweisen, dass es sich um eine Werbemitteilung handelt und ggf. Compliance einzubinden ist.

## Pitfalls

- Keine konkrete Anlageberatung oder -empfehlung im Post (kein "kaufen Sie X", keine ISIN-Tipps, keine "jetzt einsteigen"-Aussagen). Eine BaFin-regulierte Vermoegensverwaltung darf oeffentlich keine individuelle Anlageempfehlung geben.
- Posts der Unternehmensseite sind Werbemitteilungen im Sinne des WpHG: ausgewogen (Chancen UND Risiken), nicht irrefuehrend, keine Renditeversprechen oder Erfolgsgarantien; bei anlagebezogenen Aussagen Standard-Disclaimer/Quellenvermerk beifuegen und ggf. als Werbung kenntlich machen.
- Keine vertraulichen Mandanten- oder Portfoliodaten, keine Personennamen ohne ausdrueckliche Freigabe der betroffenen Person.
- Account-Perspektive nicht vermischen — Ich (Profil) und Wir (Firmenseite) konsequent durchhalten; nie im selben Post wechseln.
- Hashtags nur mit Grund und sparsam (3-5), nicht inflationaer; keine generischen Hashtag-Wolken.
- Keine reisserische Click-Bait-Sprache oder Superlative ("revolutionaer", "garantiert") — der Hausstandard ist sachlich-serioes.
- Konkrete Marktzahlen nur mit Quelle und Stichtag; ohne Beleg keine Zahlen im Post.

## Verification

- Account-Typ und Perspektive (Ich vs. Wir) sind eindeutig und durchgaengig; Recherchemodus ist geklaert und vermerkt.
- Hausstandard angewendet (Begriffe, Tonalitaet, Datums-/Zahlenformat).
- Keine konkrete Anlageempfehlung enthalten; bei Unternehmensseiten-Posts ist der Werbe-/Disclaimer-Hinweis gesetzt.
- Konkrete Zahlen sind mit Quelle und Stichtag belegt; bei Tiefenanalyse Deep-Research-Befunde markiert.
- Post hat einen Hook in Zeile 1, kurze Absaetze, sparsame Hashtags (3-5) und ggf. einen Call-to-Action; Laenge LinkedIn-gerecht.
- Entwurf ist als Document (`release_status=draft`) abgelegt; Hinweis "Entwurf — vor Veroeffentlichung pruefen" steht im Chat.

## Detail: Post-Struktur-Bausteine

Je nach Anlass eine der folgenden Grundformen waehlen:

- **Fachimpuls / Bildungsbeitrag**: Eine Frage oder ein Missverstaendnis als Hook, dann eine kurze, verstaendliche Einordnung aus Sicht der Vermoegensverwaltung, abschliessend eine Einladung zur Diskussion. Ideal fuer Expertise-Aufbau.
- **Marktkommentar**: Aktueller Anlass (Notenbankentscheid, Marktphase) als Hook, nuechterne Einordnung mit belegten Zahlen, klare Trennung von Fakt und Einschaetzung, kein Handlungsappell. Quellen-/Stichtagspflicht beachten.
- **Unternehmens-/Team-News**: Anlass (neues Teammitglied, Auszeichnung, Jubilaeum) als Hook, Wir-Perspektive, persoenlich aber serioes; keine vertraulichen Details.
- **Event/Ankuendigung**: Was, wann, fuer wen als Hook, konkreter Nutzen, klarer Call-to-Action (Anmeldung/Kontakt).

## Detail: Laenge und Hashtags

- **Laenge**: Die ersten ~210 Zeichen erscheinen vor "mehr anzeigen" — der Hook muss dort sitzen. Gesamtlaenge fuer Fach-/Marktposts rund 800-1.300 Zeichen; kurze News duerfen kuerzer sein. Kurze Absaetze (1-3 Saetze), Leerzeilen fuer Lesbarkeit.
- **Hashtags**: 3-5 gezielte, themenrelevante Hashtags am Ende (z.B. Vermoegensverwaltung, FamilyOffice, Kapitalmarkt, Geldanlage). Keine inflationaeren Hashtag-Wolken, keine generischen Tags.
- **Call-to-Action**: optional, aber wenn vorhanden konkret (z.B. "Wie sehen Sie das?" fuer Fachimpulse, "Sprechen Sie uns an" fuer Service-Posts). Keine aggressive Akquise.

## Detail: Ton je Account-Typ

- **Persoenliches Profil (Ich)**: erste Person, etwas persoenlicher und nahbarer, eigene Einschaetzung erlaubt; bleibt fachlich serioes, keine reine Selbstdarstellung.
- **M&S-Unternehmensseite (Wir)**: erste Person Plural, formeller, repraesentiert das Haus; staerkere Compliance-Sensibilitaet, weil als Werbemitteilung einzustufen.

## Detail: Beispiel-Workflow

Mitarbeiter: "Entwirf einen LinkedIn-Post fuer die Unternehmensseite zum Thema Marktausblick Q3":

1. Pflichtfelder klaeren: Account = Unternehmensseite (Wir); Thema = Marktausblick Q3; Kernbotschaft erfragen; Laenge ~1.000 Zeichen; CTA optional.
2. Recherchemodus: bei Marktbezug Tiefenanalyse anbieten — `trigger_research` zu den Q3-Markttreibern, Befunde mit Quelle/Stichtag.
3. Post verfassen: Hook (z.B. eine praegnante Marktfrage), nuechterne Einordnung mit belegten Zahlen, ausgewogen (Chancen und Risiken), kein Handlungsappell.
4. Werbe-Disclaimer fuer Unternehmensseite anfuegen; Hausstandard anwenden.
5. Als Document `release_status=draft` mit Titel `LinkedIn-Post Unternehmensseite <TT.MM.JJJJ>` ablegen; Hinweis "Entwurf — vor Veroeffentlichung pruefen" im Chat.
