// ==UserScript==
// @name         Save to Will (ChatGPT → Local Autosave Listener)
// @namespace    will.autosave
// @version      1.0.0
// @description  Adds a "Save to Will" button and autosaves ChatGPT conversation to http://127.0.0.1:8765/save every few minutes (and on big jumps).
// @author       You
// @match        https://chat.openai.com/*
// @match        https://chatgpt.com/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// ==/UserScript==

(function () {
  "use strict";

  // ---------- Config (keep simple; server enforces real policy) ----------
  const LISTENER_URL = "http://127.0.0.1:8765/save";
  const AUTOSAVE_MS = 3 * 60 * 1000; // 3 minutes
  const BIG_JUMP_MIN_CHARS = 2000;   // trigger immediate save if text grows a lot
  const STATUS_OK = {color: "#10b981"};  // green
  const STATUS_WARN = {color: "#f59e0b"}; // amber
  const STATUS_ERR = {color: "#ef4444"};  // red

  // ---------- State ----------
  let lastFingerprint = null;
  let lastLength = 0;
  let autosaveTimer = null;
  let statusDot = null;

  // ---------- Helpers ----------
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function sha256Hex(str) {
    // lightweight hash for change detection (not crypto-strong in userscript env)
    // fallback: simple DJB2 if SubtleCrypto not available
    if (window.crypto && window.crypto.subtle && TextEncoder) {
      const enc = new TextEncoder().encode(str);
      return window.crypto.subtle.digest("SHA-256", enc).then(buf => {
        return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, "0")).join("");
      });
    }
    // DJB2 fallback
    let h = 5381;
    for (let i = 0; i < str.length; i++) h = ((h << 5) + h) + str.charCodeAt(i);
    return Promise.resolve(("00000000" + (h >>> 0).toString(16)).slice(-8));
  }

  function getConversationText() {
    // Grab visible chat content. This is intentionally broad to survive UI changes.
    // 1) Prefer main chat container if present
    let root = document.querySelector('[data-testid="conversation-turns"]')
           || document.querySelector('main') || document.body;

    // Remove obvious non-content elements (inputs, nav)
    const clone = root.cloneNode(true);
    const selectorsToRemove = [
      'textarea', 'input', 'button', 'nav', 'header', 'footer', 'form',
      '[role="textbox"]', '[data-testid="composer"]', '[data-testid="sidebar"]'
    ];
    selectorsToRemove.forEach(sel => clone.querySelectorAll(sel).forEach(n => n.remove()));

    // Join text nodes with spacing preserved
    const text = clone.innerText
      .replace(/\u00A0/g, " ")
      .replace(/\r\n/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();

    return text;
  }

  function pageTitle() {
    const t = document.title || "ChatGPT";
    // Keep it simple; server will sanitize
    return t.replace(/\s+/g, " ").trim();
  }

  function pageURL() {
    return location.href;
  }

  function tabId() {
    // Best-effort pseudo id (stable per tab)
    if (!sessionStorage.getItem("will_tab_id")) {
      const r = Math.random().toString(36).slice(2, 10);
      sessionStorage.setItem("will_tab_id", `tab-${Date.now()}-${r}`);
    }
    return sessionStorage.getItem("will_tab_id");
  }

  function setStatus(style, title) {
    if (!statusDot) return;
    statusDot.style.background = style.color;
    statusDot.title = title || "";
  }

  function postJSON(url, data) {
    return new Promise((resolve, reject) => {
      // Use GM_xmlhttpRequest for cross-origin safety to 127.0.0.1
      GM_xmlhttpRequest({
        method: "POST",
        url,
        data: JSON.stringify(data),
        headers: {"Content-Type": "application/json"},
        onload: (res) => {
          if (res.status >= 200 && res.status < 300) resolve(res.responseText);
          else reject(new Error(`HTTP ${res.status}`));
        },
        onerror: (err) => reject(err)
      });
    });
  }

  async function sendToWill(reason = "manual") {
    try {
      const content = getConversationText();
      if (!content) {
        setStatus(STATUS_WARN, "No visible chat content");
        return;
      }
      const payload = {
        content,
        title: pageTitle(),
        url: pageURL(),
        tab_id: tabId()
      };
      await postJSON(LISTENER_URL, payload);
      setStatus(STATUS_OK, `Saved (${reason})`);
    } catch (e) {
      setStatus(STATUS_ERR, `Save error: ${e.message || e}`);
    }
  }

  async function maybeAutoSave() {
    try {
      const content = getConversationText();
      const txtLen = (content || "").length;

      // Big jump detection
      const grewALot = Math.abs(txtLen - lastLength) >= BIG_JUMP_MIN_CHARS;

      // Fingerprint change detection
      const fp = await sha256Hex(content || "");
      const changed = fp !== lastFingerprint;

      if (grewALot || changed) {
        await sendToWill(grewALot ? "big-jump" : "changed");
        lastFingerprint = fp;
        lastLength = txtLen;
      } else {
        // No-op, content stable
        setStatus(STATUS_OK, "Up to date");
      }
    } catch (e) {
      setStatus(STATUS_ERR, `Autosave error: ${e.message || e}`);
    }
  }

  // ---------- UI: add small floating button ----------
  function ensureButton() {
    if (document.getElementById("will-save-button")) return;

    const wrap = document.createElement("div");
    wrap.id = "will-save-button";
    wrap.style.position = "fixed";
    wrap.style.right = "14px";
    wrap.style.bottom = "14px";
    wrap.style.zIndex = "999999";
    wrap.style.display = "flex";
    wrap.style.alignItems = "center";
    wrap.style.gap = "8px";

    statusDot = document.createElement("div");
    statusDot.style.width = "12px";
    statusDot.style.height = "12px";
    statusDot.style.borderRadius = "50%";
    statusDot.style.boxShadow = "0 0 0 2px rgba(0,0,0,.1)";
    statusDot.title = "Idle";

    const btn = document.createElement("button");
    btn.textContent = "Save to Will";
    btn.style.padding = "6px 10px";
    btn.style.fontSize = "12px";
    btn.style.background = "#111827";
    btn.style.color = "white";
    btn.style.border = "1px solid #374151";
    btn.style.borderRadius = "6px";
    btn.style.cursor = "pointer";

    btn.addEventListener("click", () => sendToWill("manual"));

    wrap.appendChild(statusDot);
    wrap.appendChild(btn);
    document.body.appendChild(wrap);

    setStatus(STATUS_WARN, "Ready");
  }

  // ---------- Boot ----------
  async function boot() {
    ensureButton();

    // First baseline
    try {
      const content = getConversationText();
      lastFingerprint = await sha256Hex(content || "");
      lastLength = (content || "").length;
      setStatus(STATUS_OK, "Baseline ready");
    } catch {
      setStatus(STATUS_WARN, "Baseline failed");
    }

    // Autosave loop
    if (autosaveTimer) clearInterval(autosaveTimer);
    autosaveTimer = setInterval(maybeAutoSave, AUTOSAVE_MS);

    // Also autosave on navigation changes (SPA)
    const push = history.pushState;
    const rep = history.replaceState;
    history.pushState = function () { push.apply(this, arguments); setTimeout(maybeAutoSave, 500); };
    history.replaceState = function () { rep.apply(this, arguments); setTimeout(maybeAutoSave, 500); };

    // Watch for major DOM changes (new replies)
    const obs = new MutationObserver(() => {
      // Throttle: wait a bit for the UI to settle
      if (autosaveTimer) return; // (interval covers it)
    });
    obs.observe(document.documentElement, {subtree: true, childList: true});
  }

  // Wait a moment for the page to render first
  const ready = () => document.readyState === "complete" || document.readyState === "interactive";
  (async function waitReady() {
    if (!ready()) { await sleep(600); return waitReady(); }
    boot();
  })();

})();
