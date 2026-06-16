# SQLAlchemy Migration Plan

## Current: psycopg2

ProjectRAG currently uses `psycopg2` with a small repository layer around SQL statements.

### Pros

- Simple and explicit SQL.
- Low abstraction overhead.
- Easy to understand generated database behavior.
- Works well for MVP-level PostgreSQL and pgvector usage.

### Cons

- Manual SQL string maintenance.
- Manual JSON serialization.
- More boilerplate for inserts, updates, and row handling.
- Harder to compose dynamic queries safely over time.
- Future schema evolution may require more discipline.

## Future: SQLAlchemy Core

The next migration step should be SQLAlchemy Core, not ORM-first.

### Pros

- Keeps SQL-like explicitness.
- Improves query composition and parameter handling.
- Easier migration path for schema metadata and Alembic later.
- Lower complexity than ORM.
- Good fit for repository pattern.

### Cons

- Adds abstraction and learning curve.
- Requires rewriting repository SQL statements.
- pgvector support needs careful handling.
- May not reduce much code for simple queries.

## Later: SQLAlchemy ORM

SQLAlchemy ORM can be considered after the domain model stabilizes.

### Pros

- Rich object mapping for documents, chunks, workflows, and memory.
- Relationship handling can simplify higher-level code.
- Better integration with migrations and model-driven schema management.
- Useful when business rules become more entity-centric.

### Cons

- More implicit behavior.
- Risk of inefficient queries if misused.
- More complexity for vector queries and graph-fact workloads.
- Potential mismatch with append-only audit tables.

## Recommended Migration Path

1. Keep the current repository pattern.
2. Add SQLAlchemy Core table definitions.
3. Migrate one repository at a time.
4. Add Alembic only when schema migrations become necessary.
5. Consider ORM later for stable domain entities only.

No migration is implemented yet.
