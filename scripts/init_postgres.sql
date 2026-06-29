--
-- PostgreSQL database dump
--

\restrict uAkNKsQ8VubUbQJi6cwNZ4OTLksaCcjDayvxa25IiIRt4GAQbFj1rZ9LxKqz4vO

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg12+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: action_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.action_plans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    status text DEFAULT 'planned'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: agent_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    task_id uuid,
    workflow_id uuid,
    agent_name text NOT NULL,
    status text DEFAULT 'completed'::text NOT NULL,
    output jsonb DEFAULT '{}'::jsonb NOT NULL,
    error text,
    latency_ms integer DEFAULT 0 NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: agent_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    agent_name text NOT NULL,
    status text NOT NULL,
    input jsonb DEFAULT '{}'::jsonb NOT NULL,
    output jsonb DEFAULT '{}'::jsonb NOT NULL,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: agent_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_tasks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    agent_name text NOT NULL,
    task_type text NOT NULL,
    priority integer DEFAULT 100 NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    input jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: approval_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.approval_requests (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    status text DEFAULT 'pending'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: background_jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.background_jobs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    job_type text NOT NULL,
    status text DEFAULT 'queued'::text NOT NULL,
    resource_type text,
    resource_id text,
    attempts integer DEFAULT 0 NOT NULL,
    max_attempts integer DEFAULT 3 NOT NULL,
    next_retry_at timestamp with time zone,
    error text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    started_at timestamp with time zone,
    completed_at timestamp with time zone
);


--
-- Name: capacity_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.capacity_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_name text NOT NULL,
    resource_type text NOT NULL,
    capacity_total numeric,
    capacity_used numeric,
    capacity_free numeric,
    utilization_percent numeric,
    risk_score numeric DEFAULT 0.0 NOT NULL,
    severity text DEFAULT 'low'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: chaos_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chaos_metrics (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_name text NOT NULL,
    entropy numeric,
    instability numeric,
    complexity_score numeric,
    risk_score numeric DEFAULT 0.0 NOT NULL,
    severity text DEFAULT 'low'::text NOT NULL,
    metrics jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: chunks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chunks (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    document_id uuid NOT NULL,
    chunk_index integer NOT NULL,
    content text NOT NULL,
    embedding public.vector(768),
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cluster_nodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cluster_nodes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    node_name text NOT NULL,
    node_type text DEFAULT 'local'::text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    capabilities jsonb DEFAULT '[]'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    last_seen_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: connector_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.connector_configs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    connector_type text NOT NULL,
    name text NOT NULL,
    status text DEFAULT 'disabled'::text NOT NULL,
    mode text DEFAULT 'read_only'::text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL,
    secret_ref text,
    last_sync_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: connector_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.connector_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    connector_id uuid,
    connector_type text NOT NULL,
    status text NOT NULL,
    items_seen integer DEFAULT 0 NOT NULL,
    items_imported integer DEFAULT 0 NOT NULL,
    error text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone
);


--
-- Name: constitution_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.constitution_rules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    rule_name text NOT NULL,
    description text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: critical_paths; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.critical_paths (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_name text NOT NULL,
    path jsonb DEFAULT '[]'::jsonb NOT NULL,
    path_length integer DEFAULT 0 NOT NULL,
    risk_score numeric DEFAULT 0.0 NOT NULL,
    severity text DEFAULT 'low'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: decision_audits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.decision_audits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    decision text NOT NULL,
    actor text DEFAULT 'system'::text NOT NULL,
    decision_status text DEFAULT 'review_required'::text NOT NULL,
    risk_level text DEFAULT 'low'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: digital_twin_snapshots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.digital_twin_snapshots (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    discovery_run_id uuid,
    snapshot_name text NOT NULL,
    entities jsonb DEFAULT '[]'::jsonb NOT NULL,
    relationships jsonb DEFAULT '[]'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: discovery_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.discovery_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    started_at timestamp without time zone DEFAULT now() NOT NULL,
    completed_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: documents; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    source text NOT NULL,
    file_hash text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: evaluation_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evaluation_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dataset_name text NOT NULL,
    question text NOT NULL,
    answer text NOT NULL,
    metrics jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evidence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    hypothesis_id uuid,
    experiment_id uuid,
    source text NOT NULL,
    content jsonb DEFAULT '{}'::jsonb NOT NULL,
    confidence numeric DEFAULT 0.0 NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: evolution_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.evolution_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    title text NOT NULL,
    status text DEFAULT 'review_required'::text NOT NULL,
    proposal jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: execution_audits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.execution_audits (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    status text DEFAULT 'recorded'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: experience_outcomes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.experience_outcomes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    experience_run_id uuid NOT NULL,
    status text NOT NULL,
    results jsonb DEFAULT '{}'::jsonb NOT NULL,
    lessons_learned jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: experience_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.experience_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    goal text NOT NULL,
    plan jsonb DEFAULT '{}'::jsonb NOT NULL,
    lessons_learned jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: experience_steps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.experience_steps (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    experience_run_id uuid NOT NULL,
    step_index integer NOT NULL,
    action jsonb DEFAULT '{}'::jsonb NOT NULL,
    result jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: experiments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.experiments (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    hypothesis_id uuid,
    workflow_id uuid,
    name text NOT NULL,
    status text DEFAULT 'planned'::text NOT NULL,
    plan jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: failure_predictions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.failure_predictions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_name text NOT NULL,
    prediction text NOT NULL,
    probability numeric DEFAULT 0.0 NOT NULL,
    risk_score numeric DEFAULT 0.0 NOT NULL,
    severity text DEFAULT 'low'::text NOT NULL,
    horizon text,
    evidence jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: fitness_scores; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fitness_scores (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    evolution_run_id uuid,
    score numeric DEFAULT 0.0 NOT NULL,
    passed boolean DEFAULT false NOT NULL,
    metrics jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: governance_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.governance_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    event_type text NOT NULL,
    decision text,
    status text DEFAULT 'recorded'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: graph_facts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.graph_facts (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subject text NOT NULL,
    predicate text NOT NULL,
    object text NOT NULL,
    source_document_id uuid,
    source_chunk_id uuid,
    confidence numeric DEFAULT 0.8 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: hypotheses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hypotheses (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    statement text NOT NULL,
    status text DEFAULT 'proposed'::text NOT NULL,
    confidence numeric DEFAULT 0.0 NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: idempotency_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.idempotency_results (
    request_id uuid DEFAULT gen_random_uuid() NOT NULL,
    idempotency_key text NOT NULL,
    result jsonb DEFAULT '{}'::jsonb NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '24:00:00'::interval) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: impact_analysis; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.impact_analysis (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_name text NOT NULL,
    direct_dependencies jsonb DEFAULT '[]'::jsonb NOT NULL,
    indirect_dependencies jsonb DEFAULT '[]'::jsonb NOT NULL,
    risk_score numeric DEFAULT 0.0 NOT NULL,
    severity text DEFAULT 'low'::text NOT NULL,
    explanation text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: incident_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.incident_history (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    entity_name text NOT NULL,
    incident_type text,
    severity text DEFAULT 'low'::text NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    description text,
    started_at timestamp with time zone,
    resolved_at timestamp with time zone,
    risk_score numeric DEFAULT 0.0 NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: inventory_entities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    discovery_run_id uuid,
    entity_name text NOT NULL,
    entity_type text NOT NULL,
    provider text,
    region text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    CONSTRAINT inventory_entities_entity_type_check CHECK ((entity_type = ANY (ARRAY['DockerContainer'::text, 'VM'::text, 'Host'::text, 'Network'::text, 'Subnet'::text, 'Database'::text, 'Service'::text, 'API'::text, 'Cluster'::text, 'Namespace'::text, 'Pod'::text])))
);


--
-- Name: inventory_relationships; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.inventory_relationships (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    discovery_run_id uuid,
    source_entity_id uuid,
    target_entity_id uuid,
    source_entity_name text NOT NULL,
    relationship text NOT NULL,
    target_entity_name text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: memory_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.memory_items (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    memory_type text NOT NULL,
    key text NOT NULL,
    value jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: policy_violations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.policy_violations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    rule_name text NOT NULL,
    severity text DEFAULT 'medium'::text NOT NULL,
    description text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: research_portfolio; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.research_portfolio (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    description text,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: research_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.research_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    hypothesis_id uuid,
    experiment_id uuid,
    status text DEFAULT 'draft'::text NOT NULL,
    conclusion text,
    metrics jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: rollback_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.rollback_plans (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    status text DEFAULT 'planned'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: security_audit_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.security_audit_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    "user" text NOT NULL,
    role text NOT NULL,
    action text NOT NULL,
    resource text NOT NULL,
    decision text NOT NULL,
    risk_level text DEFAULT 'low'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: theories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.theories (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    hypothesis_id uuid,
    statement text NOT NULL,
    status text DEFAULT 'draft'::text NOT NULL,
    confidence numeric DEFAULT 0.0 NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: tool_calls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tool_calls (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    tool_name text NOT NULL,
    risk_level text NOT NULL,
    input jsonb DEFAULT '{}'::jsonb NOT NULL,
    output jsonb DEFAULT '{}'::jsonb NOT NULL,
    status text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: tool_policies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tool_policies (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tool_name text NOT NULL,
    allowed boolean DEFAULT false NOT NULL,
    risk_level text NOT NULL,
    requires_approval boolean DEFAULT true NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: trust_scores; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.trust_scores (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    subject text NOT NULL,
    score numeric DEFAULT 0.0 NOT NULL,
    trust_level text DEFAULT 'low'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: validation_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.validation_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    agent_run_id uuid,
    validator_name text NOT NULL,
    passed boolean NOT NULL,
    details jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: verification_results; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.verification_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid,
    status text DEFAULT 'pending'::text NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


--
-- Name: workflow_checkpoints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workflow_checkpoints (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_id uuid NOT NULL,
    step_name text NOT NULL,
    state jsonb DEFAULT '{}'::jsonb NOT NULL,
    status text DEFAULT 'running'::text NOT NULL,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: workflow_runs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workflow_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    workflow_name text NOT NULL,
    status text NOT NULL,
    input jsonb DEFAULT '{}'::jsonb NOT NULL,
    output jsonb DEFAULT '{}'::jsonb NOT NULL,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: action_plans action_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_plans
    ADD CONSTRAINT action_plans_pkey PRIMARY KEY (id);


--
-- Name: agent_results agent_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_results
    ADD CONSTRAINT agent_results_pkey PRIMARY KEY (id);


--
-- Name: agent_runs agent_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_runs
    ADD CONSTRAINT agent_runs_pkey PRIMARY KEY (id);


--
-- Name: agent_tasks agent_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_tasks
    ADD CONSTRAINT agent_tasks_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: approval_requests approval_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_pkey PRIMARY KEY (id);


--
-- Name: background_jobs background_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.background_jobs
    ADD CONSTRAINT background_jobs_pkey PRIMARY KEY (id);


--
-- Name: capacity_history capacity_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.capacity_history
    ADD CONSTRAINT capacity_history_pkey PRIMARY KEY (id);


--
-- Name: chaos_metrics chaos_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chaos_metrics
    ADD CONSTRAINT chaos_metrics_pkey PRIMARY KEY (id);


--
-- Name: chunks chunks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_pkey PRIMARY KEY (id);


--
-- Name: cluster_nodes cluster_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cluster_nodes
    ADD CONSTRAINT cluster_nodes_pkey PRIMARY KEY (id);


--
-- Name: connector_configs connector_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.connector_configs
    ADD CONSTRAINT connector_configs_pkey PRIMARY KEY (id);


--
-- Name: connector_runs connector_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.connector_runs
    ADD CONSTRAINT connector_runs_pkey PRIMARY KEY (id);


--
-- Name: constitution_rules constitution_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.constitution_rules
    ADD CONSTRAINT constitution_rules_pkey PRIMARY KEY (id);


--
-- Name: critical_paths critical_paths_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.critical_paths
    ADD CONSTRAINT critical_paths_pkey PRIMARY KEY (id);


--
-- Name: decision_audits decision_audits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decision_audits
    ADD CONSTRAINT decision_audits_pkey PRIMARY KEY (id);


--
-- Name: digital_twin_snapshots digital_twin_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_twin_snapshots
    ADD CONSTRAINT digital_twin_snapshots_pkey PRIMARY KEY (id);


--
-- Name: discovery_runs discovery_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.discovery_runs
    ADD CONSTRAINT discovery_runs_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: evaluation_results evaluation_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evaluation_results
    ADD CONSTRAINT evaluation_results_pkey PRIMARY KEY (id);


--
-- Name: evidence evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_pkey PRIMARY KEY (id);


--
-- Name: evolution_runs evolution_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evolution_runs
    ADD CONSTRAINT evolution_runs_pkey PRIMARY KEY (id);


--
-- Name: execution_audits execution_audits_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.execution_audits
    ADD CONSTRAINT execution_audits_pkey PRIMARY KEY (id);


--
-- Name: experience_outcomes experience_outcomes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experience_outcomes
    ADD CONSTRAINT experience_outcomes_pkey PRIMARY KEY (id);


--
-- Name: experience_runs experience_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experience_runs
    ADD CONSTRAINT experience_runs_pkey PRIMARY KEY (id);


--
-- Name: experience_steps experience_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experience_steps
    ADD CONSTRAINT experience_steps_pkey PRIMARY KEY (id);


--
-- Name: experiments experiments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_pkey PRIMARY KEY (id);


--
-- Name: failure_predictions failure_predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.failure_predictions
    ADD CONSTRAINT failure_predictions_pkey PRIMARY KEY (id);


--
-- Name: fitness_scores fitness_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fitness_scores
    ADD CONSTRAINT fitness_scores_pkey PRIMARY KEY (id);


--
-- Name: governance_events governance_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.governance_events
    ADD CONSTRAINT governance_events_pkey PRIMARY KEY (id);


--
-- Name: graph_facts graph_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.graph_facts
    ADD CONSTRAINT graph_facts_pkey PRIMARY KEY (id);


--
-- Name: hypotheses hypotheses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hypotheses
    ADD CONSTRAINT hypotheses_pkey PRIMARY KEY (id);


--
-- Name: idempotency_results idempotency_results_idempotency_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.idempotency_results
    ADD CONSTRAINT idempotency_results_idempotency_key_key UNIQUE (idempotency_key);


--
-- Name: idempotency_results idempotency_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.idempotency_results
    ADD CONSTRAINT idempotency_results_pkey PRIMARY KEY (request_id);


--
-- Name: impact_analysis impact_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.impact_analysis
    ADD CONSTRAINT impact_analysis_pkey PRIMARY KEY (id);


--
-- Name: incident_history incident_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.incident_history
    ADD CONSTRAINT incident_history_pkey PRIMARY KEY (id);


--
-- Name: inventory_entities inventory_entities_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_entities
    ADD CONSTRAINT inventory_entities_pkey PRIMARY KEY (id);


--
-- Name: inventory_relationships inventory_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_relationships
    ADD CONSTRAINT inventory_relationships_pkey PRIMARY KEY (id);


--
-- Name: memory_items memory_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.memory_items
    ADD CONSTRAINT memory_items_pkey PRIMARY KEY (id);


--
-- Name: policy_violations policy_violations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_violations
    ADD CONSTRAINT policy_violations_pkey PRIMARY KEY (id);


--
-- Name: research_portfolio research_portfolio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_portfolio
    ADD CONSTRAINT research_portfolio_pkey PRIMARY KEY (id);


--
-- Name: research_results research_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_results
    ADD CONSTRAINT research_results_pkey PRIMARY KEY (id);


--
-- Name: rollback_plans rollback_plans_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rollback_plans
    ADD CONSTRAINT rollback_plans_pkey PRIMARY KEY (id);


--
-- Name: security_audit_events security_audit_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.security_audit_events
    ADD CONSTRAINT security_audit_events_pkey PRIMARY KEY (id);


--
-- Name: theories theories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.theories
    ADD CONSTRAINT theories_pkey PRIMARY KEY (id);


--
-- Name: tool_calls tool_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_calls
    ADD CONSTRAINT tool_calls_pkey PRIMARY KEY (id);


--
-- Name: tool_policies tool_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_policies
    ADD CONSTRAINT tool_policies_pkey PRIMARY KEY (id);


--
-- Name: trust_scores trust_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trust_scores
    ADD CONSTRAINT trust_scores_pkey PRIMARY KEY (id);


--
-- Name: validation_results validation_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.validation_results
    ADD CONSTRAINT validation_results_pkey PRIMARY KEY (id);


--
-- Name: verification_results verification_results_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_results
    ADD CONSTRAINT verification_results_pkey PRIMARY KEY (id);


--
-- Name: workflow_checkpoints workflow_checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_checkpoints
    ADD CONSTRAINT workflow_checkpoints_pkey PRIMARY KEY (id);


--
-- Name: workflow_checkpoints workflow_checkpoints_workflow_id_step_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_checkpoints
    ADD CONSTRAINT workflow_checkpoints_workflow_id_step_name_key UNIQUE (workflow_id, step_name);


--
-- Name: workflow_runs workflow_runs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_runs
    ADD CONSTRAINT workflow_runs_pkey PRIMARY KEY (id);


--
-- Name: idx_action_plans_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_action_plans_created_at ON public.action_plans USING btree (created_at);


--
-- Name: idx_action_plans_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_action_plans_status ON public.action_plans USING btree (status);


--
-- Name: idx_action_plans_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_action_plans_workflow_id ON public.action_plans USING btree (workflow_id);


--
-- Name: idx_agent_results_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_results_agent_name ON public.agent_results USING btree (agent_name);


--
-- Name: idx_agent_results_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_results_created_at ON public.agent_results USING btree (created_at);


--
-- Name: idx_agent_results_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_results_status ON public.agent_results USING btree (status);


--
-- Name: idx_agent_results_task_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_results_task_id ON public.agent_results USING btree (task_id);


--
-- Name: idx_agent_results_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_results_workflow_id ON public.agent_results USING btree (workflow_id);


--
-- Name: idx_agent_runs_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_runs_tenant_created_at ON public.agent_runs USING btree (COALESCE((input ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: idx_agent_runs_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_runs_workflow_id ON public.agent_runs USING btree (workflow_id);


--
-- Name: idx_agent_tasks_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_tasks_agent_name ON public.agent_tasks USING btree (agent_name);


--
-- Name: idx_agent_tasks_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_tasks_created_at ON public.agent_tasks USING btree (created_at);


--
-- Name: idx_agent_tasks_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_tasks_status ON public.agent_tasks USING btree (status);


--
-- Name: idx_agent_tasks_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_tasks_workflow_id ON public.agent_tasks USING btree (workflow_id);


--
-- Name: idx_approval_requests_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_approval_requests_created_at ON public.approval_requests USING btree (created_at);


--
-- Name: idx_approval_requests_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_approval_requests_status ON public.approval_requests USING btree (status);


--
-- Name: idx_approval_requests_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_approval_requests_workflow_id ON public.approval_requests USING btree (workflow_id);


--
-- Name: idx_background_jobs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_background_jobs_created_at ON public.background_jobs USING btree (created_at);


--
-- Name: idx_background_jobs_next_retry_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_background_jobs_next_retry_at ON public.background_jobs USING btree (next_retry_at);


--
-- Name: idx_background_jobs_resource; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_background_jobs_resource ON public.background_jobs USING btree (resource_type, resource_id);


--
-- Name: idx_background_jobs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_background_jobs_status ON public.background_jobs USING btree (status);


--
-- Name: idx_background_jobs_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_background_jobs_type ON public.background_jobs USING btree (job_type);


--
-- Name: idx_capacity_history_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_capacity_history_created_at ON public.capacity_history USING btree (created_at);


--
-- Name: idx_capacity_history_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_capacity_history_entity_name ON public.capacity_history USING btree (entity_name);


--
-- Name: idx_capacity_history_risk_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_capacity_history_risk_score ON public.capacity_history USING btree (risk_score);


--
-- Name: idx_capacity_history_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_capacity_history_severity ON public.capacity_history USING btree (severity);


--
-- Name: idx_chaos_metrics_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chaos_metrics_created_at ON public.chaos_metrics USING btree (created_at);


--
-- Name: idx_chaos_metrics_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chaos_metrics_entity_name ON public.chaos_metrics USING btree (entity_name);


--
-- Name: idx_chaos_metrics_risk_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chaos_metrics_risk_score ON public.chaos_metrics USING btree (risk_score);


--
-- Name: idx_chaos_metrics_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chaos_metrics_severity ON public.chaos_metrics USING btree (severity);


--
-- Name: idx_chunks_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chunks_created_at ON public.chunks USING btree (created_at);


--
-- Name: idx_chunks_document_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chunks_document_id ON public.chunks USING btree (document_id);


--
-- Name: idx_chunks_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chunks_tenant_created_at ON public.chunks USING btree (COALESCE((metadata ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: idx_chunks_tenant_document_chunk_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_chunks_tenant_document_chunk_index ON public.chunks USING btree (COALESCE((metadata ->> 'tenant_id'::text), 'local'::text), document_id, chunk_index);


--
-- Name: idx_cluster_nodes_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cluster_nodes_created_at ON public.cluster_nodes USING btree (created_at);


--
-- Name: idx_cluster_nodes_node_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cluster_nodes_node_name ON public.cluster_nodes USING btree (node_name);


--
-- Name: idx_cluster_nodes_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cluster_nodes_status ON public.cluster_nodes USING btree (status);


--
-- Name: idx_connector_configs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_connector_configs_status ON public.connector_configs USING btree (status);


--
-- Name: idx_connector_configs_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_connector_configs_type ON public.connector_configs USING btree (connector_type);


--
-- Name: idx_connector_runs_connector_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_connector_runs_connector_id ON public.connector_runs USING btree (connector_id);


--
-- Name: idx_connector_runs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_connector_runs_status ON public.connector_runs USING btree (status);


--
-- Name: idx_connector_runs_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_connector_runs_type ON public.connector_runs USING btree (connector_type);


--
-- Name: idx_constitution_rules_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_constitution_rules_created_at ON public.constitution_rules USING btree (created_at);


--
-- Name: idx_constitution_rules_rule_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_constitution_rules_rule_name ON public.constitution_rules USING btree (rule_name);


--
-- Name: idx_constitution_rules_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_constitution_rules_status ON public.constitution_rules USING btree (status);


--
-- Name: idx_critical_paths_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_critical_paths_created_at ON public.critical_paths USING btree (created_at);


--
-- Name: idx_critical_paths_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_critical_paths_entity_name ON public.critical_paths USING btree (entity_name);


--
-- Name: idx_critical_paths_risk_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_critical_paths_risk_score ON public.critical_paths USING btree (risk_score);


--
-- Name: idx_critical_paths_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_critical_paths_severity ON public.critical_paths USING btree (severity);


--
-- Name: idx_decision_audits_actor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_decision_audits_actor ON public.decision_audits USING btree (actor);


--
-- Name: idx_decision_audits_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_decision_audits_created_at ON public.decision_audits USING btree (created_at);


--
-- Name: idx_decision_audits_decision_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_decision_audits_decision_status ON public.decision_audits USING btree (decision_status);


--
-- Name: idx_decision_audits_risk_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_decision_audits_risk_level ON public.decision_audits USING btree (risk_level);


--
-- Name: idx_decision_audits_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_decision_audits_workflow_id ON public.decision_audits USING btree (workflow_id);


--
-- Name: idx_digital_twin_snapshots_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_digital_twin_snapshots_created_at ON public.digital_twin_snapshots USING btree (created_at);


--
-- Name: idx_digital_twin_snapshots_discovery_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_digital_twin_snapshots_discovery_run_id ON public.digital_twin_snapshots USING btree (discovery_run_id);


--
-- Name: idx_digital_twin_snapshots_snapshot_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_digital_twin_snapshots_snapshot_name ON public.digital_twin_snapshots USING btree (snapshot_name);


--
-- Name: idx_discovery_runs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_discovery_runs_created_at ON public.discovery_runs USING btree (created_at);


--
-- Name: idx_discovery_runs_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_discovery_runs_source ON public.discovery_runs USING btree (source);


--
-- Name: idx_discovery_runs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_discovery_runs_status ON public.discovery_runs USING btree (status);


--
-- Name: idx_documents_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_documents_created_at ON public.documents USING btree (created_at);


--
-- Name: idx_documents_file_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_documents_file_hash ON public.documents USING btree (file_hash);


--
-- Name: idx_documents_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_documents_tenant_created_at ON public.documents USING btree (COALESCE((metadata ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: idx_documents_tenant_file_hash; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_documents_tenant_file_hash ON public.documents USING btree (COALESCE((metadata ->> 'tenant_id'::text), 'local'::text), file_hash);


--
-- Name: idx_evaluation_results_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evaluation_results_created_at ON public.evaluation_results USING btree (created_at);


--
-- Name: idx_evaluation_results_dataset_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evaluation_results_dataset_name ON public.evaluation_results USING btree (dataset_name);


--
-- Name: idx_evidence_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evidence_created_at ON public.evidence USING btree (created_at);


--
-- Name: idx_evidence_experiment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evidence_experiment_id ON public.evidence USING btree (experiment_id);


--
-- Name: idx_evidence_hypothesis_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evidence_hypothesis_id ON public.evidence USING btree (hypothesis_id);


--
-- Name: idx_evidence_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evidence_source ON public.evidence USING btree (source);


--
-- Name: idx_evolution_runs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evolution_runs_created_at ON public.evolution_runs USING btree (created_at);


--
-- Name: idx_evolution_runs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evolution_runs_status ON public.evolution_runs USING btree (status);


--
-- Name: idx_evolution_runs_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_evolution_runs_workflow_id ON public.evolution_runs USING btree (workflow_id);


--
-- Name: idx_execution_audits_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_execution_audits_created_at ON public.execution_audits USING btree (created_at);


--
-- Name: idx_execution_audits_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_execution_audits_status ON public.execution_audits USING btree (status);


--
-- Name: idx_execution_audits_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_execution_audits_workflow_id ON public.execution_audits USING btree (workflow_id);


--
-- Name: idx_experience_outcomes_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experience_outcomes_run_id ON public.experience_outcomes USING btree (experience_run_id);


--
-- Name: idx_experience_outcomes_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experience_outcomes_status ON public.experience_outcomes USING btree (status);


--
-- Name: idx_experience_runs_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experience_runs_created_at ON public.experience_runs USING btree (created_at);


--
-- Name: idx_experience_runs_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experience_runs_tenant_created_at ON public.experience_runs USING btree (COALESCE((plan ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: idx_experience_steps_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experience_steps_run_id ON public.experience_steps USING btree (experience_run_id);


--
-- Name: idx_experiments_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experiments_created_at ON public.experiments USING btree (created_at);


--
-- Name: idx_experiments_hypothesis_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experiments_hypothesis_id ON public.experiments USING btree (hypothesis_id);


--
-- Name: idx_experiments_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experiments_status ON public.experiments USING btree (status);


--
-- Name: idx_experiments_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_experiments_workflow_id ON public.experiments USING btree (workflow_id);


--
-- Name: idx_failure_predictions_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_failure_predictions_created_at ON public.failure_predictions USING btree (created_at);


--
-- Name: idx_failure_predictions_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_failure_predictions_entity_name ON public.failure_predictions USING btree (entity_name);


--
-- Name: idx_failure_predictions_risk_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_failure_predictions_risk_score ON public.failure_predictions USING btree (risk_score);


--
-- Name: idx_failure_predictions_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_failure_predictions_severity ON public.failure_predictions USING btree (severity);


--
-- Name: idx_fitness_scores_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fitness_scores_created_at ON public.fitness_scores USING btree (created_at);


--
-- Name: idx_fitness_scores_evolution_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fitness_scores_evolution_run_id ON public.fitness_scores USING btree (evolution_run_id);


--
-- Name: idx_fitness_scores_passed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fitness_scores_passed ON public.fitness_scores USING btree (passed);


--
-- Name: idx_fitness_scores_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fitness_scores_score ON public.fitness_scores USING btree (score);


--
-- Name: idx_governance_events_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_governance_events_created_at ON public.governance_events USING btree (created_at);


--
-- Name: idx_governance_events_event_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_governance_events_event_type ON public.governance_events USING btree (event_type);


--
-- Name: idx_governance_events_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_governance_events_status ON public.governance_events USING btree (status);


--
-- Name: idx_governance_events_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_governance_events_workflow_id ON public.governance_events USING btree (workflow_id);


--
-- Name: idx_graph_facts_object; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_graph_facts_object ON public.graph_facts USING btree (object);


--
-- Name: idx_graph_facts_source_document_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_graph_facts_source_document_id ON public.graph_facts USING btree (source_document_id);


--
-- Name: idx_graph_facts_subject; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_graph_facts_subject ON public.graph_facts USING btree (subject);


--
-- Name: idx_hypotheses_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hypotheses_created_at ON public.hypotheses USING btree (created_at);


--
-- Name: idx_hypotheses_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hypotheses_status ON public.hypotheses USING btree (status);


--
-- Name: idx_hypotheses_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hypotheses_workflow_id ON public.hypotheses USING btree (workflow_id);


--
-- Name: idx_idempotency_results_expires_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_idempotency_results_expires_at ON public.idempotency_results USING btree (expires_at);


--
-- Name: idx_idempotency_results_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_idempotency_results_key ON public.idempotency_results USING btree (idempotency_key);


--
-- Name: idx_impact_analysis_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_impact_analysis_created_at ON public.impact_analysis USING btree (created_at);


--
-- Name: idx_impact_analysis_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_impact_analysis_entity_name ON public.impact_analysis USING btree (entity_name);


--
-- Name: idx_impact_analysis_risk_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_impact_analysis_risk_score ON public.impact_analysis USING btree (risk_score);


--
-- Name: idx_impact_analysis_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_impact_analysis_severity ON public.impact_analysis USING btree (severity);


--
-- Name: idx_incident_history_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_history_created_at ON public.incident_history USING btree (created_at);


--
-- Name: idx_incident_history_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_history_entity_name ON public.incident_history USING btree (entity_name);


--
-- Name: idx_incident_history_risk_score; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_history_risk_score ON public.incident_history USING btree (risk_score);


--
-- Name: idx_incident_history_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_incident_history_severity ON public.incident_history USING btree (severity);


--
-- Name: idx_inventory_entities_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_entities_created_at ON public.inventory_entities USING btree (created_at);


--
-- Name: idx_inventory_entities_discovery_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_entities_discovery_run_id ON public.inventory_entities USING btree (discovery_run_id);


--
-- Name: idx_inventory_entities_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_entities_entity_name ON public.inventory_entities USING btree (entity_name);


--
-- Name: idx_inventory_entities_entity_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_entities_entity_type ON public.inventory_entities USING btree (entity_type);


--
-- Name: idx_inventory_relationships_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_relationships_created_at ON public.inventory_relationships USING btree (created_at);


--
-- Name: idx_inventory_relationships_discovery_run_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_relationships_discovery_run_id ON public.inventory_relationships USING btree (discovery_run_id);


--
-- Name: idx_inventory_relationships_relationship; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_relationships_relationship ON public.inventory_relationships USING btree (relationship);


--
-- Name: idx_inventory_relationships_source_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_relationships_source_entity_name ON public.inventory_relationships USING btree (source_entity_name);


--
-- Name: idx_inventory_relationships_target_entity_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_inventory_relationships_target_entity_name ON public.inventory_relationships USING btree (target_entity_name);


--
-- Name: idx_memory_items_memory_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_memory_items_memory_type ON public.memory_items USING btree (memory_type);


--
-- Name: idx_memory_items_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_memory_items_tenant_created_at ON public.memory_items USING btree (COALESCE((value ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: idx_policy_violations_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_violations_created_at ON public.policy_violations USING btree (created_at);


--
-- Name: idx_policy_violations_rule_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_violations_rule_name ON public.policy_violations USING btree (rule_name);


--
-- Name: idx_policy_violations_severity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_violations_severity ON public.policy_violations USING btree (severity);


--
-- Name: idx_policy_violations_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_policy_violations_workflow_id ON public.policy_violations USING btree (workflow_id);


--
-- Name: idx_research_portfolio_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_portfolio_created_at ON public.research_portfolio USING btree (created_at);


--
-- Name: idx_research_portfolio_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_portfolio_name ON public.research_portfolio USING btree (name);


--
-- Name: idx_research_portfolio_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_portfolio_status ON public.research_portfolio USING btree (status);


--
-- Name: idx_research_results_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_results_created_at ON public.research_results USING btree (created_at);


--
-- Name: idx_research_results_experiment_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_results_experiment_id ON public.research_results USING btree (experiment_id);


--
-- Name: idx_research_results_hypothesis_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_results_hypothesis_id ON public.research_results USING btree (hypothesis_id);


--
-- Name: idx_research_results_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_research_results_status ON public.research_results USING btree (status);


--
-- Name: idx_rollback_plans_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rollback_plans_created_at ON public.rollback_plans USING btree (created_at);


--
-- Name: idx_rollback_plans_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rollback_plans_status ON public.rollback_plans USING btree (status);


--
-- Name: idx_rollback_plans_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_rollback_plans_workflow_id ON public.rollback_plans USING btree (workflow_id);


--
-- Name: idx_security_audit_events_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_action ON public.security_audit_events USING btree (action);


--
-- Name: idx_security_audit_events_decision; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_decision ON public.security_audit_events USING btree (decision);


--
-- Name: idx_security_audit_events_resource; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_resource ON public.security_audit_events USING btree (resource);


--
-- Name: idx_security_audit_events_risk_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_risk_level ON public.security_audit_events USING btree (risk_level);


--
-- Name: idx_security_audit_events_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_role ON public.security_audit_events USING btree (role);


--
-- Name: idx_security_audit_events_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_timestamp ON public.security_audit_events USING btree ("timestamp");


--
-- Name: idx_security_audit_events_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_security_audit_events_user ON public.security_audit_events USING btree ("user");


--
-- Name: idx_theories_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_theories_created_at ON public.theories USING btree (created_at);


--
-- Name: idx_theories_hypothesis_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_theories_hypothesis_id ON public.theories USING btree (hypothesis_id);


--
-- Name: idx_theories_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_theories_status ON public.theories USING btree (status);


--
-- Name: idx_tool_calls_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_calls_created_at ON public.tool_calls USING btree (created_at);


--
-- Name: idx_tool_calls_risk_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_calls_risk_level ON public.tool_calls USING btree (risk_level);


--
-- Name: idx_tool_calls_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_calls_status ON public.tool_calls USING btree (status);


--
-- Name: idx_tool_calls_tool_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_calls_tool_name ON public.tool_calls USING btree (tool_name);


--
-- Name: idx_tool_calls_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_calls_workflow_id ON public.tool_calls USING btree (workflow_id);


--
-- Name: idx_tool_policies_allowed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_policies_allowed ON public.tool_policies USING btree (allowed);


--
-- Name: idx_tool_policies_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_policies_created_at ON public.tool_policies USING btree (created_at);


--
-- Name: idx_tool_policies_requires_approval; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_policies_requires_approval ON public.tool_policies USING btree (requires_approval);


--
-- Name: idx_tool_policies_risk_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_policies_risk_level ON public.tool_policies USING btree (risk_level);


--
-- Name: idx_tool_policies_tool_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tool_policies_tool_name ON public.tool_policies USING btree (tool_name);


--
-- Name: idx_trust_scores_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_trust_scores_created_at ON public.trust_scores USING btree (created_at);


--
-- Name: idx_trust_scores_subject; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_trust_scores_subject ON public.trust_scores USING btree (subject);


--
-- Name: idx_trust_scores_trust_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_trust_scores_trust_level ON public.trust_scores USING btree (trust_level);


--
-- Name: idx_trust_scores_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_trust_scores_workflow_id ON public.trust_scores USING btree (workflow_id);


--
-- Name: idx_validation_results_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_validation_results_tenant_created_at ON public.validation_results USING btree (COALESCE((details ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: idx_validation_results_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_validation_results_workflow_id ON public.validation_results USING btree (workflow_id);


--
-- Name: idx_verification_results_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_verification_results_created_at ON public.verification_results USING btree (created_at);


--
-- Name: idx_verification_results_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_verification_results_status ON public.verification_results USING btree (status);


--
-- Name: idx_verification_results_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_verification_results_workflow_id ON public.verification_results USING btree (workflow_id);


--
-- Name: idx_workflow_checkpoints_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workflow_checkpoints_status ON public.workflow_checkpoints USING btree (status);


--
-- Name: idx_workflow_checkpoints_updated_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workflow_checkpoints_updated_at ON public.workflow_checkpoints USING btree (updated_at);


--
-- Name: idx_workflow_checkpoints_workflow_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workflow_checkpoints_workflow_id ON public.workflow_checkpoints USING btree (workflow_id);


--
-- Name: idx_workflow_runs_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workflow_runs_status ON public.workflow_runs USING btree (status);


--
-- Name: idx_workflow_runs_tenant_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_workflow_runs_tenant_created_at ON public.workflow_runs USING btree (COALESCE((input ->> 'tenant_id'::text), 'local'::text), created_at DESC);


--
-- Name: action_plans action_plans_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_plans
    ADD CONSTRAINT action_plans_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: agent_results agent_results_task_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_results
    ADD CONSTRAINT agent_results_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.agent_tasks(id) ON DELETE SET NULL;


--
-- Name: agent_results agent_results_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_results
    ADD CONSTRAINT agent_results_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: agent_runs agent_runs_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_runs
    ADD CONSTRAINT agent_runs_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: agent_tasks agent_tasks_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_tasks
    ADD CONSTRAINT agent_tasks_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: approval_requests approval_requests_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: chunks chunks_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chunks
    ADD CONSTRAINT chunks_document_id_fkey FOREIGN KEY (document_id) REFERENCES public.documents(id) ON DELETE CASCADE;


--
-- Name: connector_runs connector_runs_connector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.connector_runs
    ADD CONSTRAINT connector_runs_connector_id_fkey FOREIGN KEY (connector_id) REFERENCES public.connector_configs(id) ON DELETE SET NULL;


--
-- Name: decision_audits decision_audits_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decision_audits
    ADD CONSTRAINT decision_audits_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: digital_twin_snapshots digital_twin_snapshots_discovery_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.digital_twin_snapshots
    ADD CONSTRAINT digital_twin_snapshots_discovery_run_id_fkey FOREIGN KEY (discovery_run_id) REFERENCES public.discovery_runs(id) ON DELETE SET NULL;


--
-- Name: evidence evidence_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(id) ON DELETE SET NULL;


--
-- Name: evidence evidence_hypothesis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evidence
    ADD CONSTRAINT evidence_hypothesis_id_fkey FOREIGN KEY (hypothesis_id) REFERENCES public.hypotheses(id) ON DELETE SET NULL;


--
-- Name: evolution_runs evolution_runs_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.evolution_runs
    ADD CONSTRAINT evolution_runs_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: execution_audits execution_audits_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.execution_audits
    ADD CONSTRAINT execution_audits_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: experience_outcomes experience_outcomes_experience_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experience_outcomes
    ADD CONSTRAINT experience_outcomes_experience_run_id_fkey FOREIGN KEY (experience_run_id) REFERENCES public.experience_runs(id) ON DELETE CASCADE;


--
-- Name: experience_steps experience_steps_experience_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experience_steps
    ADD CONSTRAINT experience_steps_experience_run_id_fkey FOREIGN KEY (experience_run_id) REFERENCES public.experience_runs(id) ON DELETE CASCADE;


--
-- Name: experiments experiments_hypothesis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_hypothesis_id_fkey FOREIGN KEY (hypothesis_id) REFERENCES public.hypotheses(id) ON DELETE SET NULL;


--
-- Name: experiments experiments_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.experiments
    ADD CONSTRAINT experiments_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: fitness_scores fitness_scores_evolution_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fitness_scores
    ADD CONSTRAINT fitness_scores_evolution_run_id_fkey FOREIGN KEY (evolution_run_id) REFERENCES public.evolution_runs(id) ON DELETE SET NULL;


--
-- Name: governance_events governance_events_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.governance_events
    ADD CONSTRAINT governance_events_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: graph_facts graph_facts_source_chunk_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.graph_facts
    ADD CONSTRAINT graph_facts_source_chunk_id_fkey FOREIGN KEY (source_chunk_id) REFERENCES public.chunks(id) ON DELETE SET NULL;


--
-- Name: graph_facts graph_facts_source_document_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.graph_facts
    ADD CONSTRAINT graph_facts_source_document_id_fkey FOREIGN KEY (source_document_id) REFERENCES public.documents(id) ON DELETE SET NULL;


--
-- Name: hypotheses hypotheses_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hypotheses
    ADD CONSTRAINT hypotheses_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: inventory_entities inventory_entities_discovery_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_entities
    ADD CONSTRAINT inventory_entities_discovery_run_id_fkey FOREIGN KEY (discovery_run_id) REFERENCES public.discovery_runs(id) ON DELETE SET NULL;


--
-- Name: inventory_relationships inventory_relationships_discovery_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_relationships
    ADD CONSTRAINT inventory_relationships_discovery_run_id_fkey FOREIGN KEY (discovery_run_id) REFERENCES public.discovery_runs(id) ON DELETE SET NULL;


--
-- Name: inventory_relationships inventory_relationships_source_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_relationships
    ADD CONSTRAINT inventory_relationships_source_entity_id_fkey FOREIGN KEY (source_entity_id) REFERENCES public.inventory_entities(id) ON DELETE SET NULL;


--
-- Name: inventory_relationships inventory_relationships_target_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.inventory_relationships
    ADD CONSTRAINT inventory_relationships_target_entity_id_fkey FOREIGN KEY (target_entity_id) REFERENCES public.inventory_entities(id) ON DELETE SET NULL;


--
-- Name: policy_violations policy_violations_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.policy_violations
    ADD CONSTRAINT policy_violations_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: research_results research_results_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_results
    ADD CONSTRAINT research_results_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiments(id) ON DELETE SET NULL;


--
-- Name: research_results research_results_hypothesis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.research_results
    ADD CONSTRAINT research_results_hypothesis_id_fkey FOREIGN KEY (hypothesis_id) REFERENCES public.hypotheses(id) ON DELETE SET NULL;


--
-- Name: rollback_plans rollback_plans_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.rollback_plans
    ADD CONSTRAINT rollback_plans_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: theories theories_hypothesis_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.theories
    ADD CONSTRAINT theories_hypothesis_id_fkey FOREIGN KEY (hypothesis_id) REFERENCES public.hypotheses(id) ON DELETE SET NULL;


--
-- Name: tool_calls tool_calls_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tool_calls
    ADD CONSTRAINT tool_calls_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: trust_scores trust_scores_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.trust_scores
    ADD CONSTRAINT trust_scores_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: validation_results validation_results_agent_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.validation_results
    ADD CONSTRAINT validation_results_agent_run_id_fkey FOREIGN KEY (agent_run_id) REFERENCES public.agent_runs(id) ON DELETE SET NULL;


--
-- Name: validation_results validation_results_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.validation_results
    ADD CONSTRAINT validation_results_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: verification_results verification_results_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.verification_results
    ADD CONSTRAINT verification_results_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE SET NULL;


--
-- Name: workflow_checkpoints workflow_checkpoints_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_checkpoints
    ADD CONSTRAINT workflow_checkpoints_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflow_runs(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict uAkNKsQ8VubUbQJi6cwNZ4OTLksaCcjDayvxa25IiIRt4GAQbFj1rZ9LxKqz4vO

