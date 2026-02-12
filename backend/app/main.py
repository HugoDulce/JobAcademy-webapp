"""JobAcademy LMS — FastAPI backend."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import CARDS_DIR, FRONTEND_URL
from app.routers import anki, cards, code, dashboard, fire, graph, sync

app = FastAPI(title="JobAcademy LMS", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cards.router)
app.include_router(code.router)
app.include_router(dashboard.router)
app.include_router(sync.router)
app.include_router(anki.router)
app.include_router(graph.router)
app.include_router(fire.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/cards/images/{topic}/{filename:path}")
async def serve_card_image(topic: str, filename: str):
    """Serve card images from topic/images/ subdirectories."""
    image_path = CARDS_DIR / topic / "images" / filename
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)


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
