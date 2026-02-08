# JobAcademy LMS

A learning management system for structured flashcard-based study, built around the **FIRe** (Focused, Interleaved, Retrieval-based) methodology. Ships with 42 Naive Bayes ML cards organized across 6 pillars and 3 knowledge layers.

## Features

- **Card Browser** — filter/sort 42 cards by pillar, knowledge layer, and search
- **Card Editor** — create/edit cards with live LaTeX preview
- **Knowledge Graph** — interactive DAG of ML concepts (dagre + React Flow)
- **Drill Session** — spaced repetition review via AnkiConnect (optional)
- **FIRe Inspector** — heatmap, credit simulator, and encompassing tree
- **Sync Panel** — trigger Notion → Obsidian → Anki pipeline (optional)
- **Dashboard** — stats overview with graceful degradation when Anki is offline

## Quick Start

### Development (two terminals)

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` to the backend.

### Production (single service)

```bash
bash build.sh
cd backend && uvicorn app.main:app --port 8000
```

Open http://localhost:8000 — serves both API and frontend.

## Architecture

```
backend/
  app/
    config.py          # Env-var driven configuration
    main.py            # FastAPI app + static file serving
    models/            # Pydantic models (Card, Graph, FIRe)
    parsers/           # Pure functions: card, mermaid, fire parsers
    routers/           # API endpoints
    services/          # Business logic (card, anki, graph, fire, sync)
  data/
    cards/             # 42 bundled .md flashcards
    docs/              # Mermaid graph + FIRe hierarchy
  tests/               # pytest tests for parsers + validation
frontend/
  src/
    api/               # API client functions
    pages/             # 7 page components
    components/        # Layout + shared components
    types/             # TypeScript type definitions
    constants.ts       # Shared PILLARS/LAYERS constants
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CARDS_DIR` | `backend/data/cards` | Path to card .md files |
| `DOCS_DIR` | `backend/data/docs` | Path to mermaid/fire docs |
| `ANKI_URL` | `http://localhost:8765` | AnkiConnect endpoint |
| `PORT` | `8000` | Server port |
| `FRONTEND_URL` | `http://localhost:5173` | CORS origin for dev |

## Optional Integrations

### Anki (AnkiConnect)

Install the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on, then the Drill Session and Dashboard will show live review data. Without Anki, the app degrades gracefully — dashboard shows card stats only, drill page shows a friendly message.

### Notion

The Sync Panel can trigger scripts that pull cards from a Notion database. Set `SCRIPTS_DIR` to point at your sync scripts. Without them, the sync panel is informational only.

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

35 tests covering card parsing, mermaid graph parsing, FIRe hierarchy parsing, and card validation rules.

## Deployment

### Render

Connect the GitHub repo. The included `render.yaml` blueprint auto-configures:
- Build: installs Node + Python deps, builds frontend, copies to `backend/static/`
- Start: runs uvicorn serving both API and SPA

### Other platforms

Any platform that runs Python can use:
```bash
bash build.sh
cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## POC Limitations

- No authentication — single-user tool
- No database — file-based storage (sufficient for 42 cards)
- No CI/CD pipeline
- No Docker
- No API versioning
- Content is self-authored, so no HTML sanitization on LaTeX renderer
