#!/usr/bin/env python3
"""Reconciliation engine for Meeder & Seifer Kontoabgleich-Skill.

Matches transactions from an internal Family-Office PDF export against a
bank CSV/XLSX statement on signed amount (Soll negative, Haben positive)
and writes a German Markdown report.

Ported 1:1 from the Claude-Code skill (no logic changes); paths now point
to Odysseus data dirs instead of the Claude-Code /mnt/user-data layout.
"""
import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Install with: pip install pdfplumber openpyxl pandas")
    sys.exit(1)

SOLL_HABEN_THRESHOLD = 600.0  # x < 600 = Soll, x >= 600 = Haben (Kontow.)


def parse_german_amount_raw(text):
    """Parse German amount, return raw float (no abs)."""
    if text is None:
        return 0.0
    s = re.sub(r'\s+', '', str(text).strip())
    s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0


def normalize_date(date_str):
    s = str(date_str).strip().strip('"')
    for fmt in ('%d.%m.%y', '%d.%m.%Y'):
        try:
            return datetime.strptime(s, fmt).strftime('%d.%m.%Y')
        except ValueError:
            pass
    return s


def fmt_amount(val):
    """Format float as German amount string (no sign)."""
    s = f"{abs(val):,.2f}"
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s


def parse_internal_pdf(pdf_path):
    """Parse PDF using word positions to determine Soll/Haben sign."""
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            words = page.extract_words()
            if not text or not words:
                continue

            amount_map = {}
            for w in words:
                t = w['text']
                if re.match(r'^[\d.]+,\d{2}$', t):
                    y_key = round(w['top'], 0)
                    x0 = w['x0']
                    if x0 < 670:
                        amount_map.setdefault(y_key, []).append({
                            'text': t,
                            'x0': x0,
                            'is_soll': x0 < SOLL_HABEN_THRESHOLD,
                        })

            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                skips = ['Buchungstag', 'Devisenkurs', 'Transaktionsauszug',
                         'Depot ', 'Zeitraum', 'LABEL', 'Referenzw']
                if any(sw in line for sw in skips):
                    continue
                if line.startswith('Kontoumsaetze') or line.startswith('Kontoumsätze'):
                    continue
                if not re.match(r'^\d{2}\.\d{2}\.\d{4}', line):
                    continue

                dates = re.findall(r'\d{2}\.\d{2}\.\d{4}', line)
                if len(dates) < 2:
                    continue
                buchungstag, valuta = dates[0], dates[1]

                clean_amounts = []
                for m in re.finditer(r'[\d.]+,\d{2}', line):
                    rest = line[m.end():]
                    if rest and (rest[0].isdigit() or rest[0] == '%'):
                        continue
                    clean_amounts.append(m.group())
                if not clean_amounts:
                    continue

                raw_betrag = parse_german_amount_raw(clean_amounts[-1])
                if raw_betrag == 0.0:
                    continue

                abs_betrag = abs(raw_betrag)
                is_soll = None

                for w in words:
                    if re.match(r'^[\d.]+,\d{2}$', w['text']) and w['x0'] < 670:
                        parsed = parse_german_amount_raw(w['text'])
                        if abs(abs(parsed) - abs_betrag) < 0.005:
                            if w['text'] in clean_amounts:
                                is_soll = w['x0'] < SOLL_HABEN_THRESHOLD
                                break

                if is_soll is None:
                    for _y_key, amts in amount_map.items():
                        for a in amts:
                            p = abs(parse_german_amount_raw(a['text']))
                            if abs(p - abs_betrag) < 0.005 and a['text'] in clean_amounts:
                                is_soll = a['is_soll']
                                break
                        if is_soll is not None:
                            break

                if is_soll is not None:
                    signed_betrag = -abs_betrag if is_soll else abs_betrag
                else:
                    signed_betrag = abs_betrag

                pos = 0
                for d in dates[:2]:
                    idx = line.find(d, pos)
                    if idx >= 0:
                        pos = idx + len(d)
                apos = line.find(clean_amounts[0])
                bez = line[pos:apos].strip() if apos > pos else ''
                bez = re.sub(r'\d{7,}\s*EUR', '', bez).strip()
                bez = re.sub(r'\s+', ' ', bez).strip()

                rows.append({
                    'Buchungstag': normalize_date(buchungstag),
                    'Valuta': normalize_date(valuta),
                    'Betrag': round(signed_betrag, 2),
                    'Bezeichnung': bez,
                })

    return pd.DataFrame(rows)


def parse_bank_file(file_path):
    path = Path(file_path)
    ext = path.suffix.lower()
    df = None
    if ext in ('.xlsx', '.xls'):
        df = pd.read_excel(file_path, dtype=str)
    elif ext == '.csv':
        for enc in ['iso-8859-1', 'utf-8', 'cp1252']:
            for sep in [';', ',', '\t']:
                try:
                    c = pd.read_csv(file_path, encoding=enc, sep=sep, dtype=str)
                    if len(c.columns) > 3:
                        df = c
                        break
                except Exception:
                    pass
            if df is not None:
                break
        if df is None:
            raise ValueError(f"Konnte Datei nicht lesen: {file_path}")
    else:
        raise ValueError(f"Unbekanntes Dateiformat: {ext}")
    col_map = {}
    for col in df.columns:
        cc = col.strip().strip('"').lower()
        if 'buchungstag' in cc:
            col_map['Buchungstag'] = col
        elif 'valuta' in cc or 'wertstellung' in cc:
            col_map['Valuta'] = col
        elif 'betrag' in cc and 'Betrag' not in col_map:
            col_map['Betrag'] = col
        elif 'verwendungszweck' in cc:
            col_map['Bezeichnung'] = col
        elif 'buchungstext' in cc and 'Bezeichnung' not in col_map:
            col_map['Bezeichnung'] = col
    for r in ['Buchungstag', 'Valuta', 'Betrag']:
        if r not in col_map:
            raise ValueError(f"Spalte fehlt: {r}. Spalten: {list(df.columns)}")
    rows = []
    for _, row in df.iterrows():
        bt = normalize_date(str(row[col_map['Buchungstag']]).strip().strip('"'))
        vl = normalize_date(str(row[col_map['Valuta']]).strip().strip('"'))
        raw = str(row[col_map['Betrag']]).strip().strip('"')
        signed = parse_german_amount_raw(raw)
        bez = str(row[col_map['Bezeichnung']]).strip().strip('"') if 'Bezeichnung' in col_map else ''
        if signed == 0.0:
            continue
        rows.append({'Buchungstag': bt, 'Valuta': vl, 'Betrag': round(signed, 2), 'Bezeichnung': bez})
    return pd.DataFrame(rows)


def make_key(row):
    return f"{row['Betrag']:.2f}"


def reconcile(intern_df, bank_df):
    ik = [make_key(r) for _, r in intern_df.iterrows()]
    bk = [make_key(r) for _, r in bank_df.iterrows()]
    ic, bc = Counter(ik), Counter(bk)
    all_k = set(ik) | set(bk)
    limits = {k: min(ic.get(k, 0), bc.get(k, 0)) for k in all_k}
    iby, bby = {}, {}
    for _, r in intern_df.iterrows():
        iby.setdefault(make_key(r), []).append(r)
    for _, r in bank_df.iterrows():
        bby.setdefault(make_key(r), []).append(r)
    matched, um_i, um_b = [], [], []
    for k in all_k:
        ir, br, lim = iby.get(k, []), bby.get(k, []), limits[k]
        for i in range(lim):
            matched.append((ir[i], br[i]))
        for i in range(lim, len(ir)):
            um_i.append(ir[i])
        for i in range(lim, len(br)):
            um_b.append(br[i])
    return matched, um_b, um_i


def generate_report(idf, bdf, matched, um_b, um_i, out):
    L = []
    L.append("# Kontoabgleich - Ergebnis\n")
    L.append(f"*Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}*\n")
    L.append("## Zusammenfassung\n")
    L.append("| Kennzahl | Anzahl |")
    L.append("|---|---|")
    L.append(f"| Buchungen Bank | {len(bdf)} |")
    L.append(f"| Buchungen Intern | {len(idf)} |")
    L.append(f"| Uebereinstimmungen (Betrag inkl. Vorzeichen) | {len(matched)} |")
    L.append(f"| Fehlend im internen System | {len(um_b)} |")
    L.append(f"| Ueberzaehlig im internen System | {len(um_i)} |")
    L.append("")
    if not um_b and not um_i:
        L.append("**Status: ALLE BUCHUNGEN STIMMEN UEBEREIN**\n")
    else:
        L.append("**Status: DIFFERENZEN VORHANDEN**\n")

    vd = [(ir, br) for ir, br in matched if ir['Valuta'] != br['Valuta']]
    if vd:
        L.append("---\n")
        L.append("## Abweichende Valutatage\n")
        L.append("Betrag stimmt ueberein, Valuta weicht ab.\n")
        L.append("| Nr. | Betrag (EUR) | Valuta Intern | Valuta Bank | Bezeichnung (Intern) |")
        L.append("|-----|-------------|---------------|-------------|----------------------|")
        for i, (ir, br) in enumerate(vd, 1):
            bez = str(ir.get('Bezeichnung', '')).replace('|', '/')[:50]
            b = ir['Betrag']
            sign = "Soll" if b < 0 else "Haben"
            L.append(f"| {i} | {fmt_amount(b)} ({sign}) | {ir['Valuta']} | {br['Valuta']} | {bez} |")
        L.append("")
        L.append(f"*{len(vd)} von {len(matched)} mit abweichendem Valutatag.*\n")

    bd = [(ir, br) for ir, br in matched if ir['Buchungstag'] != br['Buchungstag']]
    if bd:
        L.append("---\n")
        L.append("## Abweichende Buchungstage\n")
        L.append("Betrag stimmt ueberein, Buchungstag weicht ab.\n")
        L.append("| Nr. | Betrag (EUR) | BT Intern | BT Bank | Bezeichnung (Intern) |")
        L.append("|-----|-------------|-----------|---------|----------------------|")
        for i, (ir, br) in enumerate(bd, 1):
            bez = str(ir.get('Bezeichnung', '')).replace('|', '/')[:50]
            b = ir['Betrag']
            sign = "Soll" if b < 0 else "Haben"
            L.append(f"| {i} | {fmt_amount(b)} ({sign}) | {ir['Buchungstag']} | {br['Buchungstag']} | {bez} |")
        L.append("")
        L.append(f"*{len(bd)} von {len(matched)} mit abweichendem Buchungstag.*\n")

    if um_b:
        L.append("---\n")
        L.append("## Fehlende Buchungen im internen System\n")
        L.append("Im Bankauszug vorhanden, intern fehlend. Muessen nachgebucht werden.\n")
        L.append("| Nr. | Buchungstag | Valuta | Betrag (EUR) | Soll/Haben | Bezeichnung |")
        L.append("|-----|-------------|--------|-------------|------------|-------------|")
        for i, r in enumerate(um_b, 1):
            bez = str(r.get('Bezeichnung', '')).replace('|', '/')[:50]
            b = r['Betrag']
            sh = "Soll" if b < 0 else "Haben"
            L.append(f"| {i} | {r['Buchungstag']} | {r['Valuta']} | {fmt_amount(b)} | {sh} | {bez} |")
        L.append("")
    if um_i:
        L.append("---\n")
        L.append("## Ueberzaehlige Buchungen im internen System\n")
        L.append("Intern vorhanden, im Bankauszug fehlend. Muessen geprueft werden.\n")
        L.append("| Nr. | Buchungstag | Valuta | Betrag (EUR) | Soll/Haben | Bezeichnung |")
        L.append("|-----|-------------|--------|-------------|------------|-------------|")
        for i, r in enumerate(um_i, 1):
            bez = str(r.get('Bezeichnung', '')).replace('|', '/')[:50]
            b = r['Betrag']
            sh = "Soll" if b < 0 else "Haben"
            L.append(f"| {i} | {r['Buchungstag']} | {r['Valuta']} | {fmt_amount(b)} | {sh} | {bez} |")
        L.append("")
    report = '\n'.join(L)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--intern', required=True)
    p.add_argument('--bank', required=True)
    p.add_argument('--output', default='Kontoabgleich_Ergebnis.md')
    a = p.parse_args()
    print(f"Lese internes System: {a.intern}")
    idf = parse_internal_pdf(a.intern)
    print(f"  -> {len(idf)} Buchungen")
    print(f"Lese Bankauszug: {a.bank}")
    bdf = parse_bank_file(a.bank)
    print(f"  -> {len(bdf)} Buchungen")
    print("Abgleich...")
    mp, ub, ui = reconcile(idf, bdf)
    print(f"  -> {len(mp)} Uebereinstimmungen (Betrag mit Vorzeichen)")
    print(f"  -> {len(ub)} fehlend intern")
    print(f"  -> {len(ui)} ueberzaehlig intern")
    vd = sum(1 for ir, br in mp if ir['Valuta'] != br['Valuta'])
    bd = sum(1 for ir, br in mp if ir['Buchungstag'] != br['Buchungstag'])
    if vd:
        print(f"  -> {vd} abweichende Valutatage")
    if bd:
        print(f"  -> {bd} abweichende Buchungstage")
    generate_report(idf, bdf, mp, ub, ui, a.output)
    print(f"Bericht: {a.output}")


if __name__ == '__main__':
    main()
