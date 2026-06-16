"""GraphDB HTTP client helpers."""

import requests

from app.core.config import settings
from app.core.logging import get_logger

_TIMEOUT_SECONDS = 60
logger = get_logger(__name__)


def _repository_url() -> str:
    return f"{settings.graphdb_url.rstrip('/')}/repositories/{settings.graphdb_repository}"


def sparql_query(query: str) -> dict:
    logger.info("Executing GraphDB SPARQL query")
    response = requests.get(
        _repository_url(),
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def insert_turtle(turtle_data: str) -> None:
    logger.info("Inserting Turtle data into GraphDB")
    response = requests.post(
        f"{_repository_url()}/statements",
        data=turtle_data,
        headers={"Content-Type": "text/turtle"},
        timeout=_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
