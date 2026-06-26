'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { DataTable } from '@/components/DataTable';
import { apiGet, authStatusMessage } from '@/lib/api';

type DocumentRow = {
  id?: string;
  source?: string;
  file_hash?: string;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
};

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentRow[]>([]);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiGet<DocumentRow[]>('/documents')
      .then(setDocs)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  const total = docs.length;
  const withMetadata = docs.filter((doc) => Object.keys(doc.metadata || {}).length > 0).length;

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'viewer', 'agent']}>
        {error ? <AuthErrorBanner error={error} /> : null}
        <section className="page-head">
          <div>
            <h1>Documents</h1>
            <p>Inspect ingested sources and verify coverage for retrieval and citation quality.</p>
          </div>
          <span className="badge ok">{loading ? 'Loading...' : `${total} documents`}</span>
        </section>
        <section className="grid">
          <article className="card card-soft"><h2>Total Sources</h2><div className="metric-value">{total}</div></article>
          <article className="card card-soft"><h2>With Metadata</h2><div className="metric-value">{withMetadata}</div></article>
          <article className="card card-soft"><h2>Ingestion Mode</h2><p>Background-job friendly and idempotent-ready pipeline.</p></article>
        </section>
        {error ? <p className="badge danger">{authStatusMessage(error)}</p> : null}
        <DataTable
          title="Document Registry"
          rows={docs as Record<string, unknown>[]}
          columns={[
            { key: 'id', label: 'Document ID', sortable: true },
            { key: 'source', label: 'Source', sortable: true },
            { key: 'updated_at', label: 'Updated', type: 'date', sortable: true },
            { key: 'created_at', label: 'Created', type: 'date', sortable: true },
            { key: 'file_hash', label: 'Hash', sortable: true },
            { key: 'metadata', label: 'Metadata', type: 'json' },
          ]}
          defaultSortKey="updated_at"
          defaultSortDirection="desc"
          emptyMessage={loading ? 'Loading documents...' : 'No documents available yet.'}
        />
      </ProtectedPage>
    </AppShell>
  );
}
