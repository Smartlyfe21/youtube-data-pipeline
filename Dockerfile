# Base image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (if you have one) to leverage caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default command (can be overridden in docker-compose)
CMD ["python", "src/run_etl.py"]
