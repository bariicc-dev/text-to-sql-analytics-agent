from app.providers.base import QueryCandidate

FALLBACK_MESSAGE = (
    "I do not know how to answer this yet in demo mode. "
    "Try asking about top products, monthly revenue, refund rate, or customer segments."
)

_UNSAFE_QUESTION_TERMS = ("delete", "update", "drop", "truncate", "insert", "alter")


class DemoQueryProvider:
    source = "demo"

    def generate_query(self, question: str) -> QueryCandidate:
        normalized_question = question.lower().strip()

        if has_unsafe_intent(question):
            return QueryCandidate(
                category="unsupported",
                sql=None,
                source=self.source,
                confidence=0.0,
                reason="Unsafe request is not supported in demo mode.",
                safety_status="blocked",
            )

        if _matches_top_products(normalized_question):
            return QueryCandidate(
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
                source=self.source,
                confidence=1.0,
            )

        if _matches_monthly_revenue(normalized_question):
            return QueryCandidate(
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
                source=self.source,
                confidence=1.0,
            )

        if _matches_refund_rate(normalized_question):
            return QueryCandidate(
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
                source=self.source,
                confidence=1.0,
            )

        if _matches_customer_segments(normalized_question):
            return QueryCandidate(
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
                source=self.source,
                confidence=1.0,
            )

        return QueryCandidate(
            category="unsupported",
            sql=None,
            source=self.source,
            confidence=0.0,
            reason="No demo query matched this question.",
            safety_status="not_generated",
        )


def has_unsafe_intent(question: str) -> bool:
    normalized_question = question.lower().strip()
    return any(term in normalized_question for term in _UNSAFE_QUESTION_TERMS)


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
