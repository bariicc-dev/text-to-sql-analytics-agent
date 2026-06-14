from app.main import app


def test_analytics_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/analytics/top-products" in paths
    assert "/analytics/monthly-revenue" in paths
    assert "/analytics/refund-rate" in paths
    assert "/analytics/customer-segments" in paths
