# routes/meeting_routes.py
"""Anlageausschuss-Sitzungen fuer Meeder & Seifer (Phase 2).

Verbindet Anlageausschuss-Termine mit den Dokumenten (Reports,
Briefings, Beschluesse), die im Vorfeld oder in der Sitzung entstehen.
Bewusst schlank — Beschluesse selbst leben weiterhin als ``Document``-
Eintraege mit ``release_status`` aus Phase 1; hier sind nur die
Verknuepfungen und die Termin-Metadaten gehalten.

Owner-Scope: Sitzungen sind dem Anlegenden zugeordnet. Eine team-
weite Sichtbarkeit waere fuer den Anlageausschuss naturgemaess
wuenschenswert — wird in Phase 3 ueber Rollen-ACL nachgezogen (siehe
Hauswissen-Plattform-Muster).

Auslassungen Phase 2 (siehe Plan):
- Genehmigungs-Workflow mehrerer Teilnehmer → Phase 3
- Kalender-Integration (CalDAV) → Phase 4 (vorhandene Calendar-API
  bleibt unabhaengig)
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

from core.database import Document, MeetingMinutes, SessionLocal
from src.auth_helpers import get_current_user

logger = logging.getLogger(__name__)

_ALLOWED_STATUS = ("planned", "held", "protocol", "approved")
_ALLOWED_TYPES = ("anlageausschuss", "mandant", "extern")


def _parse_dt(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d", "%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(raw[: len(fmt)], fmt)
        except ValueError:
            continue
    raise HTTPException(400, f"Datum '{raw}' konnte nicht geparst werden")


def _meeting_to_dict(m: MeetingMinutes, attached: Optional[List[Dict]] = None) -> Dict[str, Any]:
    try:
        attendees = json.loads(m.attendees_json) if m.attendees_json else []
    except Exception:
        attendees = []
    try:
        decisions = json.loads(m.decision_documents_json) if m.decision_documents_json else []
    except Exception:
        decisions = []
    return {
        "id": m.id,
        "owner": m.owner,
        "meeting_date": m.meeting_date.isoformat() + "Z" if m.meeting_date else None,
        "title": m.title,
        "location": m.location,
        "attendees": attendees,
        "status": m.status or "planned",
        "minute_document_id": m.minute_document_id,
        "decision_documents": decisions,
        "attached_documents": attached or [],
        "next_meeting_date": m.next_meeting_date.isoformat() + "Z" if m.next_meeting_date else None,
        "meeting_type": getattr(m, "meeting_type", None) or "anlageausschuss",
        "mandant_name": getattr(m, "mandant_name", None),
        "preparation_document_id": getattr(m, "preparation_document_id", None),
        "created_at": m.created_at.isoformat() + "Z" if m.created_at else None,
        "updated_at": m.updated_at.isoformat() + "Z" if m.updated_at else None,
    }


def _doc_summary(doc: Document) -> Dict[str, Any]:
    return {
        "id": doc.id,
        "title": doc.title,
        "release_status": getattr(doc, "release_status", "draft") or "draft",
        "released_by": getattr(doc, "released_by", None),
        "released_at": doc.released_at.isoformat() + "Z" if getattr(doc, "released_at", None) else None,
    }


def setup_meeting_routes():
    router = APIRouter(prefix="/api/meetings", tags=["meetings"])

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @router.get("")
    def list_meetings(request: Request, type: Optional[str] = None):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        with SessionLocal() as db:
            q = (
                db.query(MeetingMinutes)
                .filter(MeetingMinutes.owner == user)
            )
            if type and type.lower() in _ALLOWED_TYPES:
                q = q.filter(MeetingMinutes.meeting_type == type.lower())
            rows = q.order_by(MeetingMinutes.meeting_date.desc()).all()
            return {"meetings": [_meeting_to_dict(m) for m in rows]}

    @router.get("/upcoming")
    def list_upcoming(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        now = datetime.utcnow()
        with SessionLocal() as db:
            rows = (
                db.query(MeetingMinutes)
                .filter(MeetingMinutes.owner == user)
                .filter(MeetingMinutes.meeting_date >= now)
                .order_by(MeetingMinutes.meeting_date)
                .all()
            )
            return {"meetings": [_meeting_to_dict(m) for m in rows]}

    @router.post("")
    def create_meeting(request: Request, payload: Dict[str, Any]):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        title = (payload.get("title") or "").strip()
        if not title:
            raise HTTPException(400, "Pflichtfeld 'title' fehlt")
        meeting_date = _parse_dt(payload.get("meeting_date"))
        if not meeting_date:
            raise HTTPException(400, "Pflichtfeld 'meeting_date' fehlt")
        attendees = payload.get("attendees") or []
        if not isinstance(attendees, list):
            raise HTTPException(400, "'attendees' muss eine Liste sein")
        status = (payload.get("status") or "planned").lower()
        if status not in _ALLOWED_STATUS:
            raise HTTPException(400, f"status muss einer von {_ALLOWED_STATUS} sein")
        meeting_type = (payload.get("meeting_type") or "anlageausschuss").lower()
        if meeting_type not in _ALLOWED_TYPES:
            raise HTTPException(400, f"meeting_type muss einer von {_ALLOWED_TYPES} sein")
        mandant_name = (payload.get("mandant_name") or "").strip() or None
        if meeting_type == "mandant" and not mandant_name:
            raise HTTPException(400, "Bei meeting_type=mandant ist mandant_name Pflicht")

        with SessionLocal() as db:
            m = MeetingMinutes(
                id=uuid.uuid4().hex,
                owner=user,
                meeting_date=meeting_date,
                title=title,
                location=(payload.get("location") or "").strip() or None,
                attendees_json=json.dumps(attendees, ensure_ascii=False),
                status=status,
                decision_documents_json=json.dumps([]),
                next_meeting_date=_parse_dt(payload.get("next_meeting_date")),
                meeting_type=meeting_type,
                mandant_name=mandant_name,
            )
            db.add(m)
            db.commit()
            db.refresh(m)
            return _meeting_to_dict(m)

    @router.get("/{meeting_id}")
    def get_meeting(request: Request, meeting_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            m = db.query(MeetingMinutes).filter(MeetingMinutes.id == meeting_id).first()
            if not m or m.owner != user:
                raise HTTPException(404, "Sitzung nicht gefunden")
            # Documents derefenzieren
            doc_ids = []
            try:
                doc_ids = json.loads(m.decision_documents_json) or []
            except Exception:
                doc_ids = []
            if m.minute_document_id:
                doc_ids = list(dict.fromkeys([m.minute_document_id, *doc_ids]))
            attached = []
            if doc_ids:
                docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
                by_id = {d.id: d for d in docs}
                # Reihenfolge beibehalten
                attached = [_doc_summary(by_id[i]) for i in doc_ids if i in by_id]
            return _meeting_to_dict(m, attached=attached)

    @router.put("/{meeting_id}")
    def update_meeting(request: Request, meeting_id: str, payload: Dict[str, Any]):
        user = get_current_user(request)
        with SessionLocal() as db:
            m = db.query(MeetingMinutes).filter(MeetingMinutes.id == meeting_id).first()
            if not m or m.owner != user:
                raise HTTPException(404, "Sitzung nicht gefunden")
            if "title" in payload:
                title = (payload["title"] or "").strip()
                if title:
                    m.title = title
            if "meeting_date" in payload:
                md = _parse_dt(payload["meeting_date"])
                if md:
                    m.meeting_date = md
            if "location" in payload:
                m.location = (payload["location"] or "").strip() or None
            if "attendees" in payload and isinstance(payload["attendees"], list):
                m.attendees_json = json.dumps(payload["attendees"], ensure_ascii=False)
            if "status" in payload:
                st = (payload["status"] or "").lower()
                if st in _ALLOWED_STATUS:
                    m.status = st
            if "minute_document_id" in payload:
                m.minute_document_id = payload["minute_document_id"] or None
            if "preparation_document_id" in payload:
                m.preparation_document_id = payload["preparation_document_id"] or None
            if "next_meeting_date" in payload:
                m.next_meeting_date = _parse_dt(payload["next_meeting_date"])
            if "meeting_type" in payload:
                mt = (payload["meeting_type"] or "").lower()
                if mt in _ALLOWED_TYPES:
                    m.meeting_type = mt
            if "mandant_name" in payload:
                m.mandant_name = (payload["mandant_name"] or "").strip() or None
            db.commit()
            db.refresh(m)
            return _meeting_to_dict(m)

    @router.delete("/{meeting_id}")
    def delete_meeting(request: Request, meeting_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            m = db.query(MeetingMinutes).filter(MeetingMinutes.id == meeting_id).first()
            if not m or m.owner != user:
                raise HTTPException(404, "Sitzung nicht gefunden")
            db.delete(m)
            db.commit()
        return {"deleted": meeting_id}

    # ------------------------------------------------------------------
    # Documents an Sitzung haengen
    # ------------------------------------------------------------------

    @router.post("/{meeting_id}/documents")
    def attach_document(request: Request, meeting_id: str, payload: Dict[str, Any]):
        user = get_current_user(request)
        doc_id = (payload.get("document_id") or "").strip()
        role = (payload.get("role") or "decision").lower()  # decision | protocol
        if not doc_id:
            raise HTTPException(400, "document_id fehlt")
        with SessionLocal() as db:
            m = db.query(MeetingMinutes).filter(MeetingMinutes.id == meeting_id).first()
            if not m or m.owner != user:
                raise HTTPException(404, "Sitzung nicht gefunden")
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                raise HTTPException(404, "Dokument nicht gefunden")
            if (doc.owner or "") != (user or ""):
                raise HTTPException(403, "Dokument gehoert nicht dem aktuellen Nutzer")
            if role == "protocol":
                m.minute_document_id = doc_id
            else:
                try:
                    cur = json.loads(m.decision_documents_json) if m.decision_documents_json else []
                except Exception:
                    cur = []
                if doc_id not in cur:
                    cur.append(doc_id)
                m.decision_documents_json = json.dumps(cur, ensure_ascii=False)
            db.commit()
            db.refresh(m)
            return _meeting_to_dict(m)

    @router.post("/{meeting_id}/prepare")
    def attach_preparation(request: Request, meeting_id: str, payload: Dict[str, Any]):
        """Phase 4 (Meeder & Seifer): Briefing-Mappe an die Sitzung als
        Vorbereitungs-Dokument haengen. Setzt ``preparation_document_id``
        und beruehrt den Status nicht — der bleibt im Mitarbeiter-Workflow.
        """
        user = get_current_user(request)
        doc_id = (payload.get("document_id") or "").strip()
        if not doc_id:
            raise HTTPException(400, "document_id fehlt")
        with SessionLocal() as db:
            m = db.query(MeetingMinutes).filter(MeetingMinutes.id == meeting_id).first()
            if not m or m.owner != user:
                raise HTTPException(404, "Sitzung nicht gefunden")
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                raise HTTPException(404, "Dokument nicht gefunden")
            if (doc.owner or "") != (user or ""):
                raise HTTPException(403, "Dokument gehoert nicht dem aktuellen Nutzer")
            m.preparation_document_id = doc_id
            db.commit()
            db.refresh(m)
            return _meeting_to_dict(m)

    @router.delete("/{meeting_id}/documents/{doc_id}")
    def detach_document(request: Request, meeting_id: str, doc_id: str):
        user = get_current_user(request)
        with SessionLocal() as db:
            m = db.query(MeetingMinutes).filter(MeetingMinutes.id == meeting_id).first()
            if not m or m.owner != user:
                raise HTTPException(404, "Sitzung nicht gefunden")
            removed = False
            if m.minute_document_id == doc_id:
                m.minute_document_id = None
                removed = True
            try:
                cur = json.loads(m.decision_documents_json) if m.decision_documents_json else []
            except Exception:
                cur = []
            if doc_id in cur:
                cur = [x for x in cur if x != doc_id]
                m.decision_documents_json = json.dumps(cur, ensure_ascii=False)
                removed = True
            if not removed:
                raise HTTPException(404, "Document war nicht verknuepft")
            db.commit()
            db.refresh(m)
            return _meeting_to_dict(m)

    return router
