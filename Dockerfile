FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden)
CMD ["python", "bot/bot.py"]
