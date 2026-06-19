from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import FeedbackCreate, FeedbackRead
from app.services.feedback_service import (
    QueryLogNotFoundError,
    create_feedback,
    list_feedback_for_query_log,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


def _query_log_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Query log not found.")


@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def create_feedback_item(
    request: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    try:
        return create_feedback(db=db, feedback=request)
    except QueryLogNotFoundError as exc:
        raise _query_log_not_found() from exc


@router.get("/query/{query_log_id}", response_model=list[FeedbackRead])
def read_feedback_for_query_log(
    query_log_id: int,
    db: Session = Depends(get_db),
) -> list[FeedbackRead]:
    try:
        return list_feedback_for_query_log(db=db, query_log_id=query_log_id)
    except QueryLogNotFoundError as exc:
        raise _query_log_not_found() from exc
