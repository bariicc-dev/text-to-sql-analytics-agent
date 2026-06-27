from fastapi import APIRouter

from app.models.schemas import ChatRequest, PromptContextResponse
from app.prompting.builder import build_sql_prompt

router = APIRouter(prefix="/prompt", tags=["prompt"])


@router.post("/context", response_model=PromptContextResponse)
def build_prompt_context(request: ChatRequest) -> PromptContextResponse:
    return PromptContextResponse(
        question=request.question,
        prompt=build_sql_prompt(request.question),
    )
