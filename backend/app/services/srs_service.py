"""Server-side SRS engine (SM-2 algorithm) with JSON file backing."""

import json
from datetime import datetime, timedelta, timezone

from app.config import SRS_STATE_FILE
from app.services import card_service


def _load_state() -> dict:
    """Read SRS state from disk; return empty default if missing."""
    if SRS_STATE_FILE.exists():
        try:
            return json.loads(SRS_STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"cards": {}, "daily_log": {}}


def _save_state(state: dict) -> None:
    """Write SRS state to disk."""
    SRS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SRS_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_card(state: dict, card_id: str) -> dict:
    """Initialise a new card entry if it doesn't exist yet."""
    if card_id not in state["cards"]:
        state["cards"][card_id] = {
            "ease_factor": 2.5,
            "interval": 0,
            "review_count": 0,
            "next_due": _now().isoformat(),
            "last_reviewed": "",
        }
    return state["cards"][card_id]


def get_due_cards() -> list[dict]:
    """Return cards where next_due <= now, matching anki_service shape."""
    all_cards = card_service.list_cards()
    state = _load_state()
    now = _now()

    due = []
    for card in all_cards:
        entry = state["cards"].get(card.card_id)
        if entry is None:
            # New card — due immediately
            interval = 0
            ease = 2.5
        else:
            next_due = datetime.fromisoformat(entry["next_due"])
            if next_due.tzinfo is None:
                next_due = next_due.replace(tzinfo=timezone.utc)
            if next_due > now:
                continue
            interval = entry["interval"]
            ease = entry["ease_factor"]

        due.append({
            "card_id": card.card_id,
            "note_id": 0,
            "front": card.prompt,
            "back": card.solution,
            "deck": card.deck,
            "interval": interval,
            "ease": ease,
            "tags": card.tags,
        })

    # Sort: new cards first (interval 0), then lowest interval
    due.sort(key=lambda c: (0 if c["interval"] == 0 else 1, c["interval"]))
    return due


def answer_card(card_id: str, ease: int) -> None:
    """Apply SM-2 update for a card and persist."""
    state = _load_state()
    entry = _ensure_card(state, card_id)

    ef = entry["ease_factor"]
    iv = entry["interval"]
    rc = entry["review_count"]

    if ease == 1:  # Again
        iv = 0
        ef = max(1.3, ef - 0.2)
    elif ease == 2:  # Hard
        iv = max(1, iv * 1.2)
        ef = max(1.3, ef - 0.15)
    elif ease == 3:  # Good
        if rc == 0:
            iv = 1
        elif rc == 1:
            iv = 6
        else:
            iv = iv * ef
    elif ease == 4:  # Easy
        if rc == 0:
            iv = 1
        elif rc == 1:
            iv = 6
        else:
            iv = iv * ef
        iv *= 1.3
        ef += 0.15

    entry["ease_factor"] = round(ef, 4)
    entry["interval"] = round(iv, 1)
    entry["review_count"] = rc + 1
    entry["next_due"] = (_now() + timedelta(days=iv)).isoformat()
    entry["last_reviewed"] = _now().isoformat()

    # Daily log
    today = _now().strftime("%Y-%m-%d")
    log = state.setdefault("daily_log", {})
    day_list = log.setdefault(today, [])
    if card_id not in day_list:
        day_list.append(card_id)

    _save_state(state)


def get_basic_stats() -> dict:
    """Return stats matching anki_service.get_basic_stats() shape."""
    all_cards = card_service.list_cards()
    state = _load_state()
    now = _now()
    today = now.strftime("%Y-%m-%d")

    due_count = 0
    mastered = 0

    for card in all_cards:
        entry = state["cards"].get(card.card_id)
        if entry is None:
            due_count += 1  # new card = due
        else:
            next_due = datetime.fromisoformat(entry["next_due"])
            if next_due.tzinfo is None:
                next_due = next_due.replace(tzinfo=timezone.utc)
            if next_due <= now:
                due_count += 1
            if entry["interval"] >= 21:
                mastered += 1

    total = len(all_cards)
    reviewed_today = len(state.get("daily_log", {}).get(today, []))
    mastery_pct = round(mastered / total * 100) if total > 0 else 0

    return {
        "due_today": due_count,
        "total_notes": total,
        "reviewed_today": reviewed_today,
        "mastery_pct": mastery_pct,
        "mastered_count": mastered,
    }
