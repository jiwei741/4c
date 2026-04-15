param(
  [string]$RegistryNamespace = "your-dockerhub-username",
  [string]$Tag = "v1.0.0"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendImage = "$RegistryNamespace/spatio-eco-backend:$Tag"
$frontendImage = "$RegistryNamespace/spatio-eco-frontend:$Tag"

Write-Host "Repository root: $repoRoot"
Write-Host "Building backend image: $backendImage"
docker build -t $backendImage -f "$repoRoot\infra\docker\backend-runtime.Dockerfile" $repoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Backend image build failed."
}

Write-Host "Building frontend image: $frontendImage"
docker build -t $frontendImage -f "$repoRoot\services\frontend\Dockerfile" $repoRoot
if ($LASTEXITCODE -ne 0) {
  throw "Frontend image build failed."
}

Write-Host ""
Write-Host "Build completed."
Write-Host "Backend image : $backendImage"
Write-Host "Frontend image: $frontendImage"
