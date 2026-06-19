from dataclasses import dataclass


@dataclass(frozen=True)
class DemoQuery:
    sql: str
    category: str
    source: str = "demo"


FALLBACK_MESSAGE = (
    "I do not know how to answer this yet in demo mode. "
    "Try asking about top products, monthly revenue, refund rate, or customer segments."
)

_UNSAFE_QUESTION_TERMS = ("delete", "update", "drop", "truncate", "insert", "alter")


def has_unsafe_intent(question: str) -> bool:
    normalized_question = question.lower().strip()
    return any(term in normalized_question for term in _UNSAFE_QUESTION_TERMS)


def generate_demo_sql(question: str) -> DemoQuery | None:
    normalized_question = question.lower().strip()

    if _matches_top_products(normalized_question):
        return DemoQuery(
            category="top_products",
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
            """,
        )

    if _matches_monthly_revenue(normalized_question):
        return DemoQuery(
            category="monthly_revenue",
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
            """,
        )

    if _matches_refund_rate(normalized_question):
        return DemoQuery(
            category="refund_rate",
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
            """,
        )

    if _matches_customer_segments(normalized_question):
        return DemoQuery(
            category="customer_segments",
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
            """,
        )

    return None


def _matches_top_products(question: str) -> bool:
    if "best-selling" in question and "product" in question:
        return True
    if "top" in question and "product" in question:
        return True
    return "product" in question and "revenue" in question and ("most" in question or "generated" in question)


def _matches_monthly_revenue(question: str) -> bool:
    if "monthly" in question and "revenue" in question:
        return True
    return "revenue" in question and ("by month" in question or "trend" in question)


def _matches_refund_rate(question: str) -> bool:
    return "refund" in question and ("rate" in question or "category" in question)


def _matches_customer_segments(question: str) -> bool:
    if "customer" in question and "segment" in question:
        return True
    return "segment" in question and ("revenue" in question or "spend" in question)
