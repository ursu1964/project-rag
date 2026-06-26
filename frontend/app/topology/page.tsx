'use client';

import { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { AuthErrorBanner, ProtectedPage } from '@/components/AuthProvider';
import { TopologyExplorer } from '@/components/TopologyExplorer';
import { apiGet } from '@/lib/api';

type TopologyNode = { id?: string; label?: string };
type TopologyEdge = { id?: string; source?: string; target?: string; label?: string; confidence?: number };
type TopologyResponse = { nodes?: TopologyNode[]; edges?: TopologyEdge[] };

export default function TopologyPage() {
  const [graph, setGraph] = useState<TopologyResponse>({ nodes: [], edges: [] });
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    apiGet<TopologyResponse>('/graph/export?limit=50').then(setGraph).catch(setError);
  }, []);

  const nodes = graph.nodes || [];
  const edges = graph.edges || [];

  return (
    <AppShell>
      <ProtectedPage roles={['admin', 'operator', 'analyst', 'viewer', 'agent']}>
        {error ? <AuthErrorBanner error={error} /> : null}
        <section className="page-head">
          <div><h1>Topology Map</h1><p>Review current graph entities and dependency edges.</p></div>
          <span className="badge ok">{nodes.length} nodes / {edges.length} edges</span>
        </section>
        <TopologyExplorer graph={graph} />
      </ProtectedPage>
    </AppShell>
  );
}
