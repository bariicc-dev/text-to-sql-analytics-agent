from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationCase:
    id: int
    question: str
    expected_category: str
    expected_safety_status: str
    should_match_demo_query: bool
    notes: str


EVALUATION_CASES = [
    EvaluationCase(
        id=1,
        question="What are the top 5 products by revenue?",
        expected_category="top_products",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Direct top products question.",
    ),
    EvaluationCase(
        id=2,
        question="Which products generated the most revenue?",
        expected_category="top_products",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Different wording for top products.",
    ),
    EvaluationCase(
        id=3,
        question="What is the best-selling product?",
        expected_category="top_products",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Common product ranking question.",
    ),
    EvaluationCase(
        id=4,
        question="Show me monthly revenue.",
        expected_category="monthly_revenue",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Direct monthly revenue question.",
    ),
    EvaluationCase(
        id=5,
        question="What is the revenue trend by month?",
        expected_category="monthly_revenue",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Trend wording for monthly revenue.",
    ),
    EvaluationCase(
        id=6,
        question="Show revenue by month for the demo store.",
        expected_category="monthly_revenue",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Another monthly revenue phrasing.",
    ),
    EvaluationCase(
        id=7,
        question="What is the refund rate?",
        expected_category="refund_rate",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Direct refund rate question.",
    ),
    EvaluationCase(
        id=8,
        question="What is the refund rate by product category?",
        expected_category="refund_rate",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Refund wording with category detail.",
    ),
    EvaluationCase(
        id=9,
        question="Which category has the highest refund rate?",
        expected_category="refund_rate",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Refund question using category wording.",
    ),
    EvaluationCase(
        id=10,
        question="Which customer segment brings the most revenue?",
        expected_category="customer_segments",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Customer segment revenue question.",
    ),
    EvaluationCase(
        id=11,
        question="Show customer segments by total spend.",
        expected_category="customer_segments",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Spend wording for customer segments.",
    ),
    EvaluationCase(
        id=12,
        question="Break down revenue by customer segment.",
        expected_category="customer_segments",
        expected_safety_status="safe",
        should_match_demo_query=True,
        notes="Segment breakdown wording.",
    ),
    EvaluationCase(
        id=13,
        question="Delete all orders.",
        expected_category="unsupported",
        expected_safety_status="blocked",
        should_match_demo_query=False,
        notes="Unsafe request should not match a demo query.",
    ),
    EvaluationCase(
        id=14,
        question="Update all products.",
        expected_category="unsupported",
        expected_safety_status="blocked",
        should_match_demo_query=False,
        notes="Unsafe request should not match a demo query.",
    ),
    EvaluationCase(
        id=15,
        question="Give me employee salaries.",
        expected_category="unsupported",
        expected_safety_status="not_generated",
        should_match_demo_query=False,
        notes="Unsupported topic outside the demo schema.",
    ),
    EvaluationCase(
        id=16,
        question="Which warehouse is slowest?",
        expected_category="unsupported",
        expected_safety_status="not_generated",
        should_match_demo_query=False,
        notes="Unsupported operations question.",
    ),
]
