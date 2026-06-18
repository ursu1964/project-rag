"use client";

import { useMemo, useState } from "react";
import { Background, Controls, MiniMap, ReactFlow, type Edge, type Node } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type TopologyNode = { id?: string; label?: string };
type TopologyEdge = { id?: string; source?: string; target?: string; label?: string; confidence?: number };
type TopologyResponse = { nodes?: TopologyNode[]; edges?: TopologyEdge[] };

function toCanvasNodes(nodes: TopologyNode[]): Node[] {
  if (!nodes.length) return [];
  const radius = Math.max(180, nodes.length * 7);
  return nodes.map((node, index) => {
    const angle = (2 * Math.PI * index) / nodes.length;
    return {
      id: node.id || `node-${index}`,
      position: {
        x: Math.round(Math.cos(angle) * radius + radius + 80),
        y: Math.round(Math.sin(angle) * radius + radius + 60),
      },
      data: { label: node.label || node.id || "Unknown" },
      style: {
        borderRadius: 12,
        border: "1px solid rgba(154, 194, 211, 0.35)",
        background: "rgba(7, 24, 35, 0.96)",
        color: "#deebf3",
        padding: 10,
        fontSize: 12,
      },
    };
  });
}

function toCanvasEdges(edges: TopologyEdge[]): Edge[] {
  return edges
    .filter((edge) => edge.source && edge.target)
    .map((edge, index) => ({
      id: edge.id || `edge-${index}`,
      source: String(edge.source),
      target: String(edge.target),
      label: edge.label || "dependsOn",
      style: {
        stroke: "#7fdcc8",
        strokeWidth: 1.5,
      },
      labelStyle: { fill: "#c5dbe7", fontSize: 11 },
    }));
}

function useLocalStorage<T>(key: string, initial: T): [T, (value: T) => void] {
  const [state, setState] = useState<T>(() => {
    if (typeof window === "undefined") return initial;
    try {
      const stored = window.localStorage.getItem(key);
      return stored !== null ? (JSON.parse(stored) as T) : initial;
    } catch {
      return initial;
    }
  });
  const set = (value: T) => {
    setState(value);
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch { /* quota exceeded — silently ignore */ }
  };
  return [state, set];
}

type SelectedItem =
  | { kind: "node"; id: string }
  | { kind: "edge"; id: string }
  | { kind: "none" };

export function TopologyExplorer({ graph }: { graph: TopologyResponse }) {
  const [mode, setMode] = useLocalStorage<"list" | "canvas" | "raw">("topology:mode", "canvas");
  const [selected, setSelected] = useState<SelectedItem>({ kind: "none" });
  const nodes = graph.nodes || [];
  const edges = graph.edges || [];

  const flowNodes = useMemo(() => toCanvasNodes(nodes), [nodes]);
  const flowEdges = useMemo(() => toCanvasEdges(edges), [edges]);

  const selectedNode = useMemo(
    () => selected.kind === "node" ? nodes.find((n) => String(n.id || "") === selected.id) : undefined,
    [nodes, selected],
  );
  const selectedEdge = useMemo(
    () => selected.kind === "edge" ? edges.find((e) => String(e.id || "") === selected.id) : undefined,
    [edges, selected],
  );
  const relatedEdges = useMemo(
    () => selected.kind === "node"
      ? edges.filter((edge) => edge.source === selected.id || edge.target === selected.id)
      : [],
    [edges, selected],
  );
  const neighbors = useMemo(() => {
    if (selected.kind !== "node") return [];
    const values = new Set<string>();
    for (const edge of relatedEdges) {
      if (edge.source && edge.source !== selected.id) values.add(edge.source);
      if (edge.target && edge.target !== selected.id) values.add(edge.target);
    }
    return Array.from(values).sort();
  }, [relatedEdges, selected]);

  return (
    <>
      <div className="tabs" role="tablist" aria-label="Topology view modes">
        <button className={mode === "canvas" ? "tab active" : "tab"} onClick={() => setMode("canvas")}>Canvas</button>
        <button className={mode === "list" ? "tab active" : "tab"} onClick={() => setMode("list")}>List</button>
        <button className={mode === "raw" ? "tab active" : "tab"} onClick={() => setMode("raw")}>Raw JSON</button>
      </div>

      {mode === "canvas" && (
        <section className="card" style={{ marginTop: 14 }}>
          <h2>Interactive Topology Canvas</h2>
          <div className="rf-layout">
            <div className="rf-canvas">
              <ReactFlow
                nodes={flowNodes}
                edges={flowEdges}
                fitView
                onNodeClick={(_, node) => setSelected({ kind: "node", id: String(node.id) })}
                onEdgeClick={(_, edge) => setSelected({ kind: "edge", id: String(edge.id) })}
                onPaneClick={() => setSelected({ kind: "none" })}
              >
                <MiniMap />
                <Controls />
                <Background gap={18} color="rgba(154, 194, 211, 0.12)" />
              </ReactFlow>
            </div>
            <aside className="node-panel">
              {selected.kind === "none" && (
                <>
                  <h3>Details Panel</h3>
                  <p>Click a node or edge to inspect its data.</p>
                </>
              )}
              {selected.kind === "node" && (
                <>
                  <h3>Node Details</h3>
                  <p><strong>{selectedNode?.label || selected.id}</strong></p>
                  <p>ID: {selected.id}</p>
                  <p>Connections: {relatedEdges.length}</p>
                  <p>Neighbors: {neighbors.length}</p>
                  {neighbors.length > 0 && (
                    <p style={{ fontSize: "0.82rem", color: "var(--muted)" }}>{neighbors.join(", ")}</p>
                  )}
                  <div className="json-box" style={{ maxHeight: 200 }}>
                    <pre>{JSON.stringify(relatedEdges.slice(0, 20), null, 2)}</pre>
                  </div>
                </>
              )}
              {selected.kind === "edge" && (
                <>
                  <h3>Edge Details</h3>
                  <table className="kv">
                    <tbody>
                      <tr><th>Source</th><td>{selectedEdge?.source || selected.id}</td></tr>
                      <tr><th>Target</th><td>{selectedEdge?.target || "—"}</td></tr>
                      <tr><th>Relationship</th><td>{selectedEdge?.label || "—"}</td></tr>
                      <tr><th>Confidence</th><td>{selectedEdge?.confidence ?? "—"}</td></tr>
                      <tr><th>Edge ID</th><td>{selectedEdge?.id || selected.id}</td></tr>
                    </tbody>
                  </table>
                </>
              )}
            </aside>
          </div>
        </section>
      )}

      {mode === "list" && (
        <section className="grid" style={{ marginTop: 14 }}>
          <article className="card">
            <h2>Nodes</h2>
            <div className="list">
              {nodes.slice(0, 24).map((node, index) => (
                <div className="list-item" key={node.id || `node-${index}`}>
                  <h3>{node.label || node.id || "Unknown node"}</h3>
                  <p>ID: {node.id || "n/a"}</p>
                </div>
              ))}
              {nodes.length === 0 && <p>No nodes available.</p>}
            </div>
          </article>
          <article className="card">
            <h2>Edges</h2>
            <div className="list">
              {edges.slice(0, 24).map((edge, index) => (
                <div className="list-item" key={edge.id || `edge-${index}`}>
                  <h3>{`${edge.source || "unknown"} -> ${edge.target || "unknown"}`}</h3>
                  <p>{edge.label || "relationship"} | confidence: {edge.confidence ?? "n/a"}</p>
                </div>
              ))}
              {edges.length === 0 && <p>No edges available.</p>}
            </div>
          </article>
        </section>
      )}

      {mode === "raw" && (
        <section className="card" style={{ marginTop: 14 }}>
          <h2>Raw Graph Export</h2>
          <div className="json-box">
            <pre>{JSON.stringify(graph, null, 2)}</pre>
          </div>
        </section>
      )}
    </>
  );
}
