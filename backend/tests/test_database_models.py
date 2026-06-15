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
