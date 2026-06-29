'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

type MemoryRow = { id?: string; memory_type?: string; content?: string; metadata?: Record<string, unknown>; created_at?: string };

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryRow[]>([]);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    apiGet<MemoryRow[]>('/memory?limit=50').then(setMemories).catch(setError);
  }, []);

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'viewer', 'agent']}>
        {error ? <AuthErrorBanner error={error} /> : null}
        <section className="page-head">
          <div><h1>Memory</h1><p>Review durable PostgreSQL-backed memory items used by AIOS agents.</p></div>
          <span className="badge ok">{memories.length} items</span>
        </section>
        <DataTable
          title="Recent Memory"
          rows={memories as Record<string, unknown>[]}
          columns={[
            { key: 'created_at', label: 'Created', type: 'date', sortable: true },
            { key: 'memory_type', label: 'Type', sortable: true },
            { key: 'content', label: 'Content' },
            { key: 'metadata', label: 'Metadata', type: 'json' },
          ]}
          defaultSortKey="created_at"
          defaultSortDirection="desc"
          emptyMessage="No memory items available."
        />
      </ProtectedPage>
    </AppShell>
  );
}
