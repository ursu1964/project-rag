"""Turtle triple builders."""

import re

PREFIX_LINE = "@prefix project: <http://projectrag.local/> ."


def sanitize_entity(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", value.strip())
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    if not sanitized:
        return "Entity"
    if sanitized[0].isdigit():
        sanitized = f"Entity_{sanitized}"
    return sanitized


def build_triple(subject: str, predicate: str, obj: str) -> str:
    return f"project:{sanitize_entity(subject)} project:{sanitize_entity(predicate)} project:{sanitize_entity(obj)} ."


def build_turtle(triples) -> str:
    lines = [PREFIX_LINE]
    lines.extend(triples)
    return "\n".join(lines) + "\n"
