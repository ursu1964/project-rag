"""Comprehensive OIDC JWT verification tests.

Tests cover:
- Valid token verification
- Expired token rejection
- Wrong issuer rejection
- Wrong audience rejection
- Invalid signature rejection
- Missing token handling
- Malformed token handling
- JWKS caching
- Explicit JWKS URL override
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt as pyjwt
import pytest

from app.security.identity import (
    IdentityResolutionError,
    resolve_request_identity,
    _verify_oidc_claims,
)


# ============================================================================
# Test Fixtures: Key Pair and JWKS Setup
# ============================================================================


@pytest.fixture
def rsa_key_pair():
    """Generate RSA key pair for testing."""
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return {"private": private_pem, "public": public_pem, "key": private_key}


@pytest.fixture
def test_jwks(rsa_key_pair):
    """Create a valid JWKS response with test key."""

    public_key = rsa_key_pair["key"].public_key()
    public_numbers = public_key.public_numbers()

    # Convert to JWKS format
    from base64 import urlsafe_b64encode

    e = urlsafe_b64encode(public_numbers.e.to_bytes(3, byteorder="big")).decode().rstrip("=")
    n = urlsafe_b64encode(public_numbers.n.to_bytes(256, byteorder="big")).decode().rstrip("=")

    jwks = {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "kid": "test-key-id",
                "n": n,
                "e": e,
                "alg": "RS256",
            }
        ]
    }

    return jwks


def create_token(
    private_key,
    subject: str = "user123",
    issuer: str = "https://auth.example.com",
    audience: str = "projectrag-api",
    extra_claims: dict | None = None,
    expired: bool = False,
    exp_delta: int = 3600,
):
    """Create a valid JWT token for testing."""
    now = datetime.now(timezone.utc)
    exp_time = now + timedelta(seconds=exp_delta if not expired else -exp_delta)

    payload = {
        "sub": subject,
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int(exp_time.timestamp()),
        "nbf": int(now.timestamp()),
    }

    if extra_claims:
        payload.update(extra_claims)

    token = pyjwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key-id"},
    )

    return token


# ============================================================================
# Tests: Valid Token Verification
# ============================================================================


class TestValidTokenVerification:
    """Tests for successful token verification."""

    def test_valid_token_with_all_claims(self, rsa_key_pair, test_jwks):
        """Verify that a valid token with correct issuer, audience, and signature passes."""
        token = create_token(
            rsa_key_pair["key"],
            subject="alice",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="projectrag-api",
            )

            assert claims["sub"] == "alice"
            assert claims["iss"] == "https://auth.example.com"
            assert claims["aud"] == "projectrag-api"

    def test_valid_token_without_audience_validation(self, rsa_key_pair, test_jwks):
        """Verify that token passes without audience validation if audience is empty."""
        token = create_token(
            rsa_key_pair["key"],
            subject="bob",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            # No audience specified in verification
            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="",  # Empty = no validation
            )

            assert claims["sub"] == "bob"

    def test_valid_token_with_extra_claims(self, rsa_key_pair, test_jwks):
        """Verify that extra custom claims are preserved."""
        extra_claims = {
            "role": "admin",
            "org_id": "org-123",
            "permissions": ["read", "write"],
        }

        token = create_token(
            rsa_key_pair["key"],
            subject="charlie",
            issuer="https://auth.example.com",
            audience="projectrag-api",
            extra_claims=extra_claims,
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="projectrag-api",
            )

            assert claims["role"] == "admin"
            assert claims["org_id"] == "org-123"
            assert claims["permissions"] == ["read", "write"]


# ============================================================================
# Tests: Expired Token Rejection
# ============================================================================


class TestExpiredTokenRejection:
    """Tests for expired token handling."""

    def test_expired_token_is_rejected(self, rsa_key_pair):
        """Verify that expired tokens are rejected with clear error."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
            expired=True,
            exp_delta=3600,
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="expired"):
                _verify_oidc_claims(
                    token,
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )

    def test_token_about_to_expire_is_still_valid(self, rsa_key_pair):
        """Verify that tokens with near-future expiration are still valid."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
            expired=False,
            exp_delta=10,  # Expires in 10 seconds
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="projectrag-api",
            )

            assert claims["sub"] == "user123"


# ============================================================================
# Tests: Issuer Validation
# ============================================================================


class TestIssuerValidation:
    """Tests for issuer claim validation."""

    def test_wrong_issuer_is_rejected(self, rsa_key_pair):
        """Verify that tokens with wrong issuer are rejected."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://wrong-issuer.com",
            audience="projectrag-api",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="issuer mismatch"):
                _verify_oidc_claims(
                    token,
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )

    def test_issuer_with_trailing_slash_is_normalized(self, rsa_key_pair):
        """Verify that issuer URLs with trailing slashes are normalized."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            # Issuer with trailing slash should still match
            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com/",  # Trailing slash
                audience="projectrag-api",
            )

            assert claims["sub"] == "user123"

    def test_missing_issuer_raises_error(self):
        """Verify that missing issuer raises configuration error."""
        with pytest.raises(IdentityResolutionError, match="issuer is required"):
            _verify_oidc_claims(
                "token",
                issuer="",  # Empty issuer
                audience="projectrag-api",
            )


# ============================================================================
# Tests: Audience Validation
# ============================================================================


class TestAudienceValidation:
    """Tests for audience claim validation."""

    def test_wrong_audience_is_rejected(self, rsa_key_pair):
        """Verify that tokens with wrong audience are rejected."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="other-app",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="audience mismatch"):
                _verify_oidc_claims(
                    token,
                    issuer="https://auth.example.com",
                    audience="projectrag-api",  # Expected audience
                )

    def test_multiple_audiences_supported(self, rsa_key_pair):
        """Verify that tokens with multiple audiences work correctly."""
        # Create token with multiple audiences
        now = datetime.now(timezone.utc)
        payload = {
            "sub": "user123",
            "iss": "https://auth.example.com",
            "aud": ["projectrag-api", "other-api"],  # Multiple audiences
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=3600)).timestamp()),
        }

        token = pyjwt.encode(
            payload,
            rsa_key_pair["key"],
            algorithm="RS256",
            headers={"kid": "test-key-id"},
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="projectrag-api",  # Checking if this audience is in the list
            )

            assert claims["sub"] == "user123"


# ============================================================================
# Tests: Signature Validation
# ============================================================================


class TestSignatureValidation:
    """Tests for JWT signature verification."""

    def test_invalid_signature_is_rejected(self, rsa_key_pair):
        """Verify that tokens with invalid signatures are rejected."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        # Corrupt the signature
        parts = token.split(".")
        corrupted_token = f"{parts[0]}.{parts[1]}.CORRUPTED_SIGNATURE"

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="signature"):
                _verify_oidc_claims(
                    corrupted_token,
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )

    def test_token_signed_with_wrong_key_is_rejected(self, rsa_key_pair):
        """Verify that tokens signed with a different key are rejected."""
        # Create token with one key
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        # Try to verify with a different key
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        different_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=different_key.public_key()
            )
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="signature"):
                _verify_oidc_claims(
                    token,
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )


# ============================================================================
# Tests: Malformed Token Handling
# ============================================================================


class TestMalformedTokenHandling:
    """Tests for handling of malformed tokens."""

    def test_missing_token_handled_gracefully(self):
        """Verify that missing token (empty string) is handled."""
        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.side_effect = Exception("Invalid token")
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="Invalid OIDC bearer token"):
                _verify_oidc_claims(
                    "",
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )

    def test_malformed_jwt_is_rejected(self):
        """Verify that malformed JWT (wrong format) is rejected."""
        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.side_effect = Exception("Invalid token format")
            mock_jwks_client.return_value = mock_client

            with pytest.raises(IdentityResolutionError, match="Invalid OIDC bearer token"):
                _verify_oidc_claims(
                    "not.a.jwt.token",
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )

    def test_jwks_fetch_failure_handled(self):
        """Verify that JWKS fetch failure is handled gracefully."""
        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_jwks_client.side_effect = Exception("JWKS endpoint unreachable")

            with pytest.raises(IdentityResolutionError, match="Invalid OIDC bearer token"):
                _verify_oidc_claims(
                    "some.jwt.token",
                    issuer="https://auth.example.com",
                    audience="projectrag-api",
                )


# ============================================================================
# Tests: JWKS URL Configuration
# ============================================================================


class TestJWKSURLConfiguration:
    """Tests for JWKS URL handling."""

    def test_explicit_jwks_url_override(self, rsa_key_pair):
        """Verify that explicit JWKS URL is used when provided."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="projectrag-api",
                jwks_url="https://custom-jwks.example.com/keys",
            )

            # Verify that the custom JWKS URL was used
            mock_jwks_client.assert_called_with("https://custom-jwks.example.com/keys")
            assert claims["sub"] == "user123"

    def test_default_jwks_url_derived_from_issuer(self, rsa_key_pair):
        """Verify that JWKS URL is derived from issuer when not explicitly provided."""
        token = create_token(
            rsa_key_pair["key"],
            subject="user123",
            issuer="https://auth.example.com",
            audience="projectrag-api",
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            claims = _verify_oidc_claims(
                token,
                issuer="https://auth.example.com",
                audience="projectrag-api",
                jwks_url="",  # Empty = use default derived from issuer
            )

            # Verify that the standard JWKS URL was used
            mock_jwks_client.assert_called_with("https://auth.example.com/.well-known/jwks.json")
            assert claims["sub"] == "user123"


# ============================================================================
# Tests: Request Identity Resolution
# ============================================================================


class TestRequestIdentityResolution:
    """Tests for full identity resolution with JWT verification."""

    def test_valid_bearer_token_resolves_identity(self, rsa_key_pair):
        """Verify that valid bearer token resolves to proper identity."""
        token = create_token(
            rsa_key_pair["key"],
            subject="alice@example.com",
            issuer="https://auth.example.com",
            audience="projectrag-api",
            extra_claims={"role": "admin", "tenant_id": "tenant-123"},
        )

        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.return_value = MagicMock(
                key=rsa_key_pair["key"].public_key()
            )
            mock_jwks_client.return_value = mock_client

            headers = {"authorization": f"Bearer {token}"}
            identity = resolve_request_identity(
                headers,
                enforce_auth=True,
                auth_mode="oidc",
                oidc_issuer="https://auth.example.com",
                oidc_audience="projectrag-api",
            )

            assert identity.subject == "alice@example.com"
            assert identity.role == "admin"
            assert identity.tenant_id == "tenant-123"
            assert identity.metadata["provider"] == "oidc_bearer_verified"

    def test_invalid_bearer_token_fails_when_auth_required(self, rsa_key_pair):
        """Verify that invalid token fails when auth is required."""
        with patch("app.security.identity._jwks_client") as mock_jwks_client:
            mock_client = MagicMock()
            mock_client.get_signing_key_from_jwt.side_effect = Exception("Invalid token")
            mock_jwks_client.return_value = mock_client

            headers = {"authorization": "Bearer invalid.token.here"}

            with pytest.raises(IdentityResolutionError):
                resolve_request_identity(
                    headers,
                    enforce_auth=True,
                    auth_mode="oidc",
                    oidc_issuer="https://auth.example.com",
                    oidc_audience="projectrag-api",
                )

    def test_trusted_headers_bypass_bearer_token(self):
        """Verify that trusted headers take precedence in local mode."""
        headers = {
            "x-projectrag-user": "bob@example.com",
            "x-projectrag-role": "viewer",
            "x-projectrag-tenant-id": "tenant-456",
            "authorization": "Bearer some.invalid.token",
        }

        identity = resolve_request_identity(
            headers,
            enforce_auth=False,
            auth_mode="local",  # Trusted headers enabled in local mode
        )

        assert identity.subject == "bob@example.com"
        assert identity.role == "viewer"
        assert identity.tenant_id == "tenant-456"
        assert identity.metadata["provider"] == "trusted_header"
