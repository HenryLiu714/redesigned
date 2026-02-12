# Python base image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Set environment variables (if needed)
# ENV PYTHONUNBUFFERED=1

# Run the main script
CMD ["python3", "run.py"]
