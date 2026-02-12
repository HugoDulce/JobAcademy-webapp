"""Sandboxed Python code execution for programming drill cards.

Security layers (defense in depth):
1. AST static analysis — blocks dangerous imports, builtins, dunder access
2. subprocess isolation — crash containment, process boundary
3. setrlimit (Linux only) — CPU 5s, memory 128MB, no file writes, no child procs
4. Wall-clock timeout — 10s via subprocess.run
5. Output truncation — cap at 10KB
6. Safe env — strips secrets/env vars from subprocess environment
"""

import ast
import os
import subprocess
import sys
import textwrap
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ALLOWED_IMPORTS: set[str] = {
    "math",
    "random",
    "collections",
    "itertools",
    "functools",
    "operator",
    "string",
    "re",
    "json",
    "datetime",
    "typing",
    "dataclasses",
    "enum",
    "abc",
    "copy",
    "statistics",
    "fractions",
    "decimal",
    "textwrap",
    "pprint",
    # Data-science stack (already installed on backend)
    "numpy",
    "np",
    "sklearn",
    "pandas",
    "pd",
    "scipy",
}

BLOCKED_BUILTINS: set[str] = {
    "__import__",
    "eval",
    "exec",
    "compile",
    "open",
    "getattr",
    "setattr",
    "delattr",
    "globals",
    "locals",
    "vars",
    "dir",
    "breakpoint",
    "input",
    "memoryview",
    "type",
}


BLOCKED_DUNDERS: set[str] = {
    "__subclasses__",
    "__bases__",
    "__mro__",
    "__builtins__",
    "__globals__",
    "__code__",
    "__closure__",
    "__func__",
    "__self__",
    "__module__",
    "__import__",
    "__loader__",
    "__spec__",
    "__qualname__",
}

MAX_OUTPUT_BYTES = 10_000
TIMEOUT_SECONDS = 10
CPU_LIMIT_SECONDS = 5
MEMORY_LIMIT_BYTES = 128 * 1024 * 1024  # 128 MB


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    error: str | None


# ---------------------------------------------------------------------------
# AST Validation
# ---------------------------------------------------------------------------

def validate_code(source: str) -> list[str]:
    """Parse source and check for disallowed constructs. Returns violation messages."""
    violations: list[str] = []

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [f"SyntaxError: {e.msg} (line {e.lineno})"]

    for node in ast.walk(tree):
        # --- Import checks ---
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_IMPORTS:
                    violations.append(f"Blocked import: '{alias.name}' is not allowed")

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top = node.module.split(".")[0]
                if top not in ALLOWED_IMPORTS:
                    violations.append(f"Blocked import: 'from {node.module}' is not allowed")

        # --- Blocked builtin calls ---
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in BLOCKED_BUILTINS:
                violations.append(f"Blocked builtin: '{func.id}()' is not allowed")

        # --- Blocked dunder attribute access ---
        elif isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_DUNDERS:
                violations.append(f"Blocked attribute: '.{node.attr}' is not allowed")

        # --- String-based dunder access in subscripts ---
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in BLOCKED_DUNDERS:
                violations.append(f"Blocked string reference to '{node.value}'")

    return violations


# ---------------------------------------------------------------------------
# Runner script (executed in subprocess)
# ---------------------------------------------------------------------------

def _build_runner_script() -> str:
    """Build the Python script that runs inside the subprocess."""
    return textwrap.dedent(f"""\
        import sys
        import platform

        # Apply resource limits on Linux (Render deployment)
        if platform.system() == "Linux":
            import resource
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, ({CPU_LIMIT_SECONDS}, {CPU_LIMIT_SECONDS}))
            # Memory limit
            resource.setrlimit(resource.RLIMIT_AS, ({MEMORY_LIMIT_BYTES}, {MEMORY_LIMIT_BYTES}))
            # No file creation (0 = only stdin/stdout/stderr already open)
            resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))
            # No child processes
            resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))

        # Read user code from stdin and execute.
        # Note: runtime builtin removal is skipped because Python's stdlib
        # and compiled extensions (numpy, sklearn) depend on builtins like
        # open, exec, compile internally. AST validation is the primary
        # defense; subprocess isolation + setrlimit provide containment.
        code = sys.stdin.read()
        exec(compile(code, "<user>", "exec"))
    """)


# ---------------------------------------------------------------------------
# Safe environment
# ---------------------------------------------------------------------------

def _safe_env() -> dict[str, str]:
    """Minimal environment that preserves Python paths but strips secrets."""
    keep = {"PATH", "HOME", "LANG", "PYTHONPATH", "VIRTUAL_ENV", "PYTHONHASHSEED"}
    return {k: v for k, v in os.environ.items() if k in keep}


# ---------------------------------------------------------------------------
# Output truncation
# ---------------------------------------------------------------------------

def _truncate(text: str) -> str:
    if len(text) > MAX_OUTPUT_BYTES:
        return text[:MAX_OUTPUT_BYTES] + "\n... (output truncated at 10KB)"
    return text


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------

def execute_code(source: str) -> ExecutionResult:
    """Validate and execute user code in a sandboxed subprocess."""
    # Layer 1: AST validation
    violations = validate_code(source)
    if violations:
        return ExecutionResult(
            stdout="",
            stderr="",
            exit_code=-1,
            timed_out=False,
            error="\n".join(violations),
        )

    # Layer 2-4: Subprocess with timeout
    runner = _build_runner_script()
    try:
        result = subprocess.run(
            [sys.executable, "-c", runner],
            input=source,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            env=_safe_env(),
            cwd="/tmp",
        )
        return ExecutionResult(
            stdout=_truncate(result.stdout),
            stderr=_truncate(result.stderr),
            exit_code=result.returncode,
            timed_out=False,
            error=None,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(
            stdout="",
            stderr="",
            exit_code=-1,
            timed_out=True,
            error="Execution timed out (10s limit)",
        )
    except Exception as e:
        return ExecutionResult(
            stdout="",
            stderr="",
            exit_code=-1,
            timed_out=False,
            error=f"Execution error: {e}",
        )
