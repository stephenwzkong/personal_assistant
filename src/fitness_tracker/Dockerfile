FROM python:3.12-slim

WORKDIR /app

# Install Node.js (required for Reflex frontend)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Initialize the Reflex app
RUN reflex init

# Cloud Run expects PORT environment variable
ENV PORT=8080
ENV REFLEX_BACKEND_PORT=8080
ENV REFLEX_FRONTEND_PORT=8080

# Run without --backend-only, let Reflex handle both
CMD reflex run --env prod --loglevel info --backend-port $PORT --frontend-port $PORT
