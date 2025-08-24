# webhook_rules_seed.md

## Purpose
Defines the protocols, safety rules, and configuration logic Will uses when receiving or sending webhooks. These rules ensure webhook-based automation is secure, predictable, and easy to expand.

---

## Core Principles

- **Minimal Latency**: Webhooks should be processed immediately upon receipt.
- **Secure by Default**:
  - Use HTTPS only
  - Verify known sources (via shared secret, IP allowlist, or token)
  - Sanitize all payload data before internal use
- **Event-Driven**: All webhooks must map to a valid `event_type`, used to trigger a reflex or system routine.
- **Fail Gracefully**:
  - Log failures with timestamp + reason
  - Retry certain types (max 3 times)
  - Quarantine malformed payloads

---

## Accepted Webhook Methods

- `POST` — required for all inbound events.
- `GET` — never accepted (auto-reject unless explicitly whitelisted).
- `PUT`, `DELETE` — reserved for future API endpoints, not webhook triggers.

---

## Trigger Routing Logic

- Each webhook payload must include:
  - `"event_type"` — maps to a reflex
  - `"source"` — trusted sender ID (if enforced)
  - `"data"` — the actual payload content

- Will maps:
  ```json
  {
    "event_type": "client.new_signup",
    "source": "typeform",
    "data": { ... }
  }
  ```
  to:
  `reflex(client_onboarding_handler).trigger(data)`

---

## Safety Rules

- **Max Payload Size**: 1MB (auto-quarantine if exceeded)
- **Rate Limit**: No more than 5 requests/sec per source
- **Blocked Words Check**: Scan for injection attempts (SQL, shell, etc)
- **Header Authentication**: If present, validate `x-will-token` or `x-will-signature`

---

## Reflex Autoresponse Rules

- If `event_type` has an autoresponder, Will replies with:
  - `200 OK` + `{"acknowledged": true}` immediately
  - Executes reflex after acknowledgement
- If no matching reflex:
  - Return `400 Bad Request` with explanation
  - Log and store in `unknown_webhooks` quarantine bucket

---

## Reflex Examples

- `client.new_signup` → runs onboarding checklist
- `job.failed` → runs diagnostics or alert
- `system.ping` → returns status report
- `client.feedback.submitted` → triggers logging + feedback reflex

---

## Quarantine Protocol

- Invalid or suspicious payloads are stored in `/quarantine/webhooks/YYYY-MM-DD/`
- Auto-tagged with:
  - Reason for quarantine
  - Source IP
  - Time of attempt
- Quarantine review tool: `will audit webhooks`

---

## Expansion Notes

- Future reflex: `will webhook subscribe <event> --to <url>`
  - Enables outbound webhooks from Will
  - Can notify Slack, Notion, email, etc.

- Optional webhook dashboard to track traffic, failures, and source stats

---

## CLI Commands

- `will webhook list` – List registered event_type handlers
- `will webhook test <event>` – Simulate payload receipt for testing
- `will webhook quarantine review` – View blocked payloads
- `will webhook cleanup` – Purge old quarantined payloads

---

## Final Notes

- All webhook reflexes must be idempotent (safe to retry).
- Payloads should be archived to support long-term traceability.
- Any webhook-triggered reflex must be auditable by timestamp + source.

