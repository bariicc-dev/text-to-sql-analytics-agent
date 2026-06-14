# Database Schema

QueryPilot uses a small synthetic e-commerce database. The data is fake and designed for local demos, analytics endpoints, and validation tests.

## Tables

| Table | Purpose |
| --- | --- |
| `customers` | Demo customers with country and segment fields. |
| `products` | Demo products with category, price, and cost. |
| `orders` | Order headers with status, date, customer, and sales channel. |
| `order_items` | Product line items for each order. |
| `refunds` | Refund records connected to orders and products. |
| `query_logs` | Future query history for questions, SQL, safety status, and errors. |
| `feedback` | Future feedback linked to query logs and optionally customers. |

## Relationships

- `orders.customer_id` references `customers.id`
- `order_items.order_id` references `orders.id`
- `order_items.product_id` references `products.id`
- `refunds.order_id` references `orders.id`
- `refunds.product_id` references `products.id`
- `feedback.query_log_id` references `query_logs.id`
- `feedback.customer_id` references `customers.id`

## Seed Data

The demo seed script creates:

- 5 customers
- 5 products
- 6 orders
- 9 order items
- 1 refund

Run it with:

```bash
docker compose exec backend python -m app.demo.seed_data
```
