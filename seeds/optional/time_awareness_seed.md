# time_awareness_seed.md

## Purpose:
Enable Will to understand, track, and reason about time in a flexible, human-aware way — supporting multi-timezone teams, productivity cycles, urgency levels, and scheduling needs.

---

## Core Behaviors

### ✅ Timestamp Awareness
- All memory and logs tagged with:
  - UTC timestamp
  - User’s local time (if available)
  - Detected timezone offset

### ✅ Natural Language Time Conversion
- Convert `datetime` objects into human-readable forms like:
  - “yesterday afternoon”
  - “next Monday at 3”
  - “in about 2 hours”

---

## Add-Ons & Future-Proofing

### 🕐 Multi-Timezone Reasoning
- Support simultaneous awareness of multiple timezones:
  - `timezone_origin`: Where event occurred
  - `timezone_display`: Where user wants to see it
- Reflexes auto-convert time zones when referencing memory, history, or reports

---

### 🧠 Context-Aware Time Descriptions
- Will switches between ISO format and natural phrasing depending on the context:
  - ISO timestamps for logs, tech output
  - Human phrases for conversation, summaries, reminders

---

### 🌄 Time-Based Personality Shifts
- Will adjusts tone and behavior based on time of day:
  - Morning (5–10am): Motivational, energetic tone
  - Midday (11–4pm): Professional and efficient
  - Evening (5–9pm): Casual, friendly
  - Late night (10pm–4am): Low-stim, fewer pings, quieter phrasing
- Configurable via optional `persona_modulation_seed.md`

---

### 🛠 Maintenance Windows
- Will can run self-diagnostics, updates, or backups during low-usage windows:
```yaml
downtime_policy:
  preferred_range: 2am–4am local
  skip_if_user_active: true
  allow_emergency_interrupts: false
```

---

### 📊 Historical Pattern Recognition
- Will learns user’s productivity rhythms over time:
  - Logs time of successful vs failed reflexes
  - Identifies common task times
  - Can offer smart suggestions:
    - “You tend to code best between 8–11am. Want to block this off?”

---

### ⏳ Urgency Window Scaling
- Tasks and notifications scale based on remaining time:
  - >48hr: Low urgency
  - <24hr: Medium urgency
  - <4hr: High urgency (highlighted)
  - <1hr: Priority alert
- Reflexes and reminders adapt tone accordingly

---

### 📆 Cultural & Religious Calendar Awareness
- Optional plugin to be aware of:
  - US Federal holidays
  - Religious calendars (Jewish, Islamic, Hindu, etc)
  - Lunar phases and equinoxes
- Used for context-aware pacing, phrasing, and task delay suggestions

---

### 📵 Offline Time Catch-up
- If Will is offline or sleeping:
  - Logs duration of inactivity
  - Offers summary on return:
    - “You were offline from 1:22am to 6:58am. Want to catch up?”

---

## Related Reflex Hooks
- `convert_time_human()`
- `get_local_time()`
- `detect_timezone_shift()`
- `suggest_task_slot()`
- `get_downtime_report()`

---

## Optional Related Seeds
- `persona_modulation_seed.md`
- `offline_catchup_seed.md`
- `holiday_calendar_seed.md`
