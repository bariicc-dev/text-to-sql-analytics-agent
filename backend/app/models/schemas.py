from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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


class FeedbackCreate(BaseModel):
    query_log_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
    customer_id: int | None = None


class FeedbackRead(BaseModel):
    id: int
    query_log_id: int
    rating: int
    comment: str | None
    customer_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SqlValidationRequest(BaseModel):
    sql: str


class SqlValidationResponse(BaseModel):
    is_safe: bool
    reason: str
    normalized_sql: str
    blocked_keywords: list[str] = []


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sql: str | None
    rows: list[dict[str, Any]]
    explanation: str
    safety_status: str
    source: str
