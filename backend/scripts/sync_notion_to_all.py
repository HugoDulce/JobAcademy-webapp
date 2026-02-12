#!/usr/bin/env python3
"""Sync cards from Notion database to webapp (topic-organized), Obsidian, and Anki.

Usage:
    python backend/scripts/sync_notion_to_all.py              # sync to webapp cards dir
    python backend/scripts/sync_notion_to_all.py --dry-run     # preview only
    python backend/scripts/sync_notion_to_all.py --anki        # also push to Anki
    python backend/scripts/sync_notion_to_all.py --force       # re-sync all regardless of timestamps
    python backend/scripts/sync_notion_to_all.py --clean       # delete old flat nb-*.md files after sync
"""

import argparse
import json
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Allow running from project root: python backend/scripts/sync_notion_to_all.py
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent
sys.path.insert(0, str(_BACKEND_DIR))

import httpx
from notion_client import Client as NotionClient

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CARDS_DIR = Path(os.getenv("CARDS_DIR", str(_BACKEND_DIR / "data" / "cards")))
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")
ANKI_URL = os.getenv("ANKI_URL", "http://localhost:8765")
STATE_FILE = _SCRIPT_DIR / ".sync_state.json"

# ---------------------------------------------------------------------------
# Maps
# ---------------------------------------------------------------------------

# Concept name -> card ID prefix
CONCEPT_PREFIX_MAP = {
    "NORMAL": "norm",
    "POISSON": "pois",
    "BINOMIAL": "binom",
    "BERNOULLI": "bern",
    "GAMMA": "gamma",
    "BETA": "beta",
    "UNIFORM": "unif",
    "STUDENT_T": "stud",
    "WEIBULL": "weib",
    "LOGNORMAL": "lnorm",
    "DISCRETE_UNIFORM": "dunif",
    "HYPERGEOMETRIC": "hyper",
    "NEGATIVE_BINOMIAL": "nbinom",
    "GEOMETRIC": "geom",
    "PROB": "prob",
    "PROB_CAT": "prob-cat",
    "PROB_PROP": "prob-prop",
}

# Knowledge layer name -> single letter for card ID
LAYER_LETTER_MAP = {
    "Conceptual": "C",
    "Mathematical": "M",
    "Programming": "P",
    "Visual": "V",
    "Integration": "I",
}

# Card prefix -> topic
PREFIX_TOPIC_MAP = {
    "nb": "naive-bayes",
}
# All concept prefixes map to probability-distributions
for _prefix in CONCEPT_PREFIX_MAP.values():
    PREFIX_TOPIC_MAP[_prefix] = "probability-distributions"

# Layer name -> subdirectory
LAYER_DIR_MAP = {
    "Conceptual": "conceptual",
    "Mathematical": "mathematical",
    "Programming": "programming",
    "Visual": "visual",
    "Integration": "integration",
    "Special": "special",
}

# ---------------------------------------------------------------------------
# Card ID format detection
# ---------------------------------------------------------------------------

NEW_FORMAT_PATTERNS = [
    r"^nb-\d[CMPIV]-\d+[a-z]?$",                        # nb-3M-01
    r"^nb-[A-Z]+-\d+[a-z]?$",                            # nb-CF-01
    r"^[a-z](?:[a-z-]*[a-z])?-[CMPIV]-\d+[a-z]?$",      # norm-V-01
    r"^[a-z](?:[a-z-]*[a-z])?-\d+[a-z]?$",               # prob-cat-01
]


def is_new_format(card_id: str) -> bool:
    """Check if a card ID already uses the new naming convention."""
    return any(re.match(p, card_id) for p in NEW_FORMAT_PATTERNS)


# ---------------------------------------------------------------------------
# Notion helpers
# ---------------------------------------------------------------------------

def get_prop_text(page: dict, name: str) -> str:
    """Extract plain text from a Notion page property."""
    prop = page.get("properties", {}).get(name)
    if not prop:
        return ""
    ptype = prop.get("type", "")
    if ptype == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title", []))
    if ptype == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", []))
    if ptype == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    if ptype == "checkbox":
        return str(prop.get("checkbox", False))
    if ptype == "number":
        val = prop.get("number")
        return str(val) if val is not None else ""
    return ""


def fetch_all_pages(notion: NotionClient, database_id: str) -> list[dict]:
    """Fetch all pages from a Notion database, handling pagination."""
    pages: list[dict] = []
    cursor = None
    while True:
        kwargs: dict = {"database_id": database_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        response = notion.databases.query(**kwargs)
        pages.extend(response.get("results", []))
        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")
    return pages


# ---------------------------------------------------------------------------
# Card ID transformation
# ---------------------------------------------------------------------------

def transform_card_id(
    old_id: str,
    concept: str,
    layer: str,
    counters: dict[str, int],
) -> str:
    """Transform an old-format card ID into the new format.

    Args:
        old_id: Original card ID from Notion
        concept: Concept name (e.g. "NORMAL", "POISSON")
        layer: Knowledge layer name (e.g. "Visual", "Conceptual")
        counters: Running counter per (prefix, layer_letter) to auto-increment

    Returns:
        New card ID in format prefix-Layer-NN or prefix-NN
    """
    if is_new_format(old_id):
        return old_id

    prefix = CONCEPT_PREFIX_MAP.get(concept, "")
    if not prefix:
        logging.warning("No prefix mapping for concept=%r, keeping old ID: %s", concept, old_id)
        return old_id

    layer_letter = LAYER_LETTER_MAP.get(layer, "")
    if layer_letter:
        key = f"{prefix}-{layer_letter}"
        counters[key] = counters.get(key, 0) + 1
        seq = f"{counters[key]:02d}"
        return f"{prefix}-{layer_letter}-{seq}"
    else:
        key = prefix
        counters[key] = counters.get(key, 0) + 1
        seq = f"{counters[key]:02d}"
        return f"{prefix}-{seq}"


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def build_markdown(
    card_id: str,
    deck: str,
    tags: list[str],
    fire_weight: float,
    notion_last_edited: str,
    prompt: str,
    solution: str,
    topic: str | None = None,
    concept: str | None = None,
    has_visual: bool = False,
) -> str:
    """Build a card markdown file matching the webapp's expected format."""
    tags_str = ", ".join(tags)
    lines = [
        "---",
        f'deck: "{deck}"',
        f"tags: [{tags_str}]",
        f'card_id: "{card_id}"',
        f"fire_weight: {fire_weight}",
        f'notion_last_edited: "{notion_last_edited}"',
    ]
    if topic:
        lines.append(f'topic: "{topic}"')
    if concept:
        lines.append(f'concept: "{concept}"')
    if has_visual:
        lines.append("has_visual: true")
    lines.extend([
        "---",
        "",
        f"# {card_id}",
        "",
        "START",
        prompt,
        "END",
        "",
        "START",
        solution,
        "END",
        "",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def write_card_file(
    base_dir: Path,
    topic: str,
    layer: str,
    card_id: str,
    content: str,
    dry_run: bool = False,
) -> Path:
    """Write a card markdown file to the appropriate subdirectory."""
    layer_dir = LAYER_DIR_MAP.get(layer, layer.lower())
    subdir = base_dir / topic / layer_dir
    filepath = subdir / f"{card_id}.md"

    if dry_run:
        logging.info("  [DRY-RUN] Would write: %s", filepath.relative_to(base_dir))
        return filepath

    subdir.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding="utf-8")
    return filepath


def push_to_anki(cards_data: list[dict], dry_run: bool = False) -> int:
    """Push cards to Anki via AnkiConnect. Returns count of cards pushed."""
    if dry_run:
        logging.info("[DRY-RUN] Would push %d cards to Anki", len(cards_data))
        return 0

    try:
        # Check AnkiConnect is available
        resp = httpx.post(ANKI_URL, json={"action": "version", "version": 6}, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logging.warning("AnkiConnect not available at %s: %s", ANKI_URL, e)
        return 0

    pushed = 0
    # Group by deck for batch creation
    decks_needed: set[str] = {c["deck"] for c in cards_data}
    for deck_name in decks_needed:
        httpx.post(ANKI_URL, json={
            "action": "createDeck",
            "version": 6,
            "params": {"deck": deck_name},
        }, timeout=10)

    for card in cards_data:
        note = {
            "deckName": card["deck"],
            "modelName": "Basic",
            "fields": {
                "Front": card["prompt"],
                "Back": card["solution"],
            },
            "tags": card.get("tags", []),
        }
        try:
            resp = httpx.post(ANKI_URL, json={
                "action": "addNote",
                "version": 6,
                "params": {"note": note},
            }, timeout=10)
            result = resp.json()
            if result.get("error"):
                # Likely duplicate — try update
                logging.debug("Anki addNote error for %s: %s", card["card_id"], result["error"])
            else:
                pushed += 1
        except Exception as e:
            logging.warning("Failed to push %s to Anki: %s", card["card_id"], e)

    return pushed


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    """Load sync state from disk."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    """Persist sync state to disk."""
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main sync
# ---------------------------------------------------------------------------

def sync(
    dry_run: bool = False,
    force: bool = False,
    push_anki: bool = False,
    clean: bool = False,
) -> dict:
    """Run the full sync pipeline. Returns summary stats."""
    if not NOTION_TOKEN:
        logging.error("NOTION_TOKEN not set. Add it to .env or environment.")
        sys.exit(1)
    if not NOTION_DATABASE_ID:
        logging.error("NOTION_DATABASE_ID not set. Add it to .env or environment.")
        sys.exit(1)

    notion = NotionClient(auth=NOTION_TOKEN)
    state = load_state() if not force else {}
    stats = {"fetched": 0, "created": 0, "updated": 0, "skipped": 0, "anki_pushed": 0, "errors": 0}
    anki_cards: list[dict] = []
    counters: dict[str, int] = {}  # For auto-increment during card ID transformation
    pages_to_writeback: list[tuple[str, str]] = []  # (page_id, new_card_id) pairs

    logging.info("Fetching pages from Notion database %s...", NOTION_DATABASE_ID[:8])
    pages = fetch_all_pages(notion, NOTION_DATABASE_ID)
    stats["fetched"] = len(pages)
    logging.info("Fetched %d pages from Notion", len(pages))

    for page in pages:
        page_id = page["id"]
        last_edited = page.get("last_edited_time", "")

        # Idempotency check
        prev = state.get(page_id, {})
        if not force and prev.get("last_edited") == last_edited:
            stats["skipped"] += 1
            continue

        try:
            # Extract properties
            drill_name = get_prop_text(page, "Drill Name") or get_prop_text(page, "Name")
            raw_card_id = get_prop_text(page, "Card ID")
            prompt = get_prop_text(page, "Prompt")
            solution = get_prop_text(page, "Solution")
            knowledge_layer = get_prop_text(page, "Knowledge Layer")
            cognitive_layer = get_prop_text(page, "Cognitive Layer")
            pillar = get_prop_text(page, "Pillar")
            has_visual_str = get_prop_text(page, "Has Visual")
            has_visual = has_visual_str.lower() == "true" if has_visual_str else False
            topic_raw = get_prop_text(page, "Topic")
            concept = get_prop_text(page, "Concept")

            if not prompt or not solution:
                logging.warning("Skipping page %s (%s) — missing prompt or solution", page_id[:8], drill_name)
                stats["errors"] += 1
                continue

            # Determine card_id
            card_id = raw_card_id.strip() if raw_card_id else ""
            if card_id and is_new_format(card_id):
                # Already in new format, use as-is
                pass
            elif concept:
                # Transform old format to new
                new_id = transform_card_id(card_id, concept, knowledge_layer, counters)
                if new_id != card_id:
                    pages_to_writeback.append((page_id, new_id))
                    card_id = new_id
            elif not card_id:
                logging.warning("Skipping page %s (%s) — no Card ID or Concept", page_id[:8], drill_name)
                stats["errors"] += 1
                continue

            # Determine topic
            topic = topic_raw.strip().lower().replace(" ", "-") if topic_raw else None
            if not topic:
                # Derive from card_id prefix
                prefix = card_id.split("-")[0]
                topic = PREFIX_TOPIC_MAP.get(prefix)
            if not topic:
                topic = "uncategorized"

            # Determine knowledge layer for directory
            layer = knowledge_layer if knowledge_layer else "Special"

            # Build tags
            tags: list[str] = []
            if topic:
                tags.append(topic)
            if knowledge_layer:
                tags.append(knowledge_layer.lower())
            if cognitive_layer:
                tags.append(cognitive_layer.lower().replace(" ", "-"))

            # Build deck name
            pillar_part = pillar if pillar else "Uncategorized"
            deck = f"JobAcademy::{topic}::{pillar_part}"

            fire_weight = 0.5

            # Build markdown
            md = build_markdown(
                card_id=card_id,
                deck=deck,
                tags=tags,
                fire_weight=fire_weight,
                notion_last_edited=last_edited,
                prompt=prompt,
                solution=solution,
                topic=topic,
                concept=concept if concept else None,
                has_visual=has_visual,
            )

            # Write to webapp cards dir
            write_card_file(CARDS_DIR, topic, layer, card_id, md, dry_run=dry_run)

            # Write to Obsidian vault (if configured)
            if OBSIDIAN_VAULT_PATH:
                obsidian_base = Path(OBSIDIAN_VAULT_PATH)
                write_card_file(obsidian_base, topic, layer, card_id, md, dry_run=dry_run)

            # Collect for Anki push
            if push_anki:
                anki_cards.append({
                    "card_id": card_id,
                    "deck": deck,
                    "prompt": prompt,
                    "solution": solution,
                    "tags": tags,
                })

            # Update state
            is_new = page_id not in state
            state[page_id] = {"card_id": card_id, "last_edited": last_edited}

            if is_new:
                stats["created"] += 1
            else:
                stats["updated"] += 1

        except Exception as e:
            logging.error("Error processing page %s: %s", page_id[:8], e, exc_info=True)
            stats["errors"] += 1

    # Write back new card IDs to Notion
    if pages_to_writeback and not dry_run:
        logging.info("Writing back %d new Card IDs to Notion...", len(pages_to_writeback))
        for pid, new_cid in pages_to_writeback:
            try:
                notion.pages.update(
                    page_id=pid,
                    properties={
                        "Card ID": {"rich_text": [{"text": {"content": new_cid}}]},
                    },
                )
            except Exception as e:
                logging.warning("Failed to write back Card ID %s to page %s: %s", new_cid, pid[:8], e)
    elif pages_to_writeback and dry_run:
        logging.info("[DRY-RUN] Would write back %d new Card IDs to Notion", len(pages_to_writeback))

    # Push to Anki
    if push_anki and anki_cards:
        stats["anki_pushed"] = push_to_anki(anki_cards, dry_run=dry_run)

    # Save state
    if not dry_run:
        save_state(state)

    # Clean old flat files
    if clean and not dry_run:
        cleaned = 0
        for f in CARDS_DIR.glob("nb-*.md"):
            if f.is_file():
                f.unlink()
                cleaned += 1
        if cleaned:
            logging.info("Cleaned %d old flat nb-*.md files from root cards dir", cleaned)
    elif clean and dry_run:
        flat_count = sum(1 for f in CARDS_DIR.glob("nb-*.md") if f.is_file())
        logging.info("[DRY-RUN] Would clean %d old flat nb-*.md files", flat_count)

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sync Notion cards to webapp, Obsidian, and Anki")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--force", action="store_true", help="Re-sync all pages regardless of timestamps")
    parser.add_argument("--anki", action="store_true", help="Also push cards to Anki via AnkiConnect")
    parser.add_argument("--clean", action="store_true", help="Delete old flat nb-*.md files after sync")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    logging.info("Starting Notion -> All sync pipeline")
    logging.info("  Cards dir: %s", CARDS_DIR)
    if OBSIDIAN_VAULT_PATH:
        logging.info("  Obsidian vault: %s", OBSIDIAN_VAULT_PATH)
    if args.anki:
        logging.info("  Anki push: enabled (%s)", ANKI_URL)
    if args.dry_run:
        logging.info("  Mode: DRY RUN")
    if args.force:
        logging.info("  Mode: FORCE (ignoring timestamps)")

    stats = sync(
        dry_run=args.dry_run,
        force=args.force,
        push_anki=args.anki,
        clean=args.clean,
    )

    logging.info("--- Sync Summary ---")
    logging.info("  Fetched:  %d pages", stats["fetched"])
    logging.info("  Created:  %d cards", stats["created"])
    logging.info("  Updated:  %d cards", stats["updated"])
    logging.info("  Skipped:  %d cards (unchanged)", stats["skipped"])
    if stats["anki_pushed"]:
        logging.info("  Anki:     %d cards pushed", stats["anki_pushed"])
    if stats["errors"]:
        logging.warning("  Errors:   %d", stats["errors"])
    logging.info("Done.")


if __name__ == "__main__":
    main()
