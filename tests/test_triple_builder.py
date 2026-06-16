from app.graph.triple_builder import build_triple, build_turtle


def test_build_turtle_includes_project_prefix():
    turtle = build_turtle([build_triple("VM1", "dependsOn", "Database01")])
    assert turtle.startswith("@prefix project: <http://projectrag.local/> .")
    assert "project:VM1 project:dependsOn project:Database01 ." in turtle
