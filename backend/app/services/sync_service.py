"""Sync service — shells out to existing scripts."""

import asyncio
import time
from pathlib import Path

from app.config import SCRIPTS_DIR, SYNC_LOG


async def run_notion_to_obsidian() -> dict:
    """Run the Notion -> Obsidian sync script."""
    script = SCRIPTS_DIR / "notion_to_obsidian.py"
    return await _run_script(script, "notion_to_obsidian")


async def run_obsidian_to_anki() -> dict:
    """Run the Obsidian -> Anki push script."""
    script = SCRIPTS_DIR / "obsidian_to_anki.py"
    return await _run_script(script, "obsidian_to_anki")


async def run_full_pipeline() -> dict:
    """Run both sync scripts in sequence."""
    r1 = await run_notion_to_obsidian()
    if not r1["success"]:
        return {
            "success": False,
            "stage": "notion_to_obsidian",
            "stdout": r1["stdout"],
            "stderr": r1["stderr"],
            "duration_ms": r1["duration_ms"],
        }

    r2 = await run_obsidian_to_anki()
    return {
        "success": r2["success"],
        "stage": "full",
        "stdout": r1["stdout"] + "\n---\n" + r2["stdout"],
        "stderr": r1["stderr"] + r2["stderr"],
        "duration_ms": r1["duration_ms"] + r2["duration_ms"],
    }


async def _run_script(script: Path, name: str) -> dict:
    """Run a Python script and capture output."""
    start = time.time()
    proc = await asyncio.create_subprocess_exec(
        "python3",
        str(script),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(SCRIPTS_DIR),
    )
    stdout, stderr = await proc.communicate()
    elapsed = int((time.time() - start) * 1000)

    return {
        "success": proc.returncode == 0,
        "stdout": stdout.decode("utf-8", errors="replace"),
        "stderr": stderr.decode("utf-8", errors="replace"),
        "duration_ms": elapsed,
    }


def read_sync_log(lines: int = 50) -> str:
    """Read the last N lines of the sync log."""
    if not SYNC_LOG.exists():
        return ""
    content = SYNC_LOG.read_text(encoding="utf-8")
    all_lines = content.strip().split("\n")
    return "\n".join(all_lines[-lines:])
