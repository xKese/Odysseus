# routes/standardanfragen_routes.py
"""Standardanfragen-Bibliothek fuer Meeder & Seifer (Phase 4).

Vorlagen liegen als Themen-Verzeichnisse unter
``data/standardanfragen/<thema-slug>/`` mit ``frage.md`` (Stichwort-Liste
fuer das Matching) und ``antwort-template.md`` (Markdown-Vorlage mit
Platzhaltern). Die API liefert Listen-, Detail- und Render-Endpunkte
analog zu ``routes/template_routes.py`` und einen Match-Endpunkt fuer
das vom Skill `standardanfrage` genutzte Token-Overlap-Verfahren.

Auslassungen Phase 4:
- Schreibende Endpoints (Bibliothek wird im Repo gepflegt).
- LLM-basiertes Matching — kommt mit `manage_skills`/`hauswissen-suche`
  ohnehin abdeckend hinzu.
- Versionierung — Templates aenderungs-getrackt durch Git.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request

from src.auth_helpers import get_current_user

logger = logging.getLogger(__name__)

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z_][\w.]*)\s*\}\}")
_TOKEN_SPLIT_RE = re.compile(r"[^a-zA-Z0-9äöüß]+")
_MATCH_THRESHOLD = 0.18  # Jaccard-Schwelle fuer "halbwegs verwandt"


def _root() -> str:
    return os.path.abspath(os.path.join("data", "standardanfragen"))


def _safe_slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "", text or "")[:80]


def _tokens(text: str) -> set:
    return {t for t in _TOKEN_SPLIT_RE.split((text or "").lower()) if len(t) > 2}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _list_themes() -> List[Dict[str, Any]]:
    root = _root()
    if not os.path.isdir(root):
        return []
    out: List[Dict[str, Any]] = []
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path):
            continue
        frage = os.path.join(path, "frage.md")
        antwort = os.path.join(path, "antwort-template.md")
        if not (os.path.isfile(frage) and os.path.isfile(antwort)):
            continue
        try:
            with open(frage, encoding="utf-8") as f:
                frage_text = f.read()
        except Exception:
            frage_text = ""
        stichworte = [
            line.strip().lstrip("-* ").strip()
            for line in frage_text.splitlines()
            if line.strip().startswith(("-", "*"))
        ]
        out.append({
            "slug": entry,
            "name": entry.replace("-", " ").title(),
            "stichwort_count": len(stichworte),
        })
    return out


def _read_theme(slug: str) -> Optional[Dict[str, Any]]:
    safe = _safe_slug(slug)
    root = _root()
    path = os.path.join(root, safe)
    if not os.path.isdir(path):
        return None
    if os.path.commonpath([os.path.abspath(path), root]) != root:
        return None
    frage = os.path.join(path, "frage.md")
    antwort = os.path.join(path, "antwort-template.md")
    if not (os.path.isfile(frage) and os.path.isfile(antwort)):
        return None
    with open(frage, encoding="utf-8") as f:
        frage_text = f.read()
    with open(antwort, encoding="utf-8") as f:
        antwort_text = f.read()
    stichworte = [
        line.strip().lstrip("-* ").strip()
        for line in frage_text.splitlines()
        if line.strip().startswith(("-", "*"))
    ]
    return {
        "slug": safe,
        "name": safe.replace("-", " ").title(),
        "stichworte": stichworte,
        "antwort_template": antwort_text,
    }


def _resolve(payload: Dict, dotted_key: str) -> Optional[str]:
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


def _render(text: str, payload: Dict) -> Dict[str, Any]:
    missing: List[str] = []

    def sub(m):
        key = m.group(1)
        v = _resolve(payload, key)
        if v is None:
            if key not in missing:
                missing.append(key)
            return m.group(0)
        return v

    return {"rendered": _PLACEHOLDER_RE.sub(sub, text), "missing": missing}


def _match(question: str) -> List[Dict[str, Any]]:
    q_tokens = _tokens(question)
    results: List[Dict[str, Any]] = []
    for theme in _list_themes():
        detail = _read_theme(theme["slug"])
        if not detail:
            continue
        # Pro Stichwort jaccard berechnen, hoechsten Wert als Score nehmen.
        best = 0.0
        best_keyword = ""
        for stichwort in detail["stichworte"]:
            score = _jaccard(q_tokens, _tokens(stichwort))
            if score > best:
                best = score
                best_keyword = stichwort
        results.append({
            "slug": theme["slug"],
            "name": theme["name"],
            "score": round(best, 3),
            "matched_keyword": best_keyword if best > 0 else None,
        })
    results.sort(key=lambda r: -r["score"])
    return results


def setup_standardanfragen_routes():
    router = APIRouter(prefix="/api/standardanfragen", tags=["standardanfragen"])

    @router.get("")
    def list_themes(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        return {"themes": _list_themes()}

    @router.get("/{slug}")
    def get_theme(request: Request, slug: str):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        t = _read_theme(slug)
        if not t:
            raise HTTPException(404, "Standardanfrage nicht gefunden")
        return t

    @router.post("/{slug}/render")
    def render_theme(request: Request, slug: str, payload: Dict[str, Any]):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        t = _read_theme(slug)
        if not t:
            raise HTTPException(404, "Standardanfrage nicht gefunden")
        result = _render(t["antwort_template"], payload or {})
        return {
            "slug": t["slug"],
            "rendered": result["rendered"],
            "missing_placeholders": result["missing"],
        }

    @router.post("/match")
    def match_question(request: Request, payload: Dict[str, Any]):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        question = (payload.get("frage") or payload.get("question") or "").strip()
        if not question:
            raise HTTPException(400, "Leere Frage")
        results = _match(question)
        top = results[0] if results else None
        return {
            "question": question,
            "best_match": top if (top and top["score"] >= _MATCH_THRESHOLD) else None,
            "candidates": results[:5],
            "threshold": _MATCH_THRESHOLD,
        }

    return router
