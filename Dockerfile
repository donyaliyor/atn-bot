FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensures /app/data exists before the volume is mounted
RUN mkdir -p /app/data logs

# Set proper permissions (important for volume mounts)
RUN chmod -R 755 /app/data logs

CMD ["python", "bot.py"]
