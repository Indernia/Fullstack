#!/bin/bash

# Set variables
IMAGE_NAME="backend-flask-app"
TAG="latest"
TAR_FILE="backend-flask-app.tar"
PLATFORM="linux/amd64"

# Build the Docker image
echo "Building Docker image: $IMAGE_NAME:$TAG..."
docker build --platform ${PLATFORM} -t ${IMAGE_NAME}:${TAG} .


# Save the image to a tar file
echo "Saving Docker image to $TAR_FILE..."
docker save -o $TAR_FILE $IMAGE_NAME:$TAG

echo "Done! Image saved as $TAR_FILE"
