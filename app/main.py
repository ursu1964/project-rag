"""FastAPI application entrypoint."""

from typing import cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import BaseRoute

from app.api.routes_audit import router as audit_router
from app.api.routes_cognitive import router as cognitive_router
from app.api.routes_connectors import router as connectors_router
from app.api.routes_devops import router as devops_router
from app.api.routes_documents import router as documents_router
from app.api.routes_embeddings import router as embeddings_router
from app.api.routes_evaluation import router as evaluation_router
from app.api.routes_feedback import router as feedback_router
from app.api.routes_graph import router as graph_router
from app.api.routes_health import router as health_router
from app.api.routes_memory import router as memory_router
from app.api.routes_operations import router as operations_router
from app.api.routes_query import router as query_router
from app.api.routes_retrieval import router as retrieval_router
from app.api.routes_sources import router as sources_router
from app.api.routes_workflow_audit import router as workflow_audit_router
from app.core.config import settings
from app.core.logging import get_logger
from app.core.settings_validator import validate_settings
from app.core.telemetry import setup_telemetry
from app.gateway.middleware import install_gateway_middleware
from app.graph.graphdb_client import ensure_repository_ready

logger = get_logger(__name__)
_VERSION_PREFIX = "/api/v1"


def _expand_included_routes(routes: list[object]) -> list[BaseRoute]:
    """Flatten included routers for FastAPI versions that expose router sentinels."""
    expanded: list[BaseRoute] = []
    for route in routes:
        if hasattr(route, "path"):
            expanded.append(cast(BaseRoute, route))
            continue

        nested_router = getattr(route, "router", None) or getattr(route, "original_router", None)
        nested_routes = getattr(nested_router, "routes", None)
        if nested_routes:
            expanded.extend(_expand_included_routes(list(nested_routes)))
        else:
            expanded.append(cast(BaseRoute, route))
    return expanded


def create_app() -> FastAPI:
    try:
        validate_settings()
    except RuntimeError as exc:
        logger.critical("Startup validation failed: %s", exc)
        raise
    logger.info("Creating ProjectRAG FastAPI application")
    if settings.graphdb_ensure_repository_on_startup:
        try:
            ensure_repository_ready()
        except Exception as exc:
            # Do not block startup; GraphDB calls remain lazily resilient.
            logger.warning("GraphDB repository readiness check failed at startup: %s", exc)
    app = FastAPI(title="ProjectRAG")
    install_gateway_middleware(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_telemetry(app)
    routers = (
        health_router,
        query_router,
        embeddings_router,
        retrieval_router,
        sources_router,
        documents_router,
        connectors_router,
        audit_router,
        devops_router,
        evaluation_router,
        feedback_router,
        graph_router,
        memory_router,
        operations_router,
        cognitive_router,
        workflow_audit_router,
    )
    for router in routers:
        app.include_router(router)
        app.include_router(router, prefix=_VERSION_PREFIX)

    @app.get(_VERSION_PREFIX, include_in_schema=False)
    async def api_v1_root() -> dict[str, str]:
        return {"status": "ok", "version": "v1"}

    @app.get(f"{_VERSION_PREFIX}/", include_in_schema=False)
    async def api_v1_root_slash() -> dict[str, str]:
        return {"status": "ok", "version": "v1"}

    if any(not hasattr(route, "path") for route in app.router.routes):
        app.router.routes[:] = _expand_included_routes(list(app.router.routes))
    return app


app = create_app()
