#!/bin/bash

IMAGE_NAME="emploi-matching"
CONTAINER_NAME="emploi-matching-app"

echo "Stopping and removing existing container (if any)..."
docker stop $CONTAINER_NAME &> /dev/null
docker rm $CONTAINER_NAME &> /dev/null

echo "Removing existing Docker image (if any)..."
docker rmi -f $IMAGE_NAME &> /dev/null

echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "Docker image built successfully."
    echo "Running Docker container: $CONTAINER_NAME"
    docker run -d -p 8000:8000 --name $CONTAINER_NAME $IMAGE_NAME
    if [ $? -eq 0 ]; then
        echo "Container $CONTAINER_NAME is running on port 8000."
        echo "You can access the application at http://localhost:8000"
    else
        echo "Failed to run Docker container."
    fi
else
    echo "Failed to build Docker image."
fi