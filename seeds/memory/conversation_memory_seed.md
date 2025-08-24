📄 conversation_memory_seed.md
Purpose:
This file defines how Will stores, recalls, and manages conversations with the user (and others, if expanded to teams). It ensures long-term memory integrity, context-sensitive recall, and zero data loss.

🧠 Core Policies
1. Permanent Storage
Will never deletes conversation data.
Instead, old conversations are:

🔹 Archived (if not accessed in a while)

🔸 Tagged as dormant (low-priority but retrievable)

🔒 Locked (e.g. finalized strategies, sensitive content)

2. Timestamps & Versioning
Every conversation is timestamped.

When content is updated (e.g. a changed plan), Will stores both the original and the new version:

Tagged with metadata like version_1, superseded_by, deprecated, etc.

3. Recall Prioritization
Will prioritizes user queries first. If you ask something directly, it surfaces relevant past chats fast.

Background routines (e.g. indexing or cleanup) never interfere with live conversation memory.

4. Context-Sensitive Recall
If your tone or urgency shifts (e.g. frustration, creative brainstorming), Will adjusts what memory to surface:

Urgent = short, actionable, relevant facts

Creative = broader references, “what ifs,” idea threads

🧩 Advanced Features (In Place or Planned)
✅ Thread Archiving System
Threads are automatically flagged as:

Active

Dormant (not used in 60+ days)

Long-term reference (locked)

You can always reactivate anything archived.

✅ Memory “Lenses” (Planned UI Feature)
Will’s GUI will support filtering memory by:

Project / topic

Tags (e.g. #blocked, #phase_2, #marketing)

Emotional tone

Date ranges

✅ Multi-User Threading (Future Expansion)
Each memory entry supports an optional speaker field to distinguish between multiple users in team environments.

⚠️ Failure Handling
If a conversation log fails to save:

Will retries once.

If it still fails, it:

Moves the convo to a quarantine_memory table.

Logs an alert.

Notifies you based on your preferred system (e.g. GUI badge or log entry).