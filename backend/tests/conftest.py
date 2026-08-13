from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.database_models import Customer, Order, OrderItem, Product, Refund


@pytest.fixture()
def test_client() -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        with testing_session_local() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app), testing_session_local
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def seeded_test_client(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> tuple[TestClient, sessionmaker[Session]]:
    _, session_factory = test_client
    with session_factory() as db:
        db.add_all(
            [
                Customer(
                    id=1,
                    name="Nora Adams",
                    email="nora.adams@example.com",
                    segment="Consumer",
                    country="France",
                    created_at=date(2025, 1, 8),
                ),
                Product(
                    id=1,
                    name="Everyday Backpack",
                    category="Bags",
                    unit_price=Decimal("79.00"),
                    unit_cost=Decimal("32.00"),
                ),
                Order(
                    id=1,
                    customer_id=1,
                    order_date=date(2025, 4, 2),
                    status="refunded",
                    channel="web",
                ),
                OrderItem(
                    id=1,
                    order_id=1,
                    product_id=1,
                    quantity=2,
                    unit_price=Decimal("79.00"),
                ),
                Refund(
                    id=1,
                    order_id=1,
                    product_id=1,
                    refund_date=date(2025, 4, 8),
                    amount=Decimal("79.00"),
                    reason="Customer returned the item",
                ),
            ]
        )
        db.commit()

    return test_client
