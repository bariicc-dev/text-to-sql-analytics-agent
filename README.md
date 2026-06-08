# Text-to-SQL Analytics Agent

AI-powered analytics assistant that converts natural-language business questions into safe SQL queries over a synthetic PostgreSQL business database.

This public portfolio project is designed for Data & AI Engineering internship applications. It uses only fake business data and runs in demo mode by default.

## Current Milestone

Milestone 3 adds analytics endpoints for top products, monthly revenue, refund rate, and customer segments.

## Quick Start

```bash
docker-compose up --build
```

Then check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Example analytics endpoints:

```bash
curl http://localhost:8000/analytics/top-products
curl http://localhost:8000/analytics/revenue-by-month
curl http://localhost:8000/analytics/refund-rate
curl http://localhost:8000/analytics/customer-segments
```

## Project Structure

```text
backend/      FastAPI application and tests
data/         Synthetic CSV seed data
sql/          Schema, seed, and example SQL files
docs/         Architecture, database, API, and evaluation notes
screenshots/ Portfolio screenshots
```

## Roadmap

- Milestone 1: project structure, FastAPI backend, `/health`, Docker Compose, docs, and CI skeleton
- Milestone 2: database schema, SQLAlchemy models, seed data, and database connection
- Milestone 3: analytics endpoints
- Milestone 4: SQL validator
- Milestone 5: text-to-SQL generation
- Milestone 6: query execution
- Milestone 7: explanations and logging
- Milestone 8: evaluation
- Milestone 9: Docker polish
- Milestone 10: GitHub polish
