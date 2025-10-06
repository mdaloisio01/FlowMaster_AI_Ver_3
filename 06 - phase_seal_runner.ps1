
param(
    [Parameter(Mandatory=$true)]
    [double] $Phase,

    [string] $Version = $null,
    [string] $Note    = $null
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- repo root (folder containing this script) ---
$ScriptPath = $MyInvocation.MyCommand.Path
$Root       = Split-Path -Parent $ScriptPath
Set-Location $Root

# --- paths (use *Path names to avoid case-insensitive collisions) ---
$ManifestPath = Join-Path $Root 'configs\ironroot_manifest_data.json'
$HistoryPath  = Join-Path $Root 'phase_history.json'
$LogsDirPath  = Join-Path $Root 'logs'
$TraceLogPath = Join-Path $LogsDirPath 'reflex_trace_log.jsonl'
$GuardLogPath = Join-Path $LogsDirPath 'phase_guard_log.jsonl'

# --- helpers ---
function NowIso {
    # ISO-8601 UTC, e.g. 2025-10-03T22:45:00Z
    (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Ensure-Dir([string]$FilePath) {
    $dir = Split-Path -Parent $FilePath
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}

function Read-Json([string]$FilePath) {
    if (Test-Path $FilePath) {
        Get-Content $FilePath -Raw -Encoding UTF8 | ConvertFrom-Json
    } else {
        $null
    }
}

function Write-Json([string]$FilePath, $Object) {
    Ensure-Dir -FilePath $FilePath
    $Object | ConvertTo-Json -Depth 100 | Out-File -FilePath $FilePath -Encoding UTF8
}

function Append-JsonL([string]$FilePath, $Object) {
    Ensure-Dir -FilePath $FilePath
    $line = $Object | ConvertTo-Json -Compress -Depth 50
    Add-Content -Path $FilePath -Value $line
}

function Set-JsonProp([object]$Obj, [string]$Name, $Value) {
    # Safely add or update a property on PSCustomObject/hashtable
    # ConvertFrom-Json returns PSCustomObject, so dot-assigning NEW props fails; Add-Member is the proper path. :contentReference[oaicite:1]{index=1}
    $prop = $Obj.PSObject.Properties[$Name]
    if ($prop) { $prop.Value = $Value } else { $Obj | Add-Member -NotePropertyName $Name -NotePropertyValue $Value }
}

# --- begin run ---
$RunId = [guid]::NewGuid().ToString()

# pre-run breadcrumbs (guard + trace)
$preGuard = @{
    ts     = (NowIso)
    run_id = $RunId
    kind   = 'sweep'
    phase  = $Phase
}
Append-JsonL -FilePath $GuardLogPath -Object $preGuard

$preTrace = @{
    ts     = (NowIso)
    event  = 'phase.guard.sweep'
    data   = @{ phase = $Phase }
    source = 'tools.phase_seal_runner'
}
Append-JsonL -FilePath $TraceLogPath -Object $preTrace

# --- manifest update ---
$manifest = Read-Json -FilePath $ManifestPath
if (-not $manifest) { $manifest = [pscustomobject]@{} }

Set-JsonProp -Obj $manifest -Name 'current_phase' -Value $Phase
if ($Version) { Set-JsonProp -Obj $manifest -Name 'current_version' -Value $Version }
Write-Json -FilePath $ManifestPath -Object $manifest

# --- history append ---
$history = Read-Json -FilePath $HistoryPath
if (-not ($history -is [System.Collections.IList])) { $history = @() }

$entry = [pscustomobject]@{
    ts    = (NowIso)
    phase = $Phase
    event = 'phase.sealed'
}
if ($Version) { $entry | Add-Member -NotePropertyName version -NotePropertyValue $Version }
if ($Note)    { $entry | Add-Member -NotePropertyName note    -NotePropertyValue $Note    }

$history += $entry
Write-Json -FilePath $HistoryPath -Object $history

# --- post-run breadcrumbs (guard + trace) ---
$postGuard = @{
    ts     = (NowIso)
    run_id = $RunId
    kind   = 'seal'
    phase  = $Phase
    version= $Version
    note   = $Note
}
Append-JsonL -FilePath $GuardLogPath -Object $postGuard

$postTrace = @{
    ts     = (NowIso)
    event  = 'phase.sealed'
    data   = @{ phase = $Phase; version = $Version; note = $Note }
    source = 'tools.phase_seal_runner'
}
Append-JsonL -FilePath $TraceLogPath -Object $postTrace

Write-Host ("SEALED phase {0}{1}" -f $Phase, $(if ($Version) { " as $Version" } else { "" })) -ForegroundColor Green
