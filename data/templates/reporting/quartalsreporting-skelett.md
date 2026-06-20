# Quartalsreporting {{ quartal }} {{ jahr }}

**Hausvorlage Meeder & Seifer · Quartalsbericht (Skelett)**

*Mandant: {{ mandant.name }}*
*Stichtag: {{ stichtag }}*
*Berichtswaehrung: {{ basiswaehrung }}*

---

## 1. Zusammenfassung

{{ zusammenfassung }}

## 2. Performance

### 2.1 Performance-Uebersicht

| Zeitraum | Portfolio | Benchmark | Differenz |
|---|---|---|---|
| YTD | {{ perf.ytd_portfolio }} | {{ perf.ytd_benchmark }} | {{ perf.ytd_diff }} |
| 1 Jahr | {{ perf.j1_portfolio }} | {{ perf.j1_benchmark }} | {{ perf.j1_diff }} |
| 3 Jahre p.a. | {{ perf.j3_portfolio }} | {{ perf.j3_benchmark }} | {{ perf.j3_diff }} |

### 2.2 Kommentar

{{ perf.kommentar }}

## 3. Allokation und Positionen

### 3.1 Asset-Allokation

| Anlageklasse | Anteil | Vormonat | Veraenderung |
|---|---|---|---|
| Aktien | {{ alloc.aktien_aktuell }} | {{ alloc.aktien_vormonat }} | {{ alloc.aktien_diff }} |
| Renten | {{ alloc.renten_aktuell }} | {{ alloc.renten_vormonat }} | {{ alloc.renten_diff }} |
| Cash | {{ alloc.cash_aktuell }} | {{ alloc.cash_vormonat }} | {{ alloc.cash_diff }} |
| Edelmetalle | {{ alloc.edelmetalle_aktuell }} | {{ alloc.edelmetalle_vormonat }} | {{ alloc.edelmetalle_diff }} |

### 3.2 Top-Positionen

{{ positionen }}

## 4. Risiko

| Kennzahl | Wert | Stichzeitraum |
|---|---|---|
| Volatilitaet p.a. | {{ risiko.volatilitaet }} | {{ risiko.zeitraum_volatilitaet }} |
| Max. Drawdown | {{ risiko.max_drawdown }} | {{ risiko.zeitraum_max_drawdown }} |
| Sharpe Ratio | {{ risiko.sharpe }} | {{ risiko.zeitraum_sharpe }} |

## 5. Markt- und Strategieausblick

{{ ausblick }}

## 6. Hinweise und Disclaimer

*Alle Angaben ohne Gewaehr. Historische Wertentwicklung ist kein verlaesslicher Indikator fuer zukuenftige Renditen. Diese Darstellung dient ausschliesslich Informationszwecken und stellt keine Anlageberatung oder Anlagevermittlung dar. Stichtag der Daten: {{ stichtag }}.*

*Meeder und Seifer Vermoegensverwaltung GmbH*
