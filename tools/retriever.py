from boot.boot_path_initializer import inject_paths; inject_paths()

import os, sqlite3, time, json, re
from typing import List, Dict, Any

from core.phase_control import ensure_phase
from core.trace_logger import log_trace_event as _lte
from core.memory_interface import log_memory_event as _lme

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

def _safe_trace(event: str):
    try: _lte(event)
    except TypeError:
        try: _lte(event, {})
        except Exception: pass
    except Exception: pass

def _safe_mem(event: str, details: Dict[str, Any] | None = None):
    try: _lme(event, details)
    except TypeError:
        try: _lme(event)
        except Exception: pass
    except Exception: pass

_safe_trace("module_import")

DB_PATH = os.path.join(os.getcwd(), "chunk_store.db")
TABLE = "file_chunks"

STOPWORDS = {
    "a","an","and","are","as","at","be","but","by","for","from","has","he","her","his","i",
    "in","is","it","its","of","on","or","that","the","their","there","they","this","to","was",
    "we","were","what","when","where","which","who","why","with","you","your","did","do","does",
    "how","me","my","our","ours","she","them","then","than","so"
}

def _connect():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Chunk DB not found at {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def _tokenize(query: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+", query.lower())

def _filter_terms(tokens: List[str]) -> List[str]:
    strong = [t for t in tokens if len(t) >= 3 and t not in STOPWORDS]
    return strong or tokens

def _build_like_clause(terms: List[str]) -> str:
    if not terms: return "1=1"
    return " OR ".join(["chunk_text LIKE ?"] * len(terms))

def _bind_terms(terms: List[str]) -> List[str]:
    return [f"%{t}%" for t in terms]

def _make_snippet(text: str, max_len: int = 240) -> str:
    if text is None: return ""
    text = text.strip().replace("\r", " ").replace("\n", " ")
    return (text[: max_len - 1] + "…") if len(text) > max_len else text

def _rank_score(file_path: str, text: str, terms: List[str]) -> float:
    if not text: return 0.0
    tl = text.lower()
    score = 0.0

    # Stronger weight for meaningful terms; de-weight ultra-common collisions like "line"
    for t in terms:
        w = 3.0
        if t in {"line", "file", "chunk"}:  # common in code
            w = 0.5
        score += tl.count(t) * w

    # Diversity bonus
    score += sum(1 for t in set(terms) if t in tl) * 2.0

    # Phrase / token bonuses for hyphenated or uppercase-like markers (e.g., CANARY-XXXX)
    if any("-" in t for t in terms):
        score += 2.0
    if "canary" in terms and ("canary" in tl or "canary-" in tl):
        score += 6.0

    # Path shaping: boost chat logs, soften tool/code files
    fp = file_path.replace("\\", "/")
    if "/repo/chat_logs/" in fp:
        score += 6.0
    if "/tools/" in fp:
        score -= 3.0

    return score

def search_chunks(query: str, top_k: int = 5, prefetch_limit: int = 200) -> List[Dict[str, Any]]:
    t0 = time.time()
    if not query or not query.strip(): return []

    tokens = _tokenize(query)
    terms = _filter_terms(tokens)

    con = _connect()
    cur = con.cursor()

    where = _build_like_clause(terms)
    bind = _bind_terms(terms)
    sql = f"""
        SELECT id, file_path, chunk_index, line_start, line_end, token_count, chunk_text, summary
        FROM {TABLE}
        WHERE {where}
        ORDER BY id DESC
        LIMIT ?
    """
    args = (prefetch_limit,) if where == "1=1" else (*bind, prefetch_limit)
    rows = list(cur.execute(sql, args))

    ranked = []
    for r in rows:
        text = (r["chunk_text"] or "") + " " + (r["summary"] or "")
        score = _rank_score(r["file_path"], text, terms)
        ranked.append((score, r))
    ranked.sort(key=lambda x: x[0], reverse=True)

    top = ranked[: top_k] if top_k > 0 else ranked
    results = [{
        "file_path": r["file_path"],
        "chunk_index": r["chunk_index"],
        "line_start": r["line_start"],
        "line_end": r["line_end"],
        "token_count": r["token_count"],
        "score": float(score),
        "snippet": _make_snippet(r["chunk_text"]),
    } for score, r in top]

    _safe_trace("retriever_search")
    _safe_mem("retriever_search", {"q": query, "returned": len(results), "duration_ms": int((time.time()-t0)*1000)})
    return results

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Will Retriever (focused LIKE+rank)")
    ap.add_argument("--q", required=True, help="Query text")
    ap.add_argument("--k", type=int, default=5, help="Top K results")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of pretty lines")
    args = ap.parse_args()

    ensure_phase(REQUIRED_PHASE)
    _safe_trace("cli_start")
    results = search_chunks(args.q, top_k=args.k)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No results.")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['file_path']} [chunk {r['chunk_index']}] "
                  f"lines {r['line_start']}-{r['line_end']} | score={r['score']:.2f}")
            print(f"   {r['snippet']}")
    _safe_trace("cli_end")

if __name__ == "__main__":
    _cli()
