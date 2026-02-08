"""Knowledge graph API endpoints."""

from fastapi import APIRouter

from app.models.graph import KnowledgeGraph
from app.services import graph_service

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("", response_model=KnowledgeGraph)
def get_graph():
    """Get the full knowledge graph with mastery overlay."""
    return graph_service.get_knowledge_graph()
