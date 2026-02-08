"""Tests for mermaid_parser — nodes, edges, layer assignment."""

from app.parsers.mermaid_parser import parse_mermaid_file


class TestParseMermaid:
    def test_finds_all_nodes(self, sample_mermaid_path):
        graph = parse_mermaid_file(sample_mermaid_path)
        ids = {n.id for n in graph.nodes}
        assert ids == {"PROB", "BAYES", "NB"}

    def test_node_labels(self, sample_mermaid_path):
        graph = parse_mermaid_file(sample_mermaid_path)
        labels = {n.id: n.label for n in graph.nodes}
        assert labels["PROB"] == "Probability Basics"
        assert labels["NB"] == "Naive Bayes"

    def test_edges(self, sample_mermaid_path):
        graph = parse_mermaid_file(sample_mermaid_path)
        edge_pairs = [(e.source, e.target) for e in graph.edges]
        assert ("PROB", "BAYES") in edge_pairs
        assert ("BAYES", "NB") in edge_pairs
        assert len(graph.edges) == 2

    def test_layer_assignment(self, sample_mermaid_path):
        graph = parse_mermaid_file(sample_mermaid_path)
        node_map = {n.id: n for n in graph.nodes}
        assert node_map["PROB"].style_class == "foundation"
        assert node_map["PROB"].layer == 0
        assert node_map["BAYES"].style_class == "core"
        assert node_map["BAYES"].layer == 1
        assert node_map["NB"].style_class == "supervised"
        assert node_map["NB"].layer == 2

    def test_layer_colors(self, sample_mermaid_path):
        graph = parse_mermaid_file(sample_mermaid_path)
        node_map = {n.id: n for n in graph.nodes}
        assert node_map["PROB"].fill_color == "#dbeafe"
        assert node_map["PROB"].stroke_color == "#3b82f6"

    def test_layers_dict(self, sample_mermaid_path):
        graph = parse_mermaid_file(sample_mermaid_path)
        assert 0 in graph.layers
        assert graph.layers[0] == "Mathematical Foundations"
