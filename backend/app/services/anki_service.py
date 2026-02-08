"""AnkiConnect HTTP API wrapper."""

import httpx

from app.config import ANKI_URL

_client = httpx.Client(timeout=5)


def _invoke(action: str, **params) -> dict:
    """Send a request to AnkiConnect."""
    payload = {"action": action, "version": 6, "params": params}
    resp = _client.post(ANKI_URL, json=payload)
    body = resp.json()
    if body.get("error"):
        raise RuntimeError(f"AnkiConnect: {body['error']}")
    return body["result"]


def check_connection() -> dict:
    """Check if AnkiConnect is reachable."""
    try:
        version = _invoke("version")
        return {"connected": True, "version": version}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def get_basic_stats() -> dict:
    """Get basic Anki stats for the dashboard."""
    try:
        due_ids = _invoke("findCards", query="deck:JobAcademy is:due")
        all_ids = _invoke("findCards", query="deck:JobAcademy")
    except Exception:
        return {
            "due_today": 0,
            "total_notes": 0,
            "reviewed_today": 0,
            "mastery_pct": 0,
            "mastered_count": 0,
        }

    reviewed_today = 0
    try:
        reviewed_today = _invoke("getNumCardsReviewedToday")
    except Exception:
        pass

    mastered = 0
    if all_ids:
        cards_info = _invoke("cardsInfo", cards=all_ids)
        for card in cards_info:
            if card.get("interval", 0) >= 21:
                mastered += 1

    total = len(all_ids)
    mastery_pct = round(mastered / total * 100) if total > 0 else 0

    return {
        "due_today": len(due_ids),
        "total_notes": total,
        "reviewed_today": reviewed_today,
        "mastery_pct": mastery_pct,
        "mastered_count": mastered,
    }


def get_due_cards() -> list[dict]:
    """Get cards due for review with their content."""
    try:
        card_ids = _invoke("findCards", query="deck:JobAcademy is:due")
    except Exception:
        return []
    if not card_ids:
        return []

    cards_info = _invoke("cardsInfo", cards=card_ids)

    # Batch: collect all note IDs, fetch in one call
    note_ids = list({c["note"] for c in cards_info})
    notes_info = _invoke("notesInfo", notes=note_ids)
    note_map = {n["noteId"]: n for n in notes_info}

    result = []
    for card in cards_info:
        note = note_map.get(card.get("note", 0))
        if note:
            result.append(
                {
                    "card_id": card["cardId"],
                    "note_id": card["note"],
                    "front": note.get("fields", {}).get("Front", {}).get("value", ""),
                    "back": note.get("fields", {}).get("Back", {}).get("value", ""),
                    "deck": card.get("deckName", ""),
                    "interval": card.get("interval", 0),
                    "ease": card.get("factor", 0),
                    "tags": note.get("tags", []),
                }
            )
    return result


def answer_card(card_id: int, ease: int) -> bool:
    """Submit an answer for a card. ease: 1=again, 2=hard, 3=good, 4=easy."""
    _invoke("answerCards", answers=[{"cardId": card_id, "ease": ease}])
    return True
