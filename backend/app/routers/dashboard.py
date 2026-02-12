"""Dashboard stats endpoint."""

from fastapi import APIRouter

from app.services import card_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats():
    """Aggregate stats from cards + Anki/SRS."""
    cards = card_service.list_cards()

    by_pillar: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    for c in cards:
        p = c.pillar or "Unknown"
        l = c.knowledge_layer or "Unknown"
        by_pillar[p] = by_pillar.get(p, 0) + 1
        by_layer[l] = by_layer.get(l, 0) + 1

    # Anki stats — try to connect, fall back to server SRS
    try:
        from app.services.anki_service import check_connection, get_basic_stats

        conn = check_connection()
        if conn.get("connected"):
            anki_stats = get_basic_stats()
        else:
            raise Exception("not connected")
    except Exception:
        from app.services import srs_service

        anki_stats = srs_service.get_basic_stats()

    due_today = anki_stats.get("due_today", 0)
    reviewed_today = anki_stats.get("reviewed_today", 0)
    mastery_pct = anki_stats.get("mastery_pct", 0)

    return {
        "total_cards": len(cards),
        "due_today": due_today,
        "mastery_pct": mastery_pct,
        "reviewed_today": reviewed_today,
        "cards_by_pillar": dict(sorted(by_pillar.items())),
        "cards_by_layer": dict(sorted(by_layer.items())),
    }
