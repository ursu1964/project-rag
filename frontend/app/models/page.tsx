'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { DataTable } from '@/components/DataTable';
import { apiGet } from '@/lib/api';

type ModelRow = { id?: string; object?: string; owned_by?: string };
type ModelsResponse = { data?: ModelRow[] };

export default function ModelsPage() {
  const [models, setModels] = useState<ModelRow[]>([]);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    apiGet<ModelsResponse>('/v1/models').then((response) => setModels(response.data || [])).catch(setError);
  }, []);

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'viewer', 'agent']}>
        {error ? <AuthErrorBanner error={error} /> : null}
        <section className="page-head">
          <div><h1>Models</h1><p>Inspect local OpenAI-compatible models exposed by the AIOS model gateway.</p></div>
          <span className="badge ok">{models.length} models</span>
        </section>
        <DataTable
          title="Local Model Gateway"
          rows={models as Record<string, unknown>[]}
          columns={[
            { key: 'id', label: 'Model', sortable: true },
            { key: 'object', label: 'Object', sortable: true },
            { key: 'owned_by', label: 'Owner', sortable: true },
          ]}
          emptyMessage="No models returned. Ensure Ollama is reachable."
        />
      </ProtectedPage>
    </AppShell>
  );
}
