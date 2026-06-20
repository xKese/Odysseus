# routes/portfolio_routes.py
"""Portfolio-Routen fuer Meeder & Seifer (Phase 2).

Owner-scoped CRUD + Snapshot-Upload + Aggregations-Endpunkte. Keine
Rollen-ACL — Portfolio-Daten sind streng mandantenbezogen und gehoeren
ausschliesslich dem Eigentuemer-Account. Wenn das spaeter team-weit
sichtbar werden soll (z.B. Vermoegensverwalter-Pool), wird das ACL-
Muster aus ``routes/knowledge_routes.py`` uebernommen.

Auslassungen Phase 2 (siehe Plan):
- TWR/MWR-Performance ueber Snapshots → Phase 2.5
- Live-Daten-Connector (MCP) → Phase 3
- Mandanten-Login → Phase 4
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from core.database import (
    Portfolio,
    PortfolioSnapshot,
    Position,
    SessionLocal,
)
from src.auth_helpers import get_current_user
from src.portfolio_import import build_snapshot_records
from src.upload_limits import read_upload_limited

logger = logging.getLogger(__name__)

_DEFAULT_UPLOAD_LIMIT = 20 * 1024 * 1024  # 20 MB


def _portfolio_to_dict(p: Portfolio, snapshot_count: int = 0) -> Dict[str, Any]:
    return {
        "id": p.id,
        "mandant_name": p.mandant_name,
        "description": p.description or "",
        "base_currency": p.base_currency or "EUR",
        "owner": p.owner,
        "snapshot_count": snapshot_count,
        "created_at": p.created_at.isoformat() + "Z" if p.created_at else None,
        "updated_at": p.updated_at.isoformat() + "Z" if p.updated_at else None,
    }


def _snapshot_to_dict(s: PortfolioSnapshot, position_count: int = 0) -> Dict[str, Any]:
    return {
        "id": s.id,
        "portfolio_id": s.portfolio_id,
        "stichtag": s.stichtag.isoformat() + "Z" if s.stichtag else None,
        "imported_by": s.imported_by,
        "source_filename": s.source_filename,
        "total_value": s.total_value,
        "position_count": position_count,
        "created_at": s.created_at.isoformat() + "Z" if s.created_at else None,
    }


def _position_to_dict(p: Position) -> Dict[str, Any]:
    return {
        "id": p.id,
        "isin": p.isin,
        "wkn": p.wkn,
        "name": p.name,
        "asset_class": p.asset_class,
        "quantity": p.quantity,
        "currency": p.currency,
        "market_value": p.market_value,
        "weight_percent": p.weight_percent,
    }


def _parse_stichtag(raw: Optional[str]) -> datetime:
    if not raw:
        return datetime.utcnow()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(raw[: len(fmt) if "T" in fmt else 10], fmt)
        except ValueError:
            continue
    raise HTTPException(400, f"Stichtag '{raw}' konnte nicht geparst werden (erlaubt: YYYY-MM-DD oder TT.MM.JJJJ)")


def setup_portfolio_routes():
    router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])

    # ------------------------------------------------------------------
    # Portfolio CRUD
    # ------------------------------------------------------------------

    @router.get("")
    def list_portfolios(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        with SessionLocal() as db:
            rows = (
                db.query(Portfolio)
                .filter(Portfolio.owner == user)
                .order_by(Portfolio.mandant_name)
                .all()
            )
            out = []
            for p in rows:
                snap_count = (
                    db.query(PortfolioSnapshot)
                    .filter(PortfolioSnapshot.portfolio_id == p.id)
                    .count()
                )
                out.append(_portfolio_to_dict(p, snapshot_count=snap_count))
            return {"portfolios": out}

    @router.post("")
    def create_portfolio(request: Request, payload: Dict[str, Any]):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        mandant_name = (payload.get("mandant_name") or "").strip()
        if not mandant_name:
            raise HTTPException(400, "Pflichtfeld 'mandant_name' fehlt")
        description = (payload.get("description") or "").strip()
        base_currency = (payload.get("base_currency") or "EUR").strip() or "EUR"
        with SessionLocal() as db:
            p = Portfolio(
                id=uuid.uuid4().hex,
                owner=user,
                mandant_name=mandant_name,
                description=description,
                base_currency=base_currency,
            )
            db.add(p)
            db.commit()
            db.refresh(p)
            return _portfolio_to_dict(p, snapshot_count=0)

    @router.get("/{portfolio_id}")
    def get_portfolio(request: Request, portfolio_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p:
                raise HTTPException(404, "Portfolio nicht gefunden")
            if p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")
            snap_count = (
                db.query(PortfolioSnapshot)
                .filter(PortfolioSnapshot.portfolio_id == p.id)
                .count()
            )
            return _portfolio_to_dict(p, snapshot_count=snap_count)

    @router.delete("/{portfolio_id}")
    def delete_portfolio(request: Request, portfolio_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p or p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")
            db.delete(p)
            db.commit()
        return {"deleted": portfolio_id}

    # ------------------------------------------------------------------
    # Snapshots
    # ------------------------------------------------------------------

    @router.get("/{portfolio_id}/snapshots")
    def list_snapshots(request: Request, portfolio_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p or p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")
            snaps = (
                db.query(PortfolioSnapshot)
                .filter(PortfolioSnapshot.portfolio_id == portfolio_id)
                .order_by(PortfolioSnapshot.stichtag.desc())
                .all()
            )
            out = []
            for s in snaps:
                pos_count = (
                    db.query(Position)
                    .filter(Position.snapshot_id == s.id)
                    .count()
                )
                out.append(_snapshot_to_dict(s, position_count=pos_count))
            return {"snapshots": out}

    @router.post("/{portfolio_id}/snapshots")
    async def upload_snapshot(
        request: Request,
        portfolio_id: str,
        file: UploadFile = File(...),
        stichtag: Optional[str] = Form(None),
    ):
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p or p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")

        stichtag_dt = _parse_stichtag(stichtag)
        blob = await read_upload_limited(file, _DEFAULT_UPLOAD_LIMIT, "Portfolio-Snapshot")
        filename = file.filename or "snapshot.csv"

        ext = os.path.splitext(filename)[1].lower() or ".csv"
        suffix = ext if ext in (".csv", ".xlsx", ".xls") else ".csv"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as fh:
            fh.write(blob)
            tmp_path = fh.name
        try:
            snapshot_rec, position_recs = build_snapshot_records(
                portfolio_id=portfolio_id,
                file_path=tmp_path,
                stichtag=stichtag_dt,
                imported_by=user,
            )
            snapshot_rec["source_filename"] = filename
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        if not position_recs:
            raise HTTPException(400, "Keine Positionen erkannt — Spaltennamen pruefen")

        with SessionLocal() as db:
            snap = PortfolioSnapshot(**snapshot_rec)
            db.add(snap)
            db.flush()  # ID materialisieren
            for rec in position_recs:
                pos = Position(snapshot_id=snap.id, **rec)
                db.add(pos)
            db.commit()
            db.refresh(snap)
            return _snapshot_to_dict(snap, position_count=len(position_recs))

    @router.get("/{portfolio_id}/snapshots/{snapshot_id}")
    def get_snapshot(request: Request, portfolio_id: str, snapshot_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p or p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")
            s = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.id == snapshot_id,
                PortfolioSnapshot.portfolio_id == portfolio_id,
            ).first()
            if not s:
                raise HTTPException(404, "Snapshot nicht gefunden")
            positions = (
                db.query(Position)
                .filter(Position.snapshot_id == snapshot_id)
                .order_by(Position.id)
                .all()
            )
            return {
                "snapshot": _snapshot_to_dict(s, position_count=len(positions)),
                "positions": [_position_to_dict(pos) for pos in positions],
            }

    @router.delete("/{portfolio_id}/snapshots/{snapshot_id}")
    def delete_snapshot(request: Request, portfolio_id: str, snapshot_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p or p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")
            s = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.id == snapshot_id,
                PortfolioSnapshot.portfolio_id == portfolio_id,
            ).first()
            if not s:
                raise HTTPException(404, "Snapshot nicht gefunden")
            db.delete(s)
            db.commit()
        return {"deleted": snapshot_id}

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------

    @router.get("/{portfolio_id}/snapshots/{snapshot_id}/summary")
    def snapshot_summary(request: Request, portfolio_id: str, snapshot_id: str):
        """Aggregierte Sicht: Allokation je Asset-Klasse, Top-5 Positionen,
        Gesamtwert. Bereitet die Daten so auf, wie der Skill
        ``portfolio-aufbereitung`` sie konsumiert."""
        user = get_current_user(request)
        with SessionLocal() as db:
            p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            if not p or p.owner != user:
                raise HTTPException(404, "Portfolio nicht gefunden")
            s = db.query(PortfolioSnapshot).filter(
                PortfolioSnapshot.id == snapshot_id,
                PortfolioSnapshot.portfolio_id == portfolio_id,
            ).first()
            if not s:
                raise HTTPException(404, "Snapshot nicht gefunden")
            positions = (
                db.query(Position)
                .filter(Position.snapshot_id == snapshot_id)
                .all()
            )

        allocation: Dict[str, float] = defaultdict(float)
        total = 0.0
        for pos in positions:
            try:
                mv = float(pos.market_value) if pos.market_value else 0.0
            except (TypeError, ValueError):
                mv = 0.0
            total += mv
            cls = pos.asset_class or "Sonstiges"
            allocation[cls] += mv

        alloc_list = sorted(
            [
                {
                    "asset_class": k,
                    "market_value": round(v, 2),
                    "weight_percent": round((v / total * 100.0), 2) if total else None,
                }
                for k, v in allocation.items()
            ],
            key=lambda x: -(x["market_value"] or 0),
        )

        def _mv(pos):
            try:
                return float(pos.market_value) if pos.market_value else 0.0
            except (TypeError, ValueError):
                return 0.0

        top_positions = sorted(positions, key=_mv, reverse=True)[:5]
        return {
            "portfolio_id": portfolio_id,
            "snapshot_id": snapshot_id,
            "stichtag": s.stichtag.isoformat() + "Z" if s.stichtag else None,
            "total_value": round(total, 2),
            "position_count": len(positions),
            "allocation": alloc_list,
            "top_positions": [_position_to_dict(pos) for pos in top_positions],
            "base_currency": p.base_currency or "EUR",
        }

    return router
