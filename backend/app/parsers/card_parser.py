"""Parse .md card files from ~/Obsidian/JobAcademy/cards/."""

import re
from pathlib import Path

from app.models.card import Card

# Pillar mapping from card_id digit
PILLAR_MAP = {
    "1": "1-Use Case",
    "2": "2-Data",
    "3": "3-Algorithm",
    "4": "4-Objective",
    "5": "5-Evaluation",
    "6": "6-Integration",
}

# Knowledge layer from card_id letter
LAYER_MAP = {
    "C": "Conceptual",
    "M": "Mathematical",
    "P": "Programming",
    "I": "Integration",
}

# Special prefixes
SPECIAL_PREFIXES = {"CF", "D", "EXT", "MKT"}


def parse_card_id(card_id: str) -> dict:
    """Extract pillar and knowledge layer from card_id like 'nb-3M-02'."""
    # Match standard pattern: concept-pillarLayer-number
    m = re.match(r"^[a-z]+-(\d)([CMPI])-(\d+[a-z]?)$", card_id)
    if m:
        pillar_num, layer_letter, _ = m.groups()
        return {
            "pillar": PILLAR_MAP.get(pillar_num, f"{pillar_num}-Unknown"),
            "knowledge_layer": LAYER_MAP.get(layer_letter, "Unknown"),
        }
    # Match special prefix pattern: concept-PREFIX-number
    m = re.match(r"^[a-z]+-([A-Z]+)-(\d+[a-z]?)$", card_id)
    if m:
        prefix = m.group(1)
        if prefix in SPECIAL_PREFIXES:
            return {"pillar": prefix, "knowledge_layer": "Special"}
    return {"pillar": None, "knowledge_layer": None}


def parse_card_file(filepath: Path) -> Card | None:
    """Parse a single .md card file into a Card model."""
    text = filepath.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        return None

    fm = fm_match.group(1)

    # Parse frontmatter fields
    deck_match = re.search(r'deck:\s*"?([^"\n]+)"?', fm)
    deck = deck_match.group(1).strip() if deck_match else "JobAcademy"

    tags_match = re.search(r"tags:\s*\[([^\]]*)\]", fm)
    tags = []
    if tags_match:
        tags = [t.strip() for t in tags_match.group(1).split(",") if t.strip()]

    cid_match = re.search(r'card_id:\s*"?([^"\n]+)"?', fm)
    card_id = cid_match.group(1).strip() if cid_match else filepath.stem

    fw_match = re.search(r"fire_weight:\s*([\d.]+)", fm)
    fire_weight = float(fw_match.group(1)) if fw_match else 0.5

    edited_match = re.search(r'notion_last_edited:\s*"?([^"\n]+)"?', fm)
    notion_last_edited = edited_match.group(1).strip() if edited_match else ""

    # Extract START/END blocks
    blocks = re.findall(r"START\n(.*?)\nEND", text, re.DOTALL)
    if len(blocks) < 2:
        return None

    prompt = blocks[0].strip()
    solution = blocks[1].strip()

    # Derive pillar/layer from card_id
    id_info = parse_card_id(card_id)

    # Derive cognitive layer from tags
    cognitive_layer = None
    cognitive_tags = {
        "fill-in-blank": "1 - Fill-in-blank",
        "predict-output": "2 - Predict-output",
        "explain": "3 - Explain",
        "debug": "4 - Debug",
        "build": "5 - Build",
        "extend": "6 - Extend",
        "integration": "7 - Integration",
    }
    for tag in tags:
        if tag in cognitive_tags:
            cognitive_layer = cognitive_tags[tag]
            break

    return Card(
        card_id=card_id,
        deck=deck,
        tags=tags,
        fire_weight=fire_weight,
        notion_last_edited=notion_last_edited,
        prompt=prompt,
        solution=solution,
        pillar=id_info["pillar"],
        knowledge_layer=id_info["knowledge_layer"],
        cognitive_layer=cognitive_layer,
        filename=filepath.name,
    )


def card_to_markdown(card: Card) -> str:
    """Render a Card back to .md format matching notion_to_obsidian.py output."""
    tags_str = ", ".join(card.tags)
    lines = [
        "---",
        f'deck: "{card.deck}"',
        f"tags: [{tags_str}]",
        f'card_id: "{card.card_id}"',
        f"fire_weight: {card.fire_weight}",
        f'notion_last_edited: "{card.notion_last_edited}"',
        "---",
        "",
        f"# {card.card_id}",
        "",
        "START",
        card.prompt,
        "END",
        "",
        "START",
        card.solution,
        "END",
        "",
    ]
    return "\n".join(lines)
