"""Sync API endpoints."""

from fastapi import APIRouter

from app.services import sync_service

router = APIRouter(prefix="/api/sync", tags=["sync"])


@router.post("/notion-to-obsidian")
async def sync_notion_to_obsidian():
    """Trigger Notion -> Obsidian sync."""
    return await sync_service.run_notion_to_obsidian()


@router.post("/obsidian-to-anki")
async def sync_obsidian_to_anki():
    """Trigger Obsidian -> Anki push."""
    return await sync_service.run_obsidian_to_anki()


@router.post("/full")
async def sync_full():
    """Run full pipeline: Notion -> Obsidian -> Anki."""
    return await sync_service.run_full_pipeline()


@router.get("/log")
def get_sync_log(lines: int = 50):
    """Read the last N lines of the sync log."""
    return {"log": sync_service.read_sync_log(lines)}
