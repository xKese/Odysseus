# routes/knowledge_routes.py
"""Hauswissen-Plattform fuer Meeder und Seifer.

Sammlungen (``KnowledgeCollection``) gruppieren kuratierte Hausdokumente
unter einem Slug. Rollen-ACL (``KnowledgeCollectionAcl``) regeln Lese-,
Schreib- und Admin-Rechte je Sammlung, gemappt auf das pro-User-Feld
``roles`` aus dem Auth-Store. Embeddings landen im gemeinsamen Chroma-
Store, gefiltert per Metadatenfeld ``collection``.

Auslassungen Phase 1 (siehe Plan): kein Vier-Augen-Prinzip, keine
Versions-Historie, kein Workflow-Engine. Wer ``write`` auf eine Sammlung
hat, kann hochladen und loeschen; Admin-Rolle erstellt Sammlungen und
setzt ACL.
"""

from __future__ import annotations

import logging
import os
import re
import time
import uuid
from typing import Dict, Iterable, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from core.auth import AuthManager
from core.database import (
    KnowledgeCollection,
    KnowledgeCollectionAcl,
    KnowledgeDocument,
    SessionLocal,
)
from core.middleware import require_admin
from src.auth_helpers import get_current_user
from src.rag_singleton import get_rag_manager
from src.upload_limits import read_upload_limited

logger = logging.getLogger(__name__)

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_KNOWN_PERMISSIONS = ("read", "write", "admin")
_DEFAULT_UPLOAD_LIMIT = 20 * 1024 * 1024  # 20 MB pro Dokument


def _slugify(text: str, fallback: str = "sammlung") -> str:
    s = (text or "").strip().lower()
    s = _SLUG_RE.sub("-", s).strip("-")
    return (s or fallback)[:60]


def _now_iso(ts: Optional[float] = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts or time.time()))


def _split_chunks(text: str, target: int = 1200, overlap: int = 150) -> List[str]:
    """Whitespace-respektierender Splitter — bewusst simpel; identisch zur
    Logik in ``_split_into_chunks`` von VectorRAG, hier mit konservativer
    Default-Groesse."""
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + target)
        if end < n:
            window = text[start:end]
            cut = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("\n"))
            if cut > target // 3:
                end = start + cut + 1
        chunks.append(text[start:end].strip())
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return [c for c in chunks if c]


def _extract_text(filename: str, blob: bytes) -> str:
    """Extrahiert Text aus den am haeufigsten kuratierten Quellformaten.
    PDF nutzt den vorhandenen Extractor aus ``src/personal_docs.py``; alle
    anderen Formate werden bestmoeglich als UTF-8/Latin-1 dekodiert.
    Nicht-textuelle Dateien geben Leerstring zurueck — die Route lehnt
    den Upload ab, sobald nichts Brauchbares extrahiert werden konnte."""
    ext = os.path.splitext(filename or "")[1].lower()
    if ext == ".pdf":
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
            fh.write(blob)
            tmp_path = fh.name
        try:
            from src.personal_docs import extract_pdf_text
            return extract_pdf_text(tmp_path) or ""
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    for enc in ("utf-8", "utf-16", "iso-8859-1", "cp1252"):
        try:
            return blob.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def setup_knowledge_routes(auth_manager: AuthManager):
    """Factory: registriert ``/api/knowledge``-Routes.

    Args:
        auth_manager: gemeinsamer ``AuthManager``-Singleton fuer Rollen-/
            Admin-Lookups. Der ``RAGManager`` wird ueber das vorhandene
            Singleton ``get_rag_manager()`` lazy aufgeloest, damit Restarts
            ohne ChromaDB-Server nicht crashen.
    """
    router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

    # ------------------------------------------------------------------
    # ACL helpers
    # ------------------------------------------------------------------

    def _user_roles(username: Optional[str]) -> List[str]:
        if not username:
            return []
        return auth_manager.get_user_roles(username)

    def _can(collection_id: str, username: Optional[str], permission: str) -> bool:
        if not username:
            return False
        # Admins haben Vollzugriff — kein ACL-Lookup noetig.
        if auth_manager.is_admin(username):
            return True
        roles = set(_user_roles(username))
        if not roles:
            return False
        with SessionLocal() as db:
            grants = (
                db.query(KnowledgeCollectionAcl)
                .filter(KnowledgeCollectionAcl.collection_id == collection_id)
                .all()
            )
        levels = {"read": 1, "write": 2, "admin": 3}
        needed = levels.get(permission, 1)
        best = 0
        for g in grants:
            if g.role in roles:
                best = max(best, levels.get(g.permission, 0))
        return best >= needed

    def _visible_collection_ids(username: Optional[str]) -> Optional[set]:
        """Sammlungs-IDs, die der Nutzer mindestens lesen darf. ``None`` =
        Admin-Pass (alle sichtbar) zur Vermeidung eines unnoetigen Joins."""
        if not username:
            return set()
        if auth_manager.is_admin(username):
            return None
        roles = set(_user_roles(username))
        if not roles:
            return set()
        with SessionLocal() as db:
            grants = (
                db.query(KnowledgeCollectionAcl)
                .filter(KnowledgeCollectionAcl.role.in_(list(roles)))
                .all()
            )
        return {g.collection_id for g in grants}

    def _collection_to_dict(c: KnowledgeCollection, doc_count: int = 0) -> Dict:
        return {
            "id": c.id,
            "slug": c.slug,
            "name": c.name,
            "description": c.description or "",
            "created_by": c.created_by,
            "created_at": c.created_at.isoformat() + "Z" if c.created_at else None,
            "updated_at": c.updated_at.isoformat() + "Z" if c.updated_at else None,
            "doc_count": doc_count,
        }

    # ------------------------------------------------------------------
    # Collections
    # ------------------------------------------------------------------

    @router.get("/collections")
    def list_collections(request: Request):
        user = get_current_user(request)
        if not user:
            raise HTTPException(401, "Authentifizierung erforderlich")
        visible = _visible_collection_ids(user)
        with SessionLocal() as db:
            q = db.query(KnowledgeCollection)
            if visible is not None:
                if not visible:
                    return {"collections": []}
                q = q.filter(KnowledgeCollection.id.in_(list(visible)))
            rows = q.order_by(KnowledgeCollection.name).all()
            out = []
            for c in rows:
                doc_count = (
                    db.query(KnowledgeDocument)
                    .filter(KnowledgeDocument.collection_id == c.id)
                    .count()
                )
                out.append(_collection_to_dict(c, doc_count=doc_count))
        return {"collections": out}

    @router.post("/collections")
    async def create_collection(request: Request, payload: Dict):
        require_admin(request)
        user = get_current_user(request)
        name = (payload.get("name") or "").strip()
        slug = _slugify(payload.get("slug") or name)
        if not name or not slug:
            raise HTTPException(400, "Name und Slug erforderlich")
        description = (payload.get("description") or "").strip()
        with SessionLocal() as db:
            existing = db.query(KnowledgeCollection).filter_by(slug=slug).first()
            if existing:
                raise HTTPException(409, f"Sammlung mit Slug '{slug}' existiert bereits")
            c = KnowledgeCollection(
                id=uuid.uuid4().hex,
                slug=slug,
                name=name,
                description=description,
                created_by=user,
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            return _collection_to_dict(c, doc_count=0)

    @router.get("/collections/{collection_id}")
    def get_collection(request: Request, collection_id: str):
        user = get_current_user(request)
        if not _can(collection_id, user, "read"):
            raise HTTPException(403, "Keine Berechtigung fuer diese Sammlung")
        with SessionLocal() as db:
            c = db.query(KnowledgeCollection).filter_by(id=collection_id).first()
            if not c:
                raise HTTPException(404, "Sammlung nicht gefunden")
            doc_count = (
                db.query(KnowledgeDocument)
                .filter(KnowledgeDocument.collection_id == c.id)
                .count()
            )
            return _collection_to_dict(c, doc_count=doc_count)

    @router.delete("/collections/{collection_id}")
    def delete_collection(request: Request, collection_id: str):
        require_admin(request)
        rag = get_rag_manager()
        with SessionLocal() as db:
            c = db.query(KnowledgeCollection).filter_by(id=collection_id).first()
            if not c:
                raise HTTPException(404, "Sammlung nicht gefunden")
            slug = c.slug
            db.delete(c)
            db.commit()
        # Vektor-Eintraege purgen — best effort, scheitert Chroma, bleibt
        # die DB-Loeschung trotzdem persistent.
        if rag is not None:
            try:
                for _name, coll in rag._collections_for_delete():  # type: ignore[attr-defined]
                    coll.delete(where={"collection": slug})
            except Exception as e:
                logger.warning(f"Vektor-Purge fuer Sammlung {slug} fehlgeschlagen: {e}")
        return {"deleted": collection_id}

    # ------------------------------------------------------------------
    # ACL
    # ------------------------------------------------------------------

    @router.get("/collections/{collection_id}/acl")
    def list_acl(request: Request, collection_id: str):
        require_admin(request)
        with SessionLocal() as db:
            rows = (
                db.query(KnowledgeCollectionAcl)
                .filter(KnowledgeCollectionAcl.collection_id == collection_id)
                .all()
            )
            return {
                "collection_id": collection_id,
                "grants": [{"role": r.role, "permission": r.permission} for r in rows],
            }

    @router.put("/collections/{collection_id}/acl")
    def set_acl(request: Request, collection_id: str, payload: Dict):
        require_admin(request)
        grants_in = payload.get("grants") or []
        cleaned: List[Dict[str, str]] = []
        for g in grants_in:
            role = str(g.get("role") or "").strip().lower()
            perm = str(g.get("permission") or "").strip().lower()
            if not role or perm not in _KNOWN_PERMISSIONS:
                continue
            cleaned.append({"role": role, "permission": perm})
        with SessionLocal() as db:
            c = db.query(KnowledgeCollection).filter_by(id=collection_id).first()
            if not c:
                raise HTTPException(404, "Sammlung nicht gefunden")
            db.query(KnowledgeCollectionAcl).filter(
                KnowledgeCollectionAcl.collection_id == collection_id
            ).delete()
            for g in cleaned:
                db.add(KnowledgeCollectionAcl(
                    collection_id=collection_id,
                    role=g["role"],
                    permission=g["permission"],
                ))
            db.commit()
        return {"collection_id": collection_id, "grants": cleaned}

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    @router.get("/collections/{collection_id}/documents")
    def list_documents(request: Request, collection_id: str):
        user = get_current_user(request)
        if not _can(collection_id, user, "read"):
            raise HTTPException(403, "Keine Berechtigung fuer diese Sammlung")
        with SessionLocal() as db:
            rows = (
                db.query(KnowledgeDocument)
                .filter(KnowledgeDocument.collection_id == collection_id)
                .order_by(KnowledgeDocument.created_at.desc())
                .all()
            )
            return {
                "documents": [
                    {
                        "id": d.id,
                        "filename": d.filename,
                        "size": d.size or 0,
                        "mime": d.mime,
                        "chunk_count": d.chunk_count or 0,
                        "uploaded_by": d.uploaded_by,
                        "created_at": d.created_at.isoformat() + "Z" if d.created_at else None,
                    }
                    for d in rows
                ],
            }

    @router.post("/collections/{collection_id}/documents")
    async def upload_document(
        request: Request,
        collection_id: str,
        file: UploadFile = File(...),
    ):
        user = get_current_user(request)
        if not _can(collection_id, user, "write"):
            raise HTTPException(403, "Keine Schreibberechtigung fuer diese Sammlung")
        rag = get_rag_manager()
        if rag is None:
            raise HTTPException(503, "Wissensbasis (ChromaDB) momentan nicht verfuegbar")

        with SessionLocal() as db:
            c = db.query(KnowledgeCollection).filter_by(id=collection_id).first()
            if not c:
                raise HTTPException(404, "Sammlung nicht gefunden")
            slug = c.slug

        blob = await read_upload_limited(file, _DEFAULT_UPLOAD_LIMIT, "Hauswissen-Upload")
        filename = file.filename or "dokument"
        text = _extract_text(filename, blob)
        if not text or not text.strip():
            raise HTTPException(400, "Aus der Datei konnte kein Text extrahiert werden")

        doc_id = uuid.uuid4().hex
        meta_base = {
            "collection": slug,
            "knowledge_doc_id": doc_id,
            "filename": filename,
            "uploaded_by": user or "",
            "uploaded_at": _now_iso(),
        }
        chunks = _split_chunks(text)
        indexed = 0
        for i, chunk in enumerate(chunks):
            if rag.add_document(chunk, {**meta_base, "chunk_id": i}):
                indexed += 1

        with SessionLocal() as db:
            d = KnowledgeDocument(
                id=doc_id,
                collection_id=collection_id,
                filename=filename,
                chroma_doc_id=doc_id,
                uploaded_by=user,
                size=len(blob),
                mime=file.content_type,
                chunk_count=indexed,
            )
            db.add(d)
            db.commit()
            db.refresh(d)
            return {
                "id": d.id,
                "filename": d.filename,
                "chunk_count": d.chunk_count,
                "size": d.size,
            }

    @router.delete("/collections/{collection_id}/documents/{doc_id}")
    def delete_document(request: Request, collection_id: str, doc_id: str):
        user = get_current_user(request)
        if not _can(collection_id, user, "write"):
            raise HTTPException(403, "Keine Schreibberechtigung fuer diese Sammlung")
        rag = get_rag_manager()
        with SessionLocal() as db:
            d = db.query(KnowledgeDocument).filter_by(
                id=doc_id, collection_id=collection_id
            ).first()
            if not d:
                raise HTTPException(404, "Dokument nicht gefunden")
            chroma_id = d.chroma_doc_id
            db.delete(d)
            db.commit()
        if rag is not None:
            try:
                for _name, coll in rag._collections_for_delete():  # type: ignore[attr-defined]
                    coll.delete(where={"knowledge_doc_id": chroma_id})
            except Exception as e:
                logger.warning(f"Vektor-Purge fuer Dokument {chroma_id} fehlgeschlagen: {e}")
        return {"deleted": doc_id}

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    @router.post("/collections/{collection_id}/search")
    def search_collection(request: Request, collection_id: str, payload: Dict):
        user = get_current_user(request)
        if not _can(collection_id, user, "read"):
            raise HTTPException(403, "Keine Berechtigung fuer diese Sammlung")
        query = (payload.get("query") or "").strip()
        if not query:
            raise HTTPException(400, "Leere Suchanfrage")
        k = int(payload.get("k") or 5)
        rag = get_rag_manager()
        if rag is None:
            raise HTTPException(503, "Wissensbasis momentan nicht verfuegbar")
        with SessionLocal() as db:
            c = db.query(KnowledgeCollection).filter_by(id=collection_id).first()
            if not c:
                raise HTTPException(404, "Sammlung nicht gefunden")
            slug = c.slug
        results = rag.search(query, k=k, collection_slug=slug)
        return {"query": query, "results": results}

    # ------------------------------------------------------------------
    # Org-wide search (any collection the caller can read)
    # ------------------------------------------------------------------

    @router.post("/search")
    def search_all_visible(request: Request, payload: Dict):
        user = get_current_user(request)
        query = (payload.get("query") or "").strip()
        if not query:
            raise HTTPException(400, "Leere Suchanfrage")
        k = int(payload.get("k") or 5)
        rag = get_rag_manager()
        if rag is None:
            raise HTTPException(503, "Wissensbasis momentan nicht verfuegbar")

        visible = _visible_collection_ids(user)
        with SessionLocal() as db:
            q = db.query(KnowledgeCollection)
            if visible is not None:
                if not visible:
                    return {"query": query, "results": []}
                q = q.filter(KnowledgeCollection.id.in_(list(visible)))
            slugs = [c.slug for c in q.all()]
        if not slugs:
            return {"query": query, "results": []}

        merged: List[Dict] = []
        for slug in slugs:
            try:
                merged.extend(rag.search(query, k=k, collection_slug=slug))
            except Exception as e:
                logger.warning(f"Sammlung {slug} Suche fehlgeschlagen: {e}")
        merged.sort(key=lambda r: r.get("similarity", 0.0), reverse=True)
        return {"query": query, "results": merged[:k]}

    return router
