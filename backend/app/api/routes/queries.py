from fastapi import APIRouter

from app.models.schemas import SqlValidationRequest, SqlValidationResponse
from app.services.sql_validation_service import validate_sql

router = APIRouter(tags=["queries"])


@router.post("/validate-sql", response_model=SqlValidationResponse)
def validate_sql_query(request: SqlValidationRequest) -> SqlValidationResponse:
    return validate_sql(request.sql)
