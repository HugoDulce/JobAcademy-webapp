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
    "V": "Visual",
}

# Special prefixes
SPECIAL_PREFIXES = {"CF", "D", "EXT", "MKT"}

# Concept prefix -> concept name (prefix in card_id -> concept)
CONCEPT_PREFIX_MAP = {
    "norm": "NORMAL",
    "pois": "POISSON",
    "binom": "BINOMIAL",
    "bern": "BERNOULLI",
    "gamma": "GAMMA",
    "beta": "BETA",
    "unif": "UNIFORM",
    "stud": "STUDENT_T",
    "weib": "WEIBULL",
    "lnorm": "LOGNORMAL",
    "dunif": "DISCRETE_UNIFORM",
    "hyper": "HYPERGEOMETRIC",
    "nbinom": "NEGATIVE_BINOMIAL",
    "geom": "GEOMETRIC",
    "prob": "PROB",
    "prob-cat": "PROB_CAT",
    "prob-prop": "PROB_PROP",
}

# Card ID prefix -> topic
TOPIC_MAP = {
    "nb": "naive-bayes",
    **{k: "probability-distributions" for k in CONCEPT_PREFIX_MAP},
}

# Graph node ID → card topic prefix(es) for linking nodes to drillable cards
NODE_CARD_MAP: dict[str, list[str]] = {
    "NB": ["nb"],
    # Future: "LOGREG": ["logreg"], "KNN": ["knn"], etc.
}

# Sorted longest-first for greedy matching
_CONCEPT_PREFIXES_SORTED = sorted(CONCEPT_PREFIX_MAP.keys(), key=len, reverse=True)


def parse_card_id(card_id: str) -> dict:
    """Extract pillar, knowledge layer, topic, and concept from card_id.

    Supports 4 formats:
    1. Legacy NB:      nb-3M-01    (prefix-digitLayer-number)
    2. Concept+Layer:  norm-V-01   (conceptPrefix-Layer-number)
    3. Concept-only:   prob-cat-01 (conceptPrefix-number)
    4. Special:        nb-CF-01    (prefix-SPECIAL-number)
    """
    result = {
        "pillar": None,
        "knowledge_layer": None,
        "topic": None,
        "concept": None,
    }

    # Strategy 1: Legacy NB — e.g. nb-3M-01, nb-1C-02a
    m = re.match(r"^([a-z]+)-(\d)([CMPIV])-(\d+[a-z]?)$", card_id)
    if m:
        prefix, pillar_num, layer_letter, _ = m.groups()
        result["pillar"] = PILLAR_MAP.get(pillar_num, f"{pillar_num}-Unknown")
        result["knowledge_layer"] = LAYER_MAP.get(layer_letter, "Unknown")
        result["topic"] = TOPIC_MAP.get(prefix)
        return result

    # Strategy 2: Concept+Layer — e.g. norm-V-01, binom-C-03, prob-cat-M-01
    for cp in _CONCEPT_PREFIXES_SORTED:
        pattern = rf"^({re.escape(cp)})-([CMPIV])-(\d+[a-z]?)$"
        m = re.match(pattern, card_id)
        if m:
            matched_prefix, layer_letter, _ = m.groups()
            result["knowledge_layer"] = LAYER_MAP.get(layer_letter, "Unknown")
            result["concept"] = CONCEPT_PREFIX_MAP.get(matched_prefix)
            result["topic"] = TOPIC_MAP.get(matched_prefix)
            return result

    # Strategy 3: Concept-only — e.g. prob-cat-01, prob-prop-02
    for cp in _CONCEPT_PREFIXES_SORTED:
        pattern = rf"^({re.escape(cp)})-(\d+[a-z]?)$"
        m = re.match(pattern, card_id)
        if m:
            matched_prefix, _ = m.groups()
            result["concept"] = CONCEPT_PREFIX_MAP.get(matched_prefix)
            result["topic"] = TOPIC_MAP.get(matched_prefix)
            return result

    # Strategy 4: Special prefix — e.g. nb-CF-01, nb-EXT-02
    m = re.match(r"^([a-z]+)-([A-Z]+)-(\d+[a-z]?)$", card_id)
    if m:
        prefix, special, _ = m.groups()
        if special in SPECIAL_PREFIXES:
            result["pillar"] = special
            result["knowledge_layer"] = "Special"
            result["topic"] = TOPIC_MAP.get(prefix)
            return result

    return result


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

    # Parse new frontmatter fields
    topic_match = re.search(r'topic:\s*"?([^"\n]+)"?', fm)
    fm_topic = topic_match.group(1).strip() if topic_match else None

    concept_match = re.search(r'concept:\s*"?([^"\n]+)"?', fm)
    fm_concept = concept_match.group(1).strip() if concept_match else None

    has_visual_match = re.search(r"has_visual:\s*(true|false)", fm, re.IGNORECASE)
    has_visual = has_visual_match.group(1).lower() == "true" if has_visual_match else False

    concept_node_match = re.search(r'concept_node:\s*"?([^"\n]+)"?', fm)
    concept_node = concept_node_match.group(1).strip() if concept_node_match else None

    subtopic_match = re.search(r'subtopic:\s*"?([^"\n]+)"?', fm)
    subtopic = subtopic_match.group(1).strip() if subtopic_match else None

    # Extract START/END blocks
    blocks = re.findall(r"START\n(.*?)\nEND", text, re.DOTALL)
    if len(blocks) < 2:
        return None

    prompt = blocks[0].strip()
    solution = blocks[1].strip()

    # Derive pillar/layer/topic/concept from card_id
    id_info = parse_card_id(card_id)

    # Frontmatter values override derived values
    topic = fm_topic or id_info.get("topic")
    concept = fm_concept or id_info.get("concept")

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
        topic=topic,
        concept=concept,
        has_visual=has_visual,
        concept_node=concept_node,
        subtopic=subtopic,
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
    ]
    if card.topic:
        lines.append(f'topic: "{card.topic}"')
    if card.concept:
        lines.append(f'concept: "{card.concept}"')
    if card.has_visual:
        lines.append("has_visual: true")
    if card.concept_node:
        lines.append(f'concept_node: "{card.concept_node}"')
    if card.subtopic:
        lines.append(f'subtopic: "{card.subtopic}"')
    lines.extend([
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
    ])
    return "\n".join(lines)
