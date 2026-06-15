from dataclasses import dataclass


@dataclass(frozen=True)
class DemoQuery:
    sql: str
    source: str = "demo"


FALLBACK_MESSAGE = (
    "I do not know how to answer this yet in demo mode. "
    "Try asking about top products, monthly revenue, refund rate, or customer segments."
)


def generate_demo_sql(question: str) -> DemoQuery | None:
    normalized_question = question.lower().strip()

    if "top" in normalized_question and "product" in normalized_question:
        return DemoQuery(
            sql="""
            SELECT
                p.name AS product_name,
                p.category,
                SUM(oi.quantity) AS units_sold,
                SUM(oi.quantity * oi.unit_price) AS revenue
            FROM products p
            JOIN order_items oi ON oi.product_id = p.id
            JOIN orders o ON o.id = oi.order_id
            WHERE o.status IN ('completed', 'refunded')
            GROUP BY p.id, p.name, p.category
            ORDER BY revenue DESC
            LIMIT 5
            """
        )

    if "monthly" in normalized_question and "revenue" in normalized_question:
        return DemoQuery(
            sql="""
            SELECT
                EXTRACT(YEAR FROM o.order_date) AS year,
                EXTRACT(MONTH FROM o.order_date) AS month,
                SUM(oi.quantity * oi.unit_price) AS revenue,
                COUNT(DISTINCT o.id) AS order_count
            FROM orders o
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.status IN ('completed', 'refunded')
            GROUP BY year, month
            ORDER BY year, month
            LIMIT 24
            """
        )

    if "refund" in normalized_question and "rate" in normalized_question:
        return DemoQuery(
            sql="""
            SELECT
                COUNT(DISTINCT o.id) AS total_orders,
                COUNT(DISTINCT r.order_id) AS refunded_orders,
                CASE
                    WHEN COUNT(DISTINCT o.id) = 0 THEN 0
                    ELSE ROUND(COUNT(DISTINCT r.order_id)::numeric / COUNT(DISTINCT o.id), 4)
                END AS refund_rate,
                COALESCE(SUM(r.amount), 0) AS refund_amount
            FROM orders o
            LEFT JOIN refunds r ON r.order_id = o.id
            LIMIT 1
            """
        )

    if "customer" in normalized_question and "segment" in normalized_question:
        return DemoQuery(
            sql="""
            SELECT
                c.segment,
                COUNT(DISTINCT c.id) AS customer_count,
                COUNT(DISTINCT o.id) AS order_count,
                SUM(oi.quantity * oi.unit_price) AS revenue
            FROM customers c
            JOIN orders o ON o.customer_id = c.id
            JOIN order_items oi ON oi.order_id = o.id
            WHERE o.status IN ('completed', 'refunded')
            GROUP BY c.segment
            ORDER BY revenue DESC
            LIMIT 10
            """
        )

    return None
