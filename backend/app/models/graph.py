from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    layer: int
    layer_name: str
    style_class: str
    fill_color: str
    stroke_color: str
    mastery: float | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str = "prerequisite"


class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    layers: dict[int, str]
