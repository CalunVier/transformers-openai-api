FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 7088

# Set environment variables
ENV PYTHONPATH=/app
ENV HOSTNAME=0.0.0.0
ENV PORT=7088

# Run the application
CMD ["python", "main.py"]
