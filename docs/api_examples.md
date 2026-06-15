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

The response includes an answer, generated SQL, rows, explanation, safety status, and source.

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
