from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CustomerRead(BaseModel):
    id: int
    name: str
    email: str
    segment: str
    country: str
    created_at: date

    model_config = ConfigDict(from_attributes=True)


class ProductRead(BaseModel):
    id: int
    name: str
    category: str
    unit_price: Decimal
    unit_cost: Decimal

    model_config = ConfigDict(from_attributes=True)


class QueryLogRead(BaseModel):
    id: int
    question: str
    generated_sql: str | None
    safety_status: str
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SqlValidationRequest(BaseModel):
    sql: str


class SqlValidationResponse(BaseModel):
    is_safe: bool
    reason: str
    normalized_sql: str
    blocked_keywords: list[str] = []
