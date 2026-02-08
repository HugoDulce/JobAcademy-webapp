"""JobAcademy LMS — FastAPI backend."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_URL
from app.routers import anki, cards, dashboard, fire, graph, sync

app = FastAPI(title="JobAcademy LMS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router)
app.include_router(dashboard.router)
app.include_router(sync.router)
app.include_router(anki.router)
app.include_router(graph.router)
app.include_router(fire.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# --- Static frontend serving (production) ---
_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


if (_STATIC_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=_STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(request: Request, full_path: str):
        """Serve index.html for all non-API routes (SPA catch-all)."""
        file = _STATIC_DIR / full_path
        if file.is_file():
            return FileResponse(file)
        return FileResponse(_STATIC_DIR / "index.html")
