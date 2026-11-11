# Smoke-test the packaged maliang-backend the same way the Electron shell does.
#
# Launch maliang-backend.exe with the env/cwd/port python-manager.ts uses,
# poll http://127.0.0.1:<port>/api/health for up to 120s, print stdout/stderr
# and any backend log files, and exit non-zero if health never comes up.
#
# Usage:
#   powershell -File desktop/build/smoke-backend.ps1 -ExePath <path-to-maliang-backend.exe>
param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,
    [int]$Port = 19876,
    [int]$TimeoutSec = 120
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "Backend executable not found: $ExePath"
}

$ExePath = (Resolve-Path -LiteralPath $ExePath).Path
$exeDir = Split-Path -Parent $ExePath
Write-Host "=== maliang backend smoke test ==="
Write-Host "exe: $ExePath"
Write-Host "exe dir listing:"
Get-ChildItem -LiteralPath $exeDir | ForEach-Object { Write-Host ("  {0,12}  {1}" -f $_.Length, $_.Name) }
$internal = Join-Path $exeDir "_internal"
if (Test-Path -LiteralPath $internal) {
    $count = (Get-ChildItem -LiteralPath $internal -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    Write-Host "_internal file count: $count"
} else {
    Write-Host "WARNING: _internal directory is missing next to the exe (onedir payload absent)"
}

$dataDir = Join-Path ([System.IO.Path]::GetTempPath()) ("maliang-smoke-" + [guid]::NewGuid().ToString("n"))
New-Item -ItemType Directory -Path $dataDir | Out-Null
Write-Host "MALIANG_DATA_DIR=$dataDir"
Write-Host "MALIANG_WEB_PORT=$Port"

$stdoutPath = Join-Path $dataDir "smoke-stdout.log"
$stderrPath = Join-Path $dataDir "smoke-stderr.log"
New-Item -ItemType File -Path $stdoutPath | Out-Null
New-Item -ItemType File -Path $stderrPath | Out-Null

# Match python-manager.ts spawn env for a packaged app.
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:MALIANG_DESKTOP = "1"
$env:MALIANG_WEB_PORT = "$Port"
$env:MALIANG_DESKTOP_TOKEN = "smoke-test-token"
$env:MALIANG_DATA_DIR = $dataDir

$proc = Start-Process -FilePath $ExePath `
    -WorkingDirectory $dataDir `
    -PassThru -NoNewWindow `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath

Write-Host ("spawned pid={0} at {1:o}" -f $proc.Id, (Get-Date).ToUniversalTime())

function Dump-Logs {
    param([string]$Reason)
    Write-Host "=== $Reason ==="
    Write-Host "--- process state ---"
    if ($proc.HasExited) {
        Write-Host ("exited code={0} at {1:o}" -f $proc.ExitCode, $proc.ExitTime.ToUniversalTime())
    } else {
        Write-Host "still running"
    }
    Write-Host "--- stdout ---"
    if (Test-Path $stdoutPath) { Get-Content -LiteralPath $stdoutPath -Raw -ErrorAction SilentlyContinue }
    Write-Host "--- stderr ---"
    if (Test-Path $stderrPath) { Get-Content -LiteralPath $stderrPath -Raw -ErrorAction SilentlyContinue }
    $runLog = Join-Path $dataDir "run.log"
    Write-Host "--- $runLog ---"
    if (Test-Path $runLog) {
        Get-Content -LiteralPath $runLog -Raw -ErrorAction SilentlyContinue
    } else {
        Write-Host "(run.log not created)"
    }
    Write-Host "--- data dir ---"
    Get-ChildItem -LiteralPath $dataDir -Force | ForEach-Object { Write-Host ("  {0,12}  {1}" -f $_.Length, $_.Name) }
}

$deadline = (Get-Date).AddSeconds($TimeoutSec)
$healthy = $false
$healthUrl = "http://127.0.0.1:$Port/api/health"
try {
    while ((Get-Date) -lt $deadline) {
        if ($proc.HasExited) {
            Dump-Logs "backend exited before becoming healthy"
            throw "maliang-backend.exe exited with code $($proc.ExitCode) before /api/health responded"
        }
        try {
            $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3
            if ($resp.StatusCode -eq 200) {
                $healthy = $true
                Write-Host ("health OK after {0:n1}s: {1}" -f ((Get-Date) - ($deadline.AddSeconds(-$TimeoutSec))).TotalSeconds, $resp.Content)
                break
            }
            Write-Host ("health status {0}" -f $resp.StatusCode)
        } catch {
            $elapsed = [int]((Get-Date) - ($deadline.AddSeconds(-$TimeoutSec))).TotalSeconds
            Write-Host ("waiting for health ({0}s): {1}" -f $elapsed, $_.Exception.Message)
        }
        Start-Sleep -Seconds 2
    }

    if (-not $healthy) {
        Dump-Logs "health check timed out after ${TimeoutSec}s"
        throw "maliang-backend.exe did not answer $healthUrl within ${TimeoutSec}s"
    }

    Dump-Logs "health check passed; captured output follows"
} finally {
    if (-not $proc.HasExited) {
        Write-Host "stopping backend pid=$($proc.Id)"
        try { taskkill /PID $proc.Id /T /F | Out-Host } catch { try { $proc.Kill() } catch {} }
        try { $proc.WaitForExit(10000) | Out-Null } catch {}
    }
}

Write-Host "smoke test passed"
