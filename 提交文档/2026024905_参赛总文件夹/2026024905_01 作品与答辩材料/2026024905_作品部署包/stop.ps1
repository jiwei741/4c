$ErrorActionPreference = "Stop"

$releaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $releaseDir

docker compose down
if ($LASTEXITCODE -ne 0) {
  throw "Docker services failed to stop cleanly."
}

Write-Host ""
Write-Host "Platform stopped."
