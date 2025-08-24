from __future__ import annotations
from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
from pathlib import Path
from typing import List, Tuple

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
    # Normalize markdown-escaped characters commonly seen in dev_file_list.md
    return s.replace("\\_", "_").replace("\\-", "-").replace("\\ ", " ")


def _load_dev_list(dev_path: Path) -> List[str]:
    raw = _read_text_no_bom(dev_path)
    if not raw:
        return []
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    # Unescape markdown artifacts and normalize slashes
    lines = [_unescape_md(ln) for ln in lines]
    return lines


def _find_backslash_issues(lines: List[str]) -> List[str]:
    """
    Return entries that still contain a backslash after markdown unescape.
    These are true policy violations.
    """
    bad = []
    for ln in lines:
        if "\\" in ln:
            bad.append(ln)
    return bad


def _autofix_lines(lines: List[str]) -> List[str]:
    """
    Apply forward-slash normalization and ensure alpha sort.
    We do not change case or remove entries.
    """
    fixed = []
    for ln in lines:
        # After unescape, convert any remaining backslashes to forward slashes
        ln = ln.replace("\\", "/")
        fixed.append(ln)
    # Alpha sort for stability
    fixed = sorted(set(fixed))
    return fixed


def run_cli() -> None:
    ensure_phase()
    src = Path(__file__).as_posix()

    parser = argparse.ArgumentParser(description="Validate that dev_file_list.md uses forward slashes and no markdown escapes/BOM.")
    parser.add_argument("--dev", default="configs/dev_file_list.md", help="Path to dev_file_list.md")
    parser.add_argument("--autofix", action="store_true", help="Rewrite the dev file with normalized entries (UTF-8 without BOM, forward slashes).")
    parser.add_argument("--backup", action="store_true", help="When --autofix, write a .bak file next to the dev file before overwriting.")
    args = parser.parse_args()

    dev_path = Path(args.dev)

    log_memory_event(
        event_text="path_validator start",
        source=src,
        tags=["tool", "start", "path_validator"],
        content={"dev": dev_path.as_posix(), "autofix": args.autofix, "backup": args.backup},
        phase=REQUIRED_PHASE,
    )

    lines = _load_dev_list(dev_path)
    bad = _find_backslash_issues(lines)

    if bad and not args.autofix:
        print("Found backslashes in dev_file_list.md:")
        for b in bad[:200]:
            print(" -", b)
        print("\nTip: run with --autofix to normalize the file (forward slashes, UTF-8 no BOM).")
    else:
        if args.autofix:
            # Normalize (forward slashes + alpha sort) and save UTF-8 without BOM
            fixed = _autofix_lines(lines)

            if args.backup and dev_path.exists():
                bak = dev_path.with_suffix(dev_path.suffix + ".bak")
                bak.write_text("\n".join(lines) + "\n", encoding="utf-8")  # original content (may include BOM/escapes)

            # Save normalized content (UTF-8 no BOM)
            from io import TextIOWrapper
            data = "\n".join(fixed) + "\n"
            # Use plain UTF-8 without BOM by writing via Python's encoding
            dev_path.write_text(data, encoding="utf-8")
            print(f"✅ Normalized {dev_path.as_posix()} (forward slashes, deduped, alpha-sorted, UTF-8 no BOM).")

            # Re-check
            re_lines = _load_dev_list(dev_path)
            re_bad = _find_backslash_issues(re_lines)
            if re_bad:
                print("⚠️ Still found entries with backslashes after autofix:")
                for rb in re_bad[:200]:
                    print(" -", rb)
            else:
                print("✅ No backslashes remain.")
        else:
            print("✅ No backslashes found in dev_file_list.md.")

    log_trace_event(
        description="path_validator done",
        source=src,
        tags=["tool", "done", "path_validator"],
        content={"bad_count": len(bad)},
        phase=REQUIRED_PHASE,
    )


if __name__ == "__main__":
    run_cli()
