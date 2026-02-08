"""Anki API endpoints — proxy to AnkiConnect."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import anki_service

router = APIRouter(prefix="/api/anki", tags=["anki"])


@router.get("/status")
def anki_status():
    """Check if AnkiConnect is reachable."""
    return anki_service.check_connection()


@router.get("/stats")
def anki_stats():
    """Get Anki deck statistics."""
    try:
        return anki_service.get_basic_stats()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Anki not available: {e}")


@router.get("/due")
def get_due_cards():
    """Get cards due for review."""
    try:
        return anki_service.get_due_cards()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Anki not available: {e}")


class AnswerRequest(BaseModel):
    card_id: int
    ease: int  # 1=again, 2=hard, 3=good, 4=easy


@router.post("/answer")
def answer_card(req: AnswerRequest):
    """Submit an answer for a card."""
    if req.ease not in (1, 2, 3, 4):
        raise HTTPException(status_code=400, detail="Ease must be 1-4")
    try:
        anki_service.answer_card(req.card_id, req.ease)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Anki error: {e}")
