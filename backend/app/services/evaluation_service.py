from dataclasses import asdict

from app.demo.evaluation_questions import EVALUATION_CASES, EvaluationCase
from app.models.schemas import EvaluationCaseRead, EvaluationResult, EvaluationRunSummary
from app.services.demo_sql_generation_service import generate_demo_sql, has_unsafe_intent
from app.services.sql_validation_service import validate_sql


def list_evaluation_cases() -> list[EvaluationCaseRead]:
    return [EvaluationCaseRead(**asdict(case)) for case in EVALUATION_CASES]


def run_evaluation_suite() -> EvaluationRunSummary:
    results = [_evaluate_case(case) for case in EVALUATION_CASES]
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


def _evaluate_case(case: EvaluationCase) -> EvaluationResult:
    demo_query = generate_demo_sql(case.question)
    actual_category = demo_query.category if demo_query is not None else "unsupported"
    actual_safety_status = _get_safety_status(case.question, demo_query.sql if demo_query else None)
    matched_demo_query = demo_query is not None

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


def _get_safety_status(question: str, sql: str | None) -> str:
    if sql is None:
        return "blocked" if has_unsafe_intent(question) else "not_generated"

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
