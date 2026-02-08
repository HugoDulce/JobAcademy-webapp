"""Tests for validation_service — valid card, empty fields, focused/precise/consistent rules."""

from app.services.validation_service import validate_card


def _make_card(**overrides) -> dict:
    """Build a valid card dict with sensible defaults, then apply overrides."""
    base = {
        "card_id": "nb-3C-01",
        "prompt": "What are the three steps of Naive Bayes?",
        "solution": "Estimate priors, compute likelihoods, pick argmax.",
        "knowledge_layer": "Conceptual",
        "fire_weight": 0.5,
        "deck": "JobAcademy::Uncategorized::3-Algorithm",
        "tags": ["conceptual"],
    }
    base.update(overrides)
    return base


class TestValidCard:
    def test_valid_card_passes(self):
        result = validate_card(_make_card())
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_checks_dict_populated(self):
        result = validate_card(_make_card())
        assert result.checks["has_prompt"] is True
        assert result.checks["has_solution"] is True
        assert result.checks["has_deck"] is True


class TestRequiredFields:
    def test_empty_prompt(self):
        result = validate_card(_make_card(prompt=""))
        assert result.is_valid is False
        assert any("Prompt is empty" in e for e in result.errors)

    def test_empty_solution(self):
        result = validate_card(_make_card(solution=""))
        assert result.is_valid is False
        assert any("Solution is empty" in e for e in result.errors)

    def test_bad_deck_format(self):
        result = validate_card(_make_card(deck="NoDeck"))
        assert result.is_valid is False
        assert any("hierarchy" in e for e in result.errors)

    def test_no_tags_is_warning(self):
        result = validate_card(_make_card(tags=[]))
        assert result.is_valid is True  # warning, not error
        assert any("tags" in w.lower() for w in result.warnings)


class TestFocusedRule:
    def test_multiple_numbered_items_fails(self):
        solution = "1. First thing\n2. Second thing\n3. Third thing"
        result = validate_card(_make_card(solution=solution))
        assert result.is_valid is False
        assert any("numbered items" in e for e in result.errors)

    def test_single_numbered_item_passes(self):
        solution = "1. Only one item"
        result = validate_card(_make_card(solution=solution))
        assert result.checks["focused"] is True


class TestPreciseRule:
    def test_vague_prompt_warns(self):
        result = validate_card(_make_card(prompt="What is the most important thing?"))
        assert any("vague" in w.lower() for w in result.warnings)


class TestConsistentRule:
    def test_it_depends_fails(self):
        result = validate_card(_make_card(solution="It depends on the dataset"))
        assert result.is_valid is False
        assert any("it depends" in e.lower() for e in result.errors)


class TestFireWeight:
    def test_out_of_range(self):
        result = validate_card(_make_card(fire_weight=1.5))
        assert result.is_valid is False
        assert any("FIRe weight" in e for e in result.errors)

    def test_valid_range(self):
        result = validate_card(_make_card(fire_weight=0.0))
        assert result.is_valid is True
