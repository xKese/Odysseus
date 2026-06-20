"""Portfolio-Importer fuer Meeder & Seifer (Phase 2).

Liest CSV- und XLSX-Exporte aus gaengigen Family-Office-/Depotsoftwares
und legt sie als ``PortfolioSnapshot`` mit zugehoerigen ``Position``-Eintraegen
in der Datenbank ab. Header-Erkennung ist tolerant: deutsche und englische
Bezeichnungen sowie haeufige Anbieter-spezifische Spaltennamen werden
gemappt.

Bewusst KEIN Anspruch auf vollstaendige Performance-Berechnung — der
Importer haelt nur den Bestand zum Stichtag. TWR/MWR-Vergleiche ueber
mehrere Snapshots folgen in Phase 2.5.

Robust gegen die typischen Quellformat-Fallen:
- CSV: Encoding (utf-8 / iso-8859-1 / cp1252), Trennzeichen (`;`, `,`, Tab)
- XLSX: erste Tabelle wird genommen (Multi-Sheet-Quellen erfordern manuelles
  Aufsplitten vor dem Upload)
- Deutsche Zahlen mit `.` als Tausender und `,` als Dezimaltrenner werden
  automatisch normalisiert.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Header-Aliase: lowercase / stripped → kanonisches Feld.
# Mehrere Eintraege koennen denselben kanonischen Wert haben (z.B.
# "wertpapier" und "name" -> "name").
_HEADER_ALIASES: Dict[str, str] = {
    "isin": "isin",
    "wkn": "wkn",
    "kennnummer": "wkn",
    "name": "name",
    "bezeichnung": "name",
    "wertpapier": "name",
    "instrument": "name",
    "position": "name",
    "anlageklasse": "asset_class",
    "asset class": "asset_class",
    "asset-klasse": "asset_class",
    "kategorie": "asset_class",
    "menge": "quantity",
    "stueck": "quantity",
    "stück": "quantity",
    "anzahl": "quantity",
    "nominal": "quantity",
    "quantity": "quantity",
    "waehrung": "currency",
    "währung": "currency",
    "currency": "currency",
    "kurswert": "market_value",
    "marktwert": "market_value",
    "wert": "market_value",
    "market value": "market_value",
    "value": "market_value",
    "betrag": "market_value",
    "anteil": "weight_percent",
    "anteil %": "weight_percent",
    "gewichtung": "weight_percent",
    "gewicht": "weight_percent",
    "anteil_prozent": "weight_percent",
    "weight": "weight_percent",
    "weight %": "weight_percent",
}


# Asset-Klassen-Heuristik via ISIN-Praefix bzw. Schluesselwoertern, wenn
# die Quelle keine ``asset_class``-Spalte mitliefert. Bewusst grob.
_ASSET_CLASS_HEURISTIK: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^cash\b|^liquidit", re.I), "Cash"),
    (re.compile(r"^gold\b|silber|platin|edelmetall", re.I), "Edelmetalle"),
    (re.compile(r"\banleihe|\bbond\b|\brente\b", re.I), "Renten"),
    (re.compile(r"\baktie|\bequity\b|\bstock\b|\bshare\b", re.I), "Aktien"),
    (re.compile(r"\bfonds|\bfund\b|\betf\b", re.I), "Sonstiges"),
]


def _parse_german_number(raw: Any) -> Optional[float]:
    """Akzeptiert ``1.234,56`` und ``1,234.56`` und reine Zahlen."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    # Entferne Waehrungssymbole und Leerzeichen.
    s = re.sub(r"[A-Z€$£\s%]", "", s, flags=re.I)
    if not s:
        return None
    # Beide Trenner vorhanden? Annahme: letzter ist Dezimaltrenner.
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _classify_asset(isin: Optional[str], name: str) -> Optional[str]:
    if name:
        for rx, cls in _ASSET_CLASS_HEURISTIK:
            if rx.search(name):
                return cls
    if isin:
        prefix = isin.strip()[:2].upper()
        # Vereinfacht: DE/US/etc. — keine echte ISIN-Klassifikation ohne
        # externe Quelle. Fallback bleibt "Sonstiges".
        if prefix:
            return "Sonstiges"
    return None


def _normalize_headers(columns: List[str]) -> Dict[str, str]:
    """Liefert ``{quellspalte: kanonisches_feld}``-Mapping."""
    out = {}
    for col in columns:
        if col is None:
            continue
        norm = str(col).strip().lower().strip('"')
        # Mehrfach-Whitespace zusammenziehen.
        norm = re.sub(r"\s+", " ", norm)
        canon = _HEADER_ALIASES.get(norm)
        if canon:
            out[col] = canon
    return out


def _read_csv(path: Path) -> List[Dict[str, Any]]:
    import pandas as pd  # type: ignore

    last_err: Optional[Exception] = None
    for enc in ("utf-8", "utf-8-sig", "iso-8859-1", "cp1252"):
        for sep in (";", ",", "\t"):
            try:
                df = pd.read_csv(path, encoding=enc, sep=sep, dtype=str)
                if len(df.columns) >= 2:
                    return df.fillna("").to_dict(orient="records")
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue
    raise ValueError(f"CSV konnte nicht gelesen werden: {last_err}")


def _read_xlsx(path: Path) -> List[Dict[str, Any]]:
    import pandas as pd  # type: ignore

    df = pd.read_excel(path, dtype=str)
    return df.fillna("").to_dict(orient="records")


def parse_snapshot_file(path: str) -> List[Dict[str, Any]]:
    """Liest CSV/XLSX und liefert eine Liste normierter Positions-Dicts.

    Felder pro Dict: ``isin``, ``wkn``, ``name``, ``asset_class``,
    ``quantity``, ``currency``, ``market_value``, ``weight_percent``.
    Werte sind durchgaengig Strings (oder ``None``), damit die Speicherung
    in den SQLite-Spalten praezisionserhaltend bleibt.
    """
    p = Path(path)
    ext = p.suffix.lower()
    if ext in (".xlsx", ".xls"):
        rows = _read_xlsx(p)
    elif ext == ".csv":
        rows = _read_csv(p)
    else:
        raise ValueError(f"Nicht unterstuetztes Format: {ext}")

    if not rows:
        return []

    header_map = _normalize_headers(list(rows[0].keys()))
    if "name" not in header_map.values():
        raise ValueError(
            "Pflichtspalte 'Name'/'Bezeichnung' nicht gefunden. "
            f"Erkannte Spalten: {list(rows[0].keys())}"
        )

    positions: List[Dict[str, Any]] = []
    for raw_row in rows:
        rec: Dict[str, Any] = {
            "isin": None, "wkn": None, "name": None, "asset_class": None,
            "quantity": None, "currency": None, "market_value": None,
            "weight_percent": None,
        }
        for src_col, canon in header_map.items():
            val = raw_row.get(src_col)
            if val is None or str(val).strip() == "":
                continue
            rec[canon] = str(val).strip().strip('"')

        if not rec["name"]:
            continue

        # Cash- und Edelmetall-Heuristik nachziehen.
        if not rec["asset_class"]:
            rec["asset_class"] = _classify_asset(rec.get("isin"), rec["name"] or "")

        # Numerische Felder leicht normalisieren (als String belassen, aber
        # auf einheitlichen Punkt-Dezimaltrenner setzen, damit spaetere
        # Aggregation in der Route ohne Locale-Hick funktioniert).
        for num_field in ("quantity", "market_value", "weight_percent"):
            num = _parse_german_number(rec.get(num_field))
            if num is not None:
                rec[num_field] = f"{num}"

        positions.append(rec)

    return positions


def build_snapshot_records(
    portfolio_id: str,
    file_path: str,
    stichtag: datetime,
    imported_by: Optional[str] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Konstruiert das ``PortfolioSnapshot``- plus ``Position``-Records.

    Aufrufer ist verantwortlich, beides per SQLAlchemy zu persistieren —
    diese Funktion bleibt bewusst dependency-arm (kein DB-Zugriff), damit
    sie isoliert testbar ist.
    """
    positions = parse_snapshot_file(file_path)

    total = 0.0
    for p in positions:
        mv = _parse_german_number(p.get("market_value"))
        if mv is not None:
            total += mv

    snapshot = {
        "id": uuid.uuid4().hex,
        "portfolio_id": portfolio_id,
        "stichtag": stichtag,
        "imported_by": imported_by,
        "source_filename": Path(file_path).name,
        "total_value": f"{total:.2f}" if total else None,
    }
    return snapshot, positions


__all__ = [
    "build_snapshot_records",
    "parse_snapshot_file",
]
