FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/src /app/src

# Expose port
EXPOSE 8004

# Run the application
CMD ["python", "-m", "uvicorn", "src.services.websocket-sync.main:app", "--host", "0.0.0.0", "--port", "8004"]
