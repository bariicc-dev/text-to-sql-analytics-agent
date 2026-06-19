from dataclasses import asdict

from app.demo.evaluation_questions import EVALUATION_CASES, EvaluationCase
from app.models.schemas import EvaluationCaseRead, EvaluationResult, EvaluationRunSummary
from app.providers.base import QueryProvider
from app.providers.factory import get_query_provider
from app.services.sql_validation_service import validate_sql


def list_evaluation_cases() -> list[EvaluationCaseRead]:
    return [EvaluationCaseRead(**asdict(case)) for case in EVALUATION_CASES]


def run_evaluation_suite(provider: QueryProvider | None = None) -> EvaluationRunSummary:
    query_provider = provider or get_query_provider()
    results = [_evaluate_case(case, query_provider) for case in EVALUATION_CASES]
    passed_count = sum(1 for result in results if result.passed)
    total_cases = len(results)
    failed_count = total_cases - passed_count
    pass_rate = round(passed_count / total_cases, 4) if total_cases else 0.0

    return EvaluationRunSummary(
        total_cases=total_cases,
        passed=passed_count,
        failed=failed_count,
        pass_rate=pass_rate,
        results=results,
    )


def _evaluate_case(case: EvaluationCase, provider: QueryProvider) -> EvaluationResult:
    candidate = provider.generate_query(case.question)
    actual_category = candidate.category
    actual_safety_status = _get_safety_status(candidate.sql, candidate.safety_status)
    matched_demo_query = candidate.sql is not None

    passed = (
        actual_category == case.expected_category
        and actual_safety_status == case.expected_safety_status
        and matched_demo_query == case.should_match_demo_query
    )

    return EvaluationResult(
        id=case.id,
        question=case.question,
        expected_category=case.expected_category,
        actual_category=actual_category,
        expected_safety_status=case.expected_safety_status,
        actual_safety_status=actual_safety_status,
        passed=passed,
        reason=_build_reason(
            passed=passed,
            expected_category=case.expected_category,
            actual_category=actual_category,
            expected_safety_status=case.expected_safety_status,
            actual_safety_status=actual_safety_status,
            expected_match=case.should_match_demo_query,
            actual_match=matched_demo_query,
        ),
    )


def _get_safety_status(sql: str | None, provider_safety_status: str) -> str:
    if sql is None:
        return provider_safety_status

    validation = validate_sql(sql)
    return "safe" if validation.is_safe else "blocked"


def _build_reason(
    passed: bool,
    expected_category: str,
    actual_category: str,
    expected_safety_status: str,
    actual_safety_status: str,
    expected_match: bool,
    actual_match: bool,
) -> str:
    if passed:
        return "Matched expected category and safety status."

    differences = []
    if expected_category != actual_category:
        differences.append(f"expected category {expected_category}, got {actual_category}")
    if expected_safety_status != actual_safety_status:
        differences.append(f"expected safety {expected_safety_status}, got {actual_safety_status}")
    if expected_match != actual_match:
        differences.append(f"expected demo match {expected_match}, got {actual_match}")

    return "; ".join(differences)
