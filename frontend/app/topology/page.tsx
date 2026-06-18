import { AppShell } from '@/components/AppShell';
import { TopologyExplorer } from '@/components/TopologyExplorer';
import { apiGet } from '@/lib/api';

type TopologyNode = { id?: string; label?: string };
type TopologyEdge = { id?: string; source?: string; target?: string; label?: string; confidence?: number };
type TopologyResponse = { nodes?: TopologyNode[]; edges?: TopologyEdge[] };

export default async function TopologyPage() {
  const graph = await apiGet<TopologyResponse>('/graph/export?limit=50').catch(() => ({ nodes: [], edges: [] }));
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];

  return (
    <AppShell>
      <section className="page-head">
        <div>
          <h1>Topology Map</h1>
          <p>Review current graph entities and dependency edges to support impact analysis and RCA workflows.</p>
        </div>
        <span className="badge ok">{nodes.length} nodes / {edges.length} edges</span>
      </section>
      <TopologyExplorer graph={graph} />
    </AppShell>
  );
}
