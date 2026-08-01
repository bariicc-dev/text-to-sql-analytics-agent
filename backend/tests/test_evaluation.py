from fastapi.testclient import TestClient

from app.core.config import Settings
from app.demo.evaluation_questions import EVALUATION_CASES
from app.main import app
from app.providers.demo_provider import DemoQueryProvider
from app.providers.llm_provider import LLMQueryProvider
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
    assert data["provider"] == "demo"
    assert data["status"] == "ready"
    assert data["total_cases"] == len(EVALUATION_CASES)
    assert data["passed"] + data["failed"] == data["total_cases"]
    assert 0 <= data["pass_rate"] <= 1
    assert len(data["results"]) == data["total_cases"]


def test_run_evaluation_accepts_demo_provider() -> None:
    response = client.post("/evaluation/run", json={"provider": "demo"})

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "demo"
    assert all(result["provider"] == "demo" for result in data["results"])


def test_evaluation_results_include_provider_and_sql_fields() -> None:
    response = client.post("/evaluation/run")

    result = response.json()["results"][0]
    assert {
        "case_id",
        "provider",
        "candidate_returned",
        "response_parseable",
        "sql_generated",
        "sql_validated",
    }.issubset(result)
    assert result["sql_generated"] is True
    assert result["sql_validated"] is True


def test_run_evaluation_handles_unconfigured_llm_without_external_call(monkeypatch) -> None:
    settings = Settings(
        llm_provider=None,
        llm_model=None,
        llm_api_base_url=None,
        llm_api_key=None,
    )
    monkeypatch.setattr("app.providers.llm_provider.get_settings", lambda: settings)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("External provider call was attempted")

    monkeypatch.setattr(LLMQueryProvider, "_post_chat_completion", fail_if_called)

    response = client.post("/evaluation/run", json={"provider": "llm"})

    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "llm"
    assert data["status"] == "not_configured"
    assert data["passed"] == 0
    assert data["failed"] == len(EVALUATION_CASES)
    assert all(result["provider"] == "llm" for result in data["results"])
    assert all(result["candidate_returned"] is True for result in data["results"])
    assert all(result["response_parseable"] is False for result in data["results"])
    assert all(result["sql_generated"] is False for result in data["results"])
    assert all(result["sql_validated"] is False for result in data["results"])


def test_compare_evaluation_returns_demo_and_unconfigured_llm(monkeypatch) -> None:
    settings = Settings(
        llm_provider=None,
        llm_model=None,
        llm_api_base_url=None,
        llm_api_key=None,
    )
    monkeypatch.setattr("app.providers.llm_provider.get_settings", lambda: settings)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("External provider call was attempted")

    monkeypatch.setattr(LLMQueryProvider, "_post_chat_completion", fail_if_called)

    response = client.post("/evaluation/compare")

    assert response.status_code == 200
    data = response.json()
    assert data["providers"] == ["demo", "llm"]
    assert data["total_cases"] == len(EVALUATION_CASES)
    assert set(data["results_by_provider"]) == {"demo", "llm"}
    assert len(data["results_by_provider"]["demo"]) == len(EVALUATION_CASES)
    assert len(data["results_by_provider"]["llm"]) == len(EVALUATION_CASES)
    assert data["summary_by_provider"]["demo"] == {
        "passed": len(EVALUATION_CASES),
        "failed": 0,
        "pass_rate": 100.0,
        "status": "ready",
    }
    assert data["summary_by_provider"]["llm"] == {
        "passed": 0,
        "failed": len(EVALUATION_CASES),
        "pass_rate": 0.0,
        "status": "not_configured",
    }


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
    candidate = DemoQueryProvider().generate_query("What are the top 5 products by revenue?")

    assert candidate.category == "top_products"
    assert candidate.sql is not None


def test_evaluation_suite_passes_current_cases() -> None:
    summary = run_evaluation_suite()

    assert summary.failed == 0
    assert summary.pass_rate == 1.0
