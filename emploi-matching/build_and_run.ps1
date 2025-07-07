$IMAGE_NAME = "emploi-matching"
$CONTAINER_NAME = "emploi-matching-app"

Write-Host "Installing Python dependencies on host..."
Write-Host "Stopping and removing existing container (if any)..."
docker stop $CONTAINER_NAME  | Out-Null
docker rm $CONTAINER_NAME  | Out-Null

Write-Host "Removing existing Docker image (if any)..."

Write-Host "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Docker image built successfully."
    Write-Host "Running Docker container: $CONTAINER_NAME"
    docker run -d -p 8000:8000 --name $CONTAINER_NAME $IMAGE_NAME
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Container $CONTAINER_NAME is running on port 8000."
        Write-Host "You can access the application at http://localhost:8000"
    } else {
        Write-Host "Failed to run Docker container."
    }
} else {
    Write-Host "Failed to build Docker image."
}