# routes/onboarding_routes.py
"""Onboarding-Routen fuer Meeder & Seifer (Phase 4).

Owner-scoped CRUD fuer ``OnboardingProcess``-Eintraege plus Checklist-
Updates und Document-Anhaenge. Die Checkliste lebt als JSON in der
Tabelle — keine separate Steps-Tabelle, weil die Schrittlisten je
Onboarding-Typ stark variieren und der Bearbeitungs-Workflow im Skill
``onboarding-unterstuetzung`` zentral gesteuert wird.

Auslassungen Phase 4 (siehe Plan):
- Kein Mehrnutzer-Onboarding (Teamleitung sieht alle) → Phase 5
- Keine SLA-Eskalation bei Fristueberschreitung → Phase 5
- Kein automatischer Versand der Welcome-Mappe → Phase 5
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

from core.database import Document, OnboardingProcess, SessionLocal
from src.auth_helpers import get_current_user

logger = logging.getLogger(__name__)

_ALLOWED_STATUS = ("started", "docs_pending", "review", "completed", "abandoned")
_ALLOWED_TYPES = ("vermoegensverwaltung", "family_office", "beratung")


def _parse_dt(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(raw[: len(fmt)], fmt)
        except ValueError:
            continue
    raise HTTPException(400, f"Datum '{raw}' konnte nicht geparst werden")


def _to_dict(o: OnboardingProcess, attached: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        checklist = json.loads(o.checklist_json) if o.checklist_json else []
    except Exception:
        checklist = []
    return {
        "id": o.id,
        "owner": o.owner,
        "mandant_name": o.mandant_name,
        "onboarding_type": o.onboarding_type or "vermoegensverwaltung",
        "status": o.status or "started",
        "started_at": o.started_at.isoformat() + "Z" if o.started_at else None,
        "target_completion_date": o.target_completion_date.isoformat() + "Z" if o.target_completion_date else None,
        "completed_at": o.completed_at.isoformat() + "Z" if o.completed_at else None,
        "checklist": checklist,
        "welcome_document_id": o.welcome_document_id,
        "notes": o.notes or "",
        "welcome_document": attached or None,
        "created_at": o.created_at.isoformat() + "Z" if o.created_at else None,
        "updated_at": o.updated_at.isoformat() + "Z" if o.updated_at else None,
    }


def _doc_summary(doc: Document) -> Dict[str, Any]:
    return {
        "id": doc.id,
        "title": doc.title,
        "release_status": getattr(doc, "release_status", "draft") or "draft",
    }


def _default_checklist(onboarding_type: str) -> List[Dict[str, Any]]:
    """Default-Checklisten je Onboarding-Typ. Pilot-Stand; kann der
    Mitarbeiter im laufenden Prozess anpassen."""
    base = [
        {"step": "Anlegerprofil (WpHG) ausfuellen", "status": "pending"},
        {"step": "Identifikation (PostIdent/VideoIdent)", "status": "pending"},
        {"step": "Verwaltungsvertrag unterschrieben", "status": "pending"},
        {"step": "Depot-/Konto-Eroeffnung bei depotfuehrender Bank", "status": "pending"},
        {"step": "Vermoegensueberleitung beauftragt", "status": "pending"},
        {"step": "Willkommensschreiben versandt", "status": "pending"},
    ]
    if onboarding_type == "family_office":
        base += [
            {"step": "Familienstruktur und Stiftungen erfasst", "status": "pending"},
            {"step": "Vermoegensuebersicht (Konsolidierung) konsolidiert", "status": "pending"},
            {"step": "Reportingfrequenz vereinbart", "status": "pending"},
        ]
    elif onboarding_type == "beratung":
        base += [
            {"step": "Beratungsumfang abgegrenzt", "status": "pending"},
            {"step": "Erstberatungstermin durchgefuehrt", "status": "pending"},
        ]
    return base


def setup_onboarding_routes():
    router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

    @router.get("")
    def list_onboardings(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        with SessionLocal() as db:
            rows = (
                db.query(OnboardingProcess)
                .filter(OnboardingProcess.owner == user)
                .order_by(OnboardingProcess.started_at.desc())
                .all()
            )
            return {"onboardings": [_to_dict(o) for o in rows]}

    @router.post("")
    def create_onboarding(request: Request, payload: Dict[str, Any]):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        mandant_name = (payload.get("mandant_name") or "").strip()
        if not mandant_name:
            raise HTTPException(400, "Pflichtfeld 'mandant_name' fehlt")
        onboarding_type = (payload.get("onboarding_type") or "vermoegensverwaltung").lower()
        if onboarding_type not in _ALLOWED_TYPES:
            raise HTTPException(400, f"onboarding_type muss einer von {_ALLOWED_TYPES} sein")
        target = _parse_dt(payload.get("target_completion_date"))
        checklist = payload.get("checklist")
        if not isinstance(checklist, list):
            checklist = _default_checklist(onboarding_type)
        with SessionLocal() as db:
            o = OnboardingProcess(
                id=uuid.uuid4().hex,
                owner=user,
                mandant_name=mandant_name,
                onboarding_type=onboarding_type,
                status="started",
                target_completion_date=target,
                checklist_json=json.dumps(checklist, ensure_ascii=False),
                notes=(payload.get("notes") or "").strip() or None,
            )
            db.add(o)
            db.commit()
            db.refresh(o)
            return _to_dict(o)

    @router.get("/{onboarding_id}")
    def get_onboarding(request: Request, onboarding_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            o = db.query(OnboardingProcess).filter(OnboardingProcess.id == onboarding_id).first()
            if not o or o.owner != user:
                raise HTTPException(404, "Onboarding-Prozess nicht gefunden")
            attached = None
            if o.welcome_document_id:
                doc = db.query(Document).filter(Document.id == o.welcome_document_id).first()
                attached = _doc_summary(doc) if doc else None
            return _to_dict(o, attached=attached)

    @router.put("/{onboarding_id}")
    def update_onboarding(request: Request, onboarding_id: str, payload: Dict[str, Any]):
        user = get_current_user(request)
        with SessionLocal() as db:
            o = db.query(OnboardingProcess).filter(OnboardingProcess.id == onboarding_id).first()
            if not o or o.owner != user:
                raise HTTPException(404, "Onboarding-Prozess nicht gefunden")
            if "status" in payload:
                st = (payload["status"] or "").lower()
                if st in _ALLOWED_STATUS:
                    o.status = st
                    if st == "completed":
                        o.completed_at = datetime.utcnow()
            if "target_completion_date" in payload:
                o.target_completion_date = _parse_dt(payload["target_completion_date"])
            if "notes" in payload:
                o.notes = (payload["notes"] or "").strip() or None
            if "mandant_name" in payload:
                mn = (payload["mandant_name"] or "").strip()
                if mn:
                    o.mandant_name = mn
            if "checklist" in payload and isinstance(payload["checklist"], list):
                o.checklist_json = json.dumps(payload["checklist"], ensure_ascii=False)
            if "welcome_document_id" in payload:
                o.welcome_document_id = payload["welcome_document_id"] or None
            db.commit()
            db.refresh(o)
            return _to_dict(o)

    @router.delete("/{onboarding_id}")
    def delete_onboarding(request: Request, onboarding_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            o = db.query(OnboardingProcess).filter(OnboardingProcess.id == onboarding_id).first()
            if not o or o.owner != user:
                raise HTTPException(404, "Onboarding-Prozess nicht gefunden")
            db.delete(o)
            db.commit()
        return {"deleted": onboarding_id}

    @router.post("/{onboarding_id}/checklist")
    def update_checklist_step(request: Request, onboarding_id: str, payload: Dict[str, Any]):
        """Update eines einzelnen Schritts: ``{step_index: int, status:
        "pending|done|skipped", evidence_document_id?: str}``. Wirft 400
        wenn der Index ausserhalb der Liste liegt."""
        user = get_current_user(request)
        idx = payload.get("step_index")
        new_status = (payload.get("status") or "").lower()
        if not isinstance(idx, int):
            raise HTTPException(400, "step_index (int) fehlt")
        if new_status not in ("pending", "done", "skipped"):
            raise HTTPException(400, "status muss pending|done|skipped sein")
        with SessionLocal() as db:
            o = db.query(OnboardingProcess).filter(OnboardingProcess.id == onboarding_id).first()
            if not o or o.owner != user:
                raise HTTPException(404, "Onboarding-Prozess nicht gefunden")
            try:
                checklist = json.loads(o.checklist_json) if o.checklist_json else []
            except Exception:
                checklist = []
            if idx < 0 or idx >= len(checklist):
                raise HTTPException(400, f"step_index {idx} ausserhalb der Liste (0..{len(checklist)-1})")
            checklist[idx]["status"] = new_status
            if payload.get("evidence_document_id"):
                checklist[idx]["evidence_document_id"] = payload["evidence_document_id"]
            o.checklist_json = json.dumps(checklist, ensure_ascii=False)
            db.commit()
            db.refresh(o)
            return _to_dict(o)

    return router
