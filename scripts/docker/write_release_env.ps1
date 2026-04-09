param(
  [string]$RegistryNamespace = "your-dockerhub-username",
  [string]$Tag = "v1.0.0",
  [int]$PlatformPort = 8080,
  [int]$BackendInternalPort = 8000,
  [string]$OutputPath = ".env.release"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$targetPath = if ([System.IO.Path]::IsPathRooted($OutputPath)) {
  $OutputPath
} else {
  Join-Path $repoRoot $OutputPath
}

$content = @"
COMPOSE_PROJECT_NAME=spatio-eco
PLATFORM_PORT=$PlatformPort
BACKEND_INTERNAL_PORT=$BackendInternalPort
BACKEND_IMAGE=$RegistryNamespace/spatio-eco-backend:$Tag
FRONTEND_IMAGE=$RegistryNamespace/spatio-eco-frontend:$Tag
"@

Set-Content -Path $targetPath -Value $content -Encoding utf8

Write-Host "Release env written to: $targetPath"
