# Standard Dashboard and Analysis Workflow

Use this as the single team process for opening dashboards and analyzing ProjectRAG behavior.

## 1) Start everything the same way

Run from the repository root:

1. source .venv/bin/activate
2. make dashboards-all

This standard command starts:

- ProjectRAG API
- Streamlit Cockpit
- Grafana, Prometheus, and Alertmanager when configured in Docker Compose

Default local URLs:

- Cockpit: http://127.0.0.1:8501
- API: http://127.0.0.1:8001
- Grafana: http://127.0.0.1:3001
- Prometheus: http://127.0.0.1:9091
- Alertmanager: http://127.0.0.1:9094

If ports are busy, the launcher auto-selects free ones for API and Cockpit.

## 2) Open dashboards in this order

1. Cockpit first: verify control-plane and workflow visibility.
2. Grafana second: verify latency, errors, ingestion, and dependency health.
3. Prometheus third: validate metrics and alert rule behavior.
4. Alertmanager fourth: confirm routing and receiver state.

## 3) Standard analysis checklist

Run this checklist for every troubleshooting or readiness review.

1. Availability
- Check API health and deep health are green.
- Confirm dependencies are reachable.

2. Data and ingestion
- Confirm documents and chunks are increasing as expected after ingestion.
- Check ingestion failures and retry behavior.

3. Retrieval quality
- Validate vector, graph, and hybrid retrieval paths.
- Confirm evidence and citations are present in answers.

4. Evaluation quality gates
- Review golden suite status: graph, vector, hybrid, safety.
- Verify no blocking regressions before release.

5. Governance and safety
- Confirm cloud connectors remain dormant unless explicitly enabled.
- Review policy blocks, validation warnings, and audit events.

6. Performance and reliability
- Check p95 and p99 query latency trends.
- Check 5xx error rate, ingestion failure rate, and dependency alerts.

7. Decision
- Ready: all quality and safety gates pass.
- Not ready: capture failing gate, owner, and next action.

## 4) Evidence to record in every analysis

Capture the following in your report or ticket:

- Time window analyzed
- Dashboard screenshots or metric snapshots
- Query examples with citations
- Evaluation gate results
- Final release recommendation

## 5) Related references

- Quick operations: PROJECTRAG_QUICK_OPERATIONS_GUIDE.md
- Full runbook: docs/operations_runbook.md
- Evaluation output examples: docs/evaluation_report.md
- Implementation and analysis plan: analiseprompt.md
