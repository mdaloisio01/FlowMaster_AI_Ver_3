\# 🤖 Dev Bot Operating Instructions — Phase 0 Only



\*\*Enforced By:\*\* IronRoot Law v1.0

\*\*Scope:\*\* Phase 0 — `IronSpine\\\_0r`

\*\*System:\*\* Will.1 (FlowMaster\_AI\_Ver\_3)

\*\*Governing File:\*\* dev\_bot\_bootstrap.md



---



\## 🧷 IronRoot Enforcement — Phase 0 Lock



All actions by dev bots must enforce:



\- 🔐 Phase 0 execution only — no file may declare or assume a later phase

\- 📜 Phase must be `0` in `ironroot\\\_manifest\\\_data.json`

\- 🧠 All memory logs must route through `memory\\\_interface.py`

\- 🔍 All reflexes/tools must log to `will\\\_memory\\\_log.json`

\- ✅ Every file must be testable via CLI



---



\## ✅ Output Rules



\- 🔒 \*\*Full file replacements only\*\*

\- 📂 Must include full file path in output

\- 📦 Always return files in alpha order within folders

\- 🧱 No patch instructions — output the whole file or folder

\- 🛑 If any file is missing, unsafe, unlisted, or ghosted:

  \*\*STOP AND RETURN AN IRONROOT VIOLATION\*\*



---



\## 🛠 Required Phase 0 Files



These must be present before declaring Phase 0 complete:



\- `/configs/dev\\\_bot\\\_bootstrap.md`

\- `/configs/dev\\\_bot\\\_instructions.md`

\- `/configs/ironroot\\\_manifest\\\_data.json`

\- `/configs/ironroot\\\_file\\\_history\\\_with\\\_dependencies.json`

\- `/core/memory\\\_interface.py`

\- `/core/memory/will\\\_memory\\\_engine.py`

\- `/reflexes/reflex\\\_core/reflex\\\_self\\\_test\\\_runner.py`

\- `/tools/system\\\_check.py`

\- `/sandbox/sandbox\\\_reflex\\\_tests.py`

\- `/logs/boot\\\_trace\\\_log.json`

\- `/logs/reflex\\\_trace\\\_log.json`

\- `/tests/test\\\_phase\\\_0\\\_integrity.py`



---



\## 🚫 DO NOT ALLOW



| Violation | Block |

|----------|-------|

| Phase drift | ❌ Reject any file referencing Phase > 0 |

| Ghost files | ❌ File must exist in manifest and history |

| Partial output | ❌ No inline code, only full file drops |

| JSON fallback | ❌ All logs must use `will\\\_data.db` if declared |

| Reflex bypass | ❌ Must use `log\\\_memory\\\_event()` wrapper |

| GUI execution | ❌ CLI test required before GUI trace |



---



\## 🧪 Minimum Exit Criteria



| Test | Must Pass |

|------|-----------|

| `test\\\_phase\\\_0\\\_integrity.py` | ✅ CLI + Reflex boot |

| `reflex\\\_self\\\_test\\\_runner.py` | ✅ Log memory, enforce phase |

| `/tools/system\\\_check.py` | ✅ Import and manifest test |

| All required files listed above | ✅ Must be physically present |



---



\## 🧠 Behavior Enforcement Loop



```python

from boot.boot\\\_phase\\\_loader import get\\\_current\\\_phase

if get\\\_current\\\_phase() < 0:

\&nbsp;   raise RuntimeError("Phase lock error: Below required phase 0")



And:





from core.memory\\\_interface import log\\\_memory\\\_event

log\\\_memory\\\_event("reflex\\\_self\\\_test triggered", source="reflex\\\_self\\\_test\\\_runner.py")

📤 Final Notes

Phase 0 is the foundational hard spine of Will



If a file fails any IronRoot condition, DO NOT PROCEED



All reflexes and tools must be phase-aware, testable, and memory-traced



When Phase 0 passes all CLI and memory validation, mark it sealed in:



phase\\\_history.json



build\\\_log.json



Only then can Phase 1 (MemorySpine\\\_1) begin.




