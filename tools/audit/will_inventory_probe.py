# /tools/audit/will_inventory_probe.py
"""
Will Inventory Probe — Phase 0.7 (IronSpine)

Plain talk:
  - Point this at your OLD "Will" folder and it will scan everything.
  - It guesses what looks like Will core (/boot, /core, /tools, /reflexes, /configs, /tests, /logs, /sandbox)
    and what looks like LLM runtimes, caches, or junk (venv, node_modules, models, .git, cache, etc).
  - It writes a simple report we can use to import only the right pieces.

Outputs (saved under your CURRENT project):
  - sandbox/inventory_report.json   (full machine-readable results)
  - sandbox/inventory_summary.txt   (easy human summary)

Run:
  python -m tools.audit.will_inventory_probe "D:\path\to\OLD_WILL_FOLDER"
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import os
import sys
import json
import hashlib
import sqlite3
from datetime import datetime

from core.phase_control import ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

# Heuristics
WILL_DIR_HINTS = {
    "boot", "core", "tools", "reflexes", "configs", "tests", "logs", "sandbox"
}
EXCLUDE_DIR_NAMES = {
    ".git", ".github", ".idea", ".vscode", ".pytest_cache", "__pycache__", "dist", "build",
    "venv", "env", ".env", "node_modules", ".next", "coverage", "site-packages",
    "models", "model", "weights", "checkpoints", "ckpt", "tensorboard", "wandb",
    "cache", ".cache", "hf_cache", "huggingface", "transformers_cache", "pip-cache",
    "oobabooga", "text-generation-webui", "koboldai", "llama.cpp", "vllm", "exllamav2",
}
# Extensions likely not Will source
BINARY_EXTS = {
    ".png",".jpg",".jpeg",".gif",".webp",".ico",
    ".pdf",".ppt",".pptx",".xls",".xlsx",".doc",".docx",
    ".zip",".7z",".rar",".tar",".gz",".bz2",
    ".exe",".dll",".so",".dylib",
    ".bin",".safetensors",".pt",".pth",
    ".mp3",".wav",".mp4",".mov",".avi"
}

# Project root (current IronSpine)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
OUT_DIR = os.path.join(PROJECT_ROOT, "sandbox")
REPORT_JSON = os.path.join(OUT_DIR, "inventory_report.json")
REPORT_TXT  = os.path.join(OUT_DIR, "inventory_summary.txt")

# Optional: also note the chunk DB path (not required to run)
CHUNK_DB = os.path.join(PROJECT_ROOT, "chunk_store.db")

def human_size(n: int) -> str:
    units = ["B","KB","MB","GB","TB"]
    i = 0
    x = float(n)
    while x >= 1024 and i < len(units)-1:
        x /= 1024.0
        i += 1
    return f"{x:.1f} {units[i]}"

def scan_root(root_path: str, max_files_listed: int = 2000, big_file_threshold_mb: int = 50):
    big_bytes = big_file_threshold_mb * 1024 * 1024
    root_path = os.path.abspath(root_path)

    summary = {
        "scanned_root": root_path,
        "started_at": datetime.utcnow().isoformat()+"Z",
        "total_files": 0,
        "total_size": 0,
        "top_dirs": [],                # [{path,size,count,is_will_like,is_excluded}]
        "keep_candidates": [],         # e.g., likely Will dirs
        "exclude_candidates": [],      # e.g., LLM/runtime/cache dirs
        "files_sample": [],            # sample of files considered keep/exclude
        "big_files": [],               # > threshold
        "notes": [],
    }

    # Build immediate subdir stats
    first_level = {}
    for name in os.listdir(root_path):
        p = os.path.join(root_path, name)
        if os.path.isdir(p):
            first_level[p] = {"size":0, "count":0}

    files_listed = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        # classify dirs on the fly
        base = os.path.basename(dirpath)

        # mark exclusion dirs to skip deeper walk
        if base in EXCLUDE_DIR_NAMES:
            summary["exclude_candidates"].append(dirpath)
            # prune traversal
            dirnames.clear()
            continue

        # tally files
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                st = os.stat(fpath)
                summary["total_files"] += 1
                summary["total_size"] += st.st_size

                # top-level bucket
                parts = os.path.relpath(dirpath, root_path).split(os.sep)
                if len(parts) == 1 and dirpath in first_level:
                    first_level[dirpath]["size"] += st.st_size
                    first_level[dirpath]["count"] += 1

                # big files
                if st.st_size >= big_bytes:
                    summary["big_files"].append({
                        "path": fpath, "size": st.st_size
                    })

                # sample some files
                if files_listed < max_files_listed:
                    ext = os.path.splitext(fname)[1].lower()
                    file_class = "keep-ish"
                    if ext in BINARY_EXTS:
                        file_class = "binary"
                    summary["files_sample"].append({
                        "path": fpath,
                        "size": st.st_size,
                        "class": file_class
                    })
                    files_listed += 1

            except Exception:
                continue

    # classify top-level dirs
    for p, stats in first_level.items():
        name = os.path.basename(p)
        is_will_like = name in WILL_DIR_HINTS
        summary["top_dirs"].append({
            "path": p,
            "size": stats["size"],
            "count": stats["count"],
            "is_will_like": is_will_like,
            "is_excluded": name in EXCLUDE_DIR_NAMES
        })
        if is_will_like:
            summary["keep_candidates"].append(p)

    # dedupe exclude list & sort
    summary["exclude_candidates"] = sorted(set(summary["exclude_candidates"]))

    # simple notes
    summary["notes"].append("Heuristics only — you confirm before import.")
    summary["notes"].append("LLM/runtime dirs were skipped to avoid bloat.")
    summary["finished_at"] = datetime.utcnow().isoformat()+"Z"
    return summary

def write_reports(data: dict):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    # human summary
    lines = []
    lines.append(f"Scanned: {data['scanned_root']}")
    lines.append(f"Total files: {data['total_files']:,}  Total size: {human_size(data['total_size'])}")
    lines.append("")
    lines.append("Top-level directories:")
    for d in sorted(data["top_dirs"], key=lambda x: x["path"].lower()):
        mark = "KEEP?" if d["is_will_like"] else ""
        if d["is_excluded"]:
            mark = "EXCLUDED"
        lines.append(f"  - {d['path']}  files={d['count']:,}  size={human_size(d['size'])}  {mark}")
    lines.append("")
    if data["big_files"]:
        lines.append("Big files (possible LLM/checkpoints):")
        for b in sorted(data["big_files"], key=lambda x: -x["size"])[:20]:
            lines.append(f"  - {b['path']}  {human_size(b['size'])}")
        lines.append("")

    with open(REPORT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def run():
    if len(sys.argv) < 2:
        print("Usage: python -m tools.audit.will_inventory_probe \"D:\\path\\to\\OLD_WILL_FOLDER\"")
        sys.exit(1)

    target = sys.argv[1]
    if not os.path.isdir(target):
        print(f"🚫 Not a directory: {target}")
        sys.exit(2)

    cur = get_current_phase()
    log_memory_event("will_inventory_probe_start", source=__file__, phase=REQUIRED_PHASE,
                     tags=["inventory","import"], content=target)
    log_trace_event("will_inventory_probe_start", source=__file__, phase=REQUIRED_PHASE,
                    tags=["inventory","import"], content=target)

    data = scan_root(target)
    write_reports(data)

    log_trace_event("will_inventory_probe_done", source=__file__, phase=REQUIRED_PHASE,
                    tags=["inventory","import"], content=json.dumps({
                        "total_files": data["total_files"],
                        "total_size": data["total_size"],
                    }))
    log_memory_event("will_inventory_probe_done", source=__file__, phase=REQUIRED_PHASE,
                     tags=["inventory","import"])

    print(f"✅ Inventory complete.\n - {REPORT_JSON}\n - {REPORT_TXT}")

def run_cli():
    run()

if __name__ == "__main__":
    run_cli()
