from unittest.mock import MagicMock

import app.tools.ollama_client as ollama_client


def test_create_embedding_posts_to_ollama(monkeypatch):
    response = MagicMock()
    response.json.return_value = {"embedding": [0.1, 0.2]}
    post = MagicMock(return_value=response)
    monkeypatch.setattr(ollama_client.requests, "post", post)

    result = ollama_client.create_embedding("hello")

    assert result == [0.1, 0.2]
    response.raise_for_status.assert_called_once()
    post.assert_called_once_with(
        f"{ollama_client.settings.ollama_url.rstrip('/')}/api/embeddings",
        json={"model": ollama_client.settings.embedding_model, "prompt": "hello"},
        timeout=ollama_client._TIMEOUT_SECONDS,
    )


def test_generate_posts_to_ollama(monkeypatch):
    response = MagicMock()
    response.json.return_value = {"response": "answer"}
    post = MagicMock(return_value=response)
    monkeypatch.setattr(ollama_client.requests, "post", post)

    result = ollama_client.generate("question")

    assert result == "answer"
    response.raise_for_status.assert_called_once()
    post.assert_called_once_with(
        f"{ollama_client.settings.ollama_url.rstrip('/')}/api/generate",
        json={"model": ollama_client.settings.ollama_model, "prompt": "question", "stream": False},
        timeout=ollama_client._TIMEOUT_SECONDS,
    )
