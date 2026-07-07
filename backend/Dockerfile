# Backend Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update && apt-get install -y build-essential libpq-dev git curl && rm -rf /var/lib/apt/lists/*

# copy
COPY ./backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./backend /app/backend

# create uploads dir
RUN mkdir -p /app/uploads && chown -R nobody:nogroup /app/uploads

ENV PYTHONPATH=/app

CMD ["gunicorn", "backend.app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "2"]
