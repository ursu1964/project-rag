import { AppShell } from '@/components/AppShell';
import { DashboardCharts } from '@/components/DashboardCharts';
import { apiGet } from '@/lib/api';

export default async function DashboardPage() {
  const health = await apiGet<Record<string, unknown>>('/health').catch(() => ({ status: 'offline' }));
  const connectors = await apiGet<{ connectors?: Array<{ type?: string; status?: string }> }>('/connectors').catch(() => ({ connectors: [] }));
  const audit = await apiGet<{ events?: Array<{ action?: string; timestamp?: string }> }>('/audit/events?limit=80').catch(() => ({ events: [] }));
  const activeConnectors = (connectors.connectors || []).filter((item) => item.status !== 'dormant').length;

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <h1>Infrastructure Intelligence Control Plane</h1>
          <p>Track platform health, evidence pathways, and governance readiness from one professional command surface.</p>
        </div>
        <span className={`badge ${String(health.status) === 'ok' ? 'ok' : 'danger'}`}>API {String(health.status)}</span>
      </section>
      <div className="grid">
        <article className="card">
          <h2>Service Health</h2>
          <p>Current API status and runtime reachability.</p>
          <div className="metric-value">{String(health.status).toUpperCase()}</div>
        </article>
        <article className="card">
          <h2>Connector Posture</h2>
          <p>Cloud execution remains dormant unless explicitly enabled.</p>
          <div className="metric-value">{activeConnectors}</div>
        </article>
        <article className="card">
          <h2>Evidence Pipeline</h2>
          <p>Hybrid graph and vector retrieval with citations, confidence, and policy decisions.</p>
          <div className="metric-value">Ready</div>
        </article>
      </div>
      <section className="split" style={{ marginTop: 14 }}>
        <article className="card card-soft">
          <h3>Operational Focus</h3>
          <div className="list">
            <div className="list-item">
              <h3>Ask and Verify</h3>
              <p>Run evidence-first Q&A through the Ask interface and review citations before actioning.</p>
            </div>
            <div className="list-item">
              <h3>Topology and Impact</h3>
              <p>Inspect dependency maps and blast-radius clues directly from graph exports.</p>
            </div>
            <div className="list-item">
              <h3>Governance and Audit</h3>
              <p>Keep policy blocks, request traces, and connector posture visible for operations assurance.</p>
            </div>
          </div>
        </article>
        <article className="card card-soft">
          <h3>Excellence Notes</h3>
          <table className="kv">
            <tbody>
              <tr>
                <th>RAG Mode</th>
                <td>Hybrid + citations + validation</td>
              </tr>
              <tr>
                <th>Security Posture</th>
                <td>Prompt policy and PII redaction enabled</td>
              </tr>
              <tr>
                <th>Cloud Strategy</th>
                <td>Dormant by default, explicit activation only</td>
              </tr>
              <tr>
                <th>Observability</th>
                <td>Metrics-backed retrieval and workflow durations</td>
              </tr>
            </tbody>
          </table>
        </article>
      </section>
      <section className="card" style={{ marginTop: 14 }}>
        <h3>Connector Snapshot</h3>
        <div className="list">
          {(connectors.connectors || []).map((item) => (
            <div className="list-item" key={item.type || 'unknown'}>
              <h3>{item.type || 'unknown'}</h3>
              <p>Status: {item.status || 'unknown'}</p>
            </div>
          ))}
          {(connectors.connectors || []).length === 0 && <p>Connector metadata is currently unavailable.</p>}
        </div>
      </section>
      <DashboardCharts connectors={connectors.connectors || []} events={audit.events || []} />
    </AppShell>
  );
}
