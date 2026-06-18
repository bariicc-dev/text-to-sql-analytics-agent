from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database_models import Feedback
from app.models.schemas import FeedbackCreate
from app.services.logging_service import get_query_log


class QueryLogNotFoundError(Exception):
    pass


def create_feedback(db: Session, feedback: FeedbackCreate) -> Feedback:
    if get_query_log(db=db, query_log_id=feedback.query_log_id) is None:
        raise QueryLogNotFoundError

    feedback_item = Feedback(
        query_log_id=feedback.query_log_id,
        rating=feedback.rating,
        comment=feedback.comment,
        customer_id=feedback.customer_id,
    )
    db.add(feedback_item)
    db.commit()
    db.refresh(feedback_item)
    return feedback_item


def list_feedback_for_query_log(db: Session, query_log_id: int) -> list[Feedback]:
    if get_query_log(db=db, query_log_id=query_log_id) is None:
        raise QueryLogNotFoundError

    statement = (
        select(Feedback)
        .where(Feedback.query_log_id == query_log_id)
        .order_by(Feedback.created_at, Feedback.id)
    )
    return list(db.scalars(statement))
