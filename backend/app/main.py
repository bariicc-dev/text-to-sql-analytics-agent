from fastapi import FastAPI

from app.api.routes.analytics import router as analytics_router
from app.api.routes.chat import router as chat_router
from app.api.routes.evaluation import router as evaluation_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.queries import router as queries_router
from app.api.routes.schema_context import router as schema_context_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(analytics_router)
    app.include_router(queries_router)
    app.include_router(chat_router)
    app.include_router(feedback_router)
    app.include_router(evaluation_router)
    app.include_router(schema_context_router)
    return app


app = create_app()
