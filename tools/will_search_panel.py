
# /tools/will_search_panel.py
"""
Will Search Panel — Phase 0.7 (IronSpine)
Local, offline search over chunk_store.db (project root).

Update:
- Path filter now matches BOTH forward- and back-slash styles automatically.
"""

from boot.boot_path_initializer import inject_paths
inject_paths()

import os, sqlite3, json
from datetime import datetime
import webview

from core.phase_control import ensure_phase, get_current_phase
from core.memory_interface import log_memory_event
from core.trace_logger import log_trace_event

REQUIRED_PHASE = 0.7
ensure_phase(REQUIRED_PHASE)

# ── Project-root DB path (NOT sandbox) ─────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DB_PATH = os.path.join(PROJECT_ROOT, "chunk_store.db")

_HTML = r"""<!doctype html><html><head><meta charset="utf-8"/>
<title>Will Search</title>
<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' data:;">
<style>
  html,body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0}
  header{padding:12px 16px;border-bottom:1px solid #ddd;display:flex;gap:12px;align-items:center}
  header h1{font-size:16px;margin:0}.pill{font-size:12px;background:#f5f5f5;padding:4px 8px;border-radius:999px;border:1px solid #ddd;color:#444}
  main{padding:16px}form{display:grid;grid-template-columns:1fr 160px 160px 1fr 120px;gap:8px;align-items:end}
  label{font-size:12px;color:#444;margin-bottom:4px;display:block}
  input[type=text],input[type=date]{padding:8px;border:1px solid #ccc;border-radius:6px;width:100%}
  button{padding:8px 12px;border:1px solid #0a66c2;background:#0a66c2;color:#fff;border-radius:6px;cursor:pointer}
  button:disabled{opacity:.6;cursor:not-allowed}.results{margin-top:16px;display:flex;flex-direction:column;gap:12px}
  .card{border:1px solid #e5e5e5;border-radius:8px;padding:12px}.meta{font-size:12px;color:#666;display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px}
  .meta .tag{background:#eef6ff;color:#084c9e;border:1px solid #cfe4ff;padding:2px 6px;border-radius:999px}
  .path{font-family:Consolas,Menlo,monospace;font-size:12px;color:#333;overflow:auto}
  .preview{margin-top:8px;white-space:pre-wrap;background:#fafafa;border:1px solid #eee;border-radius:6px;padding:8px;max-height:240px;overflow:auto}
  .row{display:flex;gap:8px}.row button.secondary{background:#fff;color:#0a66c2;border:1px solid #0a66c2}
  .empty{color:#777;font-size:13px;margin-top:12px}
</style></head><body>
<header><h1>Will Search</h1><span class="pill">Local · Offline · Phase 0.7</span></header>
<main>
<form onsubmit="doSearch(event)">
  <div><label>Keywords (space = AND, "quoted phrase")</label><input id="q" type="text" placeholder='e.g. autosave "chunk hash"'/></div>
  <div><label>From date</label><input id="from" type="date"/></div>
  <div><label>To date</label><input id="to" type="date"/></div>
  <div><label>Path contains (optional)</label><input id="path" type="text" placeholder="chat_logs or tools/chunker"/></div>
  <div><button id="btn" type="submit">Search</button></div>
</form>
<div id="out" class="results"></div>
</main>
<script>
function esc(s){return (s||'').replace(/[&<>"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function doSearch(e){e.preventDefault();const b=document.getElementById('btn');b.disabled=true;
 const q=document.getElementById('q').value||'',f=document.getElementById('from').value||'',
 t=document.getElementById('to').value||'',p=document.getElementById('path').value||'';
 try{const res=await window.pywebview.api.search(q,f,t,p);render(res)}catch(e){render({error:String(e)})}finally{b.disabled=false}}
function copyText(t){navigator.clipboard.writeText(t||'').catch(()=>{})}
function render(res){const out=document.getElementById('out');out.innerHTML='';
 if(res&&res.error){out.innerHTML=`<div class="empty">⚠️ ${esc(res.error)}</div>`;return}
 if(!res||!res.rows||res.rows.length===0){out.innerHTML=`<div class="empty">No matches.</div>`;return}
 for(const r of res.rows){const d=document.createElement('div');d.className='card';
 d.innerHTML=`<div class="meta"><span class="tag">file_chunks</span><span class="tag">chunk ${r.chunk_index}</span>
 <span class="tag">${r.token_count} tokens</span><span class="tag">${r.created_at||''}</span></div>
 <div class="path">${esc(r.file_path||'')}</div>
 <div class="row" style="margin-top:6px;"><button class="secondary" onclick="copyText(${JSON.stringify(r.chunk_text||'')})">Copy chunk text</button>
 <button class="secondary" onclick="copyText(${JSON.stringify(r.file_path||'')})">Copy file path</button></div>
 <div class="preview">${esc(r.preview||'')}</div>`;out.appendChild(d)}}
</script></body></html>
"""

def _parse_keywords(q: str):
    import shlex
    terms = [t.strip() for t in shlex.split(q or "") if t.strip()]
    return [f"%{t.replace('%','%%')}%" for t in terms]

def _date_sql(d: str):
    try:
        if not d: return None
        datetime.strptime(d, "%Y-%m-%d")
        return d
    except Exception:
        return None

def _preview(txt: str, limit: int = 360):
    txt = (txt or "").strip().replace("\r\n","\n")
    return txt if len(txt) <= limit else txt[:limit] + " …"

def _path_like_variants(path_part: str):
    """
    Return LIKE patterns that match both slash styles.
    'tools/chunker' -> ['%tools/chunker%', '%tools\\chunker%']
    'tools\\chunker' -> ['%tools\\chunker%', '%tools/chunker%']
    """
    if not path_part:
        return []
    a = path_part.replace('%', '%%')
    b = a.replace('\\', '/')
    c = a.replace('/', '\\')
    # de-dup while preserving order
    seen, out = set(), []
    for pat in (b, c, a):
        if pat not in seen:
            out.append(f"%{pat}%")
            seen.add(pat)
    return out

class Api:
    def search(self, q: str, from_date: str, to_date: str, path_part: str):
        log_trace_event("will_search_query", source=__file__, phase=REQUIRED_PHASE,
                        tags=["will_search"], content=json.dumps({"q": q, "from": from_date, "to": to_date, "path": path_part}))
        log_memory_event("will_search_query", source=__file__, phase=REQUIRED_PHASE, tags=["will_search"])

        if not os.path.exists(DB_PATH):
            return {"error": f"DB not found at {DB_PATH}"}

        likes = _parse_keywords(q)
        date_from = _date_sql(from_date)
        date_to = _date_sql(to_date)
        path_likes = _path_like_variants(path_part)

        where, params = [], []
        for like in likes:
            where.append("(chunk_text LIKE ? OR ifnull(summary,'') LIKE ?)")
            params.extend([like, like])

        if path_likes:
            # (file_path LIKE ? OR file_path LIKE ? ...)
            sub = " OR ".join(["file_path LIKE ?"] * len(path_likes))
            where.append(f"({sub})")
            params.extend(path_likes)

        if date_from:
            where.append("date(created_at) >= date(?)"); params.append(date_from)
        if date_to:
            where.append("date(created_at) <= date(?)"); params.append(date_to)

        where_sql = " AND ".join(where) if where else "1=1"
        sql = f"""SELECT file_path, chunk_index, token_count, created_at, chunk_text
                  FROM file_chunks
                  WHERE {where_sql}
                  ORDER BY created_at DESC, file_path ASC, chunk_index ASC
                  LIMIT 200;"""
        try:
            con = sqlite3.connect(DB_PATH); con.row_factory = sqlite3.Row
            cur = con.cursor(); cur.execute(sql, params)
            rows = [{"file_path": r["file_path"], "chunk_index": r["chunk_index"],
                     "token_count": r["token_count"], "created_at": r["created_at"],
                     "chunk_text": r["chunk_text"], "preview": _preview(r["chunk_text"])}
                    for r in cur.fetchall()]
            con.close()
            return {"rows": rows}
        except Exception as e:
            return {"error": str(e)}

def run():
    cur = get_current_phase()
    log_memory_event("will_search_start", source=__file__, phase=REQUIRED_PHASE,
                     tags=["will_search"], content=f"current_phase={cur}")
    log_trace_event("will_search_start", source=__file__, phase=REQUIRED_PHASE,
                    tags=["will_search"], content=f"db={DB_PATH}")
    window = webview.create_window(
        title=f"Will Search (Phase {REQUIRED_PHASE})",
        html=_HTML, width=980, height=780, resizable=True, js_api=Api()
    )
    webview.start(debug=False)

def run_cli():
    run()

if __name__ == "__main__":
    run_cli()
