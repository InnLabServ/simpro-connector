"""Strict GET-only transport; no provider-specific endpoints are presumed."""

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx


class LiveAccessDisabled(RuntimeError):
    """Raised when a live request is attempted without explicit enablement."""


class EndpointNotAllowed(ValueError):
    """Raised when an endpoint is not explicitly allowlisted."""


@dataclass(frozen=True)
class SimproConfig:
    base_url: str
    live_enabled: bool = False
    allowed_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in ("https",) or not parsed.netloc:
            raise ValueError("base_url must be an absolute HTTPS URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain credentials, query or fragment")
        if any(not path.startswith("/") or "?" in path or "#" in path for path in self.allowed_paths):
            raise ValueError("allowed_paths must contain absolute paths without queries")


class SimproClient:
    def __init__(
        self,
        config: SimproConfig,
        *,
        transport: httpx.BaseTransport | None = None,
        token: str | None = None,
    ) -> None:
        self.config = config
        self._token = token
        self._http = httpx.Client(
            base_url=config.base_url,
            transport=transport,
            timeout=10.0,
            follow_redirects=False,
            trust_env=False,
        )

    def get_json(self, path: str) -> object:
        """Fetch an explicitly allowed path. Never logs payloads or credentials."""
        if not self.config.live_enabled:
            raise LiveAccessDisabled("Live access is disabled by default")
        if path not in self.config.allowed_paths:
            raise EndpointNotAllowed("Endpoint not allowlisted")
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        response = self._http.get(path, headers=headers)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SimproClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
