# ProjectRAG Master Plan - Part 11
# MCP, Tooling, and External System Integration

**Version:** 1.0  
**Target OS:** Ubuntu Linux 24.x  
**Generated:** 2026-06-16  

---

## 1. Purpose

Part 10 defined the controlled DevOps execution platform.

Part 11 defines how ProjectRAG safely connects to external tools and systems.

The key principle is:

```text
Agents do not directly access everything.
Agents request controlled tool access through approved interfaces.
```

This is where MCP and tool-governed execution become important.

---

## 2. Tool Integration Philosophy

Every external system must be treated as a capability with:

- identity
- scope
- permissions
- risk level
- input schema
- output schema
- audit logging
- approval requirements

Unsafe model:

```text
LLM -> shell command -> infrastructure
```

Safe model:

```text
LLM -> Planning Agent -> Policy -> Tool Adapter -> Audit -> Verification
```

---

## 3. MCP Role

MCP can expose structured tools to the agent system.

Possible MCP servers:

```text
Filesystem MCP
GitHub MCP
PostgreSQL MCP
GraphDB MCP
Docker MCP
Terraform MCP
VirtualBox MCP
AWS MCP
Azure MCP
Kubernetes MCP
Prometheus MCP
Grafana MCP
```

ProjectRAG should not use all of them immediately.

Start with:

```text
Filesystem
PostgreSQL
GraphDB
Docker read-only
GitHub read-only
```

---

## 4. Tool Risk Classes

### Low Risk

Examples:

```text
read file
list documents
query PostgreSQL
query GraphDB
docker ps
docker logs
curl health endpoint
run pytest
```

Allowed in read-only or low-risk mode.

### Medium Risk

Examples:

```text
restart container
create branch
generate Terraform plan
run docker compose up
```

Requires approval.

### High Risk

Examples:

```text
delete container
modify database
change firewall
rotate credentials
change cloud resources
```

Requires explicit approval and rollback.

### Critical Risk

Examples:

```text
delete database
terraform destroy
kubectl delete namespace
remove storage volume
expose public ports
```

Blocked by default.

---

## 5. Tool Registry

Create future file:

```text
app/tools/tool_registry.py
```

Purpose:

```text
Define all available tools and their risk levels.
```

Example structure:

```python
TOOLS = {
    "docker_ps": {
        "command": "docker ps",
        "risk": "low",
        "requires_approval": False,
    },
    "docker_restart": {
        "command_template": "docker restart {container}",
        "risk": "medium",
        "requires_approval": True,
    },
}
```

---

## 6. Filesystem Integration

Allowed:

```text
read project files
list directories
write generated docs
write generated code only after review
```

Blocked:

```text
delete arbitrary files
overwrite secrets
change SSH keys
modify system directories
```

---

## 7. GitHub Integration

Initial mode:

```text
read repository
inspect branches
inspect diffs
generate patch
```

Later mode:

```text
create branch
commit changes
open pull request
comment on PR
read CI status
```

Recommended GitOps pattern:

```text
AI generates change
AI creates PR
CI validates
Human approves
Merge triggers deployment
```

---

## 8. PostgreSQL Tooling

Allowed:

```text
SELECT queries
schema inspection
workflow log inserts
memory inserts
validation inserts
```

Restricted:

```text
DELETE
DROP
TRUNCATE
ALTER
```

Policy:

```text
Destructive SQL blocked by default.
```

---

## 9. GraphDB Tooling

Allowed:

```text
SPARQL SELECT
SPARQL ASK
insert approved triples
export graph
```

Restricted:

```text
delete triples
drop repository
bulk overwrite
```

Graph changes should include provenance:

```text
source document
source chunk
extraction method
confidence
timestamp
```

---

## 10. Docker Tooling

Allowed initially:

```text
docker ps
docker logs
docker inspect
```

Medium-risk with approval:

```text
docker restart
docker compose up -d
docker compose down
```

Blocked initially:

```text
docker system prune
docker volume rm
docker rm -f
```

---

## 11. Terraform Tooling

Allowed initially:

```text
terraform fmt
terraform validate
terraform plan
```

Blocked initially:

```text
terraform apply
terraform destroy
```

Apply should only happen through:

```text
GitOps PR
CI validation
human approval
protected environment
```

---

## 12. Cloud Tooling

AWS and Azure should start in read-only mode.

Allowed:

```text
list resources
read tags
read costs
read topology
read metrics
```

Blocked initially:

```text
create resources
delete resources
change IAM
change networking
modify firewall
```

---

## 13. Kubernetes Tooling

Allowed:

```text
kubectl get
kubectl describe
kubectl logs
```

Restricted:

```text
kubectl apply
kubectl delete
kubectl scale
kubectl rollout restart
```

---

## 14. Observability Tooling

Prometheus/Grafana integration should support:

```text
metric query
dashboard lookup
alert lookup
incident correlation
```

This feeds:

- capacity agent
- chaos agent
- RCA agent
- failure prediction agent

---

## 15. Tool Execution Workflow

```text
Agent requests tool
      ↓
Tool registry checks permission
      ↓
Risk agent classifies action
      ↓
Approval gate checks approval
      ↓
Tool adapter executes or blocks
      ↓
Result stored in audit log
      ↓
Verifier validates result
      ↓
Learning agent stores outcome
```

---

## 16. New Modules

```text
app/tools/tool_registry.py
app/tools/tool_policy.py
app/tools/tool_executor.py
app/tools/docker_tool.py
app/tools/github_tool.py
app/tools/postgres_tool.py
app/tools/graphdb_tool.py
app/tools/terraform_tool.py
app/tools/kubernetes_tool.py
app/tools/cloud_tool.py
```

---

## 17. New Tables

```sql
CREATE TABLE IF NOT EXISTS tool_calls (
    id UUID PRIMARY KEY,
    workflow_id UUID,
    tool_name TEXT NOT NULL,
    risk_level TEXT,
    input JSONB DEFAULT '{}'::jsonb,
    output JSONB DEFAULT '{}'::jsonb,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tool_policies (
    id UUID PRIMARY KEY,
    tool_name TEXT NOT NULL,
    allowed BOOLEAN DEFAULT false,
    risk_level TEXT,
    requires_approval BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT now()
);
```

---

## 18. Acceptance Criteria

Part 11 is complete when:

```text
tool registry exists
tool policy exists
tool executor exists
Docker read-only tool works
PostgreSQL read-only tool works
GraphDB read-only tool works
tool calls are audited
unsafe commands are blocked
approval gate works
```

---

## 19. Final Outcome

After Part 11, ProjectRAG can safely connect to external systems through governed tools.

This prepares the platform for:

```text
DevOps automation
GitOps
Terraform workflows
Cloud inventory
Kubernetes analysis
Observability-driven RCA
```
