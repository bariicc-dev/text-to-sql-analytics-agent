from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics_service import (
    get_customer_segments,
    get_monthly_revenue,
    get_refund_rate,
    get_top_products,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/top-products")
def top_products(
    limit: int = Query(default=5, ge=1, le=25),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return get_top_products(db=db, limit=limit)


@router.get("/monthly-revenue")
def monthly_revenue(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return get_monthly_revenue(db=db)


@router.get("/refund-rate")
def refund_rate(db: Session = Depends(get_db)) -> dict[str, Any]:
    return get_refund_rate(db=db)


@router.get("/customer-segments")
def customer_segments(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return get_customer_segments(db=db)
