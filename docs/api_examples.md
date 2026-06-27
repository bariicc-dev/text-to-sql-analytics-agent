# API Examples

These examples assume the backend is running locally on port 8000.

## Health

```bash
curl http://localhost:8000/health
```

```json
{"status":"ok"}
```

## Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top 5 products by revenue?"}'
```

The response includes an answer, SQL, rows, explanation, safety status, and source. The interaction is also saved in query history.

## Provider Config

Demo mode is the default and does not require an API key:

```text
QUERY_PROVIDER=demo
```

Optional NVIDIA-compatible provider config uses placeholders:

```text
QUERY_PROVIDER=llm
LLM_PROVIDER=nvidia
LLM_MODEL=<model-name>
LLM_API_BASE_URL=<nvidia-compatible-chat-completions-base-url>
LLM_API_KEY=<your-api-key>
```

## Query History

```bash
curl "http://localhost:8000/queries/logs?limit=20"
```

Filter by safety status:

```bash
curl "http://localhost:8000/queries/logs?safety_status=safe"
```

Read one query log:

```bash
curl http://localhost:8000/queries/logs/1
```

## Feedback

```bash
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"query_log_id":1,"rating":5,"comment":"Useful answer"}'
```

List feedback for a query log:

```bash
curl http://localhost:8000/feedback/query/1
```

## Evaluation

List evaluation cases:

```bash
curl http://localhost:8000/evaluation/cases
```

Run the evaluation suite:

```bash
curl -X POST http://localhost:8000/evaluation/run
```

## Schema Context

Read the full schema context:

```bash
curl http://localhost:8000/schema
```

Read one table context:

```bash
curl http://localhost:8000/schema/tables/products
```

Read the compact schema context:

```bash
curl http://localhost:8000/schema/compact
```

## Prompt Context

Build prompt context for a future provider:

```bash
curl -X POST http://localhost:8000/prompt/context \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the top 5 products by revenue?"}'
```

The response includes the original question and the prompt text. No external model is called.

## Validate SQL

```bash
curl -X POST http://localhost:8000/validate-sql \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT id, name FROM products LIMIT 5"}'
```

```json
{
  "is_safe": true,
  "reason": "Query is read-only and passed the current safety checks.",
  "normalized_sql": "SELECT id, name FROM products LIMIT 5",
  "blocked_keywords": []
}
```

## Top Products

```bash
curl "http://localhost:8000/analytics/top-products?limit=5"
```

Returns products sorted by revenue.

## Monthly Revenue

```bash
curl http://localhost:8000/analytics/monthly-revenue
```

Returns revenue grouped by year and month.

## Refund Rate

```bash
curl http://localhost:8000/analytics/refund-rate
```

Returns total orders, refunded orders, refund rate, and refund amount.

## Customer Segments

```bash
curl http://localhost:8000/analytics/customer-segments
```

Returns customer segment revenue and order counts.
