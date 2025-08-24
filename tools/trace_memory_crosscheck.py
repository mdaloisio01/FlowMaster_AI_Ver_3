# tools/trace_memory_crosscheck.py
# Cross-checks memory and trace logs for unmatched/duplicate snapshot events.
# - Path injection first
# - Phase lock + dual logging
# - Schema-agnostic: auto-detects text/content columns in memory_events/trace_events
# - Parses content as JSON, else falls back to Python literal (safe)

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import json
import sqlite3
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core.phase_control import ensure_phase, REQUIRED_PHASE
from core.sqlite_bootstrap import DB_PATH
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event


# ---------- schema helpers ----------

_TEXT_COLS_PRIORITY = ["event_text", "description", "message", "event", "text", "title", "name"]
_CONTENT_COLS_PRIORITY = ["content", "payload", "data", "extra", "details", "meta"]
_ID_COLS_PRIORITY = ["id", "rowid"]  # SQLite guarantees rowid when table is rowid-based


def _cols(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.execute(f"PRAGMA table_info({table});")
    return [r[1] for r in cur.fetchall()]  # 1 = name


def _pick(colset: List[str], priorities: List[str]) -> Optional[str]:
    lower = {c.lower(): c for c in colset}
    for p in priorities:
        if p in lower:
            return lower[p]
    return None


def _detect_columns(conn: sqlite3.Connection, table: str) -> Tuple[str, str, str]:
    colset = _cols(conn, table)
    if not colset:
        raise RuntimeError(f"Table not found or has no columns: {table}")

    id_col = _pick(colset, _ID_COLS_PRIORITY)
    text_col = _pick(colset, _TEXT_COLS_PRIORITY)
    content_col = _pick(colset, _CONTENT_COLS_PRIORITY)

    # Fallbacks
    id_col = id_col or colset[0]
    text_col = text_col or colset[1 if len(colset) > 1 else 0]
    content_col = content_col or (colset[2] if len(colset) > 2 else text_col)

    return id_col, text_col, content_col


def _safe_parse_obj(s: Optional[str]) -> Dict:
    if not s:
        return {}
    # 1) try JSON
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        pass
    # 2) try Python literal (safe)
    try:
        obj = ast.literal_eval(s)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def _fetch_events(table: str, limit: int = 500) -> List[Tuple[int, str, Dict]]:
    """
    Returns rows as (id, text, content_dict)
    Auto-detects text/content columns.
    """
    with sqlite3.connect(Path(DB_PATH).as_posix()) as conn:
        id_col, text_col, content_col = _detect_columns(conn, table)
        cur = conn.execute(
            f"SELECT {id_col} AS _id, {text_col} AS _txt, {content_col} AS _content FROM {table} ORDER BY _id DESC LIMIT ?;",
            (limit,),
        )
        out = []
        for _id, _txt, _content in cur.fetchall():
            text = (_txt or "").strip()
            content = _safe_parse_obj(_content if isinstance(_content, str) else None)
            out.append((int(_id) if _id is not None else 0, text, content))
        return out


# ---------- audit logic ----------

def audit(run_id: Optional[str] = None, window: int = 500) -> Dict[str, List[str]]:
    """
    Compares presence of 'snapshot_wrapper start' and 'snapshot_wrapper done'
    between memory_events and trace_events. Correlates primarily by content.run_id
    (our wrapper includes it). If missing, falls back to a generic bucket.
    """
    mem = _fetch_events("memory_events", limit=window)
    trc = _fetch_events("trace_events", limit=window)

    def collect(events):
        starts, dones = {}, {}
        for _id, text, content in events:
            rid = content.get("run_id") or ("no-runid")
            if run_id and rid != run_id:
                continue
            label = text.lower()
            if "snapshot_wrapper start" in label:
                starts[rid] = starts.get(rid, 0) + 1
            elif "snapshot_wrapper done" in label:
                dones[rid] = dones.get(rid, 0) + 1
        return starts, dones

    m_starts, m_dones = collect(mem)
    t_starts, t_dones = collect(trc)

    keys = set(m_starts) | set(t_starts) | set(m_dones) | set(t_dones)
    if run_id:
        keys = {run_id} if run_id in keys or not keys else keys

    memory_only_starts, trace_only_starts = [], []
    memory_only_dones, trace_only_dones = [], []
    duplicates = []

    for k in sorted(keys):
        ms = m_starts.get(k, 0); ts = t_starts.get(k, 0)
        md = m_dones.get(k, 0); td = t_dones.get(k, 0)

        if ms and not ts:
            memory_only_starts.append(k)
        if ts and not ms:
            trace_only_starts.append(k)
        if md and not td:
            memory_only_dones.append(k)
        if td and not md:
            trace_only_dones.append(k)

        if ms > 1 or ts > 1 or md > 1 or td > 1:
            duplicates.append(k)

    return {
        "memory_only_starts": memory_only_starts,
        "trace_only_starts": trace_only_starts,
        "memory_only_dones": memory_only_dones,
        "trace_only_dones": trace_only_dones,
        "duplicates": duplicates,
    }


# ---------- CLI ----------

def run_cli() -> None:
    ensure_phase()

    p = argparse.ArgumentParser(description="Trace↔Memory cross-check", allow_abbrev=False)
    p.add_argument("--run-id", help="Specific run_id to check (default: recent window).", default=None)
    p.add_argument("--window", type=int, default=500, help="Rows to inspect per table.")
    p.add_argument("--snapshot-mode", choices=["off", "light", "heavy"], default="heavy",
                   help="Accepted for compatibility; not used here.")
    args = p.parse_args()

    res = audit(run_id=args.run_id, window=args.window)

    # Dual logging
    src = __file__.replace("\\", "/")
    log_memory_event(
        event_text="trace_memory_crosscheck report",
        source=src,
        tags=["tool", "audit", "snapshot"],
        content=res,
        phase=REQUIRED_PHASE,
    )
    log_trace_event(
        description="trace_memory_crosscheck report",
        source=src,
        tags=["tool", "audit", "snapshot"],
        content=res,
        phase=REQUIRED_PHASE,
    )

    ok = not any(res.values())
    if ok:
        print("[crosscheck] OK — memory and trace snapshot events are aligned.")
    else:
        print("[crosscheck] ISSUES:")
        for k, v in res.items():
            if v:
                print(f"  - {k}: {v}")


if __name__ == "__main__":
    run_cli()
