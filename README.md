# Text-to-SQL Analytics Agent

Text-to-SQL Analytics Agent is a portfolio project for exploring how a backend service can translate business questions into safe SQL workflows over a synthetic analytics database.

The project is built around a simple local-first stack:

- Python and FastAPI for the API layer
- PostgreSQL for the analytics database
- SQLAlchemy for database access
- Docker Compose for local development
- Pytest for automated checks

The default goal is a recruiter-friendly demo that runs without private data or required API keys. All sample data will be synthetic.

## Current Scope

Milestone 0 rebuilds the project foundation:

- FastAPI application structure
- `/health` endpoint
- typed configuration settings
- database connection foundation
- Docker Compose services for backend and PostgreSQL
- health endpoint test
- CI workflow skeleton

## Quick Start

```bash
docker compose up --build
```

Check the backend:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Local Tests

```bash
cd backend
pytest
```

## Project Structure

```text
backend/
  app/
    api/
    core/
    db/
  tests/
.github/workflows/
docker-compose.yml
```

## Roadmap

1. Add synthetic e-commerce schema and seed data.
2. Add analytics endpoints for common business metrics.
3. Add SQL validation for read-only query execution.
4. Add demo text-to-SQL generation for common questions.
5. Add logging, evaluation cases, and documentation polish.
