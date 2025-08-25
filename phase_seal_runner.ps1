# phase_seal_runner.ps1
# IronRoot END/SEAL runner (phase-agnostic)
# - Runs pre-seal audits
# - Appends build/phase logs
# - Commits, tags, archives
# - Invokes phase-specific sealer if present (e.g., tools/phase_0_6_sealer.py)
# Usage:
#   Open PowerShell in repo root, then:
#     powershell -NoProfile -ExecutionPolicy Bypass -NoExit -File .\phase_seal_runner.ps1
# Notes:
#   - Keeps window open at the end (success or failure).
#   - Fails closed with IRONROOT VIOLATION messages.

$ErrorActionPreference = 'Stop'

function Pause-End([string]$msg = "Done. Press Enter to close...") {
  try { Read-Host $msg | Out-Null } catch {}
}

function Fail($reason, $path=".") {
  Write-Host "🚨 IRONROOT VIOLATION — $reason. Path/Artifact: $path. Build cannot proceed."
  Pause-End
  exit 1
}

function RunPyMod([string]$mod, [string[]]$args = @()) {
  & py -m $mod @args
  if ($LASTEXITCODE -ne 0) { Fail "py -m $mod failed (exit=$LASTEXITCODE)" $mod }
  return $true
}

function RunPyModCapture([string]$mod, [string[]]$args = @()) {
  $out = & py -m $mod @args 2>&1
  if ($LASTEXITCODE -ne 0) { Fail "py -m $mod failed (exit=$LASTEXITCODE)" $mod }
  return $out
}

# 0) Guard: required single sources of truth must exist
$required = @(
  "configs/dev_file_list.md",
  "configs/ironroot_manifest_data.json",
  "configs/ironroot_file_history_with_dependencies.json",
  "core/phase_control.py"
)
foreach ($p in $required) {
  if (!(Test-Path $p)) { Fail "Required file missing" $p }
}

# Detect current phase via IronRoot (phase_control)
$phase = (& py -c "from boot.boot_path_initializer import inject_paths; inject_paths(); from core.phase_control import get_current_phase; print(get_current_phase())").Trim()
if (-not $phase) { Fail "Could not detect current phase from manifest" "core/phase_control.py" }
$phase_u = ($phase -replace '\.','_')

Write-Host "=== PRE-SEAL AUDIT (Phase $phase) ==="

# 1) DB bootstrap + table sanity
RunPyMod core.sqlite_bootstrap
$tbl = RunPyModCapture tools.check_db_tables
if ($tbl -notmatch 'boot_events' -or $tbl -notmatch 'manifest' -or $tbl -notmatch 'memory_events' -or $tbl -notmatch 'reflex_registry' -or $tbl -notmatch 'trace_events') {
  Fail "DB tables missing or unexpected" "tools/check_db_tables.py"
}
Write-Host "• DB tables present: boot_events, manifest, memory_events, reflex_registry, trace_events"

# 2) Registry drift (dev list ↔ manifest ↔ history)
$aud = RunPyModCapture tools.manifest_history_auditor
if ($aud -notmatch 'manifest missing: none' -or $aud -notmatch 'history missing: none' -or $aud -notmatch 'dev_file_list missing: none') {
  Fail "Registry drift detected" "tools/manifest_history_auditor.py"
}
Write-Host "• Dev list ↔ manifest ↔ history drift = 0"

# 3) Compliance guard (AST)
$comp = RunPyModCapture tools.reflex_compliance_guard
if ($comp -notmatch 'issues=0') {
  Fail "Compliance issues present" "tools/reflex_compliance_guard.py"
}
Write-Host "• Compliance guard (AST): issues=0 (future-skips allowed)"

# 4) Seeds gating check
if (!(Test-Path "root/first_boot.lock")) {
  Fail "Seeds gate missing" "root/first_boot.lock"
}
Write-Host "• Seeds gating respected (root/first_boot.lock)"

# 5) Snapshot trace/memory ping (fresh dual logs)
RunPyMod tools.trace_memory_snapshot @("--snapshot-mode","light")
$xc = RunPyModCapture tools.trace_memory_crosscheck
if ($xc -notmatch 'OK — memory and trace snapshot events are aligned') {
  Fail "Trace↔Memory crosscheck failed" "tools/trace_memory_crosscheck.py"
}
Write-Host "• Snapshot & cross-check OK (dual-logging observed)"

# 6) Tests — auto-discover & run (tests/test_phase_*.py)
$testMods = Get-ChildItem tests -Filter "test_phase_*.py" -File | Sort-Object Name | ForEach-Object {
  $_.FullName.Replace('\','/') -replace '^.*/','' -replace '\.py$',''
} | ForEach-Object { "tests.$_" }

$passed = @()
foreach($m in $testMods) {
  & py -m $m
  if ($LASTEXITCODE -ne 0) { Fail "Test failed" $m }
  $passed += $m
}
Write-Host ("• Tests pass: " + ($(if($passed.Count){ $passed -join ', ' } else { "(none found)" })))

# 7) Recent logs visibility (human check)
RunPyMod tools.trace_inspector @("--tag","snapshot")
RunPyMod tools.trace_inspector @("--tag","audit")
RunPyMod tools.trace_inspector @("--tag","manifest")

Write-Host ""
Write-Host "PRE-SEAL — Full System Audit for Phase $phase"
Write-Host "• Dev list ↔ manifest ↔ history drift = 0"
Write-Host "• Compliance guard (AST): issues=0 (future-skips allowed)"
Write-Host "• DB tables present: boot_events, manifest, memory_events, reflex_registry, trace_events"
Write-Host "• Seeds gating respected (root/first_boot.lock)"
Write-Host "• Snapshot & cross-check OK (dual-logging observed)"
Write-Host ("• Tests pass: " + ($(if($passed.Count){ $passed -join ', ' } else { "(none found)" })))
Write-Host ""
Write-Host "=== ALL CHECKS GREEN — sealing Phase $phase ==="

# Append seal entries to build logs (build_log.json + phase_history.json)
& py -c "from boot.boot_path_initializer import inject_paths; inject_paths(); import json, datetime, pathlib; ts=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'); b=pathlib.Path('configs/build_log.json'); d={'updated_at': ts, 'entries': []}; (d.update(json.loads(b.read_text(encoding='utf-8'))) if b.exists() else None); d.setdefault('entries', []).append({'phase':'$phase','ts': ts}); b.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8'); h=pathlib.Path('configs/phase_history.json'); ph={'updated_at': ts, 'history': []}; (ph.update(json.loads(h.read_text(encoding='utf-8'))) if h.exists() else None); ph.setdefault('history', []).append({'phase':'$phase','ts': ts}); h.write_text(json.dumps(ph, ensure_ascii=False, indent=2), encoding='utf-8')"
if ($LASTEXITCODE -ne 0) { Fail "Failed to append seal logs" "configs/build_log.json" }

# Commit the log updates (allow no-op re-seals)
git add configs/build_log.json configs/phase_history.json | Out-Null
$commitOut = (git commit -m "Seal Phase $phase" 2>&1)
if ($LASTEXITCODE -ne 0) {
  Write-Host "[info] commit skipped or failed (possibly no changes): $commitOut"
} else {
  Write-Host "[git] $commitOut"
}

# Optional: tag + archive (best-effort; do not fail if already exists)
$tagName = "phase-$phase-sealed"
$tagOut = (git tag $tagName 2>&1)
if ($LASTEXITCODE -ne 0) {
  Write-Host "[info] tag '$tagName' could not be created: $tagOut"
} else {
  Write-Host "[git] tag $tagName created"
}

$zipName = ("FlowMaster_AI_Ver_3_phase_{0}_SEALED.zip" -f $phase_u)
try {
  if (Test-Path $zipName) { Remove-Item -Force $zipName }
  Compress-Archive -Path * -DestinationPath $zipName -Force
  Write-Host "[archive] $zipName created"
} catch {
  Write-Host "[info] archive step skipped/failed: $($_.Exception.Message)"
}

# Phase-specific sealer (if present): tools/phase_<phase>_sealer.py
$sealerPath = "tools/phase_{0}_sealer.py" -f $phase_u
if (Test-Path $sealerPath) {
  $sealerMod = "tools.phase_{0}_sealer" -f $phase_u
  Write-Host "[sealer] Running $sealerMod --dry-run"
  & py -m $sealerMod --dry-run
  if ($LASTEXITCODE -ne 0) { Fail "Sealer dry-run failed" $sealerPath }
  Write-Host "[sealer] Running $sealerMod"
  & py -m $sealerMod
  if ($LASTEXITCODE -ne 0) { Fail "Sealer execution failed" $sealerPath }
} else {
  Write-Host "(No sealer module found for $phase; bump manifest using your standard sealer procedure.)"
}

Write-Host ("✅ Phase {0} sealed. Artifacts: configs/build_log.json, configs/phase_history.json, tag phase-{0}-sealed, archive FlowMaster_AI_Ver_3_phase_{1}_SEALED.zip" -f $phase, $phase_u)

Pause-End
