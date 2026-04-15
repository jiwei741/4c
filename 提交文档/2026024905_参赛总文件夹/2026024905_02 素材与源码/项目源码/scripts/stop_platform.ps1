$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pidFile = Join-Path $repoRoot "logs/platform/platform.pids.json"

if (-not (Test-Path $pidFile)) {
    Write-Host "No PID file found."
    exit 0
}

$payload = Get-Content $pidFile -Raw | ConvertFrom-Json

foreach ($procId in @($payload.backend_pid, $payload.frontend_pid)) {
    if ($procId) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "Stopped PID $procId"
        } catch {
            Write-Host "PID $procId already exited"
        }
    }
}

Remove-Item $pidFile -Force
