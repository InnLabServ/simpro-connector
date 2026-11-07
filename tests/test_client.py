"""Safety checks for the transport boundary."""

import httpx
import pytest

from ils_simpro.client import (
    EndpointNotAllowed,
    LiveAccessDisabled,
    SimproClient,
    SimproConfig,
)


def test_live_access_disabled_even_with_token() -> None:
    with (
        SimproClient(
            SimproConfig("https://example.invalid", allowed_paths=("/jobs/demo",)),
            token="never-real",
        ) as client,
        pytest.raises(LiveAccessDisabled),
    ):
        client.get_json("/jobs/demo")


def test_unlisted_path_rejected_before_network() -> None:
    config = SimproConfig(
        "https://example.invalid", live_enabled=True, allowed_paths=("/jobs/demo",)
    )
    with (
        SimproClient(config, transport=httpx.MockTransport(lambda _: pytest.fail("network"))) as client,
        pytest.raises(EndpointNotAllowed),
    ):
        client.get_json("/jobs/other")


def test_explicit_get_with_mock_transport() -> None:
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"id": "DEMO-1001"})

    config = SimproConfig(
        "https://example.invalid", live_enabled=True, allowed_paths=("/jobs/demo",), approved_hosts=("example.invalid",)
    )
    with SimproClient(config, transport=httpx.MockTransport(handler), token="CANARY-TOKEN") as client:
        assert client.get_json("/jobs/demo") == {"id": "DEMO-1001"}
    assert len(seen) == 1
    assert seen[0].method == "GET"
    assert seen[0].url.host == "example.invalid"


@pytest.mark.parametrize(
    "base_url",
    ["http://example.invalid", "https://user:secret@example.invalid", "not-a-url"],
)
def test_unsafe_base_url_rejected(base_url: str) -> None:
    with pytest.raises(ValueError):
        SimproConfig(base_url)
