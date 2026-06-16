# ProjectRAG Graph Ontology

## Purpose

The ProjectRAG graph ontology defines the entity and relationship vocabulary used for GraphRAG extraction, storage, querying, and auditability.

## Ontology Version

Current version: `0.1.0`

Versioning strategy:

- Patch versions update descriptions or aliases without changing meaning.
- Minor versions add new entity or relationship types in a backward-compatible way.
- Major versions may rename or remove types and require migration scripts.
- Store future ontology version metadata with imported graph facts when schema support is added.

## Entities

Supported MVP entity examples:

| Entity Type | Description |
| --- | --- |
| `VM` | Virtual machine or compute node |
| `Database` | Database system or database instance |
| `Subnet` | Network subnet |
| `Firewall` | Firewall, security appliance, or filtering component |
| `Service` | Application or platform service |
| `API` | API endpoint, API service, or API gateway component |

Future entity types may include:

- `Application`
- `Queue`
- `StorageAccount`
- `LoadBalancer`
- `KubernetesCluster`
- `Namespace`
- `Container`

## Relationships

Supported MVP relationship examples:

| Relationship | Meaning | Example |
| --- | --- | --- |
| `dependsOn` | Source requires target to function | `VM1 dependsOn Database01` |
| `connectedTo` | Source is network/logically connected to target | `VM1 connectedTo SubnetA` |
| `protectedBy` | Source is protected by target | `Database01 protectedBy Firewall01` |
| `runsOn` | Source runs on target infrastructure | `ApplicationA runsOn VM1` |
| `uses` | Source uses target | `API01 uses Database01` |
| `calls` | Source calls target service/API | `ServiceA calls API01` |
| `belongsTo` | Source belongs to target grouping/network | `SubnetA belongsTo VNetDev` |
| `readsFrom` | Source reads from target | `Worker readsFrom Queue01` |
| `writesTo` | Source writes to target | `Worker writesTo Database01` |
| `type` | Entity type assertion | `VM1 type VM` |

## Aliases

Entity aliases used by deterministic extraction:

| Canonical Type | Aliases |
| --- | --- |
| `VM` | `vm`, `virtual machine` |
| `Database` | `database`, `db` |
| `Subnet` | `subnet` |
| `Firewall` | `firewall` |
| `VNet` | `vnet`, `virtual network` |
| `Service` | `service` |
| `API` | `api` |

Relationship aliases:

| Canonical Relationship | Extracted Phrase |
| --- | --- |
| `dependsOn` | `depends on` |
| `connectedTo` | `is connected to` |
| `uses` | `uses` |
| `protectedBy` | `is protected by` |
| `runsOn` | `runs on` |
| `belongsTo` | `belongs to` |
| `calls` | `calls` |
| `readsFrom` | `reads from` |
| `writesTo` | `writes to` |

## Validation Rules

Graph ingestion applies MVP validation rules:

- Subject, predicate, and object must be non-empty.
- Subject, predicate, and object are normalized before insertion.
- Exact duplicate triples are removed.
- Predicate must exist in `ontology.RELATION_TYPES`.
- Rejected triples are returned separately for audit/debugging.
- Valid graph facts are stored in GraphDB and PostgreSQL `graph_facts`.

## Naming Conventions

- Use PascalCase or stable infrastructure names when possible: `Database01`, `Firewall01`.
- Spaces and unsupported characters are converted to underscores.
- Identifiers are stored as `project:<EntityName>` in RDF.
- Predicates use camelCase: `dependsOn`, `connectedTo`, `protectedBy`.
- Avoid natural-language predicates in stored graph facts.

## Examples

Turtle example:

```turtle
@prefix project: <http://projectrag.local/> .
project:VM1 project:type project:VM .
project:Database01 project:type project:Database .
project:VM1 project:dependsOn project:Database01 .
project:VM1 project:connectedTo project:SubnetA .
project:Database01 project:protectedBy project:Firewall01 .
project:ApplicationA project:runsOn project:VM1 .
```

SPARQL example:

```sparql
PREFIX project: <http://projectrag.local/>
SELECT ?dependency WHERE {
  project:VM1 project:dependsOn ?dependency .
}
```
