CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    file_hash TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS workflow_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow_runs(id) ON DELETE SET NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID REFERENCES workflow_runs(id) ON DELETE SET NULL,
    agent_run_id UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
    validator_name TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_created_at ON chunks(created_at);
CREATE INDEX IF NOT EXISTS idx_memory_items_memory_type ON memory_items(memory_type);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON workflow_runs(status);
CREATE INDEX IF NOT EXISTS idx_agent_runs_workflow_id ON agent_runs(workflow_id);

CREATE TABLE IF NOT EXISTS graph_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    source_document_id UUID NULL REFERENCES documents(id) ON DELETE SET NULL,
    source_chunk_id UUID NULL REFERENCES chunks(id) ON DELETE SET NULL,
    confidence NUMERIC NOT NULL DEFAULT 0.8,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_graph_facts_subject ON graph_facts(subject);
CREATE INDEX IF NOT EXISTS idx_graph_facts_object ON graph_facts(object);
CREATE INDEX IF NOT EXISTS idx_graph_facts_source_document_id ON graph_facts(source_document_id);

CREATE TABLE IF NOT EXISTS evaluation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_name TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_evaluation_results_dataset_name ON evaluation_results(dataset_name);
CREATE INDEX IF NOT EXISTS idx_evaluation_results_created_at ON evaluation_results(created_at);

CREATE TABLE IF NOT EXISTS experience_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal TEXT NOT NULL,
    plan JSONB NOT NULL DEFAULT '{}'::jsonb,
    lessons_learned JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experience_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_run_id UUID NOT NULL REFERENCES experience_runs(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    action JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experience_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experience_run_id UUID NOT NULL REFERENCES experience_runs(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    results JSONB NOT NULL DEFAULT '{}'::jsonb,
    lessons_learned JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_experience_runs_created_at ON experience_runs(created_at);
CREATE INDEX IF NOT EXISTS idx_experience_steps_run_id ON experience_steps(experience_run_id);
CREATE INDEX IF NOT EXISTS idx_experience_outcomes_run_id ON experience_outcomes(experience_run_id);
CREATE INDEX IF NOT EXISTS idx_experience_outcomes_status ON experience_outcomes(status);

CREATE TABLE IF NOT EXISTS chaos_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    entropy NUMERIC,
    instability NUMERIC,
    complexity_score NUMERIC,
    risk_score NUMERIC NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'low',
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS incident_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    incident_type TEXT,
    severity TEXT NOT NULL DEFAULT 'low',
    status TEXT NOT NULL DEFAULT 'open',
    description TEXT,
    started_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    risk_score NUMERIC NOT NULL DEFAULT 0.0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS capacity_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    capacity_total NUMERIC,
    capacity_used NUMERIC,
    capacity_free NUMERIC,
    utilization_percent NUMERIC,
    risk_score NUMERIC NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'low',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS failure_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    prediction TEXT NOT NULL,
    probability NUMERIC NOT NULL DEFAULT 0.0,
    risk_score NUMERIC NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'low',
    horizon TEXT,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS critical_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    path JSONB NOT NULL DEFAULT '[]'::jsonb,
    path_length INTEGER NOT NULL DEFAULT 0,
    risk_score NUMERIC NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'low',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS impact_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_name TEXT NOT NULL,
    direct_dependencies JSONB NOT NULL DEFAULT '[]'::jsonb,
    indirect_dependencies JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_score NUMERIC NOT NULL DEFAULT 0.0,
    severity TEXT NOT NULL DEFAULT 'low',
    explanation TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chaos_metrics_entity_name ON chaos_metrics(entity_name);
CREATE INDEX IF NOT EXISTS idx_chaos_metrics_created_at ON chaos_metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_chaos_metrics_severity ON chaos_metrics(severity);
CREATE INDEX IF NOT EXISTS idx_chaos_metrics_risk_score ON chaos_metrics(risk_score);

CREATE INDEX IF NOT EXISTS idx_incident_history_entity_name ON incident_history(entity_name);
CREATE INDEX IF NOT EXISTS idx_incident_history_created_at ON incident_history(created_at);
CREATE INDEX IF NOT EXISTS idx_incident_history_severity ON incident_history(severity);
CREATE INDEX IF NOT EXISTS idx_incident_history_risk_score ON incident_history(risk_score);

CREATE INDEX IF NOT EXISTS idx_capacity_history_entity_name ON capacity_history(entity_name);
CREATE INDEX IF NOT EXISTS idx_capacity_history_created_at ON capacity_history(created_at);
CREATE INDEX IF NOT EXISTS idx_capacity_history_severity ON capacity_history(severity);
CREATE INDEX IF NOT EXISTS idx_capacity_history_risk_score ON capacity_history(risk_score);

CREATE INDEX IF NOT EXISTS idx_failure_predictions_entity_name ON failure_predictions(entity_name);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_created_at ON failure_predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_severity ON failure_predictions(severity);
CREATE INDEX IF NOT EXISTS idx_failure_predictions_risk_score ON failure_predictions(risk_score);

CREATE INDEX IF NOT EXISTS idx_critical_paths_entity_name ON critical_paths(entity_name);
CREATE INDEX IF NOT EXISTS idx_critical_paths_created_at ON critical_paths(created_at);
CREATE INDEX IF NOT EXISTS idx_critical_paths_severity ON critical_paths(severity);
CREATE INDEX IF NOT EXISTS idx_critical_paths_risk_score ON critical_paths(risk_score);

CREATE INDEX IF NOT EXISTS idx_impact_analysis_entity_name ON impact_analysis(entity_name);
CREATE INDEX IF NOT EXISTS idx_impact_analysis_created_at ON impact_analysis(created_at);
CREATE INDEX IF NOT EXISTS idx_impact_analysis_severity ON impact_analysis(severity);
CREATE INDEX IF NOT EXISTS idx_impact_analysis_risk_score ON impact_analysis(risk_score);

CREATE TABLE IF NOT EXISTS action_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approval_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS execution_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'recorded',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rollback_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS verification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_action_plans_workflow_id ON action_plans(workflow_id);
CREATE INDEX IF NOT EXISTS idx_action_plans_status ON action_plans(status);
CREATE INDEX IF NOT EXISTS idx_action_plans_created_at ON action_plans(created_at);

CREATE INDEX IF NOT EXISTS idx_approval_requests_workflow_id ON approval_requests(workflow_id);
CREATE INDEX IF NOT EXISTS idx_approval_requests_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_requests_created_at ON approval_requests(created_at);

CREATE INDEX IF NOT EXISTS idx_execution_audits_workflow_id ON execution_audits(workflow_id);
CREATE INDEX IF NOT EXISTS idx_execution_audits_status ON execution_audits(status);
CREATE INDEX IF NOT EXISTS idx_execution_audits_created_at ON execution_audits(created_at);

CREATE INDEX IF NOT EXISTS idx_rollback_plans_workflow_id ON rollback_plans(workflow_id);
CREATE INDEX IF NOT EXISTS idx_rollback_plans_status ON rollback_plans(status);
CREATE INDEX IF NOT EXISTS idx_rollback_plans_created_at ON rollback_plans(created_at);

CREATE INDEX IF NOT EXISTS idx_verification_results_workflow_id ON verification_results(workflow_id);
CREATE INDEX IF NOT EXISTS idx_verification_results_status ON verification_results(status);
CREATE INDEX IF NOT EXISTS idx_verification_results_created_at ON verification_results(created_at);

CREATE TABLE IF NOT EXISTS tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    tool_name TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tool_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tool_name TEXT NOT NULL,
    allowed BOOLEAN NOT NULL DEFAULT false,
    risk_level TEXT NOT NULL,
    requires_approval BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_workflow_id ON tool_calls(workflow_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_tool_name ON tool_calls(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_calls_risk_level ON tool_calls(risk_level);
CREATE INDEX IF NOT EXISTS idx_tool_calls_status ON tool_calls(status);
CREATE INDEX IF NOT EXISTS idx_tool_calls_created_at ON tool_calls(created_at);

CREATE INDEX IF NOT EXISTS idx_tool_policies_tool_name ON tool_policies(tool_name);
CREATE INDEX IF NOT EXISTS idx_tool_policies_allowed ON tool_policies(allowed);
CREATE INDEX IF NOT EXISTS idx_tool_policies_risk_level ON tool_policies(risk_level);
CREATE INDEX IF NOT EXISTS idx_tool_policies_requires_approval ON tool_policies(requires_approval);
CREATE INDEX IF NOT EXISTS idx_tool_policies_created_at ON tool_policies(created_at);

CREATE TABLE IF NOT EXISTS discovery_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMP NOT NULL DEFAULT now(),
    completed_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inventory_entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discovery_run_id UUID NULL REFERENCES discovery_runs(id) ON DELETE SET NULL,
    entity_name TEXT NOT NULL,
    entity_type TEXT NOT NULL CHECK (
        entity_type IN (
            'DockerContainer',
            'VM',
            'Host',
            'Network',
            'Subnet',
            'Database',
            'Service',
            'API',
            'Cluster',
            'Namespace',
            'Pod'
        )
    ),
    provider TEXT,
    region TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS inventory_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discovery_run_id UUID NULL REFERENCES discovery_runs(id) ON DELETE SET NULL,
    source_entity_id UUID NULL REFERENCES inventory_entities(id) ON DELETE SET NULL,
    target_entity_id UUID NULL REFERENCES inventory_entities(id) ON DELETE SET NULL,
    source_entity_name TEXT NOT NULL,
    relationship TEXT NOT NULL,
    target_entity_name TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS digital_twin_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    discovery_run_id UUID NULL REFERENCES discovery_runs(id) ON DELETE SET NULL,
    snapshot_name TEXT NOT NULL,
    entities JSONB NOT NULL DEFAULT '[]'::jsonb,
    relationships JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_discovery_runs_source ON discovery_runs(source);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_status ON discovery_runs(status);
CREATE INDEX IF NOT EXISTS idx_discovery_runs_created_at ON discovery_runs(created_at);

CREATE INDEX IF NOT EXISTS idx_inventory_entities_discovery_run_id ON inventory_entities(discovery_run_id);
CREATE INDEX IF NOT EXISTS idx_inventory_entities_entity_name ON inventory_entities(entity_name);
CREATE INDEX IF NOT EXISTS idx_inventory_entities_entity_type ON inventory_entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_inventory_entities_created_at ON inventory_entities(created_at);

CREATE INDEX IF NOT EXISTS idx_inventory_relationships_discovery_run_id ON inventory_relationships(discovery_run_id);
CREATE INDEX IF NOT EXISTS idx_inventory_relationships_source_entity_name ON inventory_relationships(source_entity_name);
CREATE INDEX IF NOT EXISTS idx_inventory_relationships_target_entity_name ON inventory_relationships(target_entity_name);
CREATE INDEX IF NOT EXISTS idx_inventory_relationships_relationship ON inventory_relationships(relationship);
CREATE INDEX IF NOT EXISTS idx_inventory_relationships_created_at ON inventory_relationships(created_at);

CREATE INDEX IF NOT EXISTS idx_digital_twin_snapshots_discovery_run_id ON digital_twin_snapshots(discovery_run_id);
CREATE INDEX IF NOT EXISTS idx_digital_twin_snapshots_snapshot_name ON digital_twin_snapshots(snapshot_name);
CREATE INDEX IF NOT EXISTS idx_digital_twin_snapshots_created_at ON digital_twin_snapshots(created_at);

CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    agent_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 100,
    status TEXT NOT NULL DEFAULT 'pending',
    input JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NULL REFERENCES agent_tasks(id) ON DELETE SET NULL,
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    output JSONB NOT NULL DEFAULT '{}'::jsonb,
    error TEXT,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cluster_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    node_name TEXT NOT NULL,
    node_type TEXT NOT NULL DEFAULT 'local',
    status TEXT NOT NULL DEFAULT 'active',
    capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_seen_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent_name ON agent_tasks(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_workflow_id ON agent_tasks(workflow_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_created_at ON agent_tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_results_task_id ON agent_results(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_workflow_id ON agent_results(workflow_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_agent_name ON agent_results(agent_name);
CREATE INDEX IF NOT EXISTS idx_agent_results_status ON agent_results(status);
CREATE INDEX IF NOT EXISTS idx_agent_results_created_at ON agent_results(created_at);

CREATE INDEX IF NOT EXISTS idx_cluster_nodes_node_name ON cluster_nodes(node_name);
CREATE INDEX IF NOT EXISTS idx_cluster_nodes_status ON cluster_nodes(status);
CREATE INDEX IF NOT EXISTS idx_cluster_nodes_created_at ON cluster_nodes(created_at);

CREATE TABLE IF NOT EXISTS security_audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "user" TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    decision TEXT NOT NULL,
    risk_level TEXT NOT NULL DEFAULT 'low',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_security_audit_events_user ON security_audit_events("user");
CREATE INDEX IF NOT EXISTS idx_security_audit_events_role ON security_audit_events(role);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_action ON security_audit_events(action);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_resource ON security_audit_events(resource);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_decision ON security_audit_events(decision);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_risk_level ON security_audit_events(risk_level);
CREATE INDEX IF NOT EXISTS idx_security_audit_events_timestamp ON security_audit_events(timestamp);

CREATE TABLE IF NOT EXISTS hypotheses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    statement TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'proposed',
    confidence NUMERIC NOT NULL DEFAULT 0.0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_id UUID NULL REFERENCES hypotheses(id) ON DELETE SET NULL,
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'planned',
    plan JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_id UUID NULL REFERENCES hypotheses(id) ON DELETE SET NULL,
    experiment_id UUID NULL REFERENCES experiments(id) ON DELETE SET NULL,
    source TEXT NOT NULL,
    content JSONB NOT NULL DEFAULT '{}'::jsonb,
    confidence NUMERIC NOT NULL DEFAULT 0.0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_id UUID NULL REFERENCES hypotheses(id) ON DELETE SET NULL,
    experiment_id UUID NULL REFERENCES experiments(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    conclusion TEXT,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_portfolio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    description TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS theories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hypothesis_id UUID NULL REFERENCES hypotheses(id) ON DELETE SET NULL,
    statement TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    confidence NUMERIC NOT NULL DEFAULT 0.0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_hypotheses_workflow_id ON hypotheses(workflow_id);
CREATE INDEX IF NOT EXISTS idx_hypotheses_status ON hypotheses(status);
CREATE INDEX IF NOT EXISTS idx_hypotheses_created_at ON hypotheses(created_at);

CREATE INDEX IF NOT EXISTS idx_experiments_hypothesis_id ON experiments(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_experiments_workflow_id ON experiments(workflow_id);
CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_created_at ON experiments(created_at);

CREATE INDEX IF NOT EXISTS idx_evidence_hypothesis_id ON evidence(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_evidence_experiment_id ON evidence(experiment_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source);
CREATE INDEX IF NOT EXISTS idx_evidence_created_at ON evidence(created_at);

CREATE INDEX IF NOT EXISTS idx_research_results_hypothesis_id ON research_results(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_research_results_experiment_id ON research_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_research_results_status ON research_results(status);
CREATE INDEX IF NOT EXISTS idx_research_results_created_at ON research_results(created_at);

CREATE INDEX IF NOT EXISTS idx_research_portfolio_name ON research_portfolio(name);
CREATE INDEX IF NOT EXISTS idx_research_portfolio_status ON research_portfolio(status);
CREATE INDEX IF NOT EXISTS idx_research_portfolio_created_at ON research_portfolio(created_at);

CREATE INDEX IF NOT EXISTS idx_theories_hypothesis_id ON theories(hypothesis_id);
CREATE INDEX IF NOT EXISTS idx_theories_status ON theories(status);
CREATE INDEX IF NOT EXISTS idx_theories_created_at ON theories(created_at);

CREATE TABLE IF NOT EXISTS constitution_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS governance_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    decision TEXT,
    status TEXT NOT NULL DEFAULT 'recorded',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS trust_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    subject TEXT NOT NULL,
    score NUMERIC NOT NULL DEFAULT 0.0,
    trust_level TEXT NOT NULL DEFAULT 'low',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS policy_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    rule_name TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'medium',
    description TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS decision_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    decision TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'system',
    decision_status TEXT NOT NULL DEFAULT 'review_required',
    risk_level TEXT NOT NULL DEFAULT 'low',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_constitution_rules_rule_name ON constitution_rules(rule_name);
CREATE INDEX IF NOT EXISTS idx_constitution_rules_status ON constitution_rules(status);
CREATE INDEX IF NOT EXISTS idx_constitution_rules_created_at ON constitution_rules(created_at);

CREATE INDEX IF NOT EXISTS idx_governance_events_workflow_id ON governance_events(workflow_id);
CREATE INDEX IF NOT EXISTS idx_governance_events_event_type ON governance_events(event_type);
CREATE INDEX IF NOT EXISTS idx_governance_events_status ON governance_events(status);
CREATE INDEX IF NOT EXISTS idx_governance_events_created_at ON governance_events(created_at);

CREATE INDEX IF NOT EXISTS idx_trust_scores_workflow_id ON trust_scores(workflow_id);
CREATE INDEX IF NOT EXISTS idx_trust_scores_subject ON trust_scores(subject);
CREATE INDEX IF NOT EXISTS idx_trust_scores_trust_level ON trust_scores(trust_level);
CREATE INDEX IF NOT EXISTS idx_trust_scores_created_at ON trust_scores(created_at);

CREATE INDEX IF NOT EXISTS idx_policy_violations_workflow_id ON policy_violations(workflow_id);
CREATE INDEX IF NOT EXISTS idx_policy_violations_rule_name ON policy_violations(rule_name);
CREATE INDEX IF NOT EXISTS idx_policy_violations_severity ON policy_violations(severity);
CREATE INDEX IF NOT EXISTS idx_policy_violations_created_at ON policy_violations(created_at);

CREATE INDEX IF NOT EXISTS idx_decision_audits_workflow_id ON decision_audits(workflow_id);
CREATE INDEX IF NOT EXISTS idx_decision_audits_actor ON decision_audits(actor);
CREATE INDEX IF NOT EXISTS idx_decision_audits_decision_status ON decision_audits(decision_status);
CREATE INDEX IF NOT EXISTS idx_decision_audits_risk_level ON decision_audits(risk_level);
CREATE INDEX IF NOT EXISTS idx_decision_audits_created_at ON decision_audits(created_at);

CREATE TABLE IF NOT EXISTS evolution_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NULL REFERENCES workflow_runs(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'review_required',
    proposal JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS fitness_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evolution_run_id UUID NULL REFERENCES evolution_runs(id) ON DELETE SET NULL,
    score NUMERIC NOT NULL DEFAULT 0.0,
    passed BOOLEAN NOT NULL DEFAULT false,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_evolution_runs_workflow_id ON evolution_runs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_evolution_runs_status ON evolution_runs(status);
CREATE INDEX IF NOT EXISTS idx_evolution_runs_created_at ON evolution_runs(created_at);

CREATE INDEX IF NOT EXISTS idx_fitness_scores_evolution_run_id ON fitness_scores(evolution_run_id);
CREATE INDEX IF NOT EXISTS idx_fitness_scores_score ON fitness_scores(score);
CREATE INDEX IF NOT EXISTS idx_fitness_scores_passed ON fitness_scores(passed);
CREATE INDEX IF NOT EXISTS idx_fitness_scores_created_at ON fitness_scores(created_at);

CREATE TABLE IF NOT EXISTS connector_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_type TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'disabled',
    mode TEXT NOT NULL DEFAULT 'read_only',
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    secret_ref TEXT,
    last_sync_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS connector_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connector_id UUID REFERENCES connector_configs(id) ON DELETE SET NULL,
    connector_type TEXT NOT NULL,
    status TEXT NOT NULL,
    items_seen INTEGER NOT NULL DEFAULT 0,
    items_imported INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS background_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    resource_type TEXT,
    resource_id TEXT,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    next_retry_at TIMESTAMPTZ,
    error TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS idempotency_results (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key TEXT NOT NULL UNIQUE,
    result JSONB NOT NULL DEFAULT '{}'::jsonb,
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '24 hours'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_connector_configs_type ON connector_configs(connector_type);
CREATE INDEX IF NOT EXISTS idx_connector_configs_status ON connector_configs(status);
CREATE INDEX IF NOT EXISTS idx_connector_runs_connector_id ON connector_runs(connector_id);
CREATE INDEX IF NOT EXISTS idx_connector_runs_type ON connector_runs(connector_type);
CREATE INDEX IF NOT EXISTS idx_connector_runs_status ON connector_runs(status);
CREATE INDEX IF NOT EXISTS idx_background_jobs_type ON background_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_background_jobs_status ON background_jobs(status);
CREATE INDEX IF NOT EXISTS idx_background_jobs_resource ON background_jobs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_background_jobs_created_at ON background_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_background_jobs_next_retry_at ON background_jobs(next_retry_at);
CREATE INDEX IF NOT EXISTS idx_idempotency_results_key ON idempotency_results(idempotency_key);
CREATE INDEX IF NOT EXISTS idx_idempotency_results_expires_at ON idempotency_results(expires_at);

CREATE TABLE IF NOT EXISTS workflow_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_runs(id) ON DELETE CASCADE,
    step_name TEXT NOT NULL,
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'running',
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (workflow_id, step_name)
);

CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_workflow_id ON workflow_checkpoints(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_status ON workflow_checkpoints(status);
CREATE INDEX IF NOT EXISTS idx_workflow_checkpoints_updated_at ON workflow_checkpoints(updated_at);
