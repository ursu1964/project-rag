'use client';

import { AppShell } from '@/components/AppShell';
import { ProtectedPage, useAuth } from '@/components/AuthProvider';

type DashboardLink = {
  title: string;
  description: string;
  href: string;
  badge?: string;
};

const appDashboards: DashboardLink[] = [
  { title: 'Ask AI', href: '/ask', badge: 'App', description: 'Ask questions over ingested documents and inspect answers/citations.' },
  { title: 'Documents', href: '/documents', badge: 'App', description: 'Upload, ingest, and review document metadata stored by ProjectRAG.' },
  { title: 'Models', href: '/models', badge: 'AIOS', description: 'Inspect local models exposed by the OpenAI-compatible model gateway.' },
  { title: 'Memory', href: '/memory', badge: 'AIOS', description: 'Review durable memory items available to local agents and workflows.' },
  { title: 'Workflows', href: '/workflows', badge: 'AIOS', description: 'Discover registered agent workflows and their orchestration engines.' },
  { title: 'Topology', href: '/topology', badge: 'App', description: 'Analyze graph nodes, edges, and dependency relationships interactively.' },
  { title: 'Audit', href: '/audit', badge: 'Admin', description: 'Review policy decisions, denials, uploads, and security events.' },
  { title: 'Evaluation', href: '/evaluation', badge: 'App', description: 'Inspect evaluation and quality-gate readiness.' },
  { title: 'Admin', href: '/admin', badge: 'Admin', description: 'Review connector posture and administrative controls.' },
];

const grafanaDashboards: DashboardLink[] = [
  {
    title: 'PostgreSQL Data and Ingestion',
    href: 'http://localhost:3001/d/projectrag-postgres-data/projectrag-postgresql-data-and-ingestion',
    badge: 'Grafana + PostgreSQL',
    description: 'Documents, chunks, graph facts, workflow runs, audit events, validations, and jobs.',
  },
  {
    title: 'Health and Availability',
    href: 'http://localhost:3001/d/projectrag-health/projectrag-health-and-availability',
    badge: 'Grafana + Prometheus/PostgreSQL',
    description: 'API health, probes, request rate, availability, and PostgreSQL data health cards.',
  },
  {
    title: 'Latency and Error Rate',
    href: 'http://localhost:3001/d/projectrag-latency-errors/projectrag-latency-and-error-rate-by-endpoint',
    badge: 'Grafana + Prometheus/PostgreSQL',
    description: 'Endpoint latency, request volume, workflow errors, and authorization denials.',
  },
  {
    title: 'Workflow and Agent Performance',
    href: 'http://localhost:3001/d/projectrag-workflow-agents/projectrag-workflow-and-agent-performance',
    badge: 'Grafana + Prometheus/PostgreSQL',
    description: 'Workflow runs, agent runs, validation results, background jobs, and retries.',
  },
];

const tools: DashboardLink[] = [
  { title: 'Grafana Home', href: 'http://localhost:3001', badge: 'admin/admin', description: 'Open Grafana and browse all ProjectRAG dashboards.' },
  { title: 'Prometheus', href: 'http://localhost:9091', badge: 'Metrics', description: 'Inspect raw Prometheus targets, metrics, and alert rules.' },
  { title: 'API Docs', href: 'http://localhost:18000/docs', badge: 'OpenAPI', description: 'Explore and test ProjectRAG API routes.' },
  { title: 'Qdrant', href: 'http://localhost:6333/dashboard', badge: 'Vector DB', description: 'Inspect vector collections and local semantic search storage.' },
  { title: 'GraphDB', href: 'http://localhost:7200', badge: 'Graph DB', description: 'Inspect RDF repositories and graph database state.' },
  { title: 'Alertmanager', href: 'http://localhost:19094', badge: 'Alerts', description: 'Inspect active and silenced monitoring alerts.' },
];

function Card({ item, external = false }: { item: DashboardLink; external?: boolean }) {
  const content = (
    <>
      <div className="status-strip"><span className="badge ok">{item.badge || 'Dashboard'}</span></div>
      <h3>{item.title}</h3>
      <p>{item.description}</p>
      <p style={{ color: '#b9fff1', fontSize: '0.82rem', overflowWrap: 'anywhere' }}>{item.href}</p>
    </>
  );

  if (external) {
    return <a className="list-item" href={item.href} target="_blank" rel="noreferrer">{content}</a>;
  }
  return <a className="list-item" href={item.href}>{content}</a>;
}

export default function DashboardsPage() {
  const auth = useAuth();
  const canUseInfraTools = auth.canAccess(['admin', 'operator']);

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'viewer', 'agent']}>
        <section className="page-head">
          <div>
            <h1>Dashboard Launcher</h1>
            <p>All services are started by run.sh, but browsers are not opened automatically. Open dashboards here only when you need them.</p>
          </div>
          <span className="badge ok">Manual open</span>
        </section>

        <section className="card">
          <h2>Application Dashboards</h2>
          <div className="grid">{appDashboards.map((item) => <Card key={item.href} item={item} />)}</div>
        </section>

        {canUseInfraTools ? (
          <section className="card" style={{ marginTop: 16 }}>
            <h2>Grafana Dashboards</h2>
            <p><span className="badge warn">Sensitive tools</span> Open only from trusted local machines.</p>
            <div className="grid">{grafanaDashboards.map((item) => <Card key={item.href} item={item} external />)}</div>
          </section>
        ) : null}

        {canUseInfraTools ? (
          <section className="card" style={{ marginTop: 16 }}>
            <h2>Infrastructure Tools</h2>
            <p><span className="badge warn">Admin/operator only</span> These links expose operational consoles.</p>
            <div className="grid">{tools.map((item) => <Card key={item.href} item={item} external />)}</div>
          </section>
        ) : null}
      </ProtectedPage>
    </AppShell>
  );
}
