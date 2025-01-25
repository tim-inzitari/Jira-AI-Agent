FROM python:3.11-slim

WORKDIR /app

# Set Python path to include /app directory
ENV PYTHONPATH=/app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application with proper directory structure
COPY src/ src/
COPY tests/ tests/

CMD ["python", "src/main.py"]