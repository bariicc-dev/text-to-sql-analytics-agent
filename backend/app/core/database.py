from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
application_engine = create_engine(settings.application_database_url)
generated_query_engine = create_engine(settings.generated_query_database_url)

ApplicationSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=application_engine,
)
GeneratedQuerySessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=generated_query_engine,
)


def get_db() -> Generator[Session, None, None]:
    db = ApplicationSessionLocal()
    try:
        yield db
    finally:
        db.close()
