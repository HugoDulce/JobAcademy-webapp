"""Anki API endpoints — proxy to AnkiConnect with server-SRS fallback."""

import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import anki_service, srs_service

router = APIRouter(prefix="/api/anki", tags=["anki"])

# Cached Anki availability check (60s TTL)
_anki_available: bool | None = None
_anki_checked_at: float = 0


def _is_anki_available() -> bool:
    global _anki_available, _anki_checked_at
    now = time.time()
    if _anki_available is None or (now - _anki_checked_at) > 60:
        result = anki_service.check_connection()
        _anki_available = result.get("connected", False)
        _anki_checked_at = now
    return _anki_available


@router.get("/status")
def anki_status():
    """Check if AnkiConnect is reachable."""
    if _is_anki_available():
        return anki_service.check_connection()
    return {"connected": False, "mode": "server-srs"}


@router.get("/stats")
def anki_stats():
    """Get deck statistics (Anki or server-SRS)."""
    if _is_anki_available():
        try:
            return anki_service.get_basic_stats()
        except Exception:
            pass
    return srs_service.get_basic_stats()


@router.get("/due")
def get_due_cards():
    """Get cards due for review (Anki or server-SRS)."""
    if _is_anki_available():
        try:
            return anki_service.get_due_cards()
        except Exception:
            pass
    return srs_service.get_due_cards()


class AnswerRequest(BaseModel):
    card_id: int | str  # Anki uses int, server SRS uses str
    ease: int  # 1=again, 2=hard, 3=good, 4=easy


@router.post("/answer")
def answer_card(req: AnswerRequest):
    """Submit an answer for a card."""
    if req.ease not in (1, 2, 3, 4):
        raise HTTPException(status_code=400, detail="Ease must be 1-4")

    if _is_anki_available() and isinstance(req.card_id, int):
        try:
            anki_service.answer_card(req.card_id, req.ease)
            return {"success": True}
        except Exception:
            pass

    srs_service.answer_card(str(req.card_id), req.ease)
    return {"success": True}
