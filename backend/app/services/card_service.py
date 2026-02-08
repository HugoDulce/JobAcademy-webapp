"""Card service: read/write cards from Obsidian vault."""

from pathlib import Path

from app.config import CARDS_DIR
from app.models.card import Card
from app.parsers.card_parser import card_to_markdown, parse_card_file


def list_cards() -> list[Card]:
    """Read all card .md files and return parsed Cards."""
    cards = []
    for filepath in sorted(CARDS_DIR.glob("nb-*.md")):
        card = parse_card_file(filepath)
        if card:
            cards.append(card)
    return cards


def get_card(card_id: str) -> Card | None:
    """Get a single card by card_id."""
    # Try direct filename match first
    filepath = CARDS_DIR / f"{card_id}.md"
    if filepath.exists():
        return parse_card_file(filepath)
    # Fallback: scan all files
    for filepath in CARDS_DIR.glob("*.md"):
        card = parse_card_file(filepath)
        if card and card.card_id == card_id:
            return card
    return None


def save_card(card: Card) -> Path:
    """Write a card to disk as .md file."""
    safe_name = card.card_id.replace(" ", "_")
    filepath = CARDS_DIR / f"{safe_name}.md"
    content = card_to_markdown(card)
    filepath.write_text(content, encoding="utf-8")
    return filepath


def delete_card(card_id: str) -> bool:
    """Delete a card .md file. Returns True if deleted."""
    filepath = CARDS_DIR / f"{card_id}.md"
    if filepath.exists():
        filepath.unlink()
        return True
    return False
