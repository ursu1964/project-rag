"""GraphDB HTTP client helpers."""

from copy import deepcopy
from typing import Any

import requests

from app.core.config import settings
from app.core.logging import get_logger
from app.ragos.cognitive_cache import cache_graph_query, get_cached_graph_query, invalidate_by_tag

_TIMEOUT_SECONDS = 60
logger = get_logger(__name__)
_repository_ready = False


def _repository_url() -> str:
    return f"{settings.graphdb_url.rstrip('/')}/repositories/{settings.graphdb_repository}"


def _repository_config() -> str:
    repository_id = settings.graphdb_repository
    return f"""@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rep: <http://www.openrdf.org/config/repository#> .
@prefix sr: <http://www.openrdf.org/config/repository/sail#> .
@prefix sail: <http://www.openrdf.org/config/sail#> .
@prefix graphdb: <http://www.ontotext.com/config/graphdb#> .

[] a rep:Repository ;
    rep:repositoryID "{repository_id}" ;
    rdfs:label "ProjectRAG" ;
    rep:repositoryImpl [
        rep:repositoryType "graphdb:SailRepository" ;
        sr:sailImpl [
            sail:sailType "graphdb:Sail" ;
            graphdb:ruleset "rdfsplus-optimized" ;
            graphdb:disableSameAs "true" ;
            graphdb:enableContextIndex "true" ;
            graphdb:enablePredicateList "true" ;
            graphdb:entityIndexSize "10000000" ;
            graphdb:entityIdSize "32" ;
            graphdb:imports "" ;
            graphdb:repositoryType "file-repository"
        ]
    ] .
"""


def create_repository() -> None:
    """Create the configured GraphDB repository if it is missing."""
    logger.info("Creating GraphDB repository: %s", settings.graphdb_repository)
    response = requests.post(
        f"{settings.graphdb_url.rstrip('/')}/rest/repositories",
        files={
            "config": (
                f"{settings.graphdb_repository}.ttl",
                _repository_config(),
                "text/turtle",
            )
        },
        timeout=_TIMEOUT_SECONDS,
    )
    if response.status_code not in {200, 201, 204, 400}:
        response.raise_for_status()


def ensure_repository_ready() -> None:
    """Ensure configured GraphDB repository exists and is reachable.

    This is safe to call repeatedly; success is memoized for process lifetime.
    """
    global _repository_ready
    if _repository_ready:
        return

    response = requests.get(
        f"{settings.graphdb_url.rstrip('/')}/rest/repositories/{settings.graphdb_repository}",
        timeout=_TIMEOUT_SECONDS,
    )
    if response.status_code == 404:
        create_repository()
    elif response.status_code not in {200, 204}:
        response.raise_for_status()

    _repository_ready = True


def sparql_query(query: str) -> dict:
    ensure_repository_ready()
    cached = get_cached_graph_query(query)
    if isinstance(cached, dict):
        logger.info("Returning cached GraphDB SPARQL query result")
        return deepcopy(cached)

    logger.info("Executing GraphDB SPARQL query")
    response = requests.get(
        _repository_url(),
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
        timeout=_TIMEOUT_SECONDS,
    )
    if response.status_code == 404:
        create_repository()
        response = requests.get(
            _repository_url(),
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=_TIMEOUT_SECONDS,
        )
    response.raise_for_status()
    result = response.json()
    cache_graph_query(query, deepcopy(result))
    return result


def insert_turtle(turtle_data: str) -> None:
    ensure_repository_ready()
    logger.info("Inserting Turtle data into GraphDB")
    response = requests.post(
        f"{_repository_url()}/statements",
        data=turtle_data,
        headers={"Content-Type": "text/turtle"},
        timeout=_TIMEOUT_SECONDS,
    )
    if response.status_code == 404:
        create_repository()
        response = requests.post(
            f"{_repository_url()}/statements",
            data=turtle_data,
            headers={"Content-Type": "text/turtle"},
            timeout=_TIMEOUT_SECONDS,
        )
    response.raise_for_status()
    invalidate_by_tag("graph")


def sparql_update(update: str) -> None:
    """Execute a SPARQL update against the configured repository."""
    ensure_repository_ready()
    logger.info("Executing GraphDB SPARQL update")
    response = requests.post(
        f"{_repository_url()}/statements",
        data={"update": update},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=_TIMEOUT_SECONDS,
    )
    if response.status_code == 404:
        create_repository()
        response = requests.post(
            f"{_repository_url()}/statements",
            data={"update": update},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=_TIMEOUT_SECONDS,
        )
    response.raise_for_status()
    invalidate_by_tag("graph")


def delete_graph_facts(facts: list[dict[str, Any]]) -> int:
    """Delete GraphDB triples represented by PostgreSQL graph facts."""
    triples = []
    for fact in facts:
        subject = fact.get("subject")
        predicate = fact.get("predicate")
        obj = fact.get("object")
        if not subject or not predicate or not obj:
            continue
        from app.graph.triple_builder import build_triple

        triples.append(build_triple(str(subject), str(predicate), str(obj)))

    if not triples:
        return 0

    update = "PREFIX project: <http://projectrag.local/>\nDELETE DATA {\n"
    update += "\n".join(f"  {triple}" for triple in triples)
    update += "\n}"
    sparql_update(update)
    return len(triples)
