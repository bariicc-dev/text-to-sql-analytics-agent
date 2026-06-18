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
from app.models.database_models import Customer, Feedback, Order, OrderItem, Product, QueryLog


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
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app), testing_session_local
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def seed_chat_data(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as db:
        customer = Customer(
            id=1,
            name="Nora Adams",
            email="nora.adams@example.com",
            segment="Consumer",
            country="France",
            created_at=date(2025, 1, 8),
        )
        product = Product(
            id=1,
            name="Everyday Backpack",
            category="Bags",
            unit_price=Decimal("79.00"),
            unit_cost=Decimal("32.00"),
        )
        order = Order(
            id=1,
            customer_id=1,
            order_date=date(2025, 4, 2),
            status="completed",
            channel="web",
        )
        order_item = OrderItem(
            id=1,
            order_id=1,
            product_id=1,
            quantity=2,
            unit_price=Decimal("79.00"),
        )
        db.add_all([customer, product, order, order_item])
        db.commit()


def create_log(session_factory: sessionmaker[Session], safety_status: str = "safe") -> QueryLog:
    with session_factory() as db:
        query_log = QueryLog(
            question="What are the top products?",
            generated_sql="SELECT id FROM products LIMIT 5",
            safety_status=safety_status,
            error_message=None,
        )
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        return query_log


def test_chat_creates_query_log_for_matched_question(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = test_client
    seed_chat_data(session_factory)

    response = client.post("/chat", json={"question": "What are the top 5 products by revenue?"})

    assert response.status_code == 200
    assert response.json()["safety_status"] == "safe"
    with session_factory() as db:
        logs = db.query(QueryLog).all()
        assert len(logs) == 1
        assert logs[0].question == "What are the top 5 products by revenue?"
        assert logs[0].safety_status == "safe"
        assert logs[0].generated_sql is not None


def test_chat_creates_query_log_for_unmatched_question(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = test_client

    response = client.post("/chat", json={"question": "Which warehouse is slowest?"})

    assert response.status_code == 200
    assert response.json()["safety_status"] == "not_generated"
    with session_factory() as db:
        log = db.query(QueryLog).one()
        assert log.safety_status == "not_generated"
        assert log.generated_sql is None
        assert log.error_message == "No demo query matched this question."


def test_read_query_logs_returns_logs(test_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, session_factory = test_client
    create_log(session_factory)

    response = client.get("/queries/logs")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["safety_status"] == "safe"


def test_read_query_log_returns_one_log(test_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, session_factory = test_client
    query_log = create_log(session_factory)

    response = client.get(f"/queries/logs/{query_log.id}")

    assert response.status_code == 200
    assert response.json()["id"] == query_log.id


def test_read_query_log_returns_404_when_missing(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = test_client

    response = client.get("/queries/logs/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Query log not found."


def test_create_feedback_for_existing_query_log(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = test_client
    query_log = create_log(session_factory)

    response = client.post(
        "/feedback",
        json={"query_log_id": query_log.id, "rating": 5, "comment": "Useful answer"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["query_log_id"] == query_log.id
    assert data["rating"] == 5


def test_create_feedback_rejects_invalid_rating(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = test_client
    query_log = create_log(session_factory)

    response = client.post("/feedback", json={"query_log_id": query_log.id, "rating": 6})

    assert response.status_code == 422


def test_create_feedback_returns_404_for_missing_query_log(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = test_client

    response = client.post("/feedback", json={"query_log_id": 999, "rating": 4})

    assert response.status_code == 404
    assert response.json()["detail"] == "Query log not found."


def test_read_feedback_for_query_log(test_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, session_factory = test_client
    query_log = create_log(session_factory)
    with session_factory() as db:
        db.add(Feedback(query_log_id=query_log.id, rating=4, comment="Clear enough"))
        db.commit()

    response = client.get(f"/feedback/query/{query_log.id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["rating"] == 4
