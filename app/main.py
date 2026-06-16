"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.core.logging import get_logger
from app.core.settings_validator import validate_settings

from app.api.routes_cognitive import router as cognitive_router
from app.api.routes_devops import router as devops_router
from app.api.routes_documents import router as documents_router
from app.api.routes_graph import router as graph_router
from app.api.routes_health import router as health_router
from app.api.routes_memory import router as memory_router
from app.api.routes_query import router as query_router

logger = get_logger(__name__)


def create_app() -> FastAPI:
    validate_settings()
    logger.info("Creating ProjectRAG FastAPI application")
    app = FastAPI(title="ProjectRAG")
    app.include_router(health_router)
    app.include_router(query_router)
    app.include_router(documents_router)
    app.include_router(devops_router)
    app.include_router(graph_router)
    app.include_router(memory_router)
    app.include_router(cognitive_router)
    # Some FastAPI/Starlette versions can leave internal router sentinel objects
    # in ``app.routes``. They are not dispatchable HTTP routes and do not expose
    # ``path``, which breaks route introspection in tests and tooling.
    app.routes[:] = [route for route in app.routes if hasattr(route, "path")]
    return app


app = create_app()
