from fastapi.testclient import TestClient

from app.demo.evaluation_questions import EVALUATION_CASES
from app.main import app
from app.services.demo_sql_generation_service import generate_demo_sql
from app.services.evaluation_service import run_evaluation_suite

client = TestClient(app)


def test_read_evaluation_cases_returns_cases() -> None:
    response = client.get("/evaluation/cases")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 15
    assert {case["expected_category"] for case in data}.issuperset(
        {"top_products", "monthly_revenue", "refund_rate", "customer_segments", "unsupported"}
    )


def test_run_evaluation_returns_summary() -> None:
    response = client.post("/evaluation/run")

    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] == len(EVALUATION_CASES)
    assert data["passed"] + data["failed"] == data["total_cases"]
    assert 0 <= data["pass_rate"] <= 1
    assert len(data["results"]) == data["total_cases"]


def test_unsupported_questions_are_handled_cleanly() -> None:
    summary = run_evaluation_suite()
    result = next(item for item in summary.results if item.question == "Give me employee salaries.")

    assert result.actual_category == "unsupported"
    assert result.actual_safety_status == "not_generated"
    assert result.passed is True


def test_unsafe_questions_are_classified_as_blocked() -> None:
    summary = run_evaluation_suite()
    result = next(item for item in summary.results if item.question == "Delete all orders.")

    assert result.actual_category == "unsupported"
    assert result.actual_safety_status == "blocked"
    assert result.passed is True


def test_normal_demo_question_matches_expected_category() -> None:
    query = generate_demo_sql("What are the top 5 products by revenue?")

    assert query is not None
    assert query.category == "top_products"


def test_evaluation_suite_passes_current_cases() -> None:
    summary = run_evaluation_suite()

    assert summary.failed == 0
    assert summary.pass_rate == 1.0
