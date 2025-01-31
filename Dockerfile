FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY templates/ templates/
COPY static/ static/

CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]