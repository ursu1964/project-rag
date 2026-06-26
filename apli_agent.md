# ProjectRAG Agents and LLM Architecture Presentation

## 1. Executive Summary
ProjectRAG already has a multi-agent architecture with strong local-first behavior and clear safety defaults.

Current state from code:
- Total agent modules in app/agents: 23
- Agents wired into active workflows: 13
- LLM provider actively used in runtime generation: 1 (Ollama)
- Models actively used by default: 2
  - 1 generation model: ollama_model (default llama3.1:8b)
  - 1 embedding model: embedding_model (default nomic-embed-text)
- Claude support: configuration and allocation path exists, but text generation is not yet fully provider-abstracted end-to-end.

## 2. How the application works (agent perspective)
ProjectRAG runs two orchestrated LangGraph workflows:

1) RAG workflow (query answering):
router -> memory -> vector -> graph -> merge -> compress -> reason -> validate

2) Cognitive workflow (planning and governance style):
chief -> memory -> retrieval -> graph -> planning -> security -> cost -> validation -> learning

Practical effect:
- Retrieval and graph context are both used before answer generation.
- Validation gates confidence and approval.
- Security blocks risky execution by default.
- Learning stores outcomes for future improvement.

## 3. Complete Agent Catalog

### A. Agents currently orchestrated in active workflows

| Agent | What it does | How it does it | Effect on thinking process | Possible improvements |
|---|---|---|---|---|
| chief_agent | Breaks objective into tasks and required agents | Splits objective text into task list and builds orchestration summary | Turns a broad goal into a structured reasoning agenda | Add priority scoring and dependency ordering between tasks |
| router | Selects retrieval route (vector/graph/hybrid/action) | Keyword deterministic routing; optional LLM JSON routing when enabled | Sets reasoning path before retrieval starts | Add confidence calibration from historical route success |
| memory_agent | Retrieves relevant memory context | Queries memory store with question and top-k | Injects prior project memory into reasoning | Add memory freshness and source trust weighting |
| vector_retriever | Retrieves semantic evidence | Creates embedding and runs similarity search | Brings textual semantic evidence | Add adaptive top-k and domain filters |
| graph_retriever | Retrieves relationship/dependency evidence | Entity extraction + SPARQL templates for incoming/outgoing/impact/2-hop | Adds structural causal context | Improve entity disambiguation and ontology normalization |
| context_merger | Combines and scores evidence | Dedup + rerank + weighted evidence scoring across vector/graph/memory | Creates unified evidence ranking for reasoning | Add learned weighting by question category |
| context_compressor | Reduces context size before LLM | Shortens content fields and packages compact context payload | Improves LLM focus and token efficiency | Introduce salience-based compression instead of fixed char trim |
| reasoner | Generates final answer | Builds strict grounded prompt and calls LLM generation | Produces explainable answer with evidence sections | Add provider abstraction and citation-level grounding checks |
| validator | Validates groundedness and confidence | Evidence-based confidence calibration + optional LLM judge + safety checks | Controls trust, warns uncertainty, can require human approval | Add benchmark-calibrated confidence and policy-specific reject reasons |
| planning_agent | Produces recommendation plan | Converts tasks into recommendation-only plan with approval flags | Prevents premature action execution | Add plan feasibility, risk/effort scores |
| security_agent | Classifies risk and blocks execution | High-risk term detection; execution blocked by default | Injects safety-first policy in reasoning chain | Replace keyword-only risk logic with policy graph + context-aware classifier |
| cost_agent | Estimates local resource impact | Computes storage/graph/embedding/inference estimates from context | Adds operational realism to recommendations | Add real telemetry-based cost model and cloud what-if mode |
| learning_agent | Summarizes and stores lessons | Extracts mistakes/successes/lessons and persists experience runs | Creates feedback loop for process improvement | Add automatic strategy updates from recurring failure patterns |

### B. Specialized agents available in code (not default-wired in main workflows)

| Agent | What it does | How it does it | Effect on thinking process | Possible improvements |
|---|---|---|---|---|
| query_planner | Builds retrieval strategy plan | Route + graph depth + token budget heuristics | Adds explicit pre-reasoning plan controls | Wire directly before router/retrievers in main path |
| topology_agent | Topology analysis around entities | Intent detection + traversal functions (neighbors/dependencies/impact) | Helps with architecture and dependency explanation | Merge outputs with standard graph evidence format |
| impact_agent | Computes direct/indirect impact entities | Uses graph impact analysis helpers + dedup | Supports blast/impact-oriented decision making | Add uncertainty labels and missing-data explanations |
| blast_radius_agent | Bounded impact expansion by depth | Iterative neighbor traversal with depth cap | Improves failure-impact reasoning clarity | Add edge criticality and service tier weighting |
| rca_agent | Root-cause candidate generation | Symptom parsing + dependency/reverse-dependency evidence scoring | Introduces causal hypothesis reasoning | Add incident timeline correlation and confidence decomposition |
| failure_prediction_agent | Failure risk forecasting | Calls statistical predictor over metric history | Adds predictive operations reasoning | Add model ensemble and drift monitoring |
| recommendation_agent | Converts evidence to ranked recommendations | Confidence from evidence type/score and recommendation-only mode | Produces action guidance without auto-execution | Add business-impact ranking and owner assignment |
| resource_allocator (agent) | Selects model tier by task | Tier mapping (small/medium/large) based on task type | Makes reasoning pipeline resource-aware | Connect to real latency/cost feedback loop |
| discovery_agent | Read-only infrastructure discovery | Docker discovery and optional persistence | Adds environment awareness into reasoning | Expand sources beyond Docker (K8s, cloud inventory in safe mode) |
| execution_agent | Execution policy placeholder | Reports current security mode and execution disabled state | Enforces safety boundary clearly | Implement approval workflow with signed audit trail |

## 4. LLM status now and Claude readiness

## 4.1 What is running now
For production query generation in current code paths:
- Active LLM provider: Ollama
- Active generation model count: 1
- Active embedding model count: 1

Optional same-provider LLM usage:
- Router LLM mode can be enabled (use_llm_router=true)
- LLM judge can be enabled (use_llm_judge=true)
- Both still use Ollama generate() in current implementation

So, practically today:
- Provider count actively used for generation: 1
- Distinct active model roles: 2 (generation + embeddings)

## 4.2 Can it be updated to Claude?
Yes, partially prepared but not fully completed.

Already present:
- enable_claude_provider flag in settings
- claude_model setting
- Local-first resource allocation logic with Claude dormancy guard
- Runtime manager recognizes claude runtime label

Still required for full Claude runtime:
1. Provider abstraction layer for text generation and embeddings (not Ollama-only calls).
2. Claude client implementation with retries, timeouts, and structured output guarantees.
3. Routing of reasoner/router/llm_judge to provider-agnostic interface.
4. Cost, latency, and token accounting per provider.
5. Tenant-safe secret management for remote keys.

## 5. How many LLMs can this architecture support (estimation)
Current architecture can safely support:
- Immediate, low-risk: 2 providers (Ollama + Claude) after provider abstraction completion.
- Medium-term, with stronger model registry and policy controls: 3 to 5 providers.
- Beyond that, complexity increases sharply (routing policy, eval drift, cost governance, failover logic).

Practical recommendation:
- Target 3 providers maximum in near-term production to keep quality and governance manageable.

## 6. Effects on the reasoning process
This agent design has strong practical reasoning effects:
- Better grounding: retrieval + graph + memory before generation.
- Better safety: security and validator can block low-confidence or high-risk paths.
- Better explainability: evidence scoring and structured answer sections.
- Better operability: cost and learning agents add operational and iterative improvement context.

Main reasoning limitations today:
- Some specialized agents are not yet wired into default workflows.
- Risk classification is still heuristic-heavy.
- Model provider abstraction is not complete, limiting multi-LLM strategy.

## 7. Future development and practical effect
High-value future steps:
1. Full provider abstraction (Ollama + Claude) and unified model gateway.
2. Integrate query_planner/topology/impact/rca into default decision path.
3. Add continuous evaluation per route and per model tier.
4. Add real action approval pipeline for execution agent (human-in-the-loop).
5. Add production dashboards for model quality, hallucination rate, route accuracy, and cost.

Practical effect if implemented:
- Higher answer reliability for infrastructure questions.
- Better incident triage and root-cause speed.
- Safer production operations with measurable governance.
- Lower model spend through tiered allocation and better route selection.

## 8. Comparison with similar existing applications

| Platform type | Similarity | Difference vs ProjectRAG |
|---|---|---|
| GraphRAG implementations | Use graph + retrieval for grounded answers | ProjectRAG is local-first with stronger operational safety defaults |
| LangChain/LlamaIndex multi-agent apps | Agent orchestration and retrieval pipelines | ProjectRAG emphasizes infra operations reasoning and policy blocking |
| Enterprise AI assistants (Glean/Notion AI) | Document question answering | ProjectRAG is more self-hosted/customizable but less product-polished |
| Incident/observability assistants | RCA and impact analysis goals overlap | ProjectRAG combines docs + graph + memory in one internal platform |

## 9. Final assessment
ProjectRAG already has a serious multi-agent base: good modularity, grounded reasoning path, and strong safety posture. The most important upgrade is not adding more agents first, but finishing provider abstraction and integrating specialized analysis agents into the default workflow. That will deliver the highest practical production impact.