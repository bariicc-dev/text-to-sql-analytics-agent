from fastapi import FastAPI

from app.api.routes.analytics import router as analytics_router
from app.api.routes.health import router as health_router
from app.api.routes.queries import router as queries_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(analytics_router)
    app.include_router(queries_router)
    return app


app = create_app()
