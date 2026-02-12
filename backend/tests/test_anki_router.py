"""Tests for PUT /api/anki/update-note — inline card editing endpoint."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_update_payload(**overrides) -> dict:
    base = {
        "note_id": 12345,
        "front": "Updated front",
        "back": "Updated back",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class TestUpdateNoteValidation:
    def test_missing_front_returns_422(self):
        resp = client.put("/api/anki/update-note", json={"note_id": 1, "back": "b"})
        assert resp.status_code == 422

    def test_missing_back_returns_422(self):
        resp = client.put("/api/anki/update-note", json={"note_id": 1, "front": "f"})
        assert resp.status_code == 422

    def test_missing_note_id_returns_422(self):
        resp = client.put("/api/anki/update-note", json={"front": "f", "back": "b"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Anki update path
# ---------------------------------------------------------------------------

class TestUpdateNoteAnki:
    @patch("app.routers.anki._is_anki_available", return_value=True)
    @patch("app.services.anki_service.update_note", return_value=True)
    def test_calls_anki_when_connected(self, mock_update, mock_avail):
        payload = _make_update_payload(note_id=99999)
        resp = client.put("/api/anki/update-note", json=payload)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        mock_update.assert_called_once_with(99999, "Updated front", "Updated back")

    @patch("app.routers.anki._is_anki_available", return_value=False)
    @patch("app.services.anki_service.update_note")
    def test_skips_anki_when_disconnected(self, mock_update, mock_avail):
        resp = client.put("/api/anki/update-note", json=_make_update_payload())
        assert resp.status_code == 200
        mock_update.assert_not_called()

    @patch("app.routers.anki._is_anki_available", return_value=True)
    @patch("app.services.anki_service.update_note", side_effect=RuntimeError("Anki error"))
    def test_anki_failure_returns_502(self, mock_update, mock_avail):
        resp = client.put("/api/anki/update-note", json=_make_update_payload())
        assert resp.status_code == 502
        assert "Anki update failed" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Internal card update path
# ---------------------------------------------------------------------------

class TestUpdateNoteInternal:
    @patch("app.routers.anki._is_anki_available", return_value=False)
    @patch("app.services.card_service.save_card")
    @patch("app.services.card_service.get_card")
    def test_updates_internal_card_when_card_id_provided(self, mock_get, mock_save, mock_avail):
        mock_card = MagicMock()
        mock_card.prompt = "old front"
        mock_card.solution = "old back"
        mock_get.return_value = mock_card

        payload = _make_update_payload(card_id="nb-1C-01")
        resp = client.put("/api/anki/update-note", json=payload)

        assert resp.status_code == 200
        assert mock_card.prompt == "Updated front"
        assert mock_card.solution == "Updated back"
        mock_save.assert_called_once_with(mock_card)

    @patch("app.routers.anki._is_anki_available", return_value=False)
    @patch("app.services.card_service.save_card")
    @patch("app.services.card_service.get_card", return_value=None)
    def test_missing_internal_card_still_succeeds(self, mock_get, mock_save, mock_avail):
        payload = _make_update_payload(card_id="nonexistent-99")
        resp = client.put("/api/anki/update-note", json=payload)
        assert resp.status_code == 200
        mock_save.assert_not_called()

    @patch("app.routers.anki._is_anki_available", return_value=False)
    @patch("app.services.card_service.get_card")
    def test_no_card_id_skips_internal_update(self, mock_get, mock_avail):
        resp = client.put("/api/anki/update-note", json=_make_update_payload())
        assert resp.status_code == 200
        mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# Both paths together
# ---------------------------------------------------------------------------

class TestUpdateNoteDual:
    @patch("app.routers.anki._is_anki_available", return_value=True)
    @patch("app.services.anki_service.update_note", return_value=True)
    @patch("app.services.card_service.save_card")
    @patch("app.services.card_service.get_card")
    def test_updates_both_anki_and_internal(self, mock_get, mock_save, mock_anki_update, mock_avail):
        mock_card = MagicMock()
        mock_get.return_value = mock_card

        payload = _make_update_payload(note_id=12345, card_id="nb-1C-01")
        resp = client.put("/api/anki/update-note", json=payload)

        assert resp.status_code == 200
        mock_anki_update.assert_called_once()
        mock_save.assert_called_once()
