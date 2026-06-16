# ADR-004: Use GraphDB for RDF Graph Storage

## Status

Accepted

## Context

GraphRAG requires explicit representation of entities, relationships, dependencies, and impact paths beyond vector similarity.

## Decision

Use GraphDB as the RDF graph store and query it with SPARQL.

## Consequences

- Relationships can be queried directly with SPARQL.
- RDF triples provide a portable graph representation.
- GraphDB adds an additional local service to operate.
- PostgreSQL graph_facts are also stored for auditability and provenance.

## Alternatives Considered

- Neo4j property graph.
- PostgreSQL-only relationship tables.
- In-memory graph libraries.
