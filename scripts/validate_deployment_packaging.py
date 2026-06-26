"""Static deployment packaging validation for production compose and Kubernetes manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROD_COMPOSE = ROOT / "docker-compose.prod.yml"
K8S_FILES = [ROOT / "deploy/k8s/api.yaml", ROOT / "deploy/k8s/config.yaml", ROOT / "deploy/k8s/frontend.yaml"]
ENV_EXAMPLE = ROOT / ".env.example"


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _load_all(path: Path) -> list[Any]:
    return [doc for doc in yaml.safe_load_all(path.read_text(encoding="utf-8")) if doc]


def _service_env(service: dict[str, Any]) -> dict[str, str]:
    env = service.get("environment") or {}
    if isinstance(env, list):
        pairs = [item.split("=", 1) for item in env if isinstance(item, str) and "=" in item]
        return {key: value for key, value in pairs}
    return {str(key): str(value) for key, value in env.items()}


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def validate_compose() -> None:
    data = _load_yaml(PROD_COMPOSE)
    services = data.get("services") or {}
    api = services.get("projectrag-api") or {}
    env = _service_env(api)
    _assert(env.get("APP_ENV") == "production", "prod compose API must set APP_ENV=production")
    _assert(env.get("PROJECTRAG_AUTH_REQUIRED") == "true", "prod compose must require auth")
    _assert(env.get("PROJECTRAG_ENFORCE_RBAC") == "true", "prod compose must enforce RBAC")
    _assert(env.get("OTEL_ENABLED", "").startswith("${OTEL_ENABLED:-true}"), "prod compose must enable OTEL by default")
    _assert("OTEL_EXPORTER_OTLP_ENDPOINT" in env, "prod compose must configure OTEL collector endpoint")
    _assert(env.get("PROJECTRAG_CLOUD_CONNECTORS_ENABLED") == "false", "cloud connectors must be disabled by default")
    _assert("/health/ready" in str(api.get("healthcheck", {})), "prod API healthcheck must use /health/ready")

    for name, service in services.items():
        _assert(service.get("restart") == "unless-stopped", f"{name} must have restart policy")
        _assert("deploy" in service and "resources" in service["deploy"], f"{name} must define resource limits")
        _assert("security_opt" in service, f"{name} must disable privilege escalation where possible")


def validate_k8s() -> None:
    docs = [doc for path in K8S_FILES for doc in _load_all(path)]
    deployments = {doc["metadata"]["name"]: doc for doc in docs if doc.get("kind") == "Deployment"}
    api = deployments.get("projectrag-api")
    frontend = deployments.get("projectrag-frontend")
    _assert(api is not None, "missing projectrag-api Deployment")
    _assert(frontend is not None, "missing projectrag-frontend Deployment")

    for name, deployment in deployments.items():
        pod_spec = deployment["spec"]["template"]["spec"]
        _assert(pod_spec.get("securityContext", {}).get("runAsNonRoot") is True, f"{name} must run as non-root")
        for container in pod_spec.get("containers", []):
            image = str(container.get("image", ""))
            _assert(image and not image.endswith(":latest"), f"{name} image must not use latest")
            _assert("resources" in container, f"{name}/{container.get('name')} must define resources")
            _assert(container.get("securityContext", {}).get("allowPrivilegeEscalation") is False, f"{name}/{container.get('name')} must disable privilege escalation")
            _assert("readinessProbe" in container and "livenessProbe" in container, f"{name}/{container.get('name')} needs probes")

    api_container = api["spec"]["template"]["spec"]["containers"][0]
    _assert(api_container["readinessProbe"]["httpGet"]["path"] == "/health/ready", "API readiness must use /health/ready")
    _assert(api_container["livenessProbe"]["httpGet"]["path"] == "/health/live", "API liveness must use /health/live")

    config_docs = {doc.get("kind"): doc for doc in docs if doc.get("metadata", {}).get("name") in {"projectrag-config", "projectrag-secrets"}}
    config = config_docs.get("ConfigMap", {}).get("data", {})
    _assert(config.get("PROJECTRAG_AUTH_REQUIRED") == "true", "K8s config must require auth")
    _assert(config.get("PROJECTRAG_CLOUD_CONNECTORS_ENABLED") == "false", "K8s config must disable cloud connectors")
    _assert(config.get("OTEL_ENABLED") == "true", "K8s config must enable OTEL")


def validate_env_example() -> None:
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    forbidden = ["super-secret", "password123", "BEGIN PRIVATE KEY"]
    for item in forbidden:
        _assert(item not in text, f".env.example contains unsafe secret-like value: {item}")
    _assert("PROJECTRAG_CLOUD_CONNECTORS_ENABLED=false" in text, ".env.example must default cloud connectors off")


def main() -> int:
    validate_compose()
    validate_k8s()
    validate_env_example()
    print("deployment-packaging-validation-ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
