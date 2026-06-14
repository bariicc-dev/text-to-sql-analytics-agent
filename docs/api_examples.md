# API Examples

These examples assume the backend is running locally on port 8000.

## Health

```bash
curl http://localhost:8000/health
```

```json
{"status":"ok"}
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
