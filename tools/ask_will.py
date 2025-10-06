# /tools/ask_will.py
# Ask Will a question: retrieves top-K chunks from chunk_store.db, calls the local model,
# prints a concise answer **with citations** (file paths + chunk ids).

from boot.boot_path_initializer import inject_paths; inject_paths()

import json
from typing import List, Dict, Any

from core.phase_control import ensure_phase
from core.trace_logger import log_trace_event as _lte
from core.memory_interface import log_memory_event as _lme

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

# ---- safe logging wrappers (tolerate different function signatures) ----
def _safe_trace(event: str):
    try:
        _lte(event)
    except TypeError:
        try: _lte(event, {})
        except Exception: pass
    except Exception:
        pass

def _safe_mem(event: str, details: Dict[str, Any] | None = None):
    try:
        _lme(event, details)
    except TypeError:
        try: _lme(event)
        except Exception: pass
    except Exception:
        pass

# Local imports after path injection
from tools import retriever
from tools import model_router

SYSTEM_PROMPT = (
    "You are Will, a concise assistant. Answer the user's question using ONLY the provided notes.\n"
    "Always include brief bullet points and cite sources as [path#chunk]. If info is missing, say so.\n"
)

def _format_context(snips: List[Dict[str, Any]]) -> str:
    lines = []
    for s in snips:
        # Compact source tag: repo/path#chunkIndex
        tag = f"{s['file_path']}#chunk-{s['chunk_index']}"
        lines.append(f"[{tag}] {s['snippet']}")
    return "\n".join(lines) if lines else "(no context found)"

def _format_sources(snips: List[Dict[str, Any]]) -> str:
    if not snips:
        return "Sources: (none)"
    uniq = []
    seen = set()
    for s in snips:
        tag = f"{s['file_path']}#chunk-{s['chunk_index']}"
        if tag not in seen:
            seen.add(tag)
            uniq.append(tag)
    return "Sources:\n" + "\n".join(f" - {u}" for u in uniq)

def ask(q: str, *, k: int = 5, model: str | None = None, max_tokens: int = 512) -> Dict[str, Any]:
    _safe_trace("ask_start")
    ensure_phase(REQUIRED_PHASE)

    # 1) Retrieve
    snips = retriever.search_chunks(q, top_k=k)
    context = _format_context(snips)

    # 2) Build prompt for the local model (RAG style)
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {q}\n"
        f"Answer with a short summary and cite sources as [path#chunk]."
    )

    # 3) Call model
    out = model_router.generate(prompt, model=model, max_tokens=max_tokens)
    text = out.get("text", "").strip()

    # 4) Attach sources
    sources = _format_sources(snips)
    if text:
        answer = f"{text}\n\n{sources}"
    else:
        answer = f"(no answer)\n\n{sources}"

    # 5) Dual log (safe)
    _safe_mem("ask_will", {"q": q, "k": k, "model": model or "default", "chars": len(text)})

    _safe_trace("ask_end")
    return {"answer": answer, "sources": snips, "model": out.get("model"), "duration_ms": out.get("duration_ms")}

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Ask Will (retriever + local model)")
    ap.add_argument("--q", required=True, help="Your question")
    ap.add_argument("--k", type=int, default=5, help="Top-K chunks to retrieve")
    ap.add_argument("--model", default=None, help="Override model name (ollama)")
    ap.add_argument("--max", type=int, default=512, help="Max tokens to generate")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of text")
    args = ap.parse_args()

    res = ask(args.q, k=args.k, model=args.model, max_tokens=args.max)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(res["answer"])

if __name__ == "__main__":
    _cli()
