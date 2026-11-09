"""Cooperatively deadline-bounded async GET transport for fabricated/mock responses.

This is not a hard preemptive wall-clock limit: blocking synchronous callbacks,
non-cooperative transports, DNS and some C extensions may ignore cancellation.
The existing synchronous SimproClient is deliberately unchanged.
"""

import asyncio
import json
import math
import re
from contextlib import aclosing
from typing import Self

import httpx

from .client import (
    EndpointNotAllowed,
    LiveAccessDisabled,
    SimproConfig,
    SimproError,
    SimproHTTPError,
    SimproResponseError,
    SimproTransportError,
    _finite_float,
    _reject_constant,
    _reject_duplicate_keys,
    _safe_path,
)


class SimproDeadlineExceeded(SimproError):
    """The cooperative total request deadline expired."""


class AsyncSimproClient:
    """GET-only async client; no endpoint discovery, credentials or live pilot."""

    def __init__(
        self,
        config: SimproConfig,
        *,
        transport: httpx.MockTransport | None = None,
        token: str | None = None,
        deadline_seconds: float = 20.0,
    ) -> None:
        if type(config) is not SimproConfig:
            raise TypeError("config must be SimproConfig")
        if type(deadline_seconds) not in (int, float) or not (
            math.isfinite(deadline_seconds) and 0.01 <= deadline_seconds <= 120.0
        ):
            raise ValueError("deadline_seconds must be finite and between 0.01 and 120")
        if token is not None and (
            type(token) is not str or re.fullmatch(r"[\x21-\x7e]+", token) is None
        ):
            raise ValueError("Invalid token")
        if transport is not None and type(transport) is not httpx.MockTransport:
            raise TypeError("Only an HTTPX MockTransport is accepted for tests")
        self._config = config
        self._base = httpx.URL(config.base_url)
        self._token = token
        self._deadline = float(deadline_seconds)
        self._http = httpx.AsyncClient(
            base_url=config.base_url,
            transport=transport,
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
            follow_redirects=False,
            trust_env=False,
        )

    async def get_json(self, path: str) -> object:
        """Enforce a total asyncio deadline for cooperative async operations.

        URL/credential/path checking is performed before scheduling any I/O.
        Exception text and exception chains never include raw HTTP messages.
        """
        if self._config.live_enabled is not True:
            raise LiveAccessDisabled("Live access disabled")
        if type(path) is not str or path not in self._config.allowed_paths or not _safe_path(path):
            raise EndpointNotAllowed("Endpoint not allowlisted")
        if not self._token or self._base.host not in self._config.approved_hosts:
            raise LiveAccessDisabled("Authorized hostname and credential required")

        try:
            async with asyncio.timeout(self._deadline):
                outcome, value = await self._perform_request(path)
        except TimeoutError:
            raise SimproDeadlineExceeded("Total request deadline exceeded") from None
        if outcome == "destination":
            raise EndpointNotAllowed("Endpoint normalized to unexpected destination")
        if outcome == "transport":
            raise SimproTransportError("Request could not be completed")
        if outcome == "status":
            raise SimproHTTPError(value)
        if outcome == "response":
            raise SimproResponseError("JSON response rejected")
        if outcome == "json":
            raise SimproResponseError("Invalid JSON response")
        if outcome == "ok":
            return value
        raise SimproError("Unexpected transport outcome")

    async def _perform_request(self, path: str) -> tuple[str, object]:
        """Keep raw transport objects and their errors inside a sanitized boundary."""
        headers = {"Accept": "application/json", "Accept-Encoding": "identity"}
        headers["Authorization"] = f"Bearer {self._token}"
        try:
            request = self._http.build_request("GET", path, headers=headers)
            expected = self._base.path.rstrip("/") + path
            if (
                request.url.host != self._base.host
                or request.url.scheme != "https"
                or request.url.path != expected
                or request.url.query
            ):
                return ("destination", None)
            body = bytearray()
            async with aclosing(await self._http.send(request, stream=True)) as response:
                if response.status_code != 200:
                    return ("status", response.status_code)
                if (
                    response.headers.get("content-type", "").split(";")[0].strip().lower()
                    != "application/json"
                    or response.headers.get("content-encoding", "identity").lower()
                    not in ("", "identity")
                ):
                    return ("response", None)
                async for chunk in response.aiter_raw():
                    if len(body) + len(chunk) > self._config.max_response_bytes:
                        return ("response", None)
                    body.extend(chunk)
            try:
                value = json.loads(
                    body.decode("utf-8"),
                    parse_constant=_reject_constant,
                    parse_float=_finite_float,
                    object_pairs_hook=_reject_duplicate_keys,
                )
            except (ValueError, UnicodeError, RecursionError):
                return ("json", None)
            return ("ok", value)
        except (httpx.HTTPError, OSError):
            return ("transport", None)

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
