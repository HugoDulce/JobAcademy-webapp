"""Card service: read/write cards from Obsidian vault."""

from pathlib import Path

from app.config import CARDS_DIR
from app.models.card import Card
from app.parsers.card_parser import card_to_markdown, parse_card_file

# Files to skip when scanning for cards
_SKIP_NAMES = {"README.md", ".DS_Store"}


def list_cards() -> list[Card]:
    """Read all card .md files recursively and return parsed Cards."""
    cards = []
    for filepath in sorted(CARDS_DIR.rglob("*.md")):
        if filepath.name in _SKIP_NAMES or filepath.name.startswith("."):
            continue
        card = parse_card_file(filepath)
        if card:
            cards.append(card)
    return cards


def list_cards_by_concept(concept_node: str) -> list[Card]:
    """List cards by exact concept_node match."""
    concept = concept_node.strip()
    return [card for card in list_cards() if (card.concept_node or "").strip() == concept]


def get_card(card_id: str) -> Card | None:
    """Get a single card by card_id."""
    # Try direct filename match first (flat layout)
    filepath = CARDS_DIR / f"{card_id}.md"
    if filepath.exists():
        return parse_card_file(filepath)
    # Try recursive search by filename
    for filepath in CARDS_DIR.rglob(f"{card_id}.md"):
        card = parse_card_file(filepath)
        if card:
            return card
    # Fallback: full scan matching card_id field
    for filepath in CARDS_DIR.rglob("*.md"):
        if filepath.name in _SKIP_NAMES or filepath.name.startswith("."):
            continue
        card = parse_card_file(filepath)
        if card and card.card_id == card_id:
            return card
    return None


def save_card(card: Card) -> Path:
    """Write a card to disk as .md file.

    If topic and knowledge_layer are set, writes to topic/layer/ subdirectory.
    Otherwise writes flat to CARDS_DIR (legacy behavior).
    """
    safe_name = card.card_id.replace(" ", "_")
    content = card_to_markdown(card)

    if card.topic and card.knowledge_layer:
        layer_dir = card.knowledge_layer.lower()
        subdir = CARDS_DIR / card.topic / layer_dir
        subdir.mkdir(parents=True, exist_ok=True)
        filepath = subdir / f"{safe_name}.md"
    else:
        filepath = CARDS_DIR / f"{safe_name}.md"

    filepath.write_text(content, encoding="utf-8")
    return filepath


def delete_card(card_id: str) -> bool:
    """Delete a card .md file. Searches recursively. Returns True if deleted."""
    # Try flat path first
    filepath = CARDS_DIR / f"{card_id}.md"
    if filepath.exists():
        filepath.unlink()
        return True
    # Search recursively
    for filepath in CARDS_DIR.rglob(f"{card_id}.md"):
        filepath.unlink()
        return True
    return False
