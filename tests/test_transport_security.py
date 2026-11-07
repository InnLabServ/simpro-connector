"""Safety and response-hardening regression tests for restricted transport."""

import gzip

import httpx
import pytest

from ils_simpro.client import (
    EndpointNotAllowed,
    LiveAccessDisabled,
    SimproClient,
    SimproConfig,
    SimproHTTPError,
    SimproResponseError,
    SimproTransportError,
)


def _mock(response: httpx.Response, **kwargs: object) -> SimproClient:
    config = SimproConfig(
        "https://example.invalid/api",
        live_enabled=True,
        allowed_paths=("/jobs/demo",),
        **kwargs,
    )
    return SimproClient(config, transport=httpx.MockTransport(lambda _req: response))


@pytest.mark.parametrize("value", ["false", "0", "False", 1, 0, None, [], object()])
def test_live_flag_requires_actual_boolean(value: object) -> None:
    with pytest.raises(TypeError):
        SimproConfig("https://example.invalid", live_enabled=value)


def test_allowlist_defensively_copied_and_config_readonly() -> None:
    paths = ["/jobs/demo"]
    config = SimproConfig("https://example.invalid", allowed_paths=paths)
    paths.append("/admin")
    assert config.allowed_paths == ("/jobs/demo",)
    with pytest.raises(AttributeError):
        SimproClient(config).config = SimproConfig("https://example.invalid")


@pytest.mark.parametrize("value", ["/", "//other/x", "/jobs/../admin", "/a/%2e", "/a?x=1", "/a\\b", "/a//b"])
def test_unsafe_paths_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        SimproConfig("https://example.invalid", allowed_paths=(value,))


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1",
        "https://169.254.169.254",
        "https://localhost",
        "https://[::1]",
        "https://example.invalid:99999",
        "https://@example.invalid",
        " https://example.invalid",
        "https://exa mple.invalid",
        "https://example.invalid。evil.test",
    ],
)
def test_unapproved_base_url_formats_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        SimproConfig(url)


def test_source_host_and_base_path_preserved() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"ok": True})

    config = SimproConfig(
        "https://example.invalid/api",
        live_enabled=True,
        allowed_paths=("/jobs/demo",),
    )
    with SimproClient(config, transport=httpx.MockTransport(handler)) as client:
        assert client.get_json("/jobs/demo") == {"ok": True}
    assert seen[0].url.path == "/api/jobs/demo"
    assert seen[0].url.host == "example.invalid"
    assert seen[0].method == "GET"


@pytest.mark.parametrize("body", [b'{"ok": NaN}', b'{"ok":true,"ok":false}', b"<html></html>"])
def test_rejects_malformed_json_without_payload_leak(body: bytes) -> None:
    with _mock(httpx.Response(200, content=body, headers={"Content-Type": "application/json"})) as client:
        with pytest.raises(SimproResponseError) as raised:
            client.get_json("/jobs/demo")
    assert body.decode() not in repr(raised.value)


def test_rejects_compression_and_oversized_content() -> None:
    compressed = gzip.compress(b"X" * 1000000)
    response = httpx.Response(
        200,
        content=compressed,
        headers={"Content-Type": "application/json", "Content-Encoding": "gzip"},
    )
    with _mock(response) as client:
        with pytest.raises(SimproResponseError):
            client.get_json("/jobs/demo")
    response = httpx.Response(
        200,
        content=b" " * 128,
        headers={"Content-Type": "application/json"},
    )
    with _mock(response, max_response_bytes=64) as client:
        with pytest.raises(SimproResponseError):
            client.get_json("/jobs/demo")


def test_http_exception_has_no_headers_or_response() -> None:
    response = httpx.Response(
        401,
        json={"secret": "SENSITIVE-BODY"},
        headers={"Location": "https://example.invalid/?private=1"},
    )
    config = SimproConfig("https://example.invalid", live_enabled=True, allowed_paths=("/jobs/demo",))
    with SimproClient(config, transport=httpx.MockTransport(lambda _req: response), token="SECRET-TOKEN") as client:
        with pytest.raises(SimproHTTPError) as raised:
            client.get_json("/jobs/demo")
    error = raised.value
    assert error.status_code == 401
    assert "SECRET-TOKEN" not in repr(error)
    assert "SENSITIVE-BODY" not in repr(error)
    assert "request" not in vars(error)
    assert "response" not in vars(error)
    assert error.__context__ is None


def test_transport_failure_sanitized() -> None:
    def fail(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("sensitive-url-or-token")
    config = SimproConfig("https://example.invalid", live_enabled=True, allowed_paths=("/jobs/demo",))
    with SimproClient(config, transport=httpx.MockTransport(fail), token="SECRET-TOKEN") as client:
        with pytest.raises(SimproTransportError) as raised:
            client.get_json("/jobs/demo")
    assert raised.value.__context__ is None


def test_no_live_network_without_approved_host_and_token() -> None:
    config = SimproConfig("https://example.invalid", live_enabled=True, allowed_paths=("/jobs/demo",))
    with SimproClient(config) as client:
        with pytest.raises(LiveAccessDisabled):
            client.get_json("/jobs/demo")


def test_nonstring_path_fails_closed() -> None:
    config = SimproConfig("https://example.invalid", live_enabled=True, allowed_paths=("/jobs/demo",))
    with SimproClient(config, transport=httpx.MockTransport(lambda _r: pytest.fail("network"))) as client:
        with pytest.raises(EndpointNotAllowed):
            client.get_json(123)
