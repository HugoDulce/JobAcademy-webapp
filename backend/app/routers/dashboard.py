"""Dashboard stats endpoint."""

from fastapi import APIRouter

from app.services import card_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats():
    """Aggregate stats from cards + Anki."""
    cards = card_service.list_cards()

    by_pillar: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    for c in cards:
        p = c.pillar or "Unknown"
        l = c.knowledge_layer or "Unknown"
        by_pillar[p] = by_pillar.get(p, 0) + 1
        by_layer[l] = by_layer.get(l, 0) + 1

    # Anki stats — try to connect, gracefully degrade
    due_today = 0
    reviewed_today = 0
    mastery_pct = 0
    try:
        from app.services.anki_service import get_basic_stats

        anki_stats = get_basic_stats()
        due_today = anki_stats.get("due_today", 0)
        reviewed_today = anki_stats.get("reviewed_today", 0)
        mastery_pct = anki_stats.get("mastery_pct", 0)
    except Exception:
        pass

    return {
        "total_cards": len(cards),
        "due_today": due_today,
        "mastery_pct": mastery_pct,
        "reviewed_today": reviewed_today,
        "cards_by_pillar": dict(sorted(by_pillar.items())),
        "cards_by_layer": dict(sorted(by_layer.items())),
    }
