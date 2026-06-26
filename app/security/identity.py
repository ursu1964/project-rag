"""Local development identity helpers.

No real authentication provider is implemented yet.
"""

from __future__ import annotations

import base64
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class Identity:
    subject: str
    role: str = "viewer"
    tenant_id: str = "local"
    metadata: dict = field(default_factory=dict)


class IdentityResolutionError(RuntimeError):
    """Raised when authenticated identity is required but cannot be resolved."""


@lru_cache(maxsize=16)
def _jwks_client(jwks_url: str):
    """Return a cached JWKS client for OIDC key resolution."""
    from jwt import PyJWKClient

    return PyJWKClient(jwks_url)


def _decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verifying signature.

    This is an auth scaffold helper for extracting claims in local/proxy setups.
    Signature verification should be added in a dedicated OIDC validation step.
    """
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    payload = parts[1]
    payload += "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8")).decode("utf-8")
        data = json.loads(decoded)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _role_from_claims(claims: dict) -> str:
    role = claims.get("role")
    if isinstance(role, str) and role.strip():
        return role.lower().strip()
    roles = claims.get("roles")
    if isinstance(roles, list) and roles:
        first = roles[0]
        if isinstance(first, str) and first.strip():
            return first.lower().strip()
    realm_access = claims.get("realm_access")
    if isinstance(realm_access, dict):
        ra_roles = realm_access.get("roles")
        if isinstance(ra_roles, list) and ra_roles:
            first = ra_roles[0]
            if isinstance(first, str) and first.strip():
                return first.lower().strip()
    return "viewer"


def _tenant_from_claims(claims: dict) -> str:
    for key in ("tenant_id", "tid", "tenant", "org_id"):
        value = claims.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "default"


def _verify_oidc_claims(
    token: str, issuer: str, audience: str = "", jwks_url: str = ""
) -> dict:
    """Verify OIDC token signature and standard claims via issuer JWKS.

    Args:
        token: The OIDC bearer token to verify
        issuer: The OIDC issuer URL (e.g., https://auth.example.com)
        audience: The expected audience claim (e.g., projectrag-api); required for production safety
        jwks_url: Optional explicit JWKS URL override; if not provided, derived from issuer

    Raises:
        IdentityResolutionError: If token is invalid, issuer is missing, or audience mismatch
    """
    normalized_issuer = issuer.rstrip("/").strip()
    if not normalized_issuer:
        raise IdentityResolutionError("OIDC issuer is required for oidc auth mode")

    normalized_audience = str(audience or "").strip()

    try:
        import jwt
    except Exception as exc:  # pragma: no cover - exercised by runtime setup only
        raise IdentityResolutionError("PyJWT is required for oidc auth mode") from exc

    # Use explicit JWKS URL if provided, otherwise derive from issuer
    resolved_jwks_url = (
        jwks_url.strip() if jwks_url and jwks_url.strip() else f"{normalized_issuer}/.well-known/jwks.json"
    )

    try:
        signing_key = _jwks_client(resolved_jwks_url).get_signing_key_from_jwt(token)
        options = {
            "verify_signature": True,
            "verify_iss": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": bool(normalized_audience),  # Validate audience if provided
        }
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256", "RS384", "RS512", "ES256", "ES384", "ES512"],
            issuer=normalized_issuer,
            audience=normalized_audience or None,  # Only set audience if non-empty
            options=options,
        )
    except jwt.InvalidAudienceError as exc:
        raise IdentityResolutionError(
            f"OIDC token audience mismatch. Expected '{normalized_audience}'"
        ) from exc
    except jwt.ExpiredSignatureError as exc:
        raise IdentityResolutionError("OIDC token has expired") from exc
    except jwt.InvalidIssuerError as exc:
        raise IdentityResolutionError(f"OIDC token issuer mismatch. Expected '{normalized_issuer}'") from exc
    except jwt.InvalidSignatureError as exc:
        raise IdentityResolutionError("OIDC token signature verification failed") from exc
    except Exception as exc:
        raise IdentityResolutionError("Invalid OIDC bearer token") from exc

    return claims if isinstance(claims, dict) else {}


def get_local_identity() -> Identity:
    """Return local development identity from environment defaults."""
    return Identity(
        subject=os.getenv("PROJECTRAG_LOCAL_USER", "local-dev"),
        role=os.getenv("PROJECTRAG_LOCAL_ROLE", "admin").lower(),
        tenant_id=os.getenv("PROJECTRAG_LOCAL_TENANT", "local"),
        metadata={"provider": "local_development", "authenticated": False},
    )


def resolve_request_identity(
    headers: Mapping[str, str],
    enforce_auth: bool = False,
    auth_mode: str | None = None,
    oidc_issuer: str | None = None,
    oidc_audience: str | None = None,
    oidc_jwks_url: str | None = None,
    allow_trusted_headers: bool | None = None,
) -> Identity:
    """Resolve request identity from trusted headers or bearer token.

    Resolution order:
    1) Trusted proxy/dev headers: x-projectrag-user / x-projectrag-role / x-projectrag-tenant-id
       (enabled by default for local mode)
    2) Bearer token claims (verified in oidc mode; unverified only in non-enforced local dev)
    3) Local fallback identity (unless enforce_auth is true)

    Args:
        headers: HTTP request headers
        enforce_auth: Whether authentication is required
        auth_mode: 'local' or 'oidc'
        oidc_issuer: OIDC issuer URL
        oidc_audience: Expected audience claim
        oidc_jwks_url: Explicit JWKS URL (overrides default derived from issuer)
        allow_trusted_headers: Enable trusted header resolution (default True for local mode)
    """
    lower = {str(k).lower(): str(v) for k, v in headers.items()}
    effective_mode = (auth_mode or os.getenv("PROJECTRAG_AUTH_MODE", "local")).strip().lower() or "local"
    effective_issuer = (oidc_issuer if oidc_issuer is not None else os.getenv("PROJECTRAG_OIDC_ISSUER", "")).strip()
    effective_audience = (
        oidc_audience if oidc_audience is not None else os.getenv("PROJECTRAG_OIDC_AUDIENCE", "")
    ).strip()
    effective_jwks_url = (oidc_jwks_url if oidc_jwks_url is not None else os.getenv("PROJECTRAG_OIDC_JWKS_URL", "")).strip()
    trusted_headers_enabled = (
        allow_trusted_headers if allow_trusted_headers is not None else effective_mode != "oidc"
    )

    user = lower.get("x-projectrag-user", "").strip() if trusted_headers_enabled else ""
    if user:
        role = lower.get("x-projectrag-role", "viewer").strip().lower() or "viewer"
        tenant_id = lower.get("x-projectrag-tenant-id", "default").strip() or "default"
        return Identity(
            subject=user,
            role=role,
            tenant_id=tenant_id,
            metadata={"provider": "trusted_header", "authenticated": True},
        )

    authorization = lower.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        try:
            if effective_mode == "oidc":
                claims = _verify_oidc_claims(
                    token, issuer=effective_issuer, audience=effective_audience, jwks_url=effective_jwks_url
                )
                provider = "oidc_bearer_verified"
            elif not enforce_auth:
                claims = _decode_jwt_payload(token)
                provider = "oidc_bearer_unverified"
            else:
                raise IdentityResolutionError("Bearer tokens require oidc auth mode when auth is enforced")
        except IdentityResolutionError:
            if enforce_auth:
                raise
            claims = {}
            provider = "local_fallback"

        subject = str(
            claims.get("sub")
            or claims.get("preferred_username")
            or claims.get("upn")
            or ""
        ).strip()
        if subject:
            return Identity(
                subject=subject,
                role=_role_from_claims(claims),
                tenant_id=_tenant_from_claims(claims),
                metadata={"provider": provider, "authenticated": True, "claims": claims},
            )

    if enforce_auth:
        raise IdentityResolutionError("Authentication required but no valid identity was provided")

    return get_local_identity()
