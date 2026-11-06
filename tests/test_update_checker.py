from __future__ import annotations

import json
import ssl

import src.core.update_checker as update_checker
from src.core.update_checker import (
    LATEST_EXECUTABLE_DOWNLOAD_URL,
    LATEST_RELEASE_PAGE_URL,
    check_latest_release,
    is_version_newer,
)


def test_is_version_newer_compares_semantic_parts() -> None:
    assert is_version_newer("v1.10.0", "1.9.1")
    assert is_version_newer("1.9.2", "1.9.1")
    assert not is_version_newer("1.9.1", "1.9.1")
    assert not is_version_newer("1.8.9", "1.9.1")


def test_check_latest_release_uses_github_payload() -> None:
    result = check_latest_release(
        "1.9.1",
        opener=fake_opener(
            {
                "tag_name": "v1.10.0",
                "html_url": "https://github.com/machado-jean/ied-backup-tool/releases/tag/v1.10.0",
            }
        ),
    )

    assert result.current_version == "1.9.1"
    assert result.latest_version == "1.10.0"
    assert result.update_available is True
    assert result.release_url == LATEST_EXECUTABLE_DOWNLOAD_URL
    assert result.release_page_url.endswith("/releases/tag/v1.10.0")


def test_check_latest_release_uses_latest_download_url_when_current() -> None:
    result = check_latest_release("1.10.0", opener=fake_opener({"tag_name": "v1.10.0"}))

    assert result.update_available is False
    assert result.release_url == LATEST_EXECUTABLE_DOWNLOAD_URL
    assert result.release_page_url == LATEST_RELEASE_PAGE_URL
    assert LATEST_RELEASE_PAGE_URL.endswith("/releases/latest")


def test_default_update_check_uses_native_tls_context(monkeypatch) -> None:
    expected_context = object()
    captured = {}

    monkeypatch.setattr(update_checker, "_native_tls_context", lambda: expected_context)

    def native_opener(_request, *, timeout: float, context):
        captured["timeout"] = timeout
        captured["context"] = context
        return FakeResponse({"tag_name": "v1.18.0"})

    monkeypatch.setattr(update_checker, "urlopen", native_opener)

    result = check_latest_release("1.17.0")

    assert result.latest_version == "1.18.0"
    assert captured == {"timeout": 4, "context": expected_context}


def test_native_tls_context_keeps_certificate_and_hostname_validation() -> None:
    context = update_checker._native_tls_context()

    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


class FakeResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def fake_opener(payload: dict[str, str]):
    def opener(_request, *, timeout: float):
        assert timeout > 0
        return FakeResponse(payload)

    return opener
