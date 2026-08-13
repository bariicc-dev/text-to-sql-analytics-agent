from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker


def test_top_products_returns_ranked_product(
    seeded_test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = seeded_test_client

    response = client.get("/analytics/top-products", params={"limit": 1})

    assert response.status_code == 200
    assert response.json() == [
        {
            "product_id": 1,
            "product_name": "Everyday Backpack",
            "category": "Bags",
            "units_sold": 2,
            "revenue": 158.0,
        }
    ]


def test_monthly_revenue_returns_seeded_month(
    seeded_test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = seeded_test_client

    response = client.get("/analytics/monthly-revenue")

    assert response.status_code == 200
    assert response.json() == [
        {
            "year": 2025,
            "month": 4,
            "revenue": 158.0,
            "order_count": 1,
        }
    ]


def test_refund_rate_returns_seeded_refund(
    seeded_test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = seeded_test_client

    response = client.get("/analytics/refund-rate")

    assert response.status_code == 200
    assert response.json() == {
        "total_orders": 1,
        "refunded_orders": 1,
        "refund_rate": 1.0,
        "refund_amount": 79.0,
    }


def test_customer_segments_returns_seeded_segment(
    seeded_test_client: tuple[TestClient, sessionmaker[Session]],
) -> None:
    client, _ = seeded_test_client

    response = client.get("/analytics/customer-segments")

    assert response.status_code == 200
    assert response.json() == [
        {
            "segment": "Consumer",
            "customer_count": 1,
            "order_count": 1,
            "revenue": 158.0,
        }
    ]
