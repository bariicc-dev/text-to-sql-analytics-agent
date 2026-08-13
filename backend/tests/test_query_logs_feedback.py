import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.models.database_models import Feedback, QueryLog
from app.models.schemas import MAX_QUESTION_LENGTH
from app.providers.base import QueryCandidate


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
    seeded_test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = seeded_test_client

    response = client.post("/chat", json={"question": "What are the top 5 products by revenue?"})

    assert response.status_code == 200
    assert response.json()["safety_status"] == "safe"
    assert response.json()["source"] == "demo"
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


def test_chat_strips_question_whitespace(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, session_factory = test_client

    response = client.post("/chat", json={"question": "  Which warehouse is slowest?  "})

    assert response.status_code == 200
    with session_factory() as db:
        log = db.query(QueryLog).one()
        assert log.question == "Which warehouse is slowest?"


@pytest.mark.parametrize("question", ["", "   "])
def test_chat_rejects_blank_question(
    question: str,
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = test_client

    response = client.post("/chat", json={"question": question})

    assert response.status_code == 422


def test_chat_rejects_question_over_length_limit(
    test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = test_client

    response = client.post("/chat", json={"question": "x" * (MAX_QUESTION_LENGTH + 1)})

    assert response.status_code == 422


def test_chat_rolls_back_and_logs_execution_error(
    test_client: tuple[TestClient, sessionmaker[Session]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session_factory = test_client
    rollback_calls: list[Session] = []
    original_rollback = Session.rollback

    class InvalidSqlProvider:
        def generate_query(self, question: str) -> QueryCandidate:
            return QueryCandidate(
                category="invalid_sql",
                sql="SELECT missing_column FROM products LIMIT 5",
                source="test",
            )

    def track_rollback(db: Session) -> None:
        rollback_calls.append(db)
        original_rollback(db)

    monkeypatch.setattr("app.services.chat_service.get_query_provider", InvalidSqlProvider)
    monkeypatch.setattr(Session, "rollback", track_rollback)

    response = client.post("/chat", json={"question": "Run the failing query."})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "The query could not be executed safely."
    assert data["safety_status"] == "error"
    assert "no such column" not in str(data).lower()
    assert len(rollback_calls) == 1

    with session_factory() as db:
        log = db.query(QueryLog).one()
        assert log.safety_status == "error"
        assert log.error_message == "The query could not be executed safely."


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
