import { AppShell } from '@/components/AppShell';
import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

type AuditEvent = {
  id?: string;
  user?: string;
  role?: string;
  action?: string;
  resource?: string;
  decision?: string;
  risk_level?: string;
  metadata?: Record<string, unknown>;
  timestamp?: string;
};

type AuditResponse = {
  events?: AuditEvent[];
};

export default async function AuditPage() {
  const response = await apiGet<AuditResponse>('/audit/events').catch(() => ({ events: [] }));
  const events = response.events || [];
  const denied = events.filter((event) => String(event.decision || '').toLowerCase() === 'deny').length;
  const highRisk = events.filter((event) => String(event.risk_level || '').toLowerCase() === 'high').length;

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <h1>Audit Console</h1>
          <p>Track policy decisions, ingestion actions, and operational events in a centralized governance timeline.</p>
        </div>
        <span className="badge ok">{events.length} events</span>
      </section>
      <section className="grid">
        <article className="card card-soft">
          <h2>Denied Decisions</h2>
          <div className="metric-value">{denied}</div>
        </article>
        <article className="card card-soft">
          <h2>High Risk Events</h2>
          <div className="metric-value">{highRisk}</div>
        </article>
        <article className="card card-soft">
          <h2>Actors Seen</h2>
          <div className="metric-value">{new Set(events.map((event) => event.user || 'unknown')).size}</div>
        </article>
      </section>

      <DataTable
        title="Audit Timeline"
        rows={events as Record<string, unknown>[]}
        columns={[
          { key: 'timestamp', label: 'Timestamp', type: 'date', sortable: true },
          { key: 'user', label: 'User', sortable: true },
          { key: 'role', label: 'Role', sortable: true },
          { key: 'action', label: 'Action', sortable: true },
          { key: 'resource', label: 'Resource', sortable: true },
          { key: 'decision', label: 'Decision', sortable: true },
          { key: 'risk_level', label: 'Risk', sortable: true },
          { key: 'metadata', label: 'Metadata', type: 'json' },
        ]}
        defaultSortKey="timestamp"
        defaultSortDirection="desc"
        emptyMessage="No audit events available."
      />
    </AppShell>
  );
}
