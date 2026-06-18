"""Streamlit UI for ProjectRAG.

The UI talks only to the FastAPI service. It does not access the database,
GraphDB, or local files directly except for user-selected upload content.
"""

from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components

DEFAULT_API_URL = os.getenv("PROJECTRAG_API_URL", "http://127.0.0.1:8001")
GRAPH_FACTS_QUERY = """
PREFIX project: <http://projectrag.local/>
SELECT ?subject ?predicate ?object
WHERE {
  ?subject ?predicate ?object .
}
LIMIT 100
""".strip()


def api_base_url() -> str:
    """Return normalized FastAPI base URL."""
    env_url = os.getenv("PROJECTRAG_API_URL", "").strip().rstrip("/")
    return (st.session_state.get("api_base_url") or env_url or DEFAULT_API_URL).rstrip("/")


def request_json(
    method: str, path: str, **kwargs: Any
) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
    """Call the ProjectRAG API and return JSON payload or an error message."""
    url = f"{api_base_url()}{path}"
    api_key = str(st.session_state.get("api_key", "")).strip()
    if api_key:
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("X-ProjectRAG-API-Key", api_key)
        kwargs["headers"] = headers
    try:
        response = requests.request(method, url, timeout=120, **kwargs)
        response.raise_for_status()
        if not response.content:
            return {}, None
        return response.json(), None
    except requests.RequestException as exc:
        detail = getattr(exc.response, "text", "") if getattr(exc, "response", None) else ""
        message = f"{exc}"
        if detail:
            message = f"{message}: {detail}"
        return None, message
    except ValueError as exc:
        return None, f"Invalid JSON response: {exc}"


def graph_bindings(payload: dict[str, Any] | list[Any] | None) -> list[dict[str, str]]:
    """Flatten SPARQL JSON bindings into display rows."""
    if not isinstance(payload, dict):
        return []
    bindings = payload.get("results", {}).get("bindings", [])
    rows: list[dict[str, str]] = []
    for binding in bindings:
        rows.append({key: str(value.get("value", "")) for key, value in binding.items()})
    return rows


def as_list(payload: dict[str, Any] | list[Any] | None) -> list[Any]:
    return payload if isinstance(payload, list) else []


def to_csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    """Serialize row dictionaries to CSV bytes for download buttons."""
    if not rows:
        return b""
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key) for key in fieldnames})
    return buffer.getvalue().encode("utf-8")


def parse_timestamp(value: Any) -> datetime | None:
    """Parse ISO timestamp strings from API payloads."""
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def relative_time_label(value: Any) -> str:
    ts = parse_timestamp(value)
    if ts is None:
        return "n/a"
    now = datetime.now(ts.tzinfo) if ts.tzinfo else datetime.now()
    delta = now - ts
    seconds = max(int(delta.total_seconds()), 0)
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def confidence_band(confidence: Any) -> str:
    """Return human-friendly confidence quality band."""
    try:
        value = float(confidence)
    except (TypeError, ValueError):
        return "unknown"
    if value >= 0.8:
        return "high"
    if value >= 0.6:
        return "medium"
    return "low"


def render_quality_badges(validation: dict[str, Any]) -> None:
    """Render quality badges for groundedness, confidence, and validation pass state."""
    grounded = bool(validation.get("grounded", False))
    conf_band = confidence_band(validation.get("confidence"))
    passed = validation.get("passed")
    validation_label = "passed" if passed is True else "failed" if passed is False else "unknown"

    st.markdown(
        """
        <style>
        .pr-badge-row { display:flex; gap:8px; flex-wrap:wrap; margin-bottom: 0.5rem; }
        .pr-badge { padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.85rem; border: 1px solid #d1d5db; background: #f8fafc; }
        .pr-ok { border-color: #22c55e; background: #ecfdf5; color: #166534; }
        .pr-warn { border-color: #f59e0b; background: #fffbeb; color: #92400e; }
        .pr-bad { border-color: #ef4444; background: #fef2f2; color: #991b1b; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    grounded_class = "pr-ok" if grounded else "pr-bad"
    conf_class = "pr-ok" if conf_band == "high" else "pr-warn" if conf_band == "medium" else "pr-bad"
    validation_class = "pr-ok" if validation_label == "passed" else "pr-bad" if validation_label == "failed" else "pr-warn"
    st.markdown(
        (
            f"<div class='pr-badge-row'>"
            f"<span class='pr-badge {grounded_class}'>grounded: {'yes' if grounded else 'no'}</span>"
            f"<span class='pr-badge {conf_class}'>confidence: {conf_band}</span>"
            f"<span class='pr-badge {validation_class}'>validation: {validation_label}</span>"
            f"</div>"
        ),
        unsafe_allow_html=True,
    )


def render_copy_button(label: str, text: str, key: str) -> None:
    """Render a browser-side copy button for text content."""
    safe_text = json.dumps(text)
    safe_label = label.replace("<", "&lt;").replace(">", "&gt;")
    safe_key = key.replace("\"", "")
    components.html(
        f"""
        <button id=\"copy-{safe_key}\" style=\"
            background:#f8fafc;
            border:1px solid #cbd5e1;
            border-radius:8px;
            padding:6px 10px;
            cursor:pointer;
            font-size:13px;
        \">{safe_label}</button>
        <script>
            const btn = document.getElementById('copy-{safe_key}');
            if (btn) {{
                btn.onclick = async () => {{
                    try {{
                        await navigator.clipboard.writeText({safe_text});
                        btn.textContent = 'Copied';
                        setTimeout(() => btn.textContent = {json.dumps(label)}, 1200);
                    }} catch (e) {{
                        btn.textContent = 'Copy failed';
                        setTimeout(() => btn.textContent = {json.dumps(label)}, 1200);
                    }}
                }};
            }}
        </script>
        """,
        height=42,
    )


def render_evidence(title: str, evidence: Any) -> None:
    """Render evidence consistently for lists and dictionaries."""
    with st.expander(title, expanded=False):
        if not evidence:
            st.info("No evidence returned.")
        elif isinstance(evidence, list):
            st.dataframe(evidence, use_container_width=True)
        else:
            st.json(evidence)


def render_status_badge(label: str, value: Any) -> None:
    status = str(value or "unknown")
    if status in {"ok", "healthy", "passed"}:
        st.success(f"{label}: {status}")
    elif status in {"failed", "error", "unhealthy"}:
        st.error(f"{label}: {status}")
    else:
        st.info(f"{label}: {status}")


def render_dashboard_panel() -> None:
    st.header("Executive Excellence Cockpit")
    st.caption("A presentation-first overview for health, evidence readiness, graph coverage, and auditability.")

    health, health_error = request_json("GET", "/health/deep")
    documents, documents_error = request_json("GET", "/documents")
    graph, graph_error = request_json("GET", "/graph/export?limit=500")
    workflows, workflows_error = request_json("GET", "/workflows?limit=50")
    workflow_rows = [row for row in as_list(workflows) if isinstance(row, dict)]

    cols = st.columns(4)
    cols[0].metric("API", "offline" if health_error else "online")
    cols[1].metric("Documents", len(as_list(documents)))
    graph_edges = graph.get("edges", []) if isinstance(graph, dict) else []
    graph_nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    cols[2].metric("Graph nodes", len(graph_nodes))
    cols[3].metric("Graph edges", len(graph_edges))

    queue_statuses = {"pending", "queued", "running", "in_progress"}
    queued_count = sum(1 for row in workflow_rows if str(row.get("status", "")).lower() in queue_statuses)
    successful = [
        row
        for row in workflow_rows
        if str(row.get("status", "")).lower() in {"completed", "success", "passed"}
    ]
    latest_success = max(
        successful,
        key=lambda row: (parse_timestamp(row.get("updated_at")) or parse_timestamp(row.get("created_at")) or datetime.min),
        default=None,
    )

    st.subheader("Live status strip")
    strip = st.columns(6)
    strip[0].metric("API", "online" if not health_error else "offline")
    strip[1].metric("PostgreSQL", str((health or {}).get("postgres", "unknown") if isinstance(health, dict) else "unknown"))
    strip[2].metric("GraphDB", str((health or {}).get("graphdb", "unknown") if isinstance(health, dict) else "unknown"))
    strip[3].metric("Ollama", str((health or {}).get("ollama", "unknown") if isinstance(health, dict) else "unknown"))
    strip[4].metric("Ingestion queue", queued_count)
    strip[5].metric(
        "Last success",
        relative_time_label(
            latest_success.get("updated_at") if isinstance(latest_success, dict) else None
            or latest_success.get("created_at") if isinstance(latest_success, dict) else None
        ),
    )

    if isinstance(health, dict):
        st.subheader("Dependency health")
        status_cols = st.columns(4)
        with status_cols[0]:
            render_status_badge("Service", health.get("status"))
        with status_cols[1]:
            render_status_badge("PostgreSQL", health.get("postgres"))
        with status_cols[2]:
            render_status_badge("GraphDB", health.get("graphdb"))
        with status_cols[3]:
            render_status_badge("Ollama", health.get("ollama"))
        if health.get("errors"):
            st.warning("Dependency warnings")
            st.json(health["errors"])
    elif health_error:
        st.error(health_error)

    st.subheader("Readiness narrative")
    readiness = []
    readiness.append("✅ API reachable" if not health_error else "❌ API not reachable")
    readiness.append("✅ Documents registered" if as_list(documents) else "⚠️ No documents visible")
    readiness.append("✅ Graph facts available" if graph_edges else "⚠️ No graph facts exported")
    readiness.append("✅ Workflow audit available" if not workflows_error else "⚠️ Workflow audit unavailable")
    st.write("  \n".join(readiness))

    with st.expander("Recent workflows", expanded=True):
        if workflows_error:
            st.warning(workflows_error)
        elif as_list(workflows):
            st.dataframe(workflows, use_container_width=True)
        else:
            st.info("No workflow runs returned yet.")

    with st.expander("Dashboard data gaps"):
        if documents_error:
            st.warning(f"Documents endpoint: {documents_error}")
        if graph_error:
            st.warning(f"Graph export endpoint: {graph_error}")
        if not any([documents_error, graph_error, workflows_error, health_error]):
            st.success("No interface data fetch errors.")


def render_query_panel() -> None:
    st.header("Ask ProjectRAG")
    st.caption("Grounded infrastructure answers with evidence, confidence, and workflow traceability.")
    question = st.text_area("Question", placeholder="What does VM1 depend on?")
    debug = st.checkbox("Debug response", value=False)

    if st.button("Ask", type="primary", disabled=not question.strip()):
        payload, error = request_json(
            "POST",
            f"/query?debug={str(debug).lower()}",
            json={"question": question.strip()},
        )
        if error:
            st.error(error)
            return
        if not isinstance(payload, dict):
            st.error("Unexpected API response.")
            return

        st.subheader("Answer")
        answer_text = str(payload.get("answer") or "No answer returned.")
        st.markdown(answer_text)

        copy_cols = st.columns(2)
        with copy_cols[0]:
            render_copy_button("Copy answer", answer_text, key="answer")
        with copy_cols[1]:
            citations = payload.get("citations") or []
            render_copy_button("Copy citations", json.dumps(citations, indent=2), key="citations")

        cols = st.columns(4)
        cols[0].metric("Route", payload.get("route") or "unknown")
        validation = payload.get("validation") or {}
        confidence = validation.get("confidence") if isinstance(validation, dict) else None
        cols[1].metric("Confidence", f"{float(confidence or 0):.2f}")
        grounded = validation.get("grounded") if isinstance(validation, dict) else False
        cols[2].metric("Grounded", "yes" if grounded else "no")
        metrics = payload.get("metrics") or {}
        cols[3].metric("Duration", f"{metrics.get('duration_ms', 0)} ms")

        if isinstance(validation, dict):
            render_quality_badges(validation)

        policy_decision = payload.get("policy_decision") or {}
        if policy_decision:
            st.subheader("Prompt policy")
            if policy_decision.get("blocked"):
                st.error(policy_decision.get("reason") or "Prompt blocked")
            else:
                st.success(policy_decision.get("reason") or "Prompt policy passed")
            st.json(policy_decision)

        st.subheader("Validation")
        st.json(validation)

        if citations:
            st.subheader("Citations")
            st.dataframe(citations, use_container_width=True)

        evidence = payload.get("evidence") or {}
        render_evidence("Vector evidence", evidence.get("vector") if isinstance(evidence, dict) else None)
        render_evidence("Graph evidence", evidence.get("graph") if isinstance(evidence, dict) else None)
        render_evidence("Memory evidence", evidence.get("memory") if isinstance(evidence, dict) else None)

        if debug:
            with st.expander("Full debug state"):
                st.json(payload)


def render_documents_panel() -> None:
    st.header("Document Knowledge Manager")
    st.caption("Upload, ingest, delete, and reindex documents without direct database access.")

    uploaded = st.file_uploader("Upload document", type=["txt", "md", "log"])
    ingest_after_upload = st.checkbox("Ingest after upload", value=False)
    if st.button("Upload", disabled=uploaded is None):
        assert uploaded is not None
        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "text/plain")}
        payload, error = request_json(
            "POST",
            f"/documents/upload?ingest={str(ingest_after_upload).lower()}",
            files=files,
        )
        if error:
            st.error(error)
        else:
            st.success("Upload completed.")
            st.json(payload)

    if st.button("Trigger ingestion for data/raw"):
        payload, error = request_json("POST", "/ingest")
        if error:
            st.error(error)
        else:
            st.success("Ingestion completed.")
            st.json(payload)

    catalog, catalog_error = request_json("GET", "/sources/catalog")
    if catalog_error:
        st.warning(f"Source catalog unavailable: {catalog_error}")
    elif isinstance(catalog, dict):
        st.subheader("Source catalog")
        cols = st.columns(2)
        cols[0].metric("Local sources", catalog.get("total_sources", 0))
        cols[1].metric("Catalog status", catalog.get("status", "unknown"))
        if catalog.get("counts"):
            st.json(catalog.get("counts"))
        if catalog.get("sources"):
            with st.expander("Source files", expanded=False):
                st.dataframe(catalog.get("sources"), use_container_width=True)

    documents, error = request_json("GET", "/documents")
    if error:
        st.error(error)
        return
    if not documents:
        st.info("No documents returned.")
        return

    st.dataframe(documents, use_container_width=True)
    document_rows = as_list(documents)
    document_ids = [str(item.get("id")) for item in document_rows if isinstance(item, dict) and item.get("id")]
    if not document_ids:
        return

    st.subheader("Document actions")
    selected_document = st.selectbox("Document ID", document_ids)
    action_cols = st.columns(2)
    with action_cols[0]:
        if st.button("Reindex selected document"):
            payload, action_error = request_json("POST", f"/documents/{selected_document}/reindex")
            if action_error:
                st.error(action_error)
            else:
                st.success("Reindex completed.")
                st.json(payload)
    with action_cols[1]:
        confirm_delete = st.checkbox("Confirm delete selected document")
        if st.button("Delete selected document", disabled=not confirm_delete):
            payload, action_error = request_json("DELETE", f"/documents/{selected_document}")
            if action_error:
                st.error(action_error)
            else:
                st.success("Document deleted.")
                st.json(payload)


def render_graph_panel() -> None:
    st.header("Topology and Graph Intelligence")
    st.caption("Visualize exported graph facts and run read-only SPARQL queries.")

    payload, error = request_json("GET", "/graph/export?limit=500")
    if error:
        st.warning(error)
    elif isinstance(payload, dict):
        nodes = payload.get("nodes", [])
        edges = payload.get("edges", [])
        cols = st.columns(2)
        cols[0].metric("Nodes", len(nodes))
        cols[1].metric("Edges", len(edges))
        if edges:
            st.dataframe(edges, use_container_width=True)
            graph_lines = ["digraph ProjectRAG {", "  rankdir=LR;"]
            for edge in edges[:80]:
                source = str(edge.get("source", "")).replace('"', "'")
                target = str(edge.get("target", "")).replace('"', "'")
                label = str(edge.get("label", "")).replace('"', "'")
                graph_lines.append(f'  "{source}" -> "{target}" [label="{label}"];')
            graph_lines.append("}")
            st.graphviz_chart("\n".join(graph_lines), use_container_width=True)
        else:
            st.info("No graph edges exported yet. Ingest topology documents first.")

    st.subheader("SPARQL Explorer")
    st.caption("Uses the FastAPI /graph/query endpoint with a read-only SPARQL SELECT query.")
    query = st.text_area("SPARQL query", value=GRAPH_FACTS_QUERY, height=180)
    if st.button("Run graph query"):
        sparql_payload, sparql_error = request_json("POST", "/graph/query", json={"query": query})
        if sparql_error:
            st.error(sparql_error)
            return
        rows = graph_bindings(sparql_payload)
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No graph facts returned.")
        with st.expander("Raw GraphDB response"):
            st.json(sparql_payload)


def render_audit_panel() -> None:
    st.header("Audit and Governance Console")
    st.caption("Workflow runs, agent traces, and validation outputs for explainable operation.")

    workflows, workflows_error = request_json("GET", "/workflows?limit=200")
    agent_runs, agent_error = request_json("GET", "/agents/runs?limit=200")
    validation, validation_error = request_json("GET", "/validation/results?limit=200")
    evaluation_report, evaluation_error = request_json("GET", "/evaluation/report")

    workflow_rows = [row for row in as_list(workflows) if isinstance(row, dict)]
    agent_rows = [row for row in as_list(agent_runs) if isinstance(row, dict)]
    validation_rows = [row for row in as_list(validation) if isinstance(row, dict)]

    st.subheader("Filters")
    filter_cols = st.columns(4)
    statuses = sorted({str(row.get("status", "unknown")) for row in workflow_rows if row.get("status")})
    selected_statuses = filter_cols[0].multiselect("Workflow status", options=statuses)
    agent_names = sorted({str(row.get("agent_name", "")) for row in agent_rows if row.get("agent_name")})
    selected_agents = filter_cols[1].multiselect("Agent name", options=agent_names)
    workflow_ids = sorted({str(row.get("workflow_id", "")) for row in agent_rows if row.get("workflow_id")})
    selected_workflow = filter_cols[2].selectbox("Workflow id", options=["All"] + workflow_ids)
    date_window = filter_cols[3].date_input("Created date range", value=())

    start_date = None
    end_date = None
    if isinstance(date_window, tuple) and len(date_window) == 2:
        start_date, end_date = date_window

    def matches_filters(row: dict[str, Any], include_status: bool, include_agent: bool) -> bool:
        if include_status and selected_statuses:
            if str(row.get("status", "")) not in selected_statuses:
                return False
        if include_agent and selected_agents:
            if str(row.get("agent_name", "")) not in selected_agents:
                return False
        if selected_workflow != "All" and str(row.get("workflow_id", "")) != selected_workflow:
            return False
        if start_date and end_date:
            ts = parse_timestamp(row.get("created_at") or row.get("updated_at"))
            if ts is None:
                return False
            if not (start_date <= ts.date() <= end_date):
                return False
        return True

    filtered_workflows = [row for row in workflow_rows if matches_filters(row, include_status=True, include_agent=False)]
    filtered_agents = [row for row in agent_rows if matches_filters(row, include_status=True, include_agent=True)]
    filtered_validation = [row for row in validation_rows if matches_filters(row, include_status=False, include_agent=False)]

    cols = st.columns(4)
    cols[0].metric("Workflow runs", len(filtered_workflows))
    cols[1].metric("Agent runs", len(filtered_agents))
    cols[2].metric("Validation results", len(filtered_validation))
    eval_summary = evaluation_report.get("summary", {}) if isinstance(evaluation_report, dict) else {}
    cols[3].metric("Eval questions", eval_summary.get("total_questions", 0))

    if workflows_error:
        st.error(workflows_error)
    else:
        st.subheader("Recent workflows")
        st.download_button(
            "Export workflows CSV",
            data=to_csv_bytes(filtered_workflows),
            file_name="workflows.csv",
            mime="text/csv",
            disabled=not filtered_workflows,
        )
        st.dataframe(filtered_workflows, use_container_width=True)

    if agent_error:
        st.warning(agent_error)
    else:
        with st.expander("Agent runs", expanded=False):
            st.download_button(
                "Export agent runs CSV",
                data=to_csv_bytes(filtered_agents),
                file_name="agent_runs.csv",
                mime="text/csv",
                disabled=not filtered_agents,
            )
            st.dataframe(filtered_agents, use_container_width=True)

    if validation_error:
        st.warning(validation_error)
    else:
        with st.expander("Validation results", expanded=True):
            st.download_button(
                "Export validation CSV",
                data=to_csv_bytes(filtered_validation),
                file_name="validation_results.csv",
                mime="text/csv",
                disabled=not filtered_validation,
            )
            st.dataframe(filtered_validation, use_container_width=True)

    st.subheader("Evaluation report")
    if evaluation_error:
        st.warning(evaluation_error)
    elif isinstance(evaluation_report, dict) and evaluation_report.get("status") == "ok":
        st.json(evaluation_report.get("summary") or {})
        gates = evaluation_report.get("quality_gates") or {}
        if gates:
            gate_status = gates.get("status", "unknown")
            if gate_status == "passed":
                st.success("Evaluation quality gates passed")
            else:
                st.warning("Evaluation quality gates need attention")
            st.dataframe(gates.get("gates") or [], use_container_width=True)
        with st.expander("Evaluation markdown", expanded=False):
            st.markdown(str(evaluation_report.get("markdown") or ""))
    else:
        st.info("No generated evaluation report found yet.")


def render_operations_panel() -> None:
    st.header("Operations: Retry Queue")
    st.caption("Durable job retries with ETA derived from next_retry_at.")

    queue_payload, queue_error = request_json("GET", "/operations/jobs/retry-queue?limit=200")
    if queue_error:
        st.error(queue_error)
        return

    if not isinstance(queue_payload, dict):
        st.error("Unexpected operations response.")
        return

    jobs = as_list(queue_payload.get("jobs"))
    cols = st.columns(3)
    cols[0].metric("Retry queue", int(queue_payload.get("total", 0) or 0))
    cols[1].metric("Due now", int(queue_payload.get("due_now", 0) or 0))
    cols[2].metric("API status", str(queue_payload.get("status", "unknown")))

    if not jobs:
        st.info("No queued or retrying jobs.")
        return

    st.download_button(
        "Export retry queue CSV",
        data=to_csv_bytes([row for row in jobs if isinstance(row, dict)]),
        file_name="retry_queue.csv",
        mime="text/csv",
        disabled=not jobs,
    )
    st.dataframe(jobs, use_container_width=True)


def render_presentation_panel() -> None:
    st.header("Presentation Mode")
    st.caption("Use this page to demonstrate the system as an infrastructure intelligence cockpit.")

    st.markdown(
        """
        ### Executive story
        1. **Local-first control plane**: FastAPI orchestrates private RAG, GraphRAG, memory, audit, and safety.
        2. **Evidence-first answers**: every query shows route, confidence, validation, and source evidence.
        3. **Topology intelligence**: graph facts become a dependency map for impact and operational reasoning.
        4. **Safe operations**: document lifecycle, audit trails, and approval-first tooling reduce risk.
        5. **Roadmap discipline**: Part 29 MVP is prioritized before autonomous/AGII layers.

        ### Demo flow
        - Open **Cockpit** to show readiness and dependency health.
        - Open **Documents** to upload or reindex knowledge.
        - Open **Query** to ask an infrastructure question.
        - Open **Topology** to show graph edges and SPARQL evidence.
        - Open **Audit** to prove traceability.
        """
    )

    st.info("For best demo quality, ingest a topology sample first, then ask: 'What does VM1 depend on?'")


def main() -> None:
    st.set_page_config(page_title="ProjectRAG Excellence Cockpit", page_icon="🔎", layout="wide")
    st.title("ProjectRAG Excellence Cockpit")
    st.caption("Infrastructure intelligence, GraphRAG evidence, topology, document operations, and audit presentation.")

    # Seed session state from env var exactly once per browser session.
    # This ensures the env var set by the launcher is picked up even when
    # session state is empty (fresh tab, reload, or reconnect after restart).
    if "api_base_url" not in st.session_state or not st.session_state["api_base_url"]:
        st.session_state["api_base_url"] = os.getenv("PROJECTRAG_API_URL", DEFAULT_API_URL)

    with st.sidebar:
        st.header("API")
        st.session_state["api_base_url"] = st.text_input(
            "FastAPI base URL",
            value=st.session_state["api_base_url"],
        )
        st.session_state["api_key"] = st.text_input(
            "API key (optional)",
            value=os.getenv("PROJECTRAG_API_KEY", ""),
            type="password",
        )
        health, error = request_json("GET", "/health")
        if error:
            st.error("❌ API offline")
            st.warning(
                f"Cannot reach `{st.session_state.get('api_base_url', DEFAULT_API_URL)}`\n\n"
                "**Fix:** start the API with:\n"
                "```\npython scripts/launch_app.py --with-ui --auto-port --auto-ui-port\n```\n"
                "then update the **FastAPI base URL** above to match the printed API address."
            )
        else:
            status = health.get("status", "unknown") if isinstance(health, dict) else "ok"
            st.success(f"✅ API {status}")
        st.markdown("---")
        st.caption("Recommended demo order: Cockpit → Documents → Query → Topology → Audit → Presentation")

    tab_dashboard, tab_query, tab_documents, tab_graph, tab_audit, tab_operations, tab_presentation = st.tabs(
        ["Cockpit", "Query", "Documents", "Topology", "Audit", "Operations", "Presentation"]
    )
    with tab_dashboard:
        render_dashboard_panel()
    with tab_query:
        render_query_panel()
    with tab_documents:
        render_documents_panel()
    with tab_graph:
        render_graph_panel()
    with tab_audit:
        render_audit_panel()
    with tab_operations:
        render_operations_panel()
    with tab_presentation:
        render_presentation_panel()


if __name__ == "__main__":
    main()
