"""Check Compose, Kubernetes, and Dockerfile image references are stable."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_IMAGE_RE = re.compile(r"^\s*image:\s*([^\s#]+)", re.MULTILINE)
_FROM_RE = re.compile(r"^\s*FROM\s+([^\s]+)", re.MULTILINE)
_DEFAULT_FILES = (
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "deploy/k8s/api.yaml",
    "deploy/k8s/frontend.yaml",
    "Dockerfile",
    "frontend/Dockerfile",
)


def _references(paths: list[str]) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    for item in paths:
        path = Path(item)
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in _IMAGE_RE.finditer(text):
            found.append((str(path), "image", match.group(1).strip('"\'')))
        for match in _FROM_RE.finditer(text):
            image = match.group(1).split("@", 1)[0]
            found.append((str(path), "from", image.strip('"\'')))
    return found


def _has_tag_or_digest(image: str) -> bool:
    if "@sha256:" in image:
        return True
    name = image.rsplit("/", 1)[-1]
    return ":" in name and not name.endswith(":latest")


def _is_local_project_image(image: str) -> bool:
    name = image.split(":", 1)[0]
    return "/" not in name and name.startswith("projectrag-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Docker image pinning")
    parser.add_argument("--require-digest", action="store_true", help="Require image@sha256:digest for external image: references")
    parser.add_argument("files", nargs="*", default=list(_DEFAULT_FILES))
    args = parser.parse_args()

    failures: list[str] = []
    for path, kind, image in _references(args.files):
        if not _has_tag_or_digest(image):
            failures.append(f"{path}: {kind} is not tag-pinned: {image}")
        if (
            args.require_digest
            and kind == "image"
            and not _is_local_project_image(image)
            and "@sha256:" not in image
        ):
            failures.append(f"{path}: image is not digest-pinned: {image}")

    if failures:
        print("\n".join(failures))
        return 1
    mode = "digest" if args.require_digest else "tag"
    print(f"docker-image-{mode}-pins-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
