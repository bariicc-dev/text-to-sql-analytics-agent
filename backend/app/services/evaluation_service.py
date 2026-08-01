from dataclasses import asdict

from app.demo.evaluation_questions import EVALUATION_CASES, EvaluationCase
from app.models.schemas import EvaluationCaseRead, EvaluationResult, EvaluationRunSummary
from app.providers.base import QueryProvider
from app.providers.factory import get_query_provider
from app.services.sql_validation_service import validate_sql


def list_evaluation_cases() -> list[EvaluationCaseRead]:
    return [EvaluationCaseRead(**asdict(case)) for case in EVALUATION_CASES]


def run_evaluation_suite(
    provider_name: str = "demo",
    provider: QueryProvider | None = None,
) -> EvaluationRunSummary:
    query_provider = provider or get_query_provider(provider_name)
    selected_provider = getattr(query_provider, "source", provider_name)
    provider_status = getattr(query_provider, "status", "ready")
    results = [
        _evaluate_case(
            case=case,
            provider=query_provider,
            provider_name=selected_provider,
            provider_status=provider_status,
        )
        for case in EVALUATION_CASES
    ]
    passed_count = sum(1 for result in results if result.passed)
    total_cases = len(results)
    failed_count = total_cases - passed_count
    pass_rate = round(passed_count / total_cases, 4) if total_cases else 0.0

    return EvaluationRunSummary(
        provider=selected_provider,
        status=provider_status,
        total_cases=total_cases,
        passed=passed_count,
        failed=failed_count,
        pass_rate=pass_rate,
        results=results,
    )


def _evaluate_case(
    case: EvaluationCase,
    provider: QueryProvider,
    provider_name: str,
    provider_status: str,
) -> EvaluationResult:
    try:
        candidate = provider.generate_query(case.question)
    except Exception:
        return EvaluationResult(
            case_id=case.id,
            question=case.question,
            expected_category=case.expected_category,
            actual_category="error",
            expected_safety_status=case.expected_safety_status,
            actual_safety_status="error",
            provider=provider_name,
            candidate_returned=False,
            response_parseable=False,
            sql_generated=False,
            sql_validated=False,
            passed=False,
            reason="Provider did not return a query candidate.",
        )

    actual_category = candidate.category
    actual_safety_status, sql_validated = _get_safety_result(candidate.sql, candidate.safety_status)
    sql_generated = candidate.sql is not None

    passed = (
        provider_status == "ready"
        and actual_category == case.expected_category
        and actual_safety_status == case.expected_safety_status
        and sql_generated == case.should_match_demo_query
    )

    return EvaluationResult(
        case_id=case.id,
        question=case.question,
        expected_category=case.expected_category,
        actual_category=actual_category,
        expected_safety_status=case.expected_safety_status,
        actual_safety_status=actual_safety_status,
        provider=provider_name,
        candidate_returned=True,
        response_parseable=candidate.response_parseable,
        sql_generated=sql_generated,
        sql_validated=sql_validated,
        passed=passed,
        reason=_build_reason(
            passed=passed,
            provider_status=provider_status,
            provider_reason=candidate.reason,
            expected_category=case.expected_category,
            actual_category=actual_category,
            expected_safety_status=case.expected_safety_status,
            actual_safety_status=actual_safety_status,
            expected_match=case.should_match_demo_query,
            actual_match=sql_generated,
        ),
    )


def _get_safety_result(sql: str | None, provider_safety_status: str) -> tuple[str, bool]:
    if sql is None:
        return provider_safety_status, False

    validation = validate_sql(sql)
    return ("safe" if validation.is_safe else "blocked"), validation.is_safe


def _build_reason(
    passed: bool,
    provider_status: str,
    provider_reason: str | None,
    expected_category: str,
    actual_category: str,
    expected_safety_status: str,
    actual_safety_status: str,
    expected_match: bool,
    actual_match: bool,
) -> str:
    if passed:
        return "Matched expected category and safety status."

    if provider_status == "not_configured":
        return provider_reason or "Provider is not configured."

    differences = []
    if expected_category != actual_category:
        differences.append(f"expected category {expected_category}, got {actual_category}")
    if expected_safety_status != actual_safety_status:
        differences.append(f"expected safety {expected_safety_status}, got {actual_safety_status}")
    if expected_match != actual_match:
        differences.append(f"expected SQL generation {expected_match}, got {actual_match}")

    return "; ".join(differences)
