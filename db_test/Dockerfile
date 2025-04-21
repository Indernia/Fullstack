# Use the official Python image
FROM python:3.8-alpine

# from perplexity to fix alpine issue with azure-storage-blob
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    cargo

# Set the working directory inside the container
WORKDIR /app

# Copy only requirements file first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install  -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Start the application with Gunicorn
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app", "--log-level", "debug", "--error-logfile", "-", "--access-logfile", "-"]
