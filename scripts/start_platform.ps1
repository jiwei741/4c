param(
    [switch]$ForceSync,
    [switch]$OpenBrowser,
    [int]$StartupTimeoutSeconds = 45
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$logDir = Join-Path $repoRoot "logs/platform"
$pidFile = Join-Path $logDir "platform.pids.json"
$uvExe = (Get-Command uv).Source

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

$backendDir = Join-Path $repoRoot "services/backend"
$frontendDir = Join-Path $repoRoot "services/frontend"

$backendLog = Join-Path $logDir "backend.out.log"
$backendErr = Join-Path $logDir "backend.err.log"
$frontendLog = Join-Path $logDir "frontend.out.log"
$frontendErr = Join-Path $logDir "frontend.err.log"
$backendUrl = "http://127.0.0.1:8000/api/v1/health"
$frontendUrl = "http://127.0.0.1:4173/"

function Ensure-UvProject([string]$ProjectDir) {
    $venvPython = Join-Path $ProjectDir ".venv/Scripts/python.exe"
    if ((Test-Path $venvPython) -and -not $ForceSync) {
        return
    }

    Push-Location $ProjectDir
    try {
        & $uvExe sync
        if ($LASTEXITCODE -ne 0) {
            throw "uv sync failed in $ProjectDir"
        }
    }
    finally {
        Pop-Location
    }
}

function Test-PortListening([int]$Port) {
    $connections = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    return $null -ne $connections
}

function Assert-PortAvailable([int]$Port, [string]$ServiceName) {
    if (Test-PortListening $Port) {
        throw "$ServiceName cannot start because port $Port is already in use. Stop the existing process first."
    }
}

function Test-HttpReady([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500)
    }
    catch {
        return $false
    }
}

function Wait-ServiceReady([string]$Name, [System.Diagnostics.Process]$Process, [string]$Url, [int]$TimeoutSeconds) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if ($Process.HasExited) {
            throw "$Name exited before becoming ready."
        }
        if (Test-HttpReady $Url) {
            return
        }
        Start-Sleep -Seconds 2
        $Process.Refresh()
    }
    throw "$Name did not become ready within $TimeoutSeconds seconds."
}

Ensure-UvProject $backendDir
Ensure-UvProject $frontendDir
Assert-PortAvailable -Port 8000 -ServiceName "Backend"
Assert-PortAvailable -Port 4173 -ServiceName "Frontend"

$backendPython = Join-Path $backendDir ".venv/Scripts/python.exe"
$frontendPython = Join-Path $frontendDir ".venv/Scripts/python.exe"

$backend = Start-Process `
    -FilePath $backendPython `
    -ArgumentList @("-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000") `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErr `
    -PassThru

$frontend = Start-Process `
    -FilePath $frontendPython `
    -ArgumentList @("-m", "http.server", "4173", "--bind", "127.0.0.1") `
    -WorkingDirectory $frontendDir `
    -RedirectStandardOutput $frontendLog `
    -RedirectStandardError $frontendErr `
    -PassThru

try {
    Wait-ServiceReady -Name "Backend" -Process $backend -Url $backendUrl -TimeoutSeconds $StartupTimeoutSeconds
    Wait-ServiceReady -Name "Frontend" -Process $frontend -Url $frontendUrl -TimeoutSeconds $StartupTimeoutSeconds

    $payload = @{
        backend_pid = $backend.Id
        frontend_pid = $frontend.Id
        backend_log = $backendLog
        backend_err = $backendErr
        frontend_log = $frontendLog
        frontend_err = $frontendErr
        started_at = (Get-Date).ToString("o")
        mode = "uv"
    } | ConvertTo-Json

    Set-Content -Path $pidFile -Value $payload -Encoding UTF8

    Write-Host "Backend PID: $($backend.Id)"
    Write-Host "Frontend PID: $($frontend.Id)"
    Write-Host "Mode: uv"
    Write-Host "PID file: $pidFile"
    Write-Host "Frontend URL: $frontendUrl"
    Write-Host "Backend Health URL: $backendUrl"

    if ($OpenBrowser) {
        Start-Process $frontendUrl | Out-Null
    }
}
catch {
    foreach ($proc in @($backend, $frontend)) {
        if ($null -ne $proc -and -not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    throw
}
