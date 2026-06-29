"use client";

import { useState } from "react";

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

type SelectedItem =
  | { kind: "node"; title: string; data: TopologyNode }
  | { kind: "edge"; title: string; data: TopologyEdge }
  | null;

const nodePalette = [
  { fill: "#0ea5e9", stroke: "#075985" },
  { fill: "#22c55e", stroke: "#166534" },
  { fill: "#f97316", stroke: "#9a3412" },
  { fill: "#a855f7", stroke: "#6b21a8" },
  { fill: "#ef4444", stroke: "#991b1b" },
  { fill: "#14b8a6", stroke: "#115e59" },
];

function nodeColor(type: unknown) {
  const key = String(type ?? "default");
  const index = [...key].reduce((sum, char) => sum + char.charCodeAt(0), 0) % nodePalette.length;
  return nodePalette[index];
}

function nodeKey(node: TopologyNode, index: number) {
  return String(node.id ?? node.label ?? index);
}

export function TopologyExplorer({
  graph,
  nodes,
  edges,
}: TopologyExplorerProps) {
  const [selected, setSelected] = useState<SelectedItem>(null);
  const [search, setSearch] = useState("");
  const resolvedNodes = graph?.nodes ?? nodes ?? [];
  const resolvedEdges = graph?.edges ?? edges ?? [];
  const normalizedSearch = search.trim().toLowerCase();
  const nodeMatches = (node: TopologyNode) =>
    [node.id, node.label, node.type].some((value) => String(value ?? "").toLowerCase().includes(normalizedSearch));
  const edgeMatches = (edge: TopologyEdge) =>
    [edge.source, edge.target, edge.label].some((value) => String(value ?? "").toLowerCase().includes(normalizedSearch));
  const visibleNodeKeys = new Set<string>();
  if (normalizedSearch) {
    resolvedNodes.forEach((node, index) => {
      if (nodeMatches(node)) visibleNodeKeys.add(nodeKey(node, index));
    });
    resolvedEdges.forEach((edge) => {
      if (edgeMatches(edge)) {
        visibleNodeKeys.add(String(edge.source ?? ""));
        visibleNodeKeys.add(String(edge.target ?? ""));
      }
    });
  }
  const visibleNodes = normalizedSearch
    ? resolvedNodes.filter((node, index) => visibleNodeKeys.has(nodeKey(node, index)))
    : resolvedNodes;
  const visibleNodeIdSet = new Set(visibleNodes.map((node, index) => nodeKey(node, index)));
  const visibleEdges = normalizedSearch
    ? resolvedEdges.filter(
        (edge) =>
          edgeMatches(edge) ||
          (visibleNodeIdSet.has(String(edge.source ?? "")) && visibleNodeIdSet.has(String(edge.target ?? ""))),
      )
    : resolvedEdges;
  const width = 1500;
  const height = 900;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.36;
  const nodeIndex = new Map(visibleNodes.map((node, index) => [nodeKey(node, index), node]));
  const positions = new Map(
    visibleNodes.map((node, index) => {
      const angle = (2 * Math.PI * index) / Math.max(visibleNodes.length, 1) - Math.PI / 2;
      return [
        nodeKey(node, index),
        {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        },
      ];
    }),
  );

  return (
    <section>
      <h2>Topology Explorer</h2>

      <div style={{ display: "grid", gap: 16 }}>
        <div>
          <h3>Graph view</h3>
          <p style={{ color: "#475569", marginTop: 0 }}>
            Circles are services/data stores. Arrows show dependency direction. Click a node or edge to inspect details.
          </p>
          <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12, flexWrap: "wrap" }}>
            <input
              value={search}
              onChange={(event) => {
                setSearch(event.target.value);
                setSelected(null);
              }}
              placeholder="Filter by node, edge, type, or relationship"
              style={{ minWidth: 320, maxWidth: 520 }}
            />
            <span className="badge ok">
              Showing {visibleNodes.length}/{resolvedNodes.length} nodes · {visibleEdges.length}/{resolvedEdges.length} edges
            </span>
            {search ? <button className="button-muted" onClick={() => setSearch("")}>Clear</button> : null}
          </div>
          {resolvedNodes.length === 0 ? (
            <p>No topology graph available.</p>
          ) : visibleNodes.length === 0 ? (
            <p>No topology items match this filter.</p>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) 320px", gap: 14, alignItems: "start" }}>
              <div
                style={{
                  height: "72vh",
                  overflowX: "auto",
                  overflowY: "scroll",
                  border: "2px solid #0f172a",
                  borderRadius: 16,
                  background: "#ffffff",
                  boxShadow: "0 12px 30px rgba(15, 23, 42, 0.18)",
                }}
              >
                <svg
                  viewBox={`0 0 ${width} ${height}`}
                  role="img"
                  aria-label="Topology graph"
                  style={{
                    display: "block",
                    width,
                    height,
                    minWidth: width,
                    minHeight: height,
                    background: "#ffffff",
                  }}
                >
                  <defs>
                    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" orient="auto-start-reverse">
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="#111827" />
                    </marker>
                  </defs>
                  {visibleEdges.map((edge, index) => {
                    const source = positions.get(String(edge.source ?? ""));
                    const target = positions.get(String(edge.target ?? ""));
                    if (!source || !target) return null;
                    const midX = (source.x + target.x) / 2;
                    const midY = (source.y + target.y) / 2;
                    const title = `${edge.source ?? "unknown"} → ${edge.target ?? "unknown"}`;
                    const selectedEdge = selected?.kind === "edge" && selected.data === edge;
                    return (
                      <g
                        key={edge.id ?? `edge-${index}`}
                        onClick={() => setSelected({ kind: "edge", title, data: edge })}
                        style={{ cursor: "pointer" }}
                      >
                        <line x1={source.x} y1={source.y} x2={target.x} y2={target.y} stroke="transparent" strokeWidth="22" />
                        <line
                          x1={source.x}
                          y1={source.y}
                          x2={target.x}
                          y2={target.y}
                          stroke={selectedEdge ? "#dc2626" : "#111827"}
                          strokeWidth={selectedEdge ? "7" : "4"}
                          opacity="0.86"
                          markerEnd="url(#arrow)"
                        />
                        {edge.label ? (
                          <>
                            <rect x={midX - 52} y={midY - 24} width="104" height="22" rx="11" fill="#fef3c7" stroke="#92400e" />
                            <text x={midX} y={midY - 9} textAnchor="middle" fontSize="12" fontWeight="700" fill="#78350f">
                              {String(edge.label).length > 16 ? `${String(edge.label).slice(0, 15)}…` : edge.label}
                            </text>
                          </>
                        ) : null}
                      </g>
                    );
                  })}
                  {visibleNodes.map((node, index) => {
                    const key = nodeKey(node, index);
                    const position = positions.get(key) ?? { x: centerX, y: centerY };
                    const label = String(node.label ?? node.id ?? `Node ${index + 1}`);
                    const color = nodeColor(node.type ?? label);
                    const selectedNode = selected?.kind === "node" && selected.data === node;
                    return (
                      <g
                        key={key}
                        onClick={() => setSelected({ kind: "node", title: label, data: node })}
                        style={{ cursor: "pointer" }}
                      >
                        <circle cx={position.x} cy={position.y} r="46" fill={selectedNode ? "#facc15" : color.fill} stroke={selectedNode ? "#854d0e" : color.stroke} strokeWidth="5" />
                        <circle cx={position.x} cy={position.y} r="36" fill={color.fill} opacity={selectedNode ? "0.95" : "1"} />
                        <text x={position.x} y={position.y - 4} textAnchor="middle" fontSize="13" fontWeight="800" fill="#ffffff">
                          {label.length > 13 ? `${label.slice(0, 12)}…` : label}
                        </text>
                        {node.type ? (
                          <text x={position.x} y={position.y + 14} textAnchor="middle" fontSize="10" fontWeight="700" fill="#ffffff">
                            {String(node.type)}
                          </text>
                        ) : null}
                      </g>
                    );
                  })}
                </svg>
              </div>

              <aside
                style={{
                  border: "2px solid #0f172a",
                  borderRadius: 16,
                  padding: 16,
                  background: "#f8fafc",
                  color: "#020617",
                  position: "sticky",
                  top: 12,
                  maxHeight: "72vh",
                  overflowY: "auto",
                }}
              >
                <h3 style={{ marginTop: 0, color: "#0f2a6b" }}>Selected information</h3>
                {selected ? (
                  <>
                    <p style={{ color: "#020617" }}>
                      <strong>{selected.kind.toUpperCase()}:</strong> {selected.title}
                    </p>
                    {selected.kind === "node" ? (
                      (() => {
                        const key = String(selected.data.id ?? selected.data.label ?? "");
                        const incoming = visibleEdges.filter((edge) => String(edge.target ?? "") === key);
                        const outgoing = visibleEdges.filter((edge) => String(edge.source ?? "") === key);
                        return (
                          <div style={{ display: "grid", gap: 10, color: "#020617" }}>
                            <div><strong>ID:</strong> {selected.data.id ?? "n/a"}</div>
                            <div><strong>Label:</strong> {selected.data.label ?? "n/a"}</div>
                            <div><strong>Type:</strong> {selected.data.type ?? "n/a"}</div>
                            <div><strong>Outgoing edges:</strong> {outgoing.length}</div>
                            <div><strong>Incoming edges:</strong> {incoming.length}</div>
                            {outgoing.length > 0 ? (
                              <div>
                                <strong>Depends on / connects to:</strong>
                                <ul style={{ marginTop: 6, paddingLeft: 18 }}>
                                  {outgoing.map((edge, index) => (
                                    <li key={edge.id ?? index}>
                                      {edge.target ?? "unknown"}{edge.label ? ` — ${edge.label}` : ""}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            ) : null}
                            {incoming.length > 0 ? (
                              <div>
                                <strong>Used by / receives from:</strong>
                                <ul style={{ marginTop: 6, paddingLeft: 18 }}>
                                  {incoming.map((edge, index) => (
                                    <li key={edge.id ?? index}>
                                      {edge.source ?? "unknown"}{edge.label ? ` — ${edge.label}` : ""}
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            ) : null}
                          </div>
                        );
                      })()
                    ) : (
                      (() => {
                        const source = nodeIndex.get(String(selected.data.source ?? ""));
                        const target = nodeIndex.get(String(selected.data.target ?? ""));
                        return (
                          <div style={{ display: "grid", gap: 10, color: "#020617" }}>
                            <div><strong>Source:</strong> {selected.data.source ?? "unknown"} {source?.label ? `(${source.label})` : ""}</div>
                            <div><strong>Target:</strong> {selected.data.target ?? "unknown"} {target?.label ? `(${target.label})` : ""}</div>
                            <div><strong>Relationship:</strong> {selected.data.label ?? "n/a"}</div>
                            <div><strong>Confidence:</strong> {typeof selected.data.confidence === "number" ? `${Math.round(selected.data.confidence * 100)}%` : "n/a"}</div>
                          </div>
                        );
                      })()
                    )}
                    <h4 style={{ color: "#0f2a6b", marginBottom: 6 }}>Raw data</h4>
                    <pre style={{ color: "#020617", whiteSpace: "pre-wrap", fontSize: 13 }}>
                      {JSON.stringify(selected.data, null, 2)}
                    </pre>
                  </>
                ) : (
                  <p style={{ color: "#020617" }}>Click a node or arrow to see details here.</p>
                )}
              </aside>
            </div>
          )}
        </div>

        <div style={{ display: "grid", gap: 16, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
        <div style={{ border: "1px solid #0f172a", borderRadius: 12, padding: 16, background: "#f8fafc", color: "#020617" }}>
          <h3>Nodes</h3>
          {resolvedNodes.length === 0 ? (
            <p>No nodes available.</p>
          ) : (
            <ul style={{ paddingLeft: 18 }}>
              {visibleNodes.map((node, index) => (
                <li key={node.id ?? index} style={{ marginBottom: 8, color: "#020617" }}>
                  <strong style={{ color: "#0f2a6b" }}>{node.label ?? node.id ?? `Node ${index + 1}`}</strong>
                  {node.type ? <span style={{ color: "#020617" }}> — {node.type}</span> : null}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div style={{ border: "1px solid #0f172a", borderRadius: 12, padding: 16, background: "#f8fafc", color: "#020617" }}>
          <h3>Edges</h3>
          {resolvedEdges.length === 0 ? (
            <p>No edges available.</p>
          ) : (
            <ul style={{ paddingLeft: 18 }}>
              {visibleEdges.map((edge, index) => (
                <li key={edge.id ?? index} style={{ marginBottom: 8, color: "#020617" }}>
                  <strong style={{ color: "#0f2a6b" }}>{edge.source ?? "unknown"} → {edge.target ?? "unknown"}</strong>
                  {edge.label ? <span style={{ color: "#020617" }}> — {edge.label}</span> : null}
                  {typeof edge.confidence === "number"
                    ? ` (${Math.round(edge.confidence * 100)}%)`
                    : ""}
                </li>
              ))}
            </ul>
          )}
        </div>
        </div>
      </div>
    </section>
  );
}
