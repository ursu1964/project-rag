"""API key hashing and verification using bcrypt for timing-safe comparison."""

from __future__ import annotations

import hmac

try:
    import bcrypt
except ImportError:
    bcrypt = None  # pragma: no cover


class APIKeyError(Exception):
    """Raised when API key validation fails."""


def hash_api_key(plaintext_key: str) -> str:
    """Hash an API key using bcrypt for secure storage.

    Args:
        plaintext_key: The raw API key to hash

    Returns:
        The bcrypt hash (e.g., "$2b$12$...")

    Raises:
        APIKeyError: If bcrypt is not installed or key is empty
    """
    if not bcrypt:  # pragma: no cover
        raise APIKeyError("bcrypt is required for API key hashing. Install via: pip install bcrypt")

    if not plaintext_key or not str(plaintext_key).strip():
        raise APIKeyError("API key must not be empty")

    key_bytes = str(plaintext_key).strip().encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(key_bytes, salt)
    return hashed.decode("utf-8")


def verify_api_key(plaintext_key: str, hash_value: str) -> bool:
    """Verify an API key against a bcrypt hash using timing-safe comparison.

    Args:
        plaintext_key: The raw API key to verify
        hash_value: The bcrypt hash to verify against

    Returns:
        True if key matches hash, False otherwise

    Raises:
        APIKeyError: If bcrypt is not installed
    """
    if not bcrypt:  # pragma: no cover
        raise APIKeyError("bcrypt is required for API key verification. Install via: pip install bcrypt")

    if not plaintext_key or not hash_value:
        return False

    try:
        key_bytes = str(plaintext_key).strip().encode("utf-8")
        hash_bytes = str(hash_value).strip().encode("utf-8")
        # bcrypt.checkpw is timing-safe (constant-time comparison)
        return bcrypt.checkpw(key_bytes, hash_bytes)
    except (ValueError, TypeError):
        # Invalid hash format
        return False


def compare_tokens_timing_safe(provided: str, expected: str) -> bool:
    """Compare two tokens using constant-time comparison to prevent timing attacks.

    This is used as a fallback for non-bcrypt keys (e.g., during migration).

    Args:
        provided: The token provided in the request
        expected: The token to compare against

    Returns:
        True if tokens match, False otherwise
    """
    # hmac.compare_digest is timing-safe (constant-time comparison)
    provided_str = str(provided or "").strip()
    expected_str = str(expected or "").strip()
    return hmac.compare_digest(provided_str, expected_str)


def validate_api_key_format(key: str) -> None:
    """Validate API key format requirements.

    Args:
        key: The API key to validate

    Raises:
        APIKeyError: If key does not meet requirements
    """
    key_str = str(key or "").strip()

    if not key_str:
        raise APIKeyError("API key must not be empty")

    if len(key_str) < 16:
        raise APIKeyError("API key must be at least 16 characters long")

    if len(key_str) > 512:
        raise APIKeyError("API key must not exceed 512 characters")

    # Allow alphanumeric, hyphen, underscore, dot, colon (common for tokens)
    if not all(c.isalnum() or c in "-_.:~" for c in key_str):
        raise APIKeyError("API key contains invalid characters. Use only alphanumeric and -_.:~")
