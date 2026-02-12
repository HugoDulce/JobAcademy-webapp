"""Environment-driven configuration with bundled-data defaults."""

import os
from pathlib import Path

_BASE_DIR = Path(__file__).resolve().parent.parent  # backend/

# Paths — default to bundled sample data
CARDS_DIR = Path(os.getenv("CARDS_DIR", str(_BASE_DIR / "data" / "cards")))
DOCS_DIR = Path(os.getenv("DOCS_DIR", str(_BASE_DIR / "data" / "docs")))
SCRIPTS_DIR = Path(os.getenv("SCRIPTS_DIR", str(_BASE_DIR / "scripts")))
SYNC_LOG = Path(os.getenv("SYNC_LOG", str(SCRIPTS_DIR / "sync.log")))

# Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

# Obsidian
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")

# Anki
ANKI_URL = os.getenv("ANKI_URL", "http://localhost:8765")
SRS_STATE_FILE = Path(os.getenv("SRS_STATE_FILE", str(_BASE_DIR / "data" / "srs_state.json")))

# Server
PORT = int(os.getenv("PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
