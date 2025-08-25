# -*- coding: utf-8 -*-
# tools/git_hooks_precommit.py
# IronRoot Git pre-commit runner (enhanced):
# - Phase lock (ensure_phase)
# - Auto-fix manifest/history/dev_file_list via manifest_history_auditor
# - NEW: auto-register any new/changed .py under tools/ and reflexes/
# - Stages updated registry files so they’re included in the commit
# - Dual logs to memory + trace
# - Dispatcher-only (no business logic)

from boot.boot_path_initializer import inject_paths
inject_paths()

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Set

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _run(cmd: List[str]) -> tuple[int, str]:
    """Run a subprocess and return (exit_code, combined_output)."""
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout or "") + (("\n" + p.stderr) if p.stderr else "")
    return p.returncode, out.strip()


def _to_posix(paths: Iterable[str]) -> List[str]:
    return [Path(p).as_posix() for p in paths]


def _git_list_untracked(dir_glob: str) -> List[str]:
    # Untracked files under a given dir (respect .gitignore)
    code, out = _run(["git", "ls-files", "-o", "--exclude-standard", "--", dir_glob])
    if code != 0:
        return []
    return [l for l in out.splitlines() if l]


def _git_list_staged(dir_glob: str) -> List[str]:
    # Staged (cached) changes under a given dir
    code, out = _run(["git", "diff", "--name-only", "--cached", "--", dir_glob])
    if code != 0:
        return []
    return [l for l in out.splitlines() if l]


def _git_list_unstaged(dir_glob: str) -> List[str]:
    # Unstaged working tree changes under a given dir
    code, out = _run(["git", "diff", "--name-only", "--", dir_glob])
    if code != 0:
        return []
    return [l for l in out.splitlines() if l]


def _collect_changed_python() -> List[str]:
    """
    Collect any .py that are new/changed under tools/ and reflexes/.
    We include untracked, staged, and unstaged to keep the registry in sync,
    even if the developer forgot to stage the new file in this commit.
    """
    candidates: Set[str] = set()
    scopes = ["tools", "reflexes"]

    for scope in scopes:
        for getter in (_git_list_untracked, _git_list_staged, _git_list_unstaged):
            for rel in getter(scope):
                if rel.endswith(".py") and (rel.startswith("tools/") or rel.startswith("reflexes/")):
                    candidates.add(rel)

    return sorted(_to_posix(candidates))


def _stage_if_changed(paths: Iterable[str]) -> List[str]:
    """Stage listed files if they have diffs."""
    staged: List[str] = []
    for rel in _to_posix(paths):
        p = Path(rel)
        if not p.exists():
            continue
        code, diff = _run(["git", "diff", "--name-only", "--", rel])
        if code == 0 and rel in diff.splitlines():
            _run(["git", "add", rel])
            staged.append(p.as_posix())
    return staged


def _register_files(files: List[str]) -> tuple[int, str]:
    """
    Force-register specific files into manifest/history/dev_file_list by
    invoking the registrar with a JSON array argument. Using subprocess
    avoids PowerShell quoting issues we saw on the command line.
    """
    if not files:
        return 0, "no files to register"
    json_arg = json.dumps(files, ensure_ascii=False)
    return _run([sys.executable, "-m", "tools.ironroot_registrar", "--files-json", json_arg, "--apply"])


def run_cli() -> None:
    # Phase lock
    ensure_phase()

    src = Path(__file__).as_posix()
    log_memory_event(
        "git pre-commit start",
        source=src,
        tags=["tool", "git", "hook", "pre-commit"],
        content={"required_phase": float(REQUIRED_PHASE)},
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        "git pre-commit start",
        source=src,
        tags=["tool", "git", "hook", "pre-commit"],
        content={"required_phase": float(REQUIRED_PHASE)},
        phase=REQUIRED_PHASE,
    )

    # 1) Always run the auditor to auto-fix core registries
    auditor_code, auditor_out = _run([sys.executable, "-m", "tools.manifest_history_auditor", "--auto-fix"])
    if auditor_code != 0:
        raise RuntimeError(f"IRONROOT VIOLATION — manifest_history_auditor failed (exit {auditor_code}). Output:\n{auditor_out}")

    # 2) NEW: auto-register any changed Python files under tools/ and reflexes/
    changed_py = _collect_changed_python()
    reg_code, reg_out = _register_files(changed_py)
    if reg_code != 0:
        raise RuntimeError(f"IRONROOT VIOLATION — ironroot_registrar failed (exit {reg_code}). Output:\n{reg_out}")

    # 3) Stage registry files if they changed
    to_stage = [
        "configs/dev_file_list.md",
        "configs/ironroot_manifest_data.json",
        "configs/ironroot_file_history_with_dependencies.json",
    ]
    staged = _stage_if_changed(to_stage)

    # Done logs
    done_payload = {
        "auditor_summary": auditor_out[:1500],
        "registered_files": changed_py,
        "registrar_summary": reg_out[:1500],
        "staged": staged,
    }
    log_memory_event("git pre-commit done", source=src, tags=["tool", "git", "hook", "pre-commit"], content=done_payload, phase=REQUIRED_PHASE)
    log_trace_event("git pre-commit done", source=src, tags=["tool", "git", "hook", "pre-commit"], content=done_payload, phase=REQUIRED_PHASE)

    print(f"[pre-commit] auditor ok; registered={len(changed_py)}; staged={len(staged)}")


if __name__ == "__main__":
    run_cli()
