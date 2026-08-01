from fastapi import APIRouter

from app.models.schemas import (
    EvaluationCaseRead,
    EvaluationComparisonRequest,
    EvaluationComparisonResponse,
    EvaluationRunRequest,
    EvaluationRunSummary,
)
from app.services.evaluation_service import (
    compare_provider_evaluations,
    list_evaluation_cases,
    run_evaluation_suite,
)

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/cases", response_model=list[EvaluationCaseRead])
def read_evaluation_cases() -> list[EvaluationCaseRead]:
    return list_evaluation_cases()


@router.post("/run", response_model=EvaluationRunSummary)
def run_evaluation(request: EvaluationRunRequest | None = None) -> EvaluationRunSummary:
    provider = request.provider if request else "demo"
    return run_evaluation_suite(provider_name=provider)


@router.post("/compare", response_model=EvaluationComparisonResponse)
def compare_providers(request: EvaluationComparisonRequest | None = None) -> EvaluationComparisonResponse:
    providers = request.providers if request else None
    return compare_provider_evaluations(provider_names=providers)
