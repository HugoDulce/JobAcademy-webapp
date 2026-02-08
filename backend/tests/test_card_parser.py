"""Tests for card_parser — parse, roundtrip, ID extraction, edge cases."""

from pathlib import Path

from app.parsers.card_parser import card_to_markdown, parse_card_file, parse_card_id


class TestParseCardId:
    def test_standard_id(self):
        result = parse_card_id("nb-3M-01")
        assert result["pillar"] == "3-Algorithm"
        assert result["knowledge_layer"] == "Mathematical"

    def test_conceptual_layer(self):
        result = parse_card_id("nb-1C-02")
        assert result["pillar"] == "1-Use Case"
        assert result["knowledge_layer"] == "Conceptual"

    def test_programming_layer(self):
        result = parse_card_id("nb-3P-01")
        assert result["pillar"] == "3-Algorithm"
        assert result["knowledge_layer"] == "Programming"

    def test_integration_layer(self):
        result = parse_card_id("nb-6I-01")
        assert result["pillar"] == "6-Integration"
        assert result["knowledge_layer"] == "Integration"

    def test_suffix_letter(self):
        result = parse_card_id("nb-4C-02a")
        assert result["pillar"] == "4-Objective"
        assert result["knowledge_layer"] == "Conceptual"

    def test_special_prefix_cf(self):
        result = parse_card_id("nb-CF-01")
        assert result["pillar"] == "CF"
        assert result["knowledge_layer"] == "Special"

    def test_invalid_id(self):
        result = parse_card_id("random-string")
        assert result["pillar"] is None
        assert result["knowledge_layer"] is None


class TestParseCardFile:
    def test_parse_sample(self, sample_card_path):
        card = parse_card_file(sample_card_path)
        assert card is not None
        assert card.card_id == "nb-3M-01"
        assert card.deck == "JobAcademy::Uncategorized::3-Algorithm"
        assert card.fire_weight == 0.4
        assert "mathematical" in card.tags
        assert "fill-in-blank" in card.tags
        assert card.pillar == "3-Algorithm"
        assert card.knowledge_layer == "Mathematical"
        assert card.cognitive_layer == "1 - Fill-in-blank"
        assert "argmax" in card.prompt

    def test_parse_returns_none_for_no_frontmatter(self, tmp_path):
        bad = tmp_path / "bad.md"
        bad.write_text("No frontmatter here\nJust text")
        assert parse_card_file(bad) is None

    def test_parse_returns_none_for_too_few_blocks(self, tmp_path):
        bad = tmp_path / "bad.md"
        bad.write_text("---\ncard_id: test\n---\n\nSTART\nOnly one block\nEND\n")
        assert parse_card_file(bad) is None


class TestRoundtrip:
    def test_roundtrip_preserves_content(self, sample_card_path):
        card = parse_card_file(sample_card_path)
        md = card_to_markdown(card)
        # Write and re-parse
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(md)
            f.flush()
            card2 = parse_card_file(Path(f.name))

        assert card2.card_id == card.card_id
        assert card2.deck == card.deck
        assert card2.fire_weight == card.fire_weight
        assert card2.prompt == card.prompt
        assert card2.solution == card.solution
