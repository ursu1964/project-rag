# ADR-005: Use Ollama for Local-First LLM and Embeddings

## Status

Accepted

## Context

ProjectRAG should keep project data local by default and avoid requiring cloud LLM credentials for MVP operation.

## Decision

Use Ollama for local generation and embedding models.

## Consequences

- No cloud API key is required for default operation.
- Documents and prompts stay on local infrastructure.
- Model quality and latency depend on local hardware and selected models.
- Users must pull required models before ingestion/query workflows.

## Alternatives Considered

- OpenAI or other hosted LLM APIs.
- Self-hosted model servers other than Ollama.
- Embedding-only local mode with hosted generation.
