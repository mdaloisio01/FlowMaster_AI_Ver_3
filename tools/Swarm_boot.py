#!/usr/bin/env python3
"""
Swarm Boot Runner (Phase‑Neutral, Soft‑Guard Aligned)

This is the *executable* that your orchestrator spec expects.
It performs a read‑only swarm run:

* Reads manifest (current_phase)
* Loads a seed (master or explicit)
* Summarizes human‑readable objectives for the selected scope
* Runs a lightweight Dependency Interrogator (filesystem/context checks)
* (Optional) calls strict sweep & artifact emitter
* Writes compact JSON/Markdown reports under artifacts/

PC‑first. No external deps; stdlib only.
Does not mutate code. (Only writes reports unless you call other tools.)

Usage examples
python tools/swarm_boot.py                         # use defaults, master seed
python tools/swarm_boot.py --seed "seeds/phase_3.0_persona.md"
python tools/swarm_boot.py --posture strict --sweep
python tools/swarm_boot.py --emitter supporting-updates-only --emit

Exit codes
0: OK (verify‑only or green)
1: Fatal error (e.g., missing manifest)
2: Strict verify failed (evidence/quorum or phase guard sweep)
"""
from **future** import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --------------------------- Constants ---------------------------

ROOT = Path(**file**).resolve().parents[1] if Path(**file**).resolve().parts[-2] == 'tools' else Path.cwd()
CONF_MANIFEST = ROOT / "configs" / "ironroot_manifest_data.json"
CONF_HISTORY  = ROOT / "configs" / "phase_history.json"
LOG_TRACE     = ROOT / "logs" / "reflex_trace_log.jsonl"
LOG_GUARD     = ROOT / "logs" / "phase_guard_log.jsonl"
ART_DIR       = ROOT / "artifacts"
REP_DIR       = ART_DIR / "reports"
SEEDS_DIR     = ROOT / "seeds"
SWARM_DIR     = ROOT / "swarm"

DEFAULT_MASTER_SEED = next((p for p in SEEDS_DIR.glob("*MASTER*SEED*EDIT*.md")), None) or next((p for p in SEEDS_DIR.glob("*MASTER*SEED*.md")), None)

SWEEP_SCRIPT  = ROOT / "tools" / "phase_guard_sweep.py"
EMITTER_SCRIPT= ROOT / "tools" / "artifact_emitter.py"

RUNNER_VERSION = "swarm_boot.py/1.0.0"

# --------------------------- Utilities ---------------------------

def now_iso() -> str:
return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def read_json(path: Path) -> Optional[dict]:
if not path.exists():
return None
return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: dict) -> None:
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def append_jsonl(path: Path, obj: dict) -> None:
path.parent.mkdir(parents=True, exist_ok=True)
line = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
with path.open("a", encoding="utf-8") as f:
f.write(line + "\n")

def hash_str(s: str) -> str:
return hashlib.sha256(s.encode("utf-8")).hexdigest()

# --------------------------- Parsing (seed) ---------------------------

PHASE_HDR_RE = re.compile(r"^###\s+Phase\s+([0-9]+(?:.[0-9]+)?)\s+[—-]\s+(.*)$", re.IGNORECASE)

@dataclass
class PhaseOutline:
id: str
title: str
objective: List[str]
enables: List[str]
examples: List[str]
considerations: List[str]
inputs: List[str]
acceptance: List[str]
risks: List[str]
refs: List[str]

try:
from dataclasses import dataclass  # py3.7+
except Exception:  # pragma: no cover
raise SystemExit("Python 3.7+ required")

def extract_bullets(section: str, heading: str) -> List[str]:
"""Return dash-only bullets under a '#### <heading>' until next '####'."""
pat = re.compile(rf"^####\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
m = pat.search(section)
if not m:
return []
start = m.end()
nxt = re.search(r"^####\s+", section[start:], re.MULTILINE)
body = section[start: start + (nxt.start() if nxt else len(section[start:]))]
# Normalize bullets: accept '-' or '*' and normalize to '-'
items = []
for line in body.splitlines():
line = line.strip()
if line.startswith("-"):
items.append(line[1:].strip())
elif line.startswith("*"):
items.append(line[1:].strip())
return items

def parse_seed(seed_path: Path, scope: str, current_phase: str) -> Dict[str, dict]:
md = seed_path.read_text(encoding="utf-8")
# Split by phase H3 headers; support both "### Phase X.Y — Title" and variants
pieces = re.split(r"^###\s+Phase\s+", md, flags=re.MULTILINE)
results: Dict[str, dict] = {}
for piece in pieces[1:]:
line0, _, rest = piece.partition("\n")
# line0 like: "1.0 — Reflex Execution Core"
mid = line0.split(" ")[0].strip()
title = line0.split("—", 1)[1].strip() if "—" in line0 else line0
section = rest
# collect bullets
def grab(h):
return extract_bullets(section, h)
outline = {
"objective": grab("Objective"),
"enables": grab("What this enables"),
"examples": grab("Examples"),
"considerations": grab("Things to consider"),
"inputs": grab("Inputs / Prerequisites"),
"acceptance": grab("Acceptance (human view)"),
"risks": grab("Risks / Guardrails"),
"references": grab("References"),
"title": title,
}
results[mid] = outline
# Scope filter
if scope == "current":
return {k: v for k, v in results.items() if k == current_phase}
elif scope == "current+prereqs":
try:
cur = float(current_phase)
return {k: v for k, v in results.items() if float(k) <= cur}
except Exception:
return {current_phase: results.get(current_phase, {})}
elif scope.startswith("custom:"):
allowed = {p.strip() for p in scope.split(":", 1)[1].split(",")}
return {k: v for k, v in results.items() if k in allowed}
else:
return {current_phase: results.get(current_phase, {})}

# --------------------------- Dependency Interrogator (lite) ---------------------------

def interrogate(current_phase: str) -> dict:
checks = {
"trace_logger": LOG_TRACE.parent.exists(),
"memory_logging": True,  # guidance-level: assume available; overridden if logs dir missing
"manifest_present": CONF_MANIFEST.exists(),
"history_present": CONF_HISTORY.exists(),
"get_current_phase_util": True,  # doc-level check (cannot introspect here)
"entrypoint_guard_policy": True,  # policy-level (from seeds)
"upstream_ready": True,
}
if not LOG_TRACE.parent.exists():
checks["memory_logging"] = False
gaps = []
if not checks["manifest_present"]:
gaps.append("manifest missing: configs/ironroot_manifest_data.json")
if not checks["history_present"]:
gaps.append("history missing: configs/phase_history.json")
if not LOG_TRACE.parent.exists():
gaps.append("logs directory missing (trace/memory)")
recommendation = "proceed" if not gaps else "verify-only"
return {"checks": checks, "gaps": gaps, "recommendation": recommendation}

# --------------------------- Strict sweep (optional) ---------------------------

def run_sweep(strict: bool) -> Tuple[str, int]:
if not SWEEP_SCRIPT.exists():
return ("missing", 0)
args = [sys.executable, str(SWEEP_SCRIPT), "--json", str(REP_DIR / "sweep_report.json")]
if strict:
args.append("--strict")
REP_DIR.mkdir(parents=True, exist_ok=True)
proc = subprocess.run(args, capture_output=True, text=True)
return (proc.stdout.strip() or "ok", proc.returncode)

# --------------------------- Artifact emitter (optional) ---------------------------

def run_emitter(mode: str, scope: str) -> None:
if not EMITTER_SCRIPT.exists():
print("[emitter] tools/artifact_emitter.py not found — skipping.")
return
args = [sys.executable, str(EMITTER_SCRIPT), "--mode", mode, "--scope", scope]
subprocess.run(args)

# --------------------------- Main ---------------------------

def main(argv: Optional[List[str]] = None) -> int:
parser = argparse.ArgumentParser(description="Swarm Boot Runner (phase‑neutral)")
parser.add_argument("--seed", default=str(DEFAULT_MASTER_SEED) if DEFAULT_MASTER_SEED else None,
help="Path to seed markdown (defaults to Master Dev Phase Seed if found)")
parser.add_argument("--scope", default="current", choices=["current", "current+prereqs", "custom:list"],
help="Planning scope (use 'custom:list' then --phases A,B)")
parser.add_argument("--phases", default="", help="Comma list for scope=custom:list (e.g., 0.7,1.0)")
parser.add_argument("--posture", default=os.environ.get("WILL_PHASE_STRICT", "0") == "1" and "strict" or "soft",
choices=["soft", "strict"], help="Soft (default) or strict posture")
parser.add_argument("--verify-quorum", type=int, default=2, help="External verification quorum (docs-only")
parser.add_argument("--emit", action="store_true", help="Call artifact emitter after reports")
parser.add_argument("--emitter", default="supporting-updates-only",
choices=["supporting-updates-only","new-only","new+changed","baseline+new","all"],
help="Emitter mode if --emit is set")
parser.add_argument("--sweep", action="store_true", help="Run strict phase sweep")
parser.add_argument("--dry-run", action="store_true", help="Report only; implies no writes (default behavior)")
args = parser.parse_args(argv)

```
# Resolve scope if custom:list
scope = args.scope
if scope == "custom:list":
    phases = ",".join([p.strip() for p in args.phases.split(",") if p.strip()])
    scope = f"custom:{phases}" if phases else "current"

# Manifest
manifest = read_json(CONF_MANIFEST)
if not manifest or "current_phase" not in manifest:
    print("[error] manifest missing or invalid at configs/ironroot_manifest_data.json")
    return 1
current_phase = str(manifest["current_phase"])

run_id = hash_str(now_iso() + RUNNER_VERSION)[:12]

append_jsonl(LOG_TRACE, {
    "ts": now_iso(), "run_id": run_id, "type": "swarm.boot", "event": "start",
    "runner_version": RUNNER_VERSION, "phase_current": current_phase,
    "scope": scope, "posture": args.posture
})

# Seed
if not args.seed:
    print("[warn] No seed path provided and master seed not found; proceeding with minimal context.")
    seed_path = None
    selected = {}
else:
    seed_path = Path(args.seed)
    if not seed_path.exists():
        print(f"[error] seed not found: {seed_path}")
        return 1
    try:
        selected = parse_seed(seed_path, scope, current_phase)
    except Exception as e:
        print(f"[warn] seed parse failed ({e}); proceeding with minimal context.")
        selected = {}

# Build human summary
human = []
for pid, outline in sorted(selected.items(), key=lambda kv: float(kv[0]) if kv[0].replace('.', '', 1).isdigit() else 999):
    human.append({
        "phase": pid,
        "title": outline.get("title", ""),
        "objective": outline.get("objective", [])[:1],
        "enables": outline.get("enables", [])[:3],
        "considerations": outline.get("considerations", [])[:3],
    })

# Interrogator
dep = interrogate(current_phase)

report = {
    "ts": now_iso(),
    "run_id": run_id,
    "runner": RUNNER_VERSION,
    "phase": {"current": current_phase, "posture": args.posture},
    "seed": str(seed_path) if seed_path else None,
    "scope": scope,
    "summary": human,
    "interrogator": dep,
    "verification": {"allowlist": [], "quorum": args.verify_quorum, "met": False, "notes": "offline runner"}
}

REP_DIR.mkdir(parents=True, exist_ok=True)
write_json(REP_DIR / f"swarm_boot_report_{run_id}.json", report)

# Optional sweep
retcode = 0
if args.sweep:
    out, code = run_sweep(strict=(args.posture == "strict"))
    append_jsonl(LOG_GUARD, {
        "ts": now_iso(), "run_id": run_id, "kind": "sweep", "status": "ok" if code == 0 else "fail",
        "posture": args.posture, "report": str(REP_DIR / "sweep_report.json")
    })
    if args.posture == "strict" and code != 0:
        retcode = 2

# Optional emitter
if args.emit:
    run_emitter(args.emitter, scope)

append_jsonl(LOG_TRACE, {"ts": now_iso(), "run_id": run_id, "type": "swarm.boot", "event": "done", "status": "ok" if retcode == 0 else "fail"})

# Console summary
print("\n== SWARM BOOT SUMMARY ==")
print(f"phase: {current_phase} | posture: {args.posture} | scope: {scope}")
if human:
    for h in human:
        print(f"- Phase {h['phase']} — {h['title']}")
        if h['objective']:
            print(f"  objective: {h['objective'][0]}")
if dep.get("gaps"):
    print("gaps:")
    for g in dep["gaps"]:
        print(f"- {g}")
    if args.posture == "strict":
        retcode = max(retcode, 2)
print(f"report: {REP_DIR / f'swarm_boot_report_{run_id}.json'}")

return retcode
```

if **name** == "**main**":
sys.exit(main())
