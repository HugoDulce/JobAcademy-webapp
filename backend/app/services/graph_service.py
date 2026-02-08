"""Knowledge graph service — loads and enriches the DAG."""

import threading

from app.config import DOCS_DIR
from app.models.graph import KnowledgeGraph
from app.parsers.mermaid_parser import parse_mermaid_file

_cached_graph: KnowledgeGraph | None = None
_lock = threading.Lock()


def get_knowledge_graph() -> KnowledgeGraph:
    """Get the knowledge graph, enriched with mastery data if available."""
    global _cached_graph
    with _lock:
        if _cached_graph is None:
            mermaid_file = DOCS_DIR / "jobacademy-ml-marketing.mermaid"
            _cached_graph = parse_mermaid_file(mermaid_file)

    # Try to enrich with Anki mastery data
    try:
        _enrich_mastery(_cached_graph)
    except Exception:
        pass  # Anki may not be running

    return _cached_graph


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
