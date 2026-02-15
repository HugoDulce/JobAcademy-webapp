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
    card_count: int = 0


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str = "prerequisite"


class KnowledgeGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    layers: dict[int, str]


class SubtopicSummary(BaseModel):
    id: str
    name: str
    card_count: int


class SubtreeCardBreakdownItem(BaseModel):
    concept: str
    count: int
    is_prerequisite: bool


class SubtreeCardDistribution(BaseModel):
    node_id: str
    total: int
    breakdown: list[SubtreeCardBreakdownItem]
