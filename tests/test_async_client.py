"""Cooperative total-deadline transport tests, all against synthetic mocks."""

import asyncio
import time

import httpx
import pytest

from ils_simpro.async_client import AsyncSimproClient, SimproDeadlineExceeded
from ils_simpro.client import (
    EndpointNotAllowed,
    LiveAccessDisabled,
    SimproConfig,
    SimproHTTPError,
    SimproResponseError,
    SimproTransportError,
)


def config(*, enabled: bool = True, max_bytes: int = 1024) -> SimproConfig:
    return SimproConfig(
        "https://example.invalid",
        live_enabled=enabled,
        allowed_paths=("/jobs/demo",),
        approved_hosts=("example.invalid",),
        max_response_bytes=max_bytes,
    )


def run_request(
    handler,
    *,
    deadline: float = 0.08,
    enabled: bool = True,
    path: str = "/jobs/demo",
    max_bytes: int = 1024,
):
    async def runner():
        async with AsyncSimproClient(
            config(enabled=enabled, max_bytes=max_bytes),
            transport=httpx.MockTransport(handler),
            token="FAKE-TOKEN-NOT-SECRET",
            deadline_seconds=deadline,
        ) as client:
            return await client.get_json(path)

    return asyncio.run(runner())


def test_fast_mock_get_is_read_only_and_decoded() -> None:
    seen = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"DEMO": 42})

    assert run_request(handler) == {"DEMO": 42}
    assert len(seen) == 1
    assert seen[0].method == "GET"
    assert seen[0].url.host == "example.invalid"


def test_disabled_gate_never_invokes_mock_handler() -> None:
    def forbidden(_request: httpx.Request) -> httpx.Response:
        pytest.fail("No request should be made")

    with pytest.raises(LiveAccessDisabled):
        run_request(forbidden, enabled=False)


def test_unlisted_path_rejected_before_mock_handler() -> None:
    def forbidden(_request: httpx.Request) -> httpx.Response:
        pytest.fail("No request should be made")

    with pytest.raises(EndpointNotAllowed):
        run_request(forbidden, path="/jobs/other")


def test_slow_response_headers_timeout() -> None:
    async def slow_headers(_request: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.15)
        return httpx.Response(200, json={"ok": True})

    start = time.monotonic()
    with pytest.raises(SimproDeadlineExceeded, match="Total request deadline exceeded"):
        run_request(slow_headers, deadline=0.04)
    assert time.monotonic() - start < 0.3


def test_trickling_body_exceeds_total_deadline() -> None:
    class Trickle(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"x":'
            for _ in range(20):
                await asyncio.sleep(0.02)
                yield b" "
            yield b"1}"

        async def aclose(self):
            pass

    async def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/json"},
            stream=Trickle(),
        )

    start = time.monotonic()
    with pytest.raises(SimproDeadlineExceeded):
        run_request(handler, deadline=0.09)
    assert time.monotonic() - start < 0.35


def test_aggregate_budget_accepts_fast_chunks() -> None:
    class Fast(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"'
            await asyncio.sleep(0)
            yield b'x":'
            yield b"1}"

        async def aclose(self):
            pass

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "application/json"}, stream=Fast())

    assert run_request(handler) == {"x": 1}


def test_oversized_stream_rejected_with_safe_error() -> None:
    with pytest.raises(SimproResponseError, match="JSON response rejected"):
        run_request(
            lambda _: httpx.Response(200, json={"huge": "x" * 200}),
            max_bytes=20,
        )


def test_rejected_status_contains_only_status_code() -> None:
    with pytest.raises(SimproHTTPError) as failure:
        run_request(lambda _: httpx.Response(403, text="private customer name"))
    assert failure.value.status_code == 403
    assert "private customer name" not in str(failure.value)


def test_httpx_transport_error_is_sanitized() -> None:
    def handler(request: httpx.Request):
        raise httpx.ReadError("credential-canary and customer payload", request=request)

    with pytest.raises(SimproTransportError) as failure:
        run_request(handler)
    assert "credential-canary" not in str(failure.value)
    assert failure.value.__cause__ is None


def test_invalid_json_is_sanitized() -> None:
    with pytest.raises(SimproResponseError, match="Invalid JSON response"):
        run_request(
            lambda _: httpx.Response(
                200, headers={"content-type": "application/json"}, content=b'{"x":NaN}'
            )
        )


@pytest.mark.parametrize("value", [0, -1, True, float("nan"), float("inf"), 121, "3"])
def test_invalid_deadlines_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        AsyncSimproClient(config(), deadline_seconds=value)


def test_mock_transport_required_when_explicitly_supplied() -> None:
    with pytest.raises(TypeError):
        AsyncSimproClient(config(), transport=httpx.AsyncHTTPTransport())


def test_client_honors_default_disabled_even_when_token_supplied() -> None:
    async def runner():
        async with AsyncSimproClient(
            SimproConfig("https://example.invalid", allowed_paths=("/jobs/demo",)),
            token="SYNTHETIC",
        ) as client:
            with pytest.raises(LiveAccessDisabled):
                await client.get_json("/jobs/demo")

    asyncio.run(runner())
