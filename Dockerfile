# Use an ARM64 compatible base image
FROM --platform=linux/arm64 python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install build dependencies and pip packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev && \
    pip install --no-cache-dir --platform linux_x86_64 -r requirements.txt && \
    apt-get remove -y build-essential python3-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Create and set permissions for the SQLite database directory
RUN mkdir -p /app/instance && \
    chmod 777 /app/instance

# Add gunicorn
RUN pip install --no-cache-dir gunicorn

# Command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app --log-file -