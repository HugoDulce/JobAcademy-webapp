"""Knowledge graph API endpoints."""

from fastapi import APIRouter, HTTPException

from app.models.card import Card
from app.models.graph import KnowledgeGraph, SubtopicSummary, SubtreeCardDistribution
from app.services import graph_service

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=KnowledgeGraph)
def get_graph():
    """Get the full knowledge graph with mastery overlay."""
    return graph_service.get_knowledge_graph()


@router.get("/{node_id}/subtree", response_model=KnowledgeGraph)
def get_subtree(node_id: str):
    """Get the prerequisite subtree for a node (BFS backward)."""
    subtree = graph_service.get_subtree(node_id)
    if not subtree.nodes:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return subtree


@router.get("/{node_id}/cards", response_model=list[Card])
def get_node_cards(node_id: str):
    """Get all drillable cards linked to a graph node."""
    return graph_service.get_node_cards(node_id)


@router.get("/nodes/{node_id}/subtopics", response_model=list[SubtopicSummary])
def get_node_subtopics(node_id: str):
    """Get subtopics within a concept node, grouped with card counts."""
    return graph_service.get_concept_subtopics(node_id)


@router.get("/nodes/{node_id}/subtopics/{subtopic}/cards", response_model=list[Card])
def get_subtopic_cards(node_id: str, subtopic: str):
    """Get all cards for a specific subtopic within a concept."""
    return graph_service.get_subtopic_cards(node_id, subtopic)


@router.get("/nodes/{node_id}/subtree-cards", response_model=SubtreeCardDistribution)
def get_subtree_cards(node_id: str):
    """Get selected node cards grouped by concepts in its prerequisite subtree."""
    subtree = graph_service.get_subtree(node_id)
    if not subtree.nodes:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return graph_service.get_subtree_card_distribution(node_id)
