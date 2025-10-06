# tools/artifact_emitter.py
from __future__ import annotations

# Path injection (your repo setup)
from boot.boot_path_initializer import inject_paths  # type: ignore
inject_paths()

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple

from core.trace_logger import log_trace_event  # type: ignore


FILE_BLOCK_RE = re.compile(
    r"```file:\s*(?P<path>[^\r\n]+)\s*\r?\n(?P<body>.*?)(?:\r?\n)```",
    re.DOTALL | re.MULTILINE,
)

SOURCE = "tools.artifact_emitter"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _substitute(body: str) -> str:
    # Minimal token support; expand as needed later
    return body.replace("{{NOW}}", _now_iso())


def _parse_file_blocks(text: str) -> Iterable[Tuple[str, str]]:
    """
    Yields (relative_path, content) for each ```file: <path> ... ``` block.
    """
    for m in FILE_BLOCK_RE.finditer(text):
        rel_path = m.group("path").strip()
        body = m.group("body")
        yield rel_path, _substitute(body)


def _write_text_file(root: Path, rel_path: str, content: str) -> Path:
    out_path = (root / rel_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8", newline="\n")
    return out_path


def run(seed_path: Path, out_root: Path, dry_run: bool) -> int:
    # Start log
    log_trace_event(
        "artifact_emitter.start",
        {"seed": str(seed_path), "out_root": str(out_root), "dry_run": dry_run},
        source=SOURCE,
    )

    if not seed_path.exists():
        log_trace_event(
            "artifact_emitter.error",
            {"error": "seed-not-found", "seed": str(seed_path)},
            source=SOURCE,
        )
        return 2

    text = seed_path.read_text(encoding="utf-8")
    blocks = list(_parse_file_blocks(text))

    if not blocks:
        log_trace_event(
            "artifact_emitter.nothing",
            {"message": "no artifacts found in seed"},
            source=SOURCE,
        )
        return 0

    emitted = []
    for rel_path, content in blocks:
        if dry_run:
            emitted.append({"path": rel_path, "bytes": len(content), "dry_run": True})
        else:
            out_path = _write_text_file(out_root, rel_path, content)
            emitted.append({"path": str(out_path.relative_to(out_root)), "bytes": len(content)})

    log_trace_event(
        "artifact_emitter.done",
        {"count": len(emitted), "items": emitted},
        source=SOURCE,
    )
    return 0


def run_cli() -> None:
    p = argparse.ArgumentParser(
        description="Emit artifacts from a Markdown seed (IronRoot-compliant)."
    )
    p.add_argument("--seed", default="seeds/05-artifact_emitter_seed.md", help="Path to the Markdown seed file.")
    p.add_argument(
        "--out-root",
        default=".",
        help="Root folder to write outputs under (artifacts/*). Defaults to repo root.",
    )
    p.add_argument("--dry-run", action="store_true", help="List what would be written without writing files.")
    args = p.parse_args()

    seed = Path(args.seed).resolve()
    out_root = Path(args.out_root).resolve()

    rc = run(seed, out_root, args.dry_run)
    raise SystemExit(rc)


if __name__ == "__main__":
    run_cli()
