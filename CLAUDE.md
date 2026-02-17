# CLAUDE.md — JobAcademy

> Last updated: 2026-02-12

---

## Project Overview

- **Name**: JobAcademy-webapp
- **Description**: Educational web app with FastAPI backend and React/TypeScript frontend
- **Owner**: Hugo Bojorquez

---

## Project-Specific Overrides

> Anything here overrides `~/CLAUDE-GLOBAL.md` defaults for this project.

- **Additional stack**: @xyflow/react (flow diagrams), dagre, KaTeX, Tailwind CSS, CodeMirror 6 (code editor)
- **Docker**: no (deployed to Render)
- **Extra linters/tools**: ESLint + TypeScript-ESLint (frontend), ruff (backend)

---

## Project Structure

> What's mine vs what's off-limits.

### My Code (in scope)

```
JobAcademy-webapp/
  backend/
    app/            # FastAPI application
    tests/          # pytest test suite
    requirements.txt
    venv/           # Python 3.12.1 virtual environment
  frontend/
    src/            # React TypeScript app (Vite)
    public/
    package.json
  Makefile          # Build/dev shortcuts
  build.sh          # Render build script
  start.sh          # Render start script
  Procfile          # Render process file
  render.yaml       # Render deployment config
```

### Off-Limits (DO NOT MODIFY)

```
backend/venv/           # Virtual environment, never modify directly
frontend/node_modules/  # Auto-generated
~/laravel-review/       # Fran's Laravel fullstack
```

---

## Boundaries

- `.env` / `.env.production` — secrets, never commit or overwrite
- `render.yaml` — deployment config, confirm before modifying
- `Procfile` / `build.sh` / `start.sh` — deployment scripts, confirm before modifying

---

## Environment Details

| Property        | Value                                     |
|-----------------|-------------------------------------------|
| Python version  | 3.12.1                                    |
| Venv location   | ./backend/venv                            |
| Node version    | v24.13.0                                  |
| Backend port    | 8000 (uvicorn default)                    |
| Frontend port   | 5176 (Vite — avoids Docker conflict on 5173) |
| Database        | TBD (check backend/app/)                  |
| Docker compose  | N/A                                       |

---

## Common Tasks

### Start Development

```bash
# Backend
source backend/venv/bin/activate && uvicorn app.main:app --reload --app-dir backend

# Frontend
cd frontend && npm run dev
```

### Install a New Dependency

```bash
# Python
source backend/venv/bin/activate
python3.12 -m pip install <package>==<version>
pip check
# Then add to backend/requirements.txt manually

# Node
cd frontend && npm install <package>
```

### Run Tests

```bash
# Backend
source backend/venv/bin/activate && pytest backend/tests/ -v
```

### Lint / Format

```bash
# Python
ruff check backend/ && ruff format backend/

# TypeScript
cd frontend && npm run lint
```

---

## Architecture Decisions

### Code Execution (2026-02-12)

Programming drill cards support server-side Python execution via `POST /api/code/execute`.

**Security model** — 4 layers of defense in depth:
1. **AST validation** (primary) — allowlist imports, blocklist builtins + dunder access
2. **Subprocess isolation** — user code in separate process, passed via stdin
3. **setrlimit** (Linux/Render only) — CPU 5s, memory 128MB, limited fds, no child procs
4. **Wall-clock timeout** — 10s via subprocess.run

**Design decision: no runtime builtin removal.** Python's stdlib and compiled extensions (numpy, sklearn, tokenize) internally depend on builtins like `open`, `exec`, `compile`, `__import__`. Deleting them from `builtins` at runtime breaks `import numpy`. AST validation catches direct user calls; subprocess + setrlimit contain anything that slips through.

**Files:** `backend/app/services/code_executor.py`, `backend/app/routers/code.py`, `frontend/src/components/shared/CodeEditor.tsx`, `frontend/src/components/shared/CodeOutputPanel.tsx`, `frontend/src/api/code.ts`.

### Inline Card Edit Modal (2026-02-12)

Drill sessions support editing card content (front/back) without leaving the review flow, like Anki's edit button.

**Dual-system update:** Cards can come from Anki (via AnkiConnect, int `note_id`) or internal markdown (server-SRS, string `card_id`). The endpoint handles both:
- Anki path: calls `updateNoteFields` via AnkiConnect
- Internal path: updates `prompt`/`solution` fields on the Card model and saves to disk via `card_service`
- Both paths run when applicable (Anki + card_id provided)

**WYSIWYG editing:** Uses `contentEditable` divs instead of textareas so HTML content (`<br>`, `<b>`, etc.) renders visually — no raw HTML editing. On save, reads `innerHTML` from refs.

**Files:** `backend/app/services/anki_service.py` (`update_note`), `backend/app/routers/anki.py` (`PUT /api/anki/update-note`), `frontend/src/api/anki.ts` (`updateNote`), `frontend/src/components/shared/CardEditModal.tsx`, `frontend/src/pages/DrillSessionPage.tsx`.

### Subtree-Level Drilling with concept_node (2026-02-15)

Cards can now be drilled per graph node instead of all-or-nothing. Each card has a `concept_node` frontmatter field linking it to a specific graph node (e.g., `NB`, `BAYES`, `COND`).

**Dual-source card matching:** `get_node_cards(node_id)` matches by:
1. Explicit `concept_node` field (primary)
2. `NODE_CARD_MAP` prefix fallback for untagged cards only

This ensures tagged cards appear under their specific node while legacy untagged cards still work.

**Subtree card distribution:** `GET /api/graph/nodes/{id}/subtree-cards` aggregates cards across all nodes in the prerequisite subtree, grouped by concept.

**Subtopic grouping:** Cards within a concept can be grouped by a `subtopic` frontmatter field. Endpoints: `GET /api/graph/nodes/{id}/subtopics`, `GET /api/graph/nodes/{id}/subtopics/{subtopic}/cards`.

**Files:** `backend/app/models/card.py` (`concept_node`, `subtopic` fields), `backend/app/models/graph.py` (new models), `backend/app/parsers/card_parser.py` (parse + write), `backend/app/services/graph_service.py` (matching + distribution), `backend/app/routers/graph.py` (new endpoints), `frontend/src/types/graph.ts` (NavItem, Subtopic, SubtreeCardDistribution), `frontend/src/api/graph.ts` (new API functions), `frontend/src/pages/KnowledgeGraphPage.tsx` (3-level navigation).

### Recursive Subtree Navigation (2026-02-15)

Knowledge graph supports 3-level drill-down: Full Graph → Concept (prerequisite tree) → Subtopic (card list) → Card (detail).

**Navigation stack:** `NavItem[]` tracks the breadcrumb trail. Each item has an `id`, `type` (concept/subtopic/card), and display `name`. Breadcrumb renders as clickable links; clicking any level navigates back and trims the stack.

**Clickable node logic:** In prerequisite tree view, only nodes with incoming edges (prerequisites) that aren't the current root are navigable (get pointer cursor). All nodes are still selectable for the info panel. Leaf nodes (no prerequisites) show default cursor.

**Card distribution panel:** Right panel shows per-concept card counts from the subtree, each with a drill button.

**Files:** `frontend/src/pages/KnowledgeGraphPage.tsx` (Breadcrumb component, CardDistribution component, handleNodeClick, navigateToSubtree, navigateToSubtopic, navigateToBreadcrumb).

---

## Lessons Learned

### Docker port conflict (2026-02-12)

The Laravel Docker container (`webapp-laravel-laravel.test-1`) binds `0.0.0.0:5173`, hijacking the Vite default port. Symptoms: pages load blank (sidebar visible, content white) because the browser hits Docker's empty Vite instead of JobAcademy's. Fix: `vite.config.ts` → `server.port: 5176`. **Always check `lsof -i :<port>` or `docker ps` when pages are mysteriously blank.**

### TypeScript strict mode pre-existing errors (2026-02-12)

`tsconfig.app.json` has `noUnusedLocals: true` and `noUnusedParameters: true`. The build script `tsc -b && vite build` blocks on these. Pre-existing violations in `KnowledgeGraphPage.tsx` (untyped `useNodesState`), `CardEditorPage.tsx` (unused imports), and `LatexRenderer.tsx` (unused capture group) had to be fixed. **Always run `npm run build` (not just `npx tsc --noEmit`) to match the real build pipeline.**

### CORS origins (2026-02-12)

Backend CORS allowlist in `main.py` must include any dev port used by Vite. When changing Vite's port, update `allow_origins` too.

### CSP + CodeMirror lazy loading (2026-02-12)

Browser extensions can inject a Content Security Policy that blocks `eval`. CodeMirror (used by `CodeEditor.tsx`) triggers this, crashing the entire DrillSessionPage at import time — blank white page, no console errors (just a CSP warning). **Fix:** lazy-load CodeMirror components with `React.lazy()` + `<Suspense>`. The drill page loads normally; the code editor only loads when a programming card appears. **Rule: always lazy-load heavy third-party libraries (CodeMirror, Monaco, etc.) that might use eval/Function.**

### Backend tests require venv (2026-02-12)

The pyenv global Python lacks `httpx`, so `FastAPI.TestClient` fails. Always run tests with the backend venv: `./venv/bin/python -m pytest tests/ -v`. The uvicorn process uses the system Python at `/Library/Frameworks/Python.framework/Versions/3.12/` which has all deps installed.

### Stale Vite dev server (2026-02-15)

When a Vite dev server is already running on port 5176, starting a new one silently picks the next port (5177). The browser stays on 5176 serving stale code. **Always kill existing Vite processes before restarting:** `lsof -ti :5176 | xargs kill -9`. Also clear `node_modules/.vite` cache if code changes aren't reflected.

### Patching lazy imports in tests (2026-02-15)

`graph_service.py` imports `list_cards` lazily inside functions (`from app.services.card_service import list_cards`). Patching `app.services.graph_service.list_cards` fails because the attribute doesn't exist at module level. **Patch the source module:** `@patch("app.services.card_service.list_cards")`.

---

## Open TODOs (pick up next session)

1. **Add numpy + scikit-learn to `backend/requirements.txt`** — programming cards that `import numpy` or `from sklearn...` will fail on Render without these. Add pinned versions, push, and redeploy.
2. **Verify Render deploy succeeded** — check dashboard or `curl https://<render-url>/api/health`. The push to `main` should have triggered auto-deploy.
3. **Test code execution on Render** — confirm `setrlimit` activates on Linux, numpy/sklearn imports work after adding to requirements.
4. **Tag remaining NB cards with `subtopic`** — all 42 cards have `concept_node` but only test fixtures have `subtopic`. Tag real cards to enable subtopic-level drilling.
5. **Frontend test infrastructure** — no test framework exists yet. Consider adding vitest + @testing-library/react for component tests (KnowledgeGraphPage navigation, DrillSessionPage routing).

---

## Notes

- Monorepo structure: backend/ + frontend/ in one repo
- Frontend uses @xyflow/react for flow diagram visualization
- Deployed to Render (render.yaml defines services, Dockerfile builds both stages)
- No Docker locally — Render handles containerization
- ErrorBoundary in App.tsx wraps each route for debugging render crashes
- Git remote switched to SSH (`git@github.com:HugoDulce/JobAcademy-webapp.git`)
