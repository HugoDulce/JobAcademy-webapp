"""Parse a Mermaid graph TD file into nodes, edges, and layer assignments."""

import re
from pathlib import Path

from app.models.graph import GraphEdge, GraphNode, KnowledgeGraph

# Layer metadata from classDef declarations
LAYER_INFO = {
    "foundation": {
        "layer": 0,
        "name": "Mathematical Foundations",
        "fill": "#dbeafe",
        "stroke": "#3b82f6",
    },
    "core": {
        "layer": 1,
        "name": "ML Core Primitives",
        "fill": "#d1fae5",
        "stroke": "#10b981",
    },
    "supervised": {
        "layer": 2,
        "name": "Supervised Models",
        "fill": "#fef3c7",
        "stroke": "#f59e0b",
    },
    "stats": {
        "layer": 3,
        "name": "Stats & Experimentation",
        "fill": "#e0e7ff",
        "stroke": "#6366f1",
    },
    "causal": {
        "layer": 4,
        "name": "Causal Inference",
        "fill": "#fff7ed",
        "stroke": "#ea580c",
    },
    "marketing": {
        "layer": 5,
        "name": "Marketing Science",
        "fill": "#f3e8ff",
        "stroke": "#9333ea",
    },
    "systems": {
        "layer": 6,
        "name": "Marketing Systems",
        "fill": "#fee2e2",
        "stroke": "#ef4444",
    },
    "project": {
        "layer": 7,
        "name": "Sports Lab Projects",
        "fill": "#fef08a",
        "stroke": "#ca8a04",
    },
}


def parse_mermaid_file(filepath: Path) -> KnowledgeGraph:
    """Parse a mermaid graph TD file into a KnowledgeGraph."""
    text = filepath.read_text(encoding="utf-8")

    # 1. Parse node definitions: ID["label<br/>more"]
    node_defs: dict[str, str] = {}
    for m in re.finditer(r'^\s+(\w+)\["([^"]+)"\]', text, re.MULTILINE):
        node_id = m.group(1)
        # Clean label: remove emoji, replace <br/> with space
        label = m.group(2)
        label = re.sub(r"[\U0001f300-\U0001f9ff]", "", label).strip()  # Remove emoji
        label = label.replace("<br/>", " ").replace("<br>", " ")
        label = re.sub(r"\s+", " ", label).strip()
        node_defs[node_id] = label

    # 2. Parse edges: SOURCE --> TARGET
    edges: list[GraphEdge] = []
    for m in re.finditer(r"^\s+(\w+)\s+-->\s+(\w+)", text, re.MULTILINE):
        source, target = m.group(1), m.group(2)
        if source in node_defs and target in node_defs:
            edges.append(GraphEdge(source=source, target=target))

    # 3. Parse class assignments: class ID1,ID2,... styleName
    node_classes: dict[str, str] = {}
    for m in re.finditer(r"^\s+class\s+([\w,]+)\s+(\w+)", text, re.MULTILINE):
        ids = m.group(1).split(",")
        style_class = m.group(2)
        for nid in ids:
            nid = nid.strip()
            if nid in node_defs:
                node_classes[nid] = style_class

    # 4. Build nodes
    nodes: list[GraphNode] = []
    for nid, label in node_defs.items():
        style_class = node_classes.get(nid, "core")
        info = LAYER_INFO.get(style_class, LAYER_INFO["core"])
        nodes.append(
            GraphNode(
                id=nid,
                label=label,
                layer=info["layer"],
                layer_name=info["name"],
                style_class=style_class,
                fill_color=info["fill"],
                stroke_color=info["stroke"],
            )
        )

    # 5. Build layers map
    layers = {v["layer"]: v["name"] for v in LAYER_INFO.values()}

    return KnowledgeGraph(nodes=nodes, edges=edges, layers=layers)
