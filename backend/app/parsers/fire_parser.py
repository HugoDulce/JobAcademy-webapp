"""Parse FIRe encompassing relationships from the hierarchy document."""

import re
from pathlib import Path

from app.models.fire import EncompassingRelationship, FIReData


def parse_fire_hierarchy(filepath: Path) -> FIReData:
    """Parse nb-cards-fire-hierarchy.md for encompassing relationships."""
    text = filepath.read_text(encoding="utf-8")

    relationships: list[EncompassingRelationship] = []
    standalone_cards: list[str] = []
    seen: set[tuple[str, str]] = set()

    current_card_id: str | None = None

    for line in text.split("\n"):
        # Track current card via <!--ID: nb-xxx-->
        id_match = re.search(r"<!--ID:\s*(nb-[\w-]+)\s*-->", line)
        if id_match:
            current_card_id = id_match.group(1)
            continue

        # Parse <!--FIRe: encompasses nb-X (w=Y), ...-->
        fire_match = re.search(r"<!--FIRe:\s*(.*?)-->", line)
        if fire_match and current_card_id:
            content = fire_match.group(1).strip()

            if content.startswith("standalone"):
                standalone_cards.append(current_card_id)
            elif content.startswith("encompasses"):
                # Parse individual relationships
                for m in re.finditer(r"(nb-[\w-]+)\s*\(w=([\d.]+)\)", content):
                    child_id = m.group(1)
                    weight = float(m.group(2))
                    key = (current_card_id, child_id)
                    if key not in seen:
                        seen.add(key)
                        relationships.append(
                            EncompassingRelationship(
                                parent_card_id=current_card_id,
                                child_card_id=child_id,
                                weight=weight,
                            )
                        )
            elif content.startswith("encompassed by"):
                # Reverse: current card is encompassed by others
                for m in re.finditer(r"(nb-[\w-]+)\s*\(w=([\d.]+)\)", content):
                    parent_id = m.group(1)
                    weight = float(m.group(2))
                    key = (parent_id, current_card_id)
                    if key not in seen:
                        seen.add(key)
                        relationships.append(
                            EncompassingRelationship(
                                parent_card_id=parent_id,
                                child_card_id=current_card_id,
                                weight=weight,
                            )
                        )
            current_card_id = None  # Reset after processing

    # Also parse the tree at the top for any missing relationships
    # Format: nb-XXX  description  [encompasses: YYY, ZZZ]
    for m in re.finditer(
        r"(nb-[\w-]+)\s+.+?\[encompasses:\s*([^\]]+)\]", text
    ):
        parent_id = m.group(1)
        children = m.group(2).split(",")
        for child in children:
            child = child.strip()
            # Tree uses short IDs like "4M-01a" meaning "nb-4M-01a"
            if not child.startswith("nb-"):
                child = "nb-" + child
            key = (parent_id, child)
            if key not in seen:
                seen.add(key)
                relationships.append(
                    EncompassingRelationship(
                        parent_card_id=parent_id,
                        child_card_id=child,
                        weight=0.5,  # Default weight when not specified
                    )
                )

    return FIReData(relationships=relationships, standalone_cards=standalone_cards)
