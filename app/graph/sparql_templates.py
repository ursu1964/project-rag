"""SPARQL query templates."""

PREFIX = "PREFIX project: <http://projectrag.local/>"


def dependency_query(entity: str) -> str:
    return f"""
{PREFIX}
SELECT ?dependency
WHERE {{
  project:{entity} project:dependsOn ?dependency .
}}
""".strip()


def reverse_dependency_query(entity: str) -> str:
    return f"""
{PREFIX}
SELECT ?dependent
WHERE {{
  ?dependent project:dependsOn project:{entity} .
}}
""".strip()


def outgoing_relationships_query(entity: str) -> str:
    return f"""
{PREFIX}
SELECT ?predicate ?object
WHERE {{
  project:{entity} ?predicate ?object .
}}
""".strip()


def incoming_relationships_query(entity: str) -> str:
    return f"""
{PREFIX}
SELECT ?subject ?predicate
WHERE {{
  ?subject ?predicate project:{entity} .
}}
""".strip()


def two_hop_dependency_query(entity: str) -> str:
    return f"""
{PREFIX}
SELECT ?middle ?dependency
WHERE {{
  project:{entity} project:dependsOn ?middle .
  ?middle project:dependsOn ?dependency .
}}
""".strip()


def impact_query(entity: str) -> str:
    return f"""
{PREFIX}
SELECT ?impacted ?predicate ?path
WHERE {{
  ?impacted ?predicate project:{entity} .
  OPTIONAL {{ ?path project:dependsOn ?impacted . }}
}}
""".strip()
