'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

type WorkflowRow = { id?: string; name?: string; engine?: string; module?: string; nodes?: string[] };
type RegistryResponse = { workflows?: WorkflowRow[] };

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowRow[]>([]);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    apiGet<RegistryResponse>('/registry').then((response) => setWorkflows(response.workflows || [])).catch(setError);
  }, []);

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'viewer', 'agent']}>
        {error ? <AuthErrorBanner error={error} /> : null}
        <section className="page-head">
          <div><h1>Workflows</h1><p>Discover AIOS workflow definitions and orchestration engines.</p></div>
          <span className="badge ok">{workflows.length} workflows</span>
        </section>
        <DataTable
          title="Workflow Registry"
          rows={workflows.map((workflow) => ({ ...workflow, nodes: (workflow.nodes || []).join(' → ') })) as Record<string, unknown>[]}
          columns={[
            { key: 'id', label: 'ID', sortable: true },
            { key: 'name', label: 'Name', sortable: true },
            { key: 'engine', label: 'Engine', sortable: true },
            { key: 'nodes', label: 'Nodes' },
            { key: 'module', label: 'Module' },
          ]}
          emptyMessage="No workflows registered."
        />
      </ProtectedPage>
    </AppShell>
  );
}
