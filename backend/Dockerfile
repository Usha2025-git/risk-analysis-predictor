FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app

# Create startup script
RUN echo '#!/bin/bash\n\
alembic upgrade head\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/startup.sh && chmod +x /app/startup.sh

EXPOSE 8000

CMD ["/app/startup.sh"]
