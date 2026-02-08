"""Tests for fire_parser — encompasses, weights, standalone, no dupes."""

from app.parsers.fire_parser import parse_fire_hierarchy


class TestParseFireHierarchy:
    def test_finds_relationships(self, sample_fire_path):
        data = parse_fire_hierarchy(sample_fire_path)
        assert len(data.relationships) > 0

    def test_encompasses_direction(self, sample_fire_path):
        data = parse_fire_hierarchy(sample_fire_path)
        parents = {r.parent_card_id for r in data.relationships}
        assert "nb-3P-01" in parents

    def test_weights_are_valid(self, sample_fire_path):
        data = parse_fire_hierarchy(sample_fire_path)
        for r in data.relationships:
            assert 0.0 <= r.weight <= 1.0

    def test_standalone_cards(self, sample_fire_path):
        data = parse_fire_hierarchy(sample_fire_path)
        assert "nb-2P-01" in data.standalone_cards

    def test_no_duplicate_relationships(self, sample_fire_path):
        data = parse_fire_hierarchy(sample_fire_path)
        pairs = [(r.parent_card_id, r.child_card_id) for r in data.relationships]
        assert len(pairs) == len(set(pairs))

    def test_bidirectional_dedup(self, sample_fire_path):
        """The file declares nb-3P-01 encompasses nb-2C-01, AND nb-2C-01 encompassed by nb-3P-01.
        Parser should deduplicate these into a single relationship."""
        data = parse_fire_hierarchy(sample_fire_path)
        matching = [
            r for r in data.relationships
            if r.parent_card_id == "nb-3P-01" and r.child_card_id == "nb-2C-01"
        ]
        assert len(matching) == 1
