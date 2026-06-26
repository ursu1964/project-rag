'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { apiGet } from '@/lib/api';

type Connector = { type?: string; status?: string; mode?: string; enabled?: boolean };
type ConnectorResponse = { cloud_connectors_enabled?: boolean; connectors?: Connector[] };

export default function AdminPage() {
  const [connectors, setConnectors] = useState<ConnectorResponse>({ connectors: [], cloud_connectors_enabled: false });
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    apiGet<ConnectorResponse>('/connectors').then(setConnectors).catch(setError);
  }, []);

  const items = connectors.connectors || [];

  return (
    <AppShell>
      <ProtectedPage roles={['admin']}>
        {error ? <AuthErrorBanner error={error} /> : null}
        <section className="page-head">
          <div><h1>Admin Console</h1><p>Review connector posture, execution modes, and cloud dormancy guardrails.</p></div>
          <span className={`badge ${connectors.cloud_connectors_enabled ? 'danger' : 'ok'}`}>Cloud connectors {connectors.cloud_connectors_enabled ? 'enabled' : 'dormant'}</span>
        </section>
        <section className="card">
          <h2>Connector Registry</h2>
          <div className="list">
            {items.map((item, index) => (
              <div className="list-item" key={item.type || `connector-${index}`}>
                <h3>{item.type || 'unknown'}</h3>
                <p>Status: {item.status || 'n/a'} | Mode: {item.mode || 'n/a'} | Enabled: {String(item.enabled ?? false)}</p>
              </div>
            ))}
            {items.length === 0 && <p>No connectors returned.</p>}
          </div>
          <div className="json-box"><pre>{JSON.stringify(connectors, null, 2)}</pre></div>
        </section>
      </ProtectedPage>
    </AppShell>
  );
}
