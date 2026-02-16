"""Knowledge graph service — loads and enriches the DAG."""

import threading
from collections import deque

from app.config import DOCS_DIR
from app.models.card import Card
from app.models.graph import SubtopicSummary, SubtreeCardBreakdownItem, SubtreeCardDistribution, KnowledgeGraph
from app.parsers.card_parser import NODE_CARD_MAP
from app.parsers.mermaid_parser import parse_mermaid_file

_cached_graph: KnowledgeGraph | None = None
_lock = threading.Lock()


def get_knowledge_graph() -> KnowledgeGraph:
    """Get the knowledge graph, enriched with mastery and card count data."""
    global _cached_graph
    with _lock:
        if _cached_graph is None:
            mermaid_file = DOCS_DIR / "jobacademy-ml-marketing.mermaid"
            _cached_graph = parse_mermaid_file(mermaid_file)

    # Enrich with card counts from .md files
    _enrich_card_counts(_cached_graph)

    # Try to enrich with Anki mastery data
    try:
        _enrich_mastery(_cached_graph)
    except Exception:
        pass  # Anki may not be running

    return _cached_graph


def get_subtree(node_id: str) -> KnowledgeGraph:
    """BFS backward through edges to collect all prerequisite nodes + the root.

    Returns a filtered KnowledgeGraph containing only the subtree.
    """
    graph = get_knowledge_graph()

    # Build reverse adjacency: target → list of sources (prerequisites)
    reverse_adj: dict[str, list[str]] = {}
    for edge in graph.edges:
        reverse_adj.setdefault(edge.target, []).append(edge.source)

    # BFS backward from node_id
    visited: set[str] = set()
    queue: deque[str] = deque()
    if any(n.id == node_id for n in graph.nodes):
        queue.append(node_id)
        visited.add(node_id)

    while queue:
        current = queue.popleft()
        for prereq in reverse_adj.get(current, []):
            if prereq not in visited:
                visited.add(prereq)
                queue.append(prereq)

    # Filter nodes and edges to only the subtree
    subtree_nodes = [n for n in graph.nodes if n.id in visited]
    subtree_edges = [
        e for e in graph.edges if e.source in visited and e.target in visited
    ]

    return KnowledgeGraph(
        nodes=subtree_nodes,
        edges=subtree_edges,
        layers=graph.layers,
    )


def get_node_cards(node_id: str) -> list[Card]:
    """Get all cards linked to a graph node.

    Dual-source: matches cards by concept_node field first, then falls back
    to NODE_CARD_MAP prefix matching. Results are deduplicated by card_id.
    """
    from app.services.card_service import list_cards

    all_cards = list_cards()
    matched: dict[str, Card] = {}

    # Source 1: explicit concept_node field
    for card in all_cards:
        if card.concept_node == node_id:
            matched[card.card_id] = card

    # Source 2: prefix fallback via NODE_CARD_MAP (only for untagged cards)
    prefixes = NODE_CARD_MAP.get(node_id, [])
    for card in all_cards:
        if (
            card.concept_node is None
            and card.card_id not in matched
            and any(card.card_id.startswith(p + "-") for p in prefixes)
        ):
            matched[card.card_id] = card

    return list(matched.values())


def get_concept_subtopics(node_id: str) -> list[SubtopicSummary]:
    """Group cards by subtopic for a given concept node."""
    cards = get_node_cards(node_id)
    groups: dict[str, int] = {}
    for card in cards:
        key = card.subtopic or "uncategorized"
        groups[key] = groups.get(key, 0) + 1
    return [
        SubtopicSummary(
            id=subtopic,
            name=subtopic.replace("-", " ").title(),
            card_count=count,
        )
        for subtopic, count in groups.items()
    ]


def get_subtopic_cards(node_id: str, subtopic: str) -> list[Card]:
    """Get all cards for a specific subtopic within a concept."""
    all_cards = get_node_cards(node_id)
    return [c for c in all_cards if (c.subtopic or "uncategorized") == subtopic]


def get_subtree_card_distribution(node_id: str) -> SubtreeCardDistribution:
    """Get cards across all nodes in the prerequisite subtree, grouped by concept."""
    subtree = get_subtree(node_id)
    subtree_node_ids = {n.id for n in subtree.nodes}
    if node_id not in subtree_node_ids:
        return SubtreeCardDistribution(node_id=node_id, total=0, breakdown=[])

    # Collect cards from every node in the subtree
    all_cards: dict[str, str] = {}  # card_id → concept_node_id
    for sid in subtree_node_ids:
        for card in get_node_cards(sid):
            if card.card_id not in all_cards:
                all_cards[card.card_id] = sid

    breakdown: dict[str, SubtreeCardBreakdownItem] = {}
    for _card_id, concept in all_cards.items():
        item = breakdown.get(concept)
        if item is None:
            item = SubtreeCardBreakdownItem(
                concept=concept,
                count=0,
                is_prerequisite=(concept != node_id),
            )
            breakdown[concept] = item
        item.count += 1

    # Ensure all subtree nodes appear, even with zero cards.
    for concept in subtree_node_ids:
        if concept not in breakdown:
            breakdown[concept] = SubtreeCardBreakdownItem(
                concept=concept,
                count=0,
                is_prerequisite=(concept != node_id),
            )

    ordered_breakdown = sorted(
        breakdown.values(),
        key=lambda item: (item.concept == node_id, item.concept),
    )
    return SubtreeCardDistribution(
        node_id=node_id,
        total=len(all_cards),
        breakdown=ordered_breakdown,
    )


def _enrich_card_counts(graph: KnowledgeGraph):
    """Populate card_count on each node using concept_node + NODE_CARD_MAP."""
    from app.services.card_service import list_cards

    all_cards = list_cards()

    # Pre-build concept_node index: node_id → set of card_ids
    concept_index: dict[str, set[str]] = {}
    for card in all_cards:
        if card.concept_node:
            concept_index.setdefault(card.concept_node, set()).add(card.card_id)

    for node in graph.nodes:
        matched_ids: set[str] = set()

        # Source 1: concept_node field
        matched_ids.update(concept_index.get(node.id, set()))

        # Source 2: prefix fallback (only for untagged cards)
        prefixes = NODE_CARD_MAP.get(node.id, [])
        for card in all_cards:
            if card.concept_node is None and any(
                card.card_id.startswith(p + "-") for p in prefixes
            ):
                matched_ids.add(card.card_id)

        node.card_count = len(matched_ids)


def _enrich_mastery(graph: KnowledgeGraph):
    """Query Anki for card intervals and compute per-node mastery."""
    from app.services.anki_service import _invoke

    # Get all JobAcademy cards
    card_ids = _invoke("findCards", query="deck:JobAcademy")
    if not card_ids:
        return

    cards_info = _invoke("cardsInfo", cards=card_ids)

    # Get note info for tags (which contain card_id like "nb-3M-01")
    note_ids = list({c["note"] for c in cards_info})
    notes_info = _invoke("notesInfo", notes=note_ids)

    # Build note_id → intervals dict (fixes O(n²) nested loop)
    note_intervals: dict[int, int] = {}
    for ci in cards_info:
        note_intervals[ci["note"]] = ci.get("interval", 0)

    nb_intervals = []
    for note in notes_info:
        tags = note.get("tags", [])
        for tag in tags:
            if tag.startswith("nb-"):
                interval = note_intervals.get(note["noteId"], 0)
                if interval is not None:
                    nb_intervals.append(interval)
                break

    # Compute mastery for NB node
    if nb_intervals:
        avg_interval = sum(nb_intervals) / len(nb_intervals)
        mastery = min(avg_interval / 21.0, 1.0)  # 21 days = fully mastered
        for node in graph.nodes:
            if node.id == "NB":
                node.mastery = round(mastery, 2)
                break


def invalidate_cache():
    """Force re-parse of mermaid file."""
    global _cached_graph
    with _lock:
        _cached_graph = None
