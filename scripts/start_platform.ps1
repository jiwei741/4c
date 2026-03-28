param(
    [switch]$ForceSync,
    [switch]$OpenBrowser,
    [switch]$NoBrowser,
    [int]$StartupTimeoutSeconds = 60
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$logDir = Join-Path $repoRoot "logs/platform"
$pidFile = Join-Path $logDir "platform.pids.json"
$backendDir = Join-Path $repoRoot "services/backend"
$frontendDir = Join-Path $repoRoot "services/frontend"

$uvExe = (Get-Command uv -ErrorAction Stop).Source
$nodeExe = (Get-Command node -ErrorAction Stop).Source
$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
if ($null -eq $npmCommand) {
    $npmCommand = Get-Command npm -ErrorAction Stop
}
$npmExe = $npmCommand.Source

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Read-DotEnv([string]$Path) {
    $values = @{}
    if (-not (Test-Path $Path)) {
        return $values
    }

    foreach ($line in Get-Content $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }

        $parts = $trimmed -split '=', 2
        if ($parts.Count -ne 2) {
            continue
        }

        $key = $parts[0].Trim()
        $value = $parts[1].Trim()

        if (
            ($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))
        ) {
            $value = $value.Substring(1, $value.Length - 2)
        }

        $values[$key] = $value
    }

    return $values
}

function Get-ConfigString([hashtable]$Config, [string]$Key, [string]$DefaultValue) {
    if ($Config.ContainsKey($Key) -and $Config[$Key]) {
        return [string]$Config[$Key]
    }

    return $DefaultValue
}

function Get-ConfigInt([hashtable]$Config, [string]$Key, [int]$DefaultValue) {
    if ($Config.ContainsKey($Key) -and $Config[$Key]) {
        return [int]$Config[$Key]
    }

    return $DefaultValue
}

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

function Ensure-NodeProject([string]$ProjectDir) {
    $nodeModulesDir = Join-Path $ProjectDir "node_modules"
    if ((Test-Path $nodeModulesDir) -and -not $ForceSync) {
        return
    }

    Push-Location $ProjectDir
    try {
        & $npmExe ci
        if ($LASTEXITCODE -ne 0) {
            throw "npm ci failed in $ProjectDir"
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

$envConfig = Read-DotEnv (Join-Path $repoRoot ".env")
$backendHost = Get-ConfigString $envConfig "BACKEND_HOST" "127.0.0.1"
$backendPort = Get-ConfigInt $envConfig "BACKEND_PORT" 8000
$frontendHost = "127.0.0.1"
$frontendPort = Get-ConfigInt $envConfig "FRONTEND_PORT" 4173

$backendLog = Join-Path $logDir "backend.out.log"
$backendErr = Join-Path $logDir "backend.err.log"
$frontendLog = Join-Path $logDir "frontend.out.log"
$frontendErr = Join-Path $logDir "frontend.err.log"
$backendUrl = "http://{0}:{1}/api/v1/health" -f $backendHost, $backendPort
$frontendUrl = "http://{0}:{1}/" -f $frontendHost, $frontendPort

Ensure-UvProject $backendDir
Ensure-NodeProject $frontendDir

Assert-PortAvailable -Port $backendPort -ServiceName "Backend"
Assert-PortAvailable -Port $frontendPort -ServiceName "Frontend"

$backendPython = Join-Path $backendDir ".venv/Scripts/python.exe"
if (-not (Test-Path $backendPython)) {
    throw "Backend virtualenv is missing: $backendPython"
}

$frontendEntrypoint = Join-Path $frontendDir "node_modules/vite/bin/vite.js"
if (-not (Test-Path $frontendEntrypoint)) {
    throw "Vite entrypoint is missing: $frontendEntrypoint"
}

$backend = Start-Process `
    -FilePath $backendPython `
    -ArgumentList @("-m", "uvicorn", "app:app", "--host", $backendHost, "--port", "$backendPort") `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput $backendLog `
    -RedirectStandardError $backendErr `
    -PassThru

$previousApiBaseUrl = [Environment]::GetEnvironmentVariable("VITE_API_BASE_URL", "Process")
$env:VITE_API_BASE_URL = "http://{0}:{1}" -f $backendHost, $backendPort

try {
    $frontend = Start-Process `
        -FilePath $nodeExe `
        -ArgumentList @($frontendEntrypoint, "--host", $frontendHost, "--port", "$frontendPort", "--strictPort") `
        -WorkingDirectory $frontendDir `
        -RedirectStandardOutput $frontendLog `
        -RedirectStandardError $frontendErr `
        -PassThru
}
finally {
    if ($null -eq $previousApiBaseUrl) {
        Remove-Item Env:VITE_API_BASE_URL -ErrorAction SilentlyContinue
    }
    else {
        $env:VITE_API_BASE_URL = $previousApiBaseUrl
    }
}

try {
    Wait-ServiceReady -Name "Backend" -Process $backend -Url $backendUrl -TimeoutSeconds $StartupTimeoutSeconds
    Wait-ServiceReady -Name "Frontend" -Process $frontend -Url $frontendUrl -TimeoutSeconds $StartupTimeoutSeconds

    $payload = @{
        backend_pid = $backend.Id
        frontend_pid = $frontend.Id
        backend_host = $backendHost
        backend_port = $backendPort
        frontend_host = $frontendHost
        frontend_port = $frontendPort
        backend_url = $backendUrl
        frontend_url = $frontendUrl
        backend_log = $backendLog
        backend_err = $backendErr
        frontend_log = $frontendLog
        frontend_err = $frontendErr
        started_at = (Get-Date).ToString("o")
        mode = "uv+vite"
    } | ConvertTo-Json

    Set-Content -Path $pidFile -Value $payload -Encoding UTF8

    Write-Host "Backend PID: $($backend.Id)"
    Write-Host "Frontend PID: $($frontend.Id)"
    Write-Host "Mode: uv+vite"
    Write-Host "PID file: $pidFile"
    Write-Host "Frontend URL: $frontendUrl"
    Write-Host "Backend Health URL: $backendUrl"

    if (-not $NoBrowser) {
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
