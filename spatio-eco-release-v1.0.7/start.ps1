$ErrorActionPreference = "Stop"

$releaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $releaseDir

docker compose pull
if ($LASTEXITCODE -ne 0) {
  throw "Docker image pull failed."
}

docker compose up -d
if ($LASTEXITCODE -ne 0) {
  throw "Docker services failed to start."
}

Write-Host ""
Write-Host "Platform started."
Write-Host "Open: http://localhost:8080"
