import { AppShell } from '@/components/AppShell';
import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

type DocumentRow = {
  id?: string;
  source?: string;
  file_hash?: string;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
};

export default async function DocumentsPage() {
  const docs = await apiGet<DocumentRow[]>('/documents').catch(() => []);
  const total = docs.length;
  const withMetadata = docs.filter((doc) => Object.keys(doc.metadata || {}).length > 0).length;

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <h1>Documents</h1>
          <p>Inspect ingested sources and verify coverage for retrieval and citation quality.</p>
        </div>
        <span className="badge ok">{total} documents</span>
      </section>
      <section className="grid">
        <article className="card card-soft">
          <h2>Total Sources</h2>
          <div className="metric-value">{total}</div>
        </article>
        <article className="card card-soft">
          <h2>With Metadata</h2>
          <div className="metric-value">{withMetadata}</div>
        </article>
        <article className="card card-soft">
          <h2>Ingestion Mode</h2>
          <p>Background-job friendly and idempotent-ready pipeline.</p>
        </article>
      </section>

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
        emptyMessage="No documents available yet."
      />
    </AppShell>
  );
}
