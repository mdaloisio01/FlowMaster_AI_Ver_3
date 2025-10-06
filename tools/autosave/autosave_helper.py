
# /tools/autosave/autosave_helper.py
"""
Autosave Helper — Phase 0.7
Purpose (plain talk):
  - Read autosave policy (configs/autosave_policy.json)
  - On a timer OR when content grows ~10k tokens, save a bundle to /repo/chat_logs/
  - Run the chunker so the content is indexed in chunk_store.db
  - Avoid duplicates by fingerprinting content; DB also dedupes via chunk_hash

Modes:
  1) Autosave mode (recommended now):
     python -m tools.autosave.autosave_helper --source-file path/to/current_chat.txt

  2) One-shot paste mode:
     python -m tools.autosave.autosave_helper --once
     (then paste the chat text, press Ctrl+Z/Enter on Windows or Ctrl+D on macOS/Linux)

Notes:
  - This is the local helper. A small browser userscript can write the chat page
    into the --source-file so you never copy/paste. This file is ready for that.

Phase: 0.7 (IronSpine locked)
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
from typing import Optional, Tuple, List

import tiktoken

from core.phase_control import ensure_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event
from tools.chunker.chunker import run_chunker

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

# ---------- Tokenizer ----------
_tokenizer = tiktoken.get_encoding("cl100k_base")
def count_tokens(text: str) -> int:
    return len(_tokenizer.encode(text or ""))

# ---------- Policy ----------
DEFAULT_POLICY_PATH = "configs/autosave_policy.json"

def load_policy(path: str = DEFAULT_POLICY_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- Normalization & Hash ----------
_FRONTMATTER_RE = re.compile(r"^\s*---\s*\n.*?\n---\s*\n", flags=re.DOTALL)

def strip_frontmatter(text: str) -> str:
    return _FRONTMATTER_RE.sub("", text or "", count=1)

def normalize_for_hash(text: str) -> str:
    t = strip_frontmatter(text or "")
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = "\n".join(line.rstrip() for line in t.split("\n"))
    return t.strip()

def content_fingerprint(text: str) -> str:
    norm = normalize_for_hash(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()

# ---------- Safe YAML helpers ----------
def _yaml_quote(s: Optional[str]) -> str:
    """
    Safely quote a string for a simple YAML scalar line using double quotes.
    Escapes backslashes and double quotes. Returns empty string if None.
    """
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')

# ---------- Topic & Filename ----------
def slugify(s: str) -> str:
    s = (s or "general").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "general"

def derive_topic(tab_title: Optional[str], fallback_topic: str, sample_text: str) -> str:
    if tab_title and tab_title.strip().lower() not in {"chatgpt", "new chat"}:
        return tab_title.strip()
    # simple keyword fallback: take a few frequent words
    words = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", sample_text or "")
    if words:
        return " ".join(words[:6])
    return fallback_topic

def next_sequence(chat_logs_dir: str, date_str: str, topic_slug: str) -> str:
    # Finds cp-XX max for today's date+topic and returns next cp-XX
    prefix = f"{date_str}__{topic_slug}__cp-"
    max_n = 0
    if os.path.isdir(chat_logs_dir):
        for name in os.listdir(chat_logs_dir):
            if name.startswith(prefix) and name.endswith(".md"):
                m = re.search(r"__cp-(\d{2})\.md$", name)
                if m:
                    try:
                        n = int(m.group(1))
                        if n > max_n:
                            max_n = n
                    except:
                        pass
    return f"cp-{max_n+1:02d}"

def make_filename(chat_logs_dir: str, date_str: str, topic: str, seq: str) -> str:
    topic_slug = slugify(topic)
    return os.path.join(chat_logs_dir, f"{date_str}__{topic_slug}__{seq}.md")

# ---------- Save & Chunk ----------
def write_bundle_md(out_path: str, content: str, topic: str, phase: float,
                    source_title: Optional[str], source_url: Optional[str],
                    tab_id: Optional[str], seq: str, token_estimate: int) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    source_title_q = _yaml_quote(source_title)
    source_url_q = _yaml_quote(source_url)
    tab_id_q = _yaml_quote(tab_id)

    header = (
        f"---\n"
        f"date: {now_iso}\n"
        f'topic: "{_yaml_quote(topic)}"\n'
        f"phase: {phase}\n"
        f'tags: ["chatlog","autosave","will"]\n'
        f'source_page_title: "{source_title_q}"\n'
        f'source_url: "{source_url_q}"\n'
        f'tab_id: "{tab_id_q}"\n'
        f'bundle_seq: "{seq}"\n'
        f'token_estimate: "~{token_estimate}"\n'
        f"---\n\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(content)

def should_do_daily_snapshot(enabled: bool, time_local: str, last_snapshot_date: Optional[str]) -> bool:
    if not enabled:
        return False
    today = dt.date.today().isoformat()
    if last_snapshot_date == today:
        return False
    # snapshot time check — we only snapshot at or after the configured time
    try:
        hh, mm = map(int, time_local.split(":"))
        now = dt.datetime.now()
        snap_dt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        return now >= snap_dt
    except Exception:
        return False

def split_into_bundles_by_tokens(text: str, limit: int) -> List[Tuple[str, int]]:
    """
    Splits large text into ~limit token bundles.
    Returns list of (bundle_text, token_count).
    Simple approach: split by paragraphs to keep structure.
    """
    paras = re.split(r"\n\s*\n", text or "")
    bundles: List[Tuple[str, int]] = []
    cur: List[str] = []
    cur_tokens = 0
    for p in paras:
        t = count_tokens(p + "\n\n")
        if cur_tokens + t > limit and cur:
            bundle_text = "\n\n".join(cur).strip()
            bundles.append((bundle_text, cur_tokens))
            cur = []
            cur_tokens = 0
        cur.append(p)
        cur_tokens += t
    if cur:
        bundle_text = "\n\n".join(cur).strip()
        bundles.append((bundle_text, cur_tokens))
    if not bundles and (text or "").strip():
        bundles = [(text, count_tokens(text))]
    return bundles

# ---------- Core runners ----------
def one_shot_save(policy: dict, pasted_text: str, title: Optional[str], url: Optional[str], tab_id: Optional[str]) -> None:
    chat_logs_dir = policy["paths"]["chat_logs_dir"]
    phase = policy.get("metadata_defaults", {}).get("phase", REQUIRED_PHASE)
    topic = derive_topic(title, policy["metadata_defaults"]["topic"], pasted_text)
    date_str = dt.date.today().isoformat()

    bundles = split_into_bundles_by_tokens(pasted_text, policy["autosave"]["bundle_token_limit"])
    seq = next_sequence(chat_logs_dir, date_str, slugify(topic))
    saved_files = []

    base_num = int(seq.split("-")[-1])
    for i, (bundle_text, tok) in enumerate(bundles):
        seq_i = f"cp-{base_num + i:02d}"
        out_path = make_filename(chat_logs_dir, date_str, topic, seq_i)
        write_bundle_md(out_path, bundle_text, topic, phase, title, url, tab_id, seq_i, tok)
        saved_files.append(out_path)

    # log & chunk
    log_memory_event("autosave_one_shot_saved", source=__file__, phase=REQUIRED_PHASE, tags=["autosave"])
    log_trace_event("autosave_one_shot_saved", source=__file__, phase=REQUIRED_PHASE, tags=["autosave"],
                    content=f"files={len(saved_files)} topic={topic}")

    if policy["post_save_actions"].get("run_chunker", True):
        run_chunker(policy["paths"]["chunker_input_root"], write_txt=policy["post_save_actions"].get("export_txt_chunks", True))

    print(f"✅ Saved {len(saved_files)} file(s) to {chat_logs_dir} (topic: {topic}).")

def autosave_loop(policy: dict, source_file: str, title: Optional[str], url: Optional[str], tab_id: Optional[str]) -> None:
    chat_logs_dir = policy["paths"]["chat_logs_dir"]
    phase = policy.get("metadata_defaults", {}).get("phase", REQUIRED_PHASE)

    interval_s = max(30, int(policy["autosave"]["interval_minutes"]) * 60)  # floor to 30s
    limit = int(policy["autosave"]["bundle_token_limit"])
    daily_enabled = bool(policy["autosave"]["daily_snapshot"]["enabled"])
    daily_time = str(policy["autosave"]["daily_snapshot"]["time_local"])

    last_fingerprint = None
    last_snapshot_date = None

    print(f"🟢 Autosave running — every {interval_s//60} min or ~{limit} tokens. Source: {source_file}")
    while True:
        try:
            # Read current source content (full snapshot model)
            try:
                with open(source_file, "r", encoding="utf-8") as f:
                    current_text = f.read()
            except FileNotFoundError:
                current_text = ""

            fp = content_fingerprint(current_text)
            token_est = count_tokens(current_text)

            # Decide whether to save
            do_save = False
            reason = ""

            if last_fingerprint is None and current_text.strip():
                do_save = True
                reason = "initial"
            elif fp != last_fingerprint and current_text.strip():
                do_save = True
                reason = "changed"
            elif should_do_daily_snapshot(daily_enabled, daily_time, last_snapshot_date):
                do_save = True
                reason = "daily"

            if do_save:
                topic = derive_topic(title, policy["metadata_defaults"]["topic"], current_text)
                date_str = dt.date.today().isoformat()
                seq = next_sequence(chat_logs_dir, date_str, slugify(topic))

                bundles = split_into_bundles_by_tokens(current_text, limit)
                saved_files = []

                base_num = int(seq.split("-")[-1])
                for i, (bundle_text, tok) in enumerate(bundles):
                    seq_i = f"cp-{base_num + i:02d}"
                    out_path = make_filename(chat_logs_dir, date_str, topic, seq_i)
                    write_bundle_md(out_path, bundle_text, topic, phase, title, url, tab_id, seq_i, tok)
                    saved_files.append(out_path)

                # Trace/memory logs
                log_memory_event("autosave_bundle_saved", source=__file__, phase=REQUIRED_PHASE,
                                 tags=["autosave"], content=f"reason={reason} files={len(saved_files)}")
                log_trace_event("autosave_bundle_saved", source=__file__, phase=REQUIRED_PHASE,
                                tags=["autosave"], content=f"reason={reason} files={len(saved_files)} topic={topic}")

                # Run chunker after save (so DB stays current)
                if policy["post_save_actions"].get("run_chunker", True):
                    run_chunker(policy["paths"]["chunker_input_root"], write_txt=policy["post_save_actions"].get("export_txt_chunks", True))

                last_fingerprint = fp
                last_snapshot_date = dt.date.today().isoformat()

        except KeyboardInterrupt:
            print("⏸ Autosave paused by user.")
            break
        except Exception as e:
            log_trace_event("autosave_error", source=__file__, phase=REQUIRED_PHASE,
                            tags=["autosave","error"], content=str(e))
        finally:
            time.sleep(interval_s)

# ---------- CLI ----------
def run_cli():
    parser = argparse.ArgumentParser(description="Autosave Helper — save chat bundles and trigger chunker (Phase 0.7)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--source-file", help="Path to a text file containing the current chat content (snapshotted each interval).")
    mode.add_argument("--once", action="store_true", help="Save a single bundle from stdin, then exit.")

    parser.add_argument("--policy", default=DEFAULT_POLICY_PATH, help="Path to autosave_policy.json")
    parser.add_argument("--title", default=None, help="Optional tab/page title to use for topic naming")
    parser.add_argument("--url", default=None, help="Optional source URL")
    parser.add_argument("--tab-id", default=None, help="Optional tab identifier")

    args = parser.parse_args()
    policy = load_policy(args.policy)

    # sanity on paths
    os.makedirs(policy["paths"]["chat_logs_dir"], exist_ok=True)

    if args.once:
        print("Paste chat text, then end input (Ctrl+Z+Enter on Windows / Ctrl+D on macOS/Linux):")
        pasted = sys.stdin.read()
        if not pasted.strip():
            print("❌ No input received.")
            return
        one_shot_save(policy, pasted, args.title, args.url, args.tab_id)
        return

    # Autosave mode
    autosave_loop(policy, args.source_file, args.title, args.url, args.tab_id)

if __name__ == "__main__":
    run_cli()
