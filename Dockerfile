FROM python:3.11-slim

WORKDIR /app

# Set Python path
ENV PYTHONPATH=/app

# Install dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ src/
COPY tests/ tests/

CMD ["pytest", "-v", "tests/"]