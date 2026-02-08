"""Shared test fixtures."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_card_path():
    return FIXTURES_DIR / "nb-3M-01.md"


@pytest.fixture
def sample_mermaid_path():
    return FIXTURES_DIR / "sample.mermaid"


@pytest.fixture
def sample_fire_path():
    return FIXTURES_DIR / "sample-fire.md"


@pytest.fixture
def sample_card_text(sample_card_path):
    return sample_card_path.read_text(encoding="utf-8")
