'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { DataTable } from '@/components/DataTable';
import { apiGet, apiUpload, authStatusMessage } from '@/lib/api';

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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [ingestOnUpload, setIngestOnUpload] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<unknown>(null);

  function refreshDocuments() {
    setLoading(true);
    apiGet<DocumentRow[]>('/documents')
      .then(setDocs)
      .catch(setError)
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    refreshDocuments();
  }, []);

  async function uploadDocument() {
    if (!selectedFile) return;
    setUploading(true);
    setError(null);
    setUploadResult(null);
    const form = new FormData();
    form.append('file', selectedFile);
    try {
      const result = await apiUpload<unknown>(`/documents/upload?ingest=${ingestOnUpload ? 'true' : 'false'}`, form);
      setUploadResult(result);
      setSelectedFile(null);
      refreshDocuments();
    } catch (err) {
      setError(err);
    } finally {
      setUploading(false);
    }
  }

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
        <section className="card">
          <h2>Upload and Ingest</h2>
          <p>Add a supported local text document and optionally ingest it immediately for Ask AI retrieval.</p>
          <input
            type="file"
            accept=".txt,.md,.log,.json,.yaml,.yml,.tf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
          />
          <label style={{ display: 'block', marginTop: '0.75rem' }}>
            <input
              type="checkbox"
              checked={ingestOnUpload}
              onChange={(event) => setIngestOnUpload(event.target.checked)}
            />{' '}
            Ingest immediately
          </label>
          <p>
            <button onClick={uploadDocument} disabled={!selectedFile || uploading}>
              {uploading ? 'Uploading...' : ingestOnUpload ? 'Upload and ingest' : 'Upload only'}
            </button>
          </p>
          {uploadResult ? <div className="json-box"><pre>{JSON.stringify(uploadResult, null, 2)}</pre></div> : null}
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
