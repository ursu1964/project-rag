type TopologyNode = {
  id?: string;
  label?: string;
  type?: string;
  [key: string]: unknown;
};

type TopologyEdge = {
  id?: string;
  source?: string;
  target?: string;
  label?: string;
  confidence?: number;
  [key: string]: unknown;
};

type TopologyGraph = {
  nodes?: TopologyNode[];
  edges?: TopologyEdge[];
  [key: string]: unknown;
};

type TopologyExplorerProps = {
  graph?: TopologyGraph;
  nodes?: TopologyNode[];
  edges?: TopologyEdge[];
};

export function TopologyExplorer({
  graph,
  nodes,
  edges,
}: TopologyExplorerProps) {
  const resolvedNodes = graph?.nodes ?? nodes ?? [];
  const resolvedEdges = graph?.edges ?? edges ?? [];

  return (
    <section>
      <h2>Topology Explorer</h2>

      <div style={{ display: "grid", gap: 16 }}>
        <div>
          <h3>Nodes</h3>
          {resolvedNodes.length === 0 ? (
            <p>No nodes available.</p>
          ) : (
            <ul>
              {resolvedNodes.map((node, index) => (
                <li key={node.id ?? index}>
                  <strong>{node.label ?? node.id ?? `Node ${index + 1}`}</strong>
                  {node.type ? ` — ${node.type}` : ""}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3>Edges</h3>
          {resolvedEdges.length === 0 ? (
            <p>No edges available.</p>
          ) : (
            <ul>
              {resolvedEdges.map((edge, index) => (
                <li key={edge.id ?? index}>
                  {edge.source ?? "unknown"} → {edge.target ?? "unknown"}
                  {edge.label ? ` — ${edge.label}` : ""}
                  {typeof edge.confidence === "number"
                    ? ` (${Math.round(edge.confidence * 100)}%)`
                    : ""}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </section>
  );
}
