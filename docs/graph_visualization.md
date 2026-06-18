# Graph Visualization

ProjectRAG exposes a lightweight graph export endpoint for future frontend visualization.

## Endpoint

```http
GET /graph/export
```

Optional query parameter:

```text
limit=1000
```

Example:

```bash
curl http://127.0.0.1:8000/graph/export
```

Response shape:

```json
{
  "nodes": [
    {"id": "VM1", "label": "VM1"},
    {"id": "Database01", "label": "Database01"}
  ],
  "edges": [
    {
      "id": "fact-id",
      "source": "VM1",
      "target": "Database01",
      "label": "dependsOn",
      "confidence": 0.8,
      "metadata": {}
    }
  ]
}
```

The current implementation uses PostgreSQL `graph_facts` for provenance-friendly export. This avoids requiring frontend clients to understand SPARQL or RDF internals.

## Cytoscape.js Mapping

Cytoscape expects elements with `data` objects:

```javascript
const graph = await fetch('/graph/export').then(r => r.json());

const elements = [
  ...graph.nodes.map(node => ({
    data: { id: node.id, label: node.label }
  })),
  ...graph.edges.map(edge => ({
    data: {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      confidence: edge.confidence
    }
  }))
];
```

Useful Cytoscape display choices:

- Node label: `data(label)`
- Edge label: `data(label)`
- Edge direction: enabled arrows for dependency direction
- Color by relationship type, for example `dependsOn`, `connectedTo`, `protectedBy`

## D3 Mapping

D3 force graphs typically use `nodes` and `links`:

```javascript
const graph = await fetch('/graph/export').then(r => r.json());

const nodes = graph.nodes;
const links = graph.edges.map(edge => ({
  id: edge.id,
  source: edge.source,
  target: edge.target,
  relationship: edge.label,
  confidence: edge.confidence
}));
```

Recommended D3 behavior:

- Use force-link with `id(d => d.id)`.
- Render relationship labels near links.
- Use arrows to show direction.
- Size or opacity edges by confidence.

## Future Enhancements

- Add filtering by entity, relationship type, confidence, and source document.
- Add neighborhood export, for example `GET /graph/export?entity=VM1&depth=2`.
- Include entity types when ontology enrichment is stable.
- Support direct GraphDB export if named graphs/provenance are introduced.
