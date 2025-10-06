from boot.boot_path_initializer import inject_paths; inject_paths()

import os, json, time, urllib.request, urllib.error
from typing import Optional, Dict, Any

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
        try:
            _lte(event, {})
        except Exception:
            pass
    except Exception:
        pass

def _safe_mem(event: str, details: Dict[str, Any] | None = None):
    try:
        _lme(event, details)
    except TypeError:
        try:
            # try positional only
            _lme(event)
        except Exception:
            pass
    except Exception:
        pass

_safe_trace("module_import")

# ---- config ----
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("WILL_MODEL", "qwen2.5:7b-instruct")
DEFAULT_TIMEOUT_S = int(os.environ.get("WILL_MODEL_TIMEOUT_S", "30"))
DEFAULT_MAX_TOKENS = int(os.environ.get("WILL_MODEL_MAX_TOKENS", "512"))
DEFAULT_TEMPERATURE = float(os.environ.get("WILL_MODEL_TEMPERATURE", "0.2"))
DEFAULT_TOP_P = float(os.environ.get("WILL_MODEL_TOP_P", "0.9"))

def _post_json(url: str, payload: Dict[str, Any], timeout_s: int) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        # Some Ollama builds stream JSONL; fall back to the last non-empty line.
        lines = [ln for ln in body.splitlines() if ln.strip()]
        if lines:
            return json.loads(lines[-1])
        raise

def generate(
    prompt: str,
    model: Optional[str] = None,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
    stop: Optional[list] = None,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> Dict[str, Any]:
    """
    Call local Ollama and return:
      {"text": "...", "model": "...", "duration_ms": 1234, "raw": {...}}
    """
    model = model or DEFAULT_MODEL
    t0 = time.time()
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": int(max_tokens),
            "temperature": float(temperature),
            "top_p": float(top_p),
        },
    }
    if stop:
        payload["stop"] = stop

    _safe_trace("model_call_start")
    try:
        resp = _post_json(url, payload, timeout_s=timeout_s)
        text = resp.get("response", "") or ""
        dt_ms = int((time.time() - t0) * 1000)
        _safe_trace("model_call_end")
        _safe_mem("model_call", {"router": "ollama", "model": model, "duration_ms": dt_ms, "text_preview": text[:120]})
        return {"text": text, "model": model, "duration_ms": dt_ms, "raw": resp}
    except urllib.error.URLError as e:
        _safe_trace("model_call_error")
        raise

def _cli():
    import argparse
    ap = argparse.ArgumentParser(description="Will model router (Ollama)")
    ap.add_argument("--q", required=True, help="Prompt text")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Model name (ollama)")
    ap.add_argument("--max", type=int, default=DEFAULT_MAX_TOKENS, help="Max tokens to generate")
    ap.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    ap.add_argument("--top_p", type=float, default=DEFAULT_TOP_P)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_S)
    args = ap.parse_args()

    ensure_phase(REQUIRED_PHASE)
    out = generate(
        args.q,
        model=args.model,
        max_tokens=args.max,
        temperature=args.temperature,
        top_p=args.top_p,
        timeout_s=args.timeout,
    )
    print(out["text"])

if __name__ == "__main__":
    _cli()
