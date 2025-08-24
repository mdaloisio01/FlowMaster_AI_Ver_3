# proxy_rules_seed.md

## Purpose:
Define how and when Will uses proxy servers to route outbound requests, for stealth, speed, geo-matching, or bypassing blocks.

---

## 🔐 Security & Redundancy Enhancements

### Token Rotation Strategy
- Rotate API/proxy tokens based on:
  - Scheduled interval (e.g., every 24h)
  - After detected throttling
  - After authentication failures

### Encrypted Proxy Credential Storage
- Store login credentials securely using:
  - `.env` variables (default)
  - Keyring/Vault/KMS (optional override)
  - File-based fallback (encrypted)

### Fallback Tiers
- Tier 1: Premium proxies
- Tier 2: Shared pool
- Tier 3: Tor/VPN or rotating public IP
- Will escalates to next tier after 2 failed attempts

---

## 🧠 Smart Proxy Management

### Geo-Aware Proxy Matching
- Assign proxies by:
  - Target URL region
  - Use case (e.g., image scraping vs API calling)

### Proxy Feedback Loop
- Will logs every proxy use and scores it on:
  - Latency
  - Ban frequency
  - Success rate
- Low-score proxies flagged or removed

### AI Tagging System
- Automatically tags proxies by:
  - Domain scraped
  - Request size/type
  - Ban pattern
  - Performance consistency

---

## 🧩 Scalable Architecture

### Proxy Load Balancer Reflex
- Load balances across best-available proxies by:
  - Region
  - Latency
  - Health score

### Proxy Usage Ledger
- Will logs:
  - Proxy ID
  - Use timestamp
  - Target domain
  - Reflex/tool that used it
  - Outcome (success/failure)
  - Latency
  - Retry attempts

### Client-Specific Proxy Profiles
```yaml
proxies:
  - client: 'IronRoot'
    use_pool: 'fast-stealth'
  - client: 'Roaming Raven'
    use_pool: 'global-anon'
```

---

## 🧪 Testing & Simulation Mode

### Proxy Failure Sandbox
- `simulate_proxy_failures: true`
- Use test cases like:
  - `"Instagram timeout loop"`
  - `"DNS resolution error"`

---

## 🧰 CLI Command Map
```bash
will list proxies --filter=latency:<150
will test proxies --region=eu-west
will reload proxies --from=config.json
```

---

## 📊 GUI Dashboard Integration (Optional)
- Active proxy visual
- Live latency sparkline
- Health meter (per pool)
- Alert if top proxies fail 3x in a row

---

## 🔁 Routing Rules

### Domains that always require proxies
- Instagram, LinkedIn, Facebook, TikTok, Craigslist
- Any .cn, .ru, .ir TLDs

### Reflexes allowed to proxy
- web_scraper
- image_scraper
- api_harvester
- lead_gen_tool

### Anon Mode Toggle
- `anon_mode: true` forces proxy for **all** outbound traffic
- Used for stealth tasks or client privacy filters

---

## 🔄 Auto-Refresh & Quarantine
- Will attempts automatic reconnection or switches proxy on:
  - 429 rate limits
  - 403 forbidden
  - Socket timeouts
- Repeated failures trigger quarantine of the failing proxy ID

---

## 🧭 Futureproof Tags
- Proxy metadata includes:
  - `region`, `use_case`, `source`, `cost`, `auth_type`, `ban_count`, `rating`
- New proxies auto-tagged based on benchmark run

