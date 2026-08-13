from datetime import timedelta

from app.core.database import Base
from app.models import database_models


def test_database_tables_are_registered() -> None:
    assert database_models.Customer.__tablename__ == "customers"

    expected_tables = {
        "customers",
        "products",
        "orders",
        "order_items",
        "refunds",
        "query_logs",
        "feedback",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_log_timestamp_defaults_are_timezone_aware_utc() -> None:
    for model in (database_models.QueryLog, database_models.Feedback):
        created_at = model.__table__.c.created_at
        timestamp = created_at.default.arg(None)

        assert created_at.type.timezone is True
        assert timestamp.utcoffset() == timedelta(0)
