# Multi-stage build for AI Hedge Fund
# Stage 1: Build React frontend
FROM node:16-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package.json and package-lock.json first for better caching
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY frontend/ ./

# Build the React app
RUN npm run build

# Stage 2: Python backend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY src/ ./src/
COPY server.py .
COPY .env .

# Create a Python path file that adds the current directory to the path
RUN echo "import sys; sys.path.insert(0, '.')" > /app/sitecustomize.py
ENV PYTHONPATH=/app

# Copy the built frontend from the previous stage
COPY --from=frontend-build /app/frontend/build ./build

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "server.py", "--port", "5000"]