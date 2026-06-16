# ADR-003: Use PostgreSQL with pgvector

## Status

Accepted

## Context

ProjectRAG needs durable storage for documents, chunks, embeddings, memory, workflow runs, agent runs, validation results, and graph fact provenance.

## Decision

Use PostgreSQL as the primary relational store and pgvector for embedding storage/search.

## Consequences

- One database can support metadata, audit logs, memory, and vector search.
- Local Docker setup is straightforward.
- pgvector search is sufficient for the MVP.
- Advanced vector workloads may later require dedicated vector infrastructure.

## Alternatives Considered

- SQLite for local-only storage.
- Chroma or FAISS for vector storage.
- Dedicated hosted vector databases.
