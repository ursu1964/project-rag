# Dependency Policy

## Rules

- Every dependency requires a clear justification.
- Prefer the Python standard library when it is sufficient.
- Avoid abandoned or unmaintained libraries.
- Pin critical dependencies for repeatable deployments.
- Review and update dependencies quarterly.

## Review Checklist

For each dependency, confirm:

- It is required for a current feature.
- It has an active maintenance history.
- It does not introduce unnecessary transitive risk.
- It has a compatible license.
- It is documented in `requirements.txt` or a lock file.

## Critical Dependencies

Critical runtime dependencies should be pinned before production deployment, especially:

- FastAPI / Uvicorn
- pydantic / pydantic-settings
- psycopg2 / pgvector
- LangGraph / LangChain
- requests
- prometheus-client

## Update Cadence

Quarterly:

1. Run dependency report.
2. Review outdated packages.
3. Apply updates in a branch.
4. Run tests and smoke tests.
5. Review security advisories.
