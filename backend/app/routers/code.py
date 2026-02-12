"""Code execution endpoint for programming drill cards."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.code_executor import execute_code

router = APIRouter(prefix="/api/code", tags=["code"])


class CodeRequest(BaseModel):
    code: str = Field(..., max_length=10_000)


class CodeResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    error: str | None


@router.post("/execute", response_model=CodeResponse)
def execute(req: CodeRequest):
    """Execute user Python code in a sandboxed subprocess."""
    result = execute_code(req.code)
    return CodeResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        timed_out=result.timed_out,
        error=result.error,
    )
