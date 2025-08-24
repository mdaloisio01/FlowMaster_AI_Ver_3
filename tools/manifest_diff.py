from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
from pathlib import Path

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


def _read_text_no_bom(p: Path) -> str:
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8", errors="ignore")
    # Strip UTF-8 BOM if present
    if text and text[0] == "\ufeff":
        text = text[1:]
    return text


def _unescape_md(s: str) -> str:
    # Normalize markdown-escaped underscores (and a couple common escapes)
    return s.replace("\\_", "_").replace("\\-", "-").replace("\\ ", " ")


def _read_dev_list(p: Path) -> set[str]:
    text = _read_text_no_bom(p)
    if not text:
        return set()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    # Unescape markdown artifacts and normalize slashes
    norm = [_unescape_md(ln).replace("\\", "/") for ln in lines]
    return set(norm)


def _read_manifest_all_files(p: Path) -> set[str]:
    text = _read_text_no_bom(p)
    if not text:
        return set()
    obj = json.loads(text)
    all_files = obj.get("manifest", {}).get("all_files") or obj.get("all_files") or []
    return set(map(lambda s: s.replace("\\", "/"), all_files))


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Compare dev_file_list.md to ironroot_manifest_data.json (all_files).")
    parser.add_argument("--dev", default="configs/dev_file_list.md")
    parser.add_argument("--manifest", default="configs/ironroot_manifest_data.json")
    args = parser.parse_args()

    log_memory_event(
        event_text="manifest_diff start",
        source=src,
        tags=["tool", "start", "manifest_diff"],
        content={"dev": args.dev, "manifest": args.manifest},
        phase=REQUIRED_PHASE,
    )

    dev = _read_dev_list(Path(args.dev))
    man = _read_manifest_all_files(Path(args.manifest))

    only_dev = sorted(dev - man)
    only_man = sorted(man - dev)

    print(f"Only in dev_file_list.md ({len(only_dev)}):")
    for p in only_dev:
        print("  +", p)
    print(f"Only in manifest ({len(only_man)}):")
    for p in only_man:
        print("  -", p)

    log_trace_event(
        description="manifest_diff done",
        source=src,
        tags=["tool", "done", "manifest_diff"],
        content={"only_dev": only_dev[:50], "only_manifest": only_man[:50]},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()
