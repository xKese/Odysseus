# routes/template_routes.py
"""Hausvorlagen-API (Meeder & Seifer, Phase 1).

Vorlagen liegen als Markdown- (oder ggf. DOCX-) Dateien unter
``data/templates/<category>/<slug>.<ext>``. Die Render-Funktion ersetzt
Platzhalter der Form ``{{ key }}`` oder ``{{ obj.feld }}`` durch Werte
aus dem uebergebenen JSON-Body. Unaufgeloeste Platzhalter bleiben
woertlich erhalten, damit der Nutzer sieht, was noch zu fuellen ist —
ein 500er bei fehlendem Feld waere fuer einen Entwurfs-Workflow zu
strikt.

Auslassungen Phase 1: keine Versionierung, keine Editor-UI, keine
schreibenden Endpunkte. Vorlagen werden direkt im Repo (oder per
``docker cp`` ins Volume) gepflegt; ein Editor folgt in Phase 4.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

from core.middleware import require_admin
from src.auth_helpers import get_current_user

logger = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z_][\w.]*)\s*\}\}")
_ALLOWED_EXTS = (".md", ".txt", ".html")


def _templates_root() -> str:
    # data/ ist mit dem Container-Volume gebunden; relativ zum App-Root reicht.
    return os.path.abspath(os.path.join("data", "templates"))


def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", text or "")[:80]


def _list_disk() -> List[Dict]:
    root = _templates_root()
    if not os.path.isdir(root):
        return []
    out: List[Dict] = []
    for category in sorted(os.listdir(root)):
        cat_path = os.path.join(root, category)
        if not os.path.isdir(cat_path):
            continue
        for fname in sorted(os.listdir(cat_path)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in _ALLOWED_EXTS:
                continue
            slug = os.path.splitext(fname)[0]
            out.append({
                "id": f"{category}/{slug}",
                "category": category,
                "slug": slug,
                "filename": fname,
                "size": os.path.getsize(os.path.join(cat_path, fname)),
            })
    return out


def _read_template(template_id: str) -> Optional[Dict]:
    parts = (template_id or "").split("/")
    if len(parts) != 2:
        return None
    category, slug = _safe_slug(parts[0]), _safe_slug(parts[1])
    if not category or not slug:
        return None
    root = _templates_root()
    cat_path = os.path.join(root, category)
    if not os.path.isdir(cat_path):
        return None
    for ext in _ALLOWED_EXTS:
        path = os.path.join(cat_path, f"{slug}{ext}")
        if os.path.isfile(path):
            # Path-Traversal-Schutz: aufgeloeste Datei muss unter root liegen.
            if not os.path.commonpath([os.path.abspath(path), root]) == root:
                return None
            with open(path, encoding="utf-8") as f:
                return {
                    "id": template_id,
                    "category": category,
                    "slug": slug,
                    "filename": f"{slug}{ext}",
                    "content": f.read(),
                }
    return None


def _resolve(payload: Dict, dotted_key: str) -> Optional[str]:
    """Liefert ``payload[a][b][c]`` fuer ``a.b.c``; ``None`` falls Pfad
    unbekannt. Akzeptiert dabei sowohl Dicts als auch Listen (via
    Integer-Index)."""
    cur = payload
    for part in dotted_key.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        elif isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
        if cur is None:
            return None
    return str(cur)


def _render(text: str, payload: Dict) -> Dict:
    """Setzt ``{{ key.path }}``-Platzhalter ein und sammelt unerfuellte
    Felder, damit der Aufrufer sie zur Vervollstaendigung melden kann.
    Bewusst keine Jinja-Steuerstrukturen — die Vorlagen sollen statisch
    bleiben, Logik gehoert in den Skill bzw. das Agenten-Procedure."""
    missing: List[str] = []

    def sub(match: re.Match) -> str:
        key = match.group(1)
        val = _resolve(payload, key)
        if val is None:
            if key not in missing:
                missing.append(key)
            return match.group(0)
        return val

    rendered = _PLACEHOLDER_RE.sub(sub, text)
    return {"rendered": rendered, "missing": missing}


def setup_template_routes():
    router = APIRouter(prefix="/api/templates", tags=["templates"])

    @router.get("")
    def list_templates(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        return {"templates": _list_disk()}

    @router.get("/{category}/{slug}")
    def get_template(request: Request, category: str, slug: str):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        t = _read_template(f"{category}/{slug}")
        if not t:
            raise HTTPException(404, "Vorlage nicht gefunden")
        return t

    @router.post("/{category}/{slug}/render")
    def render_template(request: Request, category: str, slug: str, payload: Dict):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        t = _read_template(f"{category}/{slug}")
        if not t:
            raise HTTPException(404, "Vorlage nicht gefunden")
        result = _render(t["content"], payload or {})
        return {
            "id": t["id"],
            "category": t["category"],
            "slug": t["slug"],
            "rendered": result["rendered"],
            "missing_placeholders": result["missing"],
        }

    # Admin-only: simple reload hint (falls Vorlagen direkt auf der Platte
    # geaendert wurden — aktuell nicht persistent im Cache, also reine
    # Stub-Antwort, aber laesst Raum fuer spaeteren In-Memory-Cache).
    @router.post("/reload")
    def reload_templates(request: Request):
        require_admin(request)
        return {"ok": True, "count": len(_list_disk())}

    return router
