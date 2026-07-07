# README for SPARK Backend

This repository contains the production-ready backend for the SPARK AI Platform. It includes a FastAPI application with JWT authentication, PostgreSQL, Redis, Alembic migrations, an AI service that talks to a locally hosted GLM-5.2 inference server, SSE streaming support, and Docker Compose setup.

Quick start (development/local school network)

1. Copy environment variables

   cp backend/.env.example backend/.env
   Edit backend/.env and set SECRET_KEY and other vars as needed.

2. Start services

   docker-compose up --build -d

   This brings up Postgres, Redis, the inference service (replace the image in docker-compose.yml with your local inference image or run your inference server separately), the backend, frontend, and nginx.

3. Run Alembic migrations

   docker-compose exec backend alembic upgrade head

4. API is available at http://localhost:8000 or proxied via nginx at http://localhost/

Endpoints

- Health: GET /api/v1/health/ready
- Auth: POST /api/v1/auth/register
- Auth: POST /api/v1/auth/login
- Conversations: POST /api/v1/conversations/
- Stream chat: POST /api/v1/conversations/{conversation_id}/messages -> returns SSE streaming assistant tokens

Model Integration

The backend expects MODEL_API_URL to point to a model server exposing these endpoints:
- POST {MODEL_API_URL}/generate -> non-streaming JSON response
- POST {MODEL_API_URL}/stream -> streaming response (newline-delimited tokens or JSON with {"token":"..."})
- GET {MODEL_API_URL}/health -> health status

Make sure your local GLM-5.2 inference server implements these endpoints or provide a small proxy/wrapper that adapts your model server to this API.

Production notes

- Replace SECRET_KEY with a strong random value.
- Use a managed Postgres or secure the Postgres container for production.
- Replace the inference image with your production inference server or host.
- Place TLS termination in front of nginx and ensure only internal networks can access inference nodes.

