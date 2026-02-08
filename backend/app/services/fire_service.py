"""FIRe service — encompassing relationships and credit simulation."""

import threading

from app.config import DOCS_DIR
from app.models.fire import CreditSimResult, FIReData
from app.parsers.fire_parser import parse_fire_hierarchy

_cached_data: FIReData | None = None
_lock = threading.Lock()


def get_fire_data() -> FIReData:
    """Get all FIRe encompassing relationships."""
    global _cached_data
    with _lock:
        if _cached_data is None:
            filepath = DOCS_DIR / "nb-cards-fire-hierarchy.md"
            _cached_data = parse_fire_hierarchy(filepath)
    return _cached_data


def simulate_credit(card_id: str, passed: bool) -> CreditSimResult:
    """Simulate credit flow when a card is passed/failed.

    If passed: credit flows to all encompassed cards (children), weighted.
    If failed: penalty indicator — this card and its parents need review.
    """
    data = get_fire_data()

    credits: list[dict] = []

    if passed:
        # Find all cards encompassed by this card
        for rel in data.relationships:
            if rel.parent_card_id == card_id:
                credits.append(
                    {"card_id": rel.child_card_id, "credit": rel.weight}
                )
        # Transitive: if encompassed cards themselves encompass others, partial credit
        for rel in data.relationships:
            if rel.parent_card_id == card_id:
                for rel2 in data.relationships:
                    if rel2.parent_card_id == rel.child_card_id:
                        transitive_credit = rel.weight * rel2.weight
                        if transitive_credit > 0.1:
                            credits.append(
                                {
                                    "card_id": rel2.child_card_id,
                                    "credit": round(transitive_credit, 2),
                                }
                            )
    else:
        # Fail: flag encompassing parents as needing review
        for rel in data.relationships:
            if rel.child_card_id == card_id:
                credits.append(
                    {"card_id": rel.parent_card_id, "credit": -rel.weight}
                )

    return CreditSimResult(card_id=card_id, passed=passed, credits=credits)


def get_heatmap_data() -> list[dict]:
    """Get data formatted for heatmap visualization."""
    data = get_fire_data()
    return [
        {
            "parent": r.parent_card_id,
            "child": r.child_card_id,
            "weight": r.weight,
        }
        for r in data.relationships
    ]
