"""Tests for graph_service — concept_node matching, subtopics, distribution."""

from pathlib import Path
from unittest.mock import patch

from app.models.card import Card
from app.models.graph import GraphEdge, GraphNode, KnowledgeGraph
from app.parsers.card_parser import card_to_markdown, parse_card_file
from app.services.graph_service import (
    get_concept_subtopics,
    get_node_cards,
    get_subtopic_cards,
    get_subtree_card_distribution,
)

FIXTURES = Path(__file__).parent / "fixtures"

# Patch target: list_cards is imported lazily inside service functions,
# so we patch the source module, not graph_service itself.
_PATCH_LIST_CARDS = "app.services.card_service.list_cards"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_card(card_id: str, concept_node: str | None = None, subtopic: str | None = None) -> Card:
    return Card(
        card_id=card_id,
        deck="JobAcademy::Test",
        tags=["test"],
        fire_weight=0.5,
        notion_last_edited="",
        prompt="Q",
        solution="A",
        concept_node=concept_node,
        subtopic=subtopic,
    )


SAMPLE_CARDS = [
    _make_card("nb-3C-01", concept_node="NB", subtopic="variants"),
    _make_card("nb-3C-02", concept_node="NB", subtopic="variants"),
    _make_card("nb-3M-01", concept_node="NB", subtopic="math"),
    _make_card("nb-1M-01", concept_node="BAYES", subtopic="formula"),
    _make_card("nb-2C-01", concept_node="COND"),
    _make_card("nb-LEGACY-01"),  # No concept_node — untagged
]

SAMPLE_GRAPH = KnowledgeGraph(
    nodes=[
        GraphNode(id="PROB", label="Probability", layer=0, layer_name="Foundation",
                  style_class="foundation", fill_color="#f0f0f0", stroke_color="#ccc"),
        GraphNode(id="BAYES", label="Bayes Theorem", layer=1, layer_name="Theorem",
                  style_class="theorem", fill_color="#e0e7ff", stroke_color="#6366f1"),
        GraphNode(id="COND", label="Conditional Independence", layer=1, layer_name="Theorem",
                  style_class="theorem", fill_color="#e0e7ff", stroke_color="#6366f1"),
        GraphNode(id="NB", label="Naive Bayes", layer=2, layer_name="Algorithm",
                  style_class="algorithm", fill_color="#dbeafe", stroke_color="#3b82f6"),
    ],
    edges=[
        GraphEdge(source="PROB", target="BAYES"),
        GraphEdge(source="PROB", target="COND"),
        GraphEdge(source="BAYES", target="NB"),
        GraphEdge(source="COND", target="NB"),
    ],
    layers={0: "Foundation", 1: "Theorem", 2: "Algorithm"},
)


def _mock_list_cards():
    return SAMPLE_CARDS


# ---------------------------------------------------------------------------
# Parser: concept_node + subtopic parsing and roundtrip
# ---------------------------------------------------------------------------


class TestConceptNodeParsing:
    def test_parse_concept_node_from_frontmatter(self):
        card = parse_card_file(FIXTURES / "nb-concept-node.md")
        assert card is not None
        assert card.concept_node == "NB"
        assert card.subtopic == "variants"

    def test_parse_bayes_concept_node(self):
        card = parse_card_file(FIXTURES / "nb-bayes.md")
        assert card is not None
        assert card.concept_node == "BAYES"
        assert card.subtopic == "formula"

    def test_parse_no_concept_node(self):
        card = parse_card_file(FIXTURES / "nb-no-concept.md")
        assert card is not None
        assert card.concept_node is None
        assert card.subtopic is None

    def test_roundtrip_preserves_concept_node(self):
        card = parse_card_file(FIXTURES / "nb-concept-node.md")
        md = card_to_markdown(card)
        assert 'concept_node: "NB"' in md
        assert 'subtopic: "variants"' in md

        # Re-parse the generated markdown
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            card2 = parse_card_file(Path(f.name))

        assert card2.concept_node == card.concept_node
        assert card2.subtopic == card.subtopic

    def test_roundtrip_omits_none_fields(self):
        card = parse_card_file(FIXTURES / "nb-no-concept.md")
        md = card_to_markdown(card)
        assert 'concept_node:' not in md
        assert 'subtopic:' not in md


# ---------------------------------------------------------------------------
# get_node_cards: dual-source matching
# ---------------------------------------------------------------------------


class TestGetNodeCards:
    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_nb_returns_only_nb_tagged_cards(self, _mock):
        cards = get_node_cards("NB")
        card_ids = {c.card_id for c in cards}
        assert "nb-3C-01" in card_ids
        assert "nb-3C-02" in card_ids
        assert "nb-3M-01" in card_ids
        # Untagged card matched via prefix fallback
        assert "nb-LEGACY-01" in card_ids
        # Cards tagged to other nodes excluded
        assert "nb-1M-01" not in card_ids
        assert "nb-2C-01" not in card_ids

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_bayes_returns_only_bayes_card(self, _mock):
        cards = get_node_cards("BAYES")
        assert len(cards) == 1
        assert cards[0].card_id == "nb-1M-01"

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_cond_returns_only_cond_card(self, _mock):
        cards = get_node_cards("COND")
        assert len(cards) == 1
        assert cards[0].card_id == "nb-2C-01"

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_unknown_node_returns_empty(self, _mock):
        cards = get_node_cards("NONEXISTENT")
        assert cards == []

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_untagged_card_falls_back_to_prefix(self, _mock):
        """An untagged nb-* card should appear under NB via NODE_CARD_MAP."""
        cards = get_node_cards("NB")
        card_ids = {c.card_id for c in cards}
        assert "nb-LEGACY-01" in card_ids


# ---------------------------------------------------------------------------
# get_concept_subtopics
# ---------------------------------------------------------------------------


class TestGetConceptSubtopics:
    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_nb_subtopics(self, _mock):
        subtopics = get_concept_subtopics("NB")
        sub_map = {s.id: s.card_count for s in subtopics}
        assert sub_map["variants"] == 2
        assert sub_map["math"] == 1
        # Untagged legacy card has no subtopic → "uncategorized"
        assert sub_map["uncategorized"] == 1

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_bayes_subtopics(self, _mock):
        subtopics = get_concept_subtopics("BAYES")
        assert len(subtopics) == 1
        assert subtopics[0].id == "formula"
        assert subtopics[0].card_count == 1

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_empty_node_subtopics(self, _mock):
        subtopics = get_concept_subtopics("PROB")
        assert subtopics == []


# ---------------------------------------------------------------------------
# get_subtopic_cards
# ---------------------------------------------------------------------------


class TestGetSubtopicCards:
    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_nb_variants(self, _mock):
        cards = get_subtopic_cards("NB", "variants")
        assert len(cards) == 2
        assert {c.card_id for c in cards} == {"nb-3C-01", "nb-3C-02"}

    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_uncategorized_subtopic(self, _mock):
        cards = get_subtopic_cards("NB", "uncategorized")
        assert len(cards) == 1
        assert cards[0].card_id == "nb-LEGACY-01"


# ---------------------------------------------------------------------------
# get_subtree_card_distribution
# ---------------------------------------------------------------------------


class TestGetSubtreeCardDistribution:
    @patch("app.services.graph_service.get_knowledge_graph", return_value=SAMPLE_GRAPH)
    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_nb_distribution_includes_all_subtree_nodes(self, _mock_cards, _mock_graph):
        dist = get_subtree_card_distribution("NB")
        assert dist.node_id == "NB"
        # 3 NB + 1 BAYES + 1 COND + 1 untagged legacy (via NB prefix) = 6
        assert dist.total == 6

        breakdown_map = {b.concept: b for b in dist.breakdown}
        assert breakdown_map["NB"].count == 4  # 3 tagged + 1 legacy prefix
        assert breakdown_map["BAYES"].count == 1
        assert breakdown_map["COND"].count == 1
        assert breakdown_map["PROB"].count == 0

        assert breakdown_map["NB"].is_prerequisite is False
        assert breakdown_map["BAYES"].is_prerequisite is True
        assert breakdown_map["COND"].is_prerequisite is True
        assert breakdown_map["PROB"].is_prerequisite is True

    @patch("app.services.graph_service.get_knowledge_graph", return_value=SAMPLE_GRAPH)
    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_bayes_distribution(self, _mock_cards, _mock_graph):
        dist = get_subtree_card_distribution("BAYES")
        breakdown_map = {b.concept: b for b in dist.breakdown}
        assert dist.total == 1
        assert breakdown_map["BAYES"].count == 1
        assert breakdown_map["PROB"].count == 0

    @patch("app.services.graph_service.get_knowledge_graph", return_value=SAMPLE_GRAPH)
    @patch(_PATCH_LIST_CARDS, side_effect=_mock_list_cards)
    def test_nonexistent_node_returns_empty(self, _mock_cards, _mock_graph):
        dist = get_subtree_card_distribution("DOESNOTEXIST")
        assert dist.total == 0
        assert dist.breakdown == []
