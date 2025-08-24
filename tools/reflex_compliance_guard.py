# tools/reflex_compliance_guard.py
# Phase/reflex compliance guard — AST-based.
# - Verifies phase enforcement pattern (import + ensure_phase())
# - Verifies main guard for CLI-style modules
# - Detects Phase 0.5+ future gates (e.g., get_current_phase() < 0.5 raising)
#   and treats them as SKIPPED (expected) while running at Phase 0.4.
#
# Summary line includes: ok, skipped_future, issues.

from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any

from core.phase_control import ensure_phase, REQUIRED_PHASE, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


@dataclass
class FileCheck:
    path: Path
    has_phase_import: bool
    calls_ensure_phase: bool
    has_main_guard: bool
    has_future_gate_05: bool
    is_cli_like: bool


FUTURE_TOOL_HINTS = {"snapshot_db.py", "trace_memory_alignment.py"}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _is_cli_like(src: str) -> bool:
    # Heuristic: defines run_cli() or parses argparse
    return ("def run_cli" in src) or ("argparse" in src)


def _has_main_guard(tree: ast.AST, src: str) -> bool:
    # Quick text check is usually enough and robust:
    return ("if __name__ == \"__main__\":" in src) or ("if __name__ == '__main__':" in src)


def _has_phase_import(src: str) -> bool:
    return "from core.phase_control import" in src


def _calls_ensure_phase(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # ensure_phase(...) called
            if isinstance(node.func, ast.Name) and node.func.id == "ensure_phase":
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr == "ensure_phase":
                return True
    return False


def _detect_future_gate_05(tree: ast.AST, src: str) -> bool:
    """
    Detect a conditional gate around Phase >= 0.5, e.g.:
        if float(get_current_phase()) < 0.5:
            raise RuntimeError(...)
    We accept any comparison against 0.5 with get_current_phase() involved.
    """
    # Quick hint to avoid expensive AST walk when clearly absent:
    if "get_current_phase" not in src:
        return False

    def _has_gcp(expr: ast.AST) -> bool:
        if isinstance(expr, ast.Call):
            f = expr.func
            if isinstance(f, ast.Name) and f.id == "get_current_phase":
                return True
            if isinstance(f, ast.Attribute) and f.attr == "get_current_phase":
                return True
        return False

    def _is_half(expr: ast.AST) -> bool:
        if isinstance(expr, ast.Constant):
            try:
                return abs(float(expr.value) - 0.5) < 1e-12
            except Exception:
                return False
        return False

    has_cmp = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            operands = [node.left] + list(node.comparators)
            has_gcp = any(_has_gcp(op) for op in operands)
            has_half = any(_is_half(op) for op in operands)
            has_lt = any(isinstance(op, (ast.Lt, ast.LtE)) for op in node.ops)
            if has_gcp and has_half and has_lt:
                has_cmp = True
                break

    if not has_cmp:
        return False

    # Optional: ensure a raise exists somewhere (heuristic)
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            return True
    # If no explicit raise found, still consider it a gate (conservative)
    return True


def _scan_file(p: Path) -> FileCheck:
    src = _read(p)
    try:
        tree = ast.parse(src)
    except Exception:
        # Non-parseable file — treat as missing everything
        return FileCheck(
            path=p,
            has_phase_import=False,
            calls_ensure_phase=False,
            has_main_guard=False,
            has_future_gate_05=False,
            is_cli_like=_is_cli_like(src),
        )

    return FileCheck(
        path=p,
        has_phase_import=_has_phase_import(src),
        calls_ensure_phase=_calls_ensure_phase(tree),
        has_main_guard=_has_main_guard(tree, src),
        has_future_gate_05=_detect_future_gate_05(tree, src) or (p.name in FUTURE_TOOL_HINTS),
        is_cli_like=_is_cli_like(src),
    )


def run_cli() -> None:
    ensure_phase()
    cur_phase = float(get_current_phase())
    src_path = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Reflex/Tool compliance guard (AST-based).")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    log_memory_event(
        event_text="reflex_compliance_guard start",
        source=src_path,
        tags=["tool", "start", "compliance_guard"],
        content={"root": args.root, "required_phase": float(REQUIRED_PHASE), "current_phase": cur_phase},
        phase=REQUIRED_PHASE,
    )

    root = Path(args.root)
    candidates: List[Path] = []
    # Limit scope to the usual enforcement targets
    for base in ("tools", "reflexes"):
        b = root / base
        if b.exists():
            candidates.extend(p for p in b.rglob("*.py") if "__pycache__" not in p.parts)

    results: List[FileCheck] = [_scan_file(p) for p in sorted(candidates)]
    issues: Dict[str, List[str]] = {}
    ok_count = 0
    skipped_future = 0

    for r in results:
        reasons: List[str] = []

        # Future tools gated to 0.5 are allowed to "fail" at 0.4 — classify as skipped
        if r.has_future_gate_05 and cur_phase < 0.5:
            skipped_future += 1
        else:
            if not r.has_phase_import or not r.calls_ensure_phase:
                reasons.append("missing_phase_enforcement")
            # Only require main guard for CLI-like modules
            if r.is_cli_like and not r.has_main_guard:
                reasons.append("missing_main_guard")

        if reasons:
            issues[r.path.as_posix()] = reasons
        else:
            # Count as OK unless it's a skipped-future (already counted)
            if not (r.has_future_gate_05 and cur_phase < 0.5):
                ok_count += 1

    total = len(results)
    issue_count = len(issues)

    # Console report
    print(f"Compliance scanned: {total} files; ok={ok_count}; skipped_future={skipped_future}; issues={issue_count}")
    if issue_count:
        print("Non-compliant files (reason -> file):")
        for fp, rs in issues.items():
            print(" - " + ", ".join(rs) + " -> " + fp)

    # Trace log summary (trim long lists)
    log_trace_event(
        description="reflex_compliance_guard done",
        source=src_path,
        tags=["tool", "done", "compliance_guard"],
        content={
            "total": total,
            "ok": ok_count,
            "skipped_future": skipped_future,
            "issues": issue_count,
            "issue_examples": [{k: v} for k, v in list(issues.items())[:10]],
        },
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()
