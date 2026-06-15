from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.models.database_models import Customer, Order, OrderItem, Product, Refund


CUSTOMERS = [
    Customer(id=1, name="Nora Adams", email="nora.adams@example.com", segment="Consumer", country="France", created_at=date(2025, 1, 8)),
    Customer(id=2, name="Liam Carter", email="liam.carter@example.com", segment="Consumer", country="Germany", created_at=date(2025, 1, 18)),
    Customer(id=3, name="Maya Chen", email="maya.chen@example.com", segment="Small Business", country="France", created_at=date(2025, 2, 4)),
    Customer(id=4, name="Owen Singh", email="owen.singh@example.com", segment="Small Business", country="Netherlands", created_at=date(2025, 2, 22)),
    Customer(id=5, name="Amira Rossi", email="amira.rossi@example.com", segment="Enterprise", country="Italy", created_at=date(2025, 3, 9)),
]

PRODUCTS = [
    Product(id=1, name="Everyday Backpack", category="Bags", unit_price=Decimal("79.00"), unit_cost=Decimal("32.00")),
    Product(id=2, name="Wireless Keyboard", category="Electronics", unit_price=Decimal("119.00"), unit_cost=Decimal("54.00")),
    Product(id=3, name="Desk Lamp", category="Home Office", unit_price=Decimal("49.00"), unit_cost=Decimal("18.00")),
    Product(id=4, name="Noise Cancelling Headphones", category="Electronics", unit_price=Decimal("229.00"), unit_cost=Decimal("108.00")),
    Product(id=5, name="Travel Mug", category="Accessories", unit_price=Decimal("24.00"), unit_cost=Decimal("8.00")),
]

ORDERS = [
    Order(id=1, customer_id=1, order_date=date(2025, 4, 2), status="completed", channel="web"),
    Order(id=2, customer_id=2, order_date=date(2025, 4, 7), status="completed", channel="web"),
    Order(id=3, customer_id=3, order_date=date(2025, 5, 3), status="completed", channel="sales"),
    Order(id=4, customer_id=4, order_date=date(2025, 5, 16), status="completed", channel="partner"),
    Order(id=5, customer_id=5, order_date=date(2025, 6, 4), status="completed", channel="sales"),
    Order(id=6, customer_id=1, order_date=date(2025, 6, 15), status="refunded", channel="web"),
]

ORDER_ITEMS = [
    OrderItem(id=1, order_id=1, product_id=1, quantity=1, unit_price=Decimal("79.00")),
    OrderItem(id=2, order_id=1, product_id=5, quantity=2, unit_price=Decimal("24.00")),
    OrderItem(id=3, order_id=2, product_id=2, quantity=1, unit_price=Decimal("119.00")),
    OrderItem(id=4, order_id=3, product_id=4, quantity=2, unit_price=Decimal("229.00")),
    OrderItem(id=5, order_id=3, product_id=3, quantity=3, unit_price=Decimal("49.00")),
    OrderItem(id=6, order_id=4, product_id=1, quantity=4, unit_price=Decimal("79.00")),
    OrderItem(id=7, order_id=5, product_id=2, quantity=3, unit_price=Decimal("119.00")),
    OrderItem(id=8, order_id=5, product_id=4, quantity=1, unit_price=Decimal("229.00")),
    OrderItem(id=9, order_id=6, product_id=4, quantity=1, unit_price=Decimal("229.00")),
]

REFUNDS = [
    Refund(id=1, order_id=6, product_id=4, refund_date=date(2025, 6, 20), amount=Decimal("229.00"), reason="Customer returned the item"),
]


def seed_database(session: Session) -> None:
    if session.query(Customer).first():
        return

    session.add_all(CUSTOMERS)
    session.add_all(PRODUCTS)
    session.add_all(ORDERS)
    session.add_all(ORDER_ITEMS)
    session.add_all(REFUNDS)
    session.commit()


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)


if __name__ == "__main__":
    main()
