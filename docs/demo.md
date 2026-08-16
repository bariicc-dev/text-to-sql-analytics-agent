# QueryPilot local demo guide

This guide runs QueryPilot with the default demo provider, so the main flow works without an API key. The optional NVIDIA-compatible provider can be tested separately with local credentials.

## Prerequisites

- Docker with Docker Compose
- `curl`, or a browser for Swagger
- Python 3.12 only if you run the backend outside Docker

## Start and seed the project

From the repository root, start PostgreSQL and the backend:

```bash
docker compose up --build -d
```

Seed the synthetic e-commerce data:

```bash
docker compose exec backend python -m app.demo.seed_data
```

Open Swagger at [http://localhost:8000/docs](http://localhost:8000/docs) to inspect and run the endpoints.

## Demo provider test flow

Docker Compose starts QueryPilot with `QUERY_PROVIDER=demo`. The following requests can also be run from Swagger.

### 1. Health check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "ok"
}
```

### 2. Chat demo

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top selling products?"}'
```

Trimmed response shape:

```json
{
  "answer": "The demo query returned ...",
  "sql": "SELECT ... FROM products ... ORDER BY revenue DESC LIMIT 5",
  "rows": [
    {
      "product_name": "...",
      "category": "...",
      "units_sold": "...",
      "revenue": "..."
    }
  ],
  "explanation": "...",
  "safety_status": "safe",
  "source": "demo"
}
```

The ellipses show shortened values. In demo mode:

- the provider maps known analytics questions to SQL templates
- the returned rows come from the seeded PostgreSQL database, not hardcoded responses
- the SQL candidate still passes through SQL validation before execution

### 3. SQL safety

Check a safe read-only query:

```bash
curl -X POST http://localhost:8000/validate-sql \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT * FROM products LIMIT 5;"}'
```

```json
{
  "is_safe": true,
  "reason": "Query is read-only and passed the current safety checks.",
  "normalized_sql": "SELECT * FROM products LIMIT 5",
  "blocked_keywords": []
}
```

Now check an unsafe query:

```bash
curl -X POST http://localhost:8000/validate-sql \
  -H "Content-Type: application/json" \
  -d '{"sql":"DROP TABLE products;"}'
```

```json
{
  "is_safe": false,
  "reason": "This query was blocked because DROP statements are not allowed.",
  "normalized_sql": "DROP TABLE products;",
  "blocked_keywords": ["DROP"]
}
```

The validation endpoint does not execute either query. Unsafe SQL is blocked before it can reach the execution step.

### 4. Provider evaluation

Run the evaluation cases with the default demo provider:

```bash
curl -X POST http://localhost:8000/evaluation/run
```

Selected fields from the response:

```json
{
  "provider": "demo",
  "status": "ready",
  "total_cases": 16,
  "results": [
    {
      "case_id": 1,
      "expected_category": "top_products",
      "actual_category": "top_products",
      "provider": "demo",
      "sql_generated": true,
      "sql_validated": true,
      "passed": true
    }
  ]
}
```

### 5. Provider comparison

Compare the demo and LLM providers with the same cases:

```bash
curl -X POST http://localhost:8000/evaluation/compare
```

Selected fields from the default local response:

```json
{
  "providers": ["demo", "llm"],
  "total_cases": 16,
  "summary_by_provider": {
    "demo": {
      "status": "ready"
    },
    "llm": {
      "status": "not_configured"
    }
  }
}
```

The full response includes per-provider counts and case results. Each result records:

- expected and actual category
- expected and actual safety status
- whether SQL was generated
- whether the SQL passed validation
- which provider was used
- pass or fail with a reason

An unconfigured LLM provider reports `not_configured` instead of crashing or making a request.

## Optional NVIDIA-compatible provider test

The Docker demo remains the default. To test the optional provider manually, keep PostgreSQL running and stop the Docker backend:

```bash
docker compose stop backend
```

Create `backend/.env` locally with your own values:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/querypilot
QUERY_PROVIDER=llm
LLM_PROVIDER=nvidia
LLM_MODEL=<model-name>
LLM_API_BASE_URL=<nvidia-compatible-chat-completions-base-url>
LLM_API_KEY=<local-api-key>
```

Then run the backend from the `backend` directory:

```bash
cd backend
python -m pip install -r requirements.txt
python -m app.demo.seed_data
python -m uvicorn app.main:app --reload
```

Call `POST /chat` with the same demo question and confirm that the response has `source: "llm"`. The provider returns a SQL candidate, but SQL validation still decides whether it can be executed. Actual model behavior depends on the configured endpoint, so test it manually rather than treating demo provider results as LLM results.

Keep credentials local:

- never commit `.env`
- never commit API keys
- use NVIDIA API keys for local testing only
- keep `.env` ignored by Git

When finished, stop the local server, remove the local `backend/.env` if it is no longer needed, and restart the default backend with `docker compose up -d backend`.

## Screenshots to capture

- GitHub README top section
- FastAPI Swagger overview
- `/chat` successful response
- `/validate-sql` blocking unsafe SQL
- `/evaluation/compare` provider summary
- GitHub Actions passing
- optional NVIDIA-compatible `/chat` response with credentials hidden

Do not include `.env`, request headers, terminal history, or API keys in screenshots.

## Stop the services

```bash
docker compose down
```

For additional endpoints, see [API examples](api_examples.md).
