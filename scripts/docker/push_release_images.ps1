param(
  [string]$RegistryNamespace = "your-dockerhub-username",
  [string]$Tag = "v1.0.0"
)

$ErrorActionPreference = "Stop"

$backendImage = "$RegistryNamespace/spatio-eco-backend:$Tag"
$frontendImage = "$RegistryNamespace/spatio-eco-frontend:$Tag"

Write-Host "Pushing backend image: $backendImage"
docker push $backendImage
if ($LASTEXITCODE -ne 0) {
  throw "Backend image push failed."
}

Write-Host "Pushing frontend image: $frontendImage"
docker push $frontendImage
if ($LASTEXITCODE -ne 0) {
  throw "Frontend image push failed."
}

Write-Host ""
Write-Host "Push completed."
Write-Host "Backend image : $backendImage"
Write-Host "Frontend image: $frontendImage"
