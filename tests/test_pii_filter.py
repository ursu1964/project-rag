from app.security.pii_filter import redact_sensitive_data, redact_sensitive_text


def test_redact_sensitive_text_masks_common_pii_and_secrets():
    text = "user ssn 123-45-6789 password=supersecret api_key: abc123"

    redacted = redact_sensitive_text(text)

    assert "123-45-6789" not in redacted
    assert "supersecret" not in redacted
    assert "abc123" not in redacted
    assert "[REDACTED_SSN]" in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_redact_sensitive_data_recurses_json_like_values():
    value = {"items": ["card 4111 1111 1111 1111"]}

    assert redact_sensitive_data(value) == {"items": ["card [REDACTED_CARD]"]}
