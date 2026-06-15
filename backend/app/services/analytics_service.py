from decimal import Decimal
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.database_models import Customer, Order, OrderItem, Product, Refund


def _money(value: Decimal | int | float | None) -> float:
    if value is None:
        return 0.0
    return round(float(value), 2)


def get_top_products(db: Session, limit: int = 5) -> list[dict[str, Any]]:
    revenue = func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue")
    statement = (
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.category,
            func.sum(OrderItem.quantity).label("units_sold"),
            revenue,
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status.in_(["completed", "refunded"]))
        .group_by(Product.id, Product.name, Product.category)
        .order_by(desc(revenue))
        .limit(limit)
    )

    rows = db.execute(statement).mappings().all()
    return [
        {
            "product_id": row["product_id"],
            "product_name": row["product_name"],
            "category": row["category"],
            "units_sold": row["units_sold"],
            "revenue": _money(row["revenue"]),
        }
        for row in rows
    ]


def get_monthly_revenue(db: Session) -> list[dict[str, Any]]:
    revenue = func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue")
    statement = (
        select(
            func.extract("year", Order.order_date).label("year"),
            func.extract("month", Order.order_date).label("month"),
            revenue,
            func.count(func.distinct(Order.id)).label("order_count"),
        )
        .join(OrderItem, OrderItem.order_id == Order.id)
        .where(Order.status.in_(["completed", "refunded"]))
        .group_by("year", "month")
        .order_by("year", "month")
    )

    rows = db.execute(statement).mappings().all()
    return [
        {
            "year": int(row["year"]),
            "month": int(row["month"]),
            "revenue": _money(row["revenue"]),
            "order_count": row["order_count"],
        }
        for row in rows
    ]


def get_refund_rate(db: Session) -> dict[str, Any]:
    total_orders = db.scalar(select(func.count(Order.id))) or 0
    refunded_orders = db.scalar(select(func.count(func.distinct(Refund.order_id)))) or 0
    refund_amount = db.scalar(select(func.sum(Refund.amount))) or Decimal("0")

    return {
        "total_orders": total_orders,
        "refunded_orders": refunded_orders,
        "refund_rate": round(refunded_orders / total_orders, 4) if total_orders else 0.0,
        "refund_amount": _money(refund_amount),
    }


def get_customer_segments(db: Session) -> list[dict[str, Any]]:
    revenue = func.sum(OrderItem.quantity * OrderItem.unit_price).label("revenue")
    statement = (
        select(
            Customer.segment,
            func.count(func.distinct(Customer.id)).label("customer_count"),
            func.count(func.distinct(Order.id)).label("order_count"),
            revenue,
        )
        .join(Order, Order.customer_id == Customer.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .where(Order.status.in_(["completed", "refunded"]))
        .group_by(Customer.segment)
        .order_by(desc(revenue))
    )

    rows = db.execute(statement).mappings().all()
    return [
        {
            "segment": row["segment"],
            "customer_count": row["customer_count"],
            "order_count": row["order_count"],
            "revenue": _money(row["revenue"]),
        }
        for row in rows
    ]
