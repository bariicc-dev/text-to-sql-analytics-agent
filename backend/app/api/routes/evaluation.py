from fastapi import APIRouter

from app.models.schemas import EvaluationCaseRead, EvaluationRunRequest, EvaluationRunSummary
from app.services.evaluation_service import list_evaluation_cases, run_evaluation_suite

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("/cases", response_model=list[EvaluationCaseRead])
def read_evaluation_cases() -> list[EvaluationCaseRead]:
    return list_evaluation_cases()


@router.post("/run", response_model=EvaluationRunSummary)
def run_evaluation(request: EvaluationRunRequest | None = None) -> EvaluationRunSummary:
    provider = request.provider if request else "demo"
    return run_evaluation_suite(provider_name=provider)
