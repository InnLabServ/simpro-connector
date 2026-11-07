"""Fail-closed, read-only transport. No production credentials or endpoints included."""

import ipaddress
import json
import re
import time
from dataclasses import dataclass
from typing import Self

import httpx

_PATH_SEGMENT = re.compile(r"[A-Za-z0-9_.~-]+\Z")
_HOST_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\Z")
_DEFAULT_MAX_BYTES = 5 * 1024 * 1024


class SimproError(Exception):
    """Sanitized outward-facing exception, without raw HTTP objects."""


class LiveAccessDisabled(SimproError):
    """The live transport has not been explicitly configured."""


class EndpointNotAllowed(SimproError):
    """The requested endpoint is not precisely allowlisted."""


class SimproTransportError(SimproError):
    """A transport problem; underlying request details are withheld."""


class SimproResponseError(SimproError):
    """A response was malformed, oversized or unsupported."""


class SimproHTTPError(SimproError):
    """HTTP status error without headers, URLs or response body."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"Simpro HTTP status {status_code}")


def _safe_path(value: str) -> bool:
    if type(value) is not str or not value.startswith("/") or value.startswith("//"):
        return False
    segments = value.split("/")[1:]
    return bool(segments) and all(
        segment not in ("", ".", "..") and _PATH_SEGMENT.fullmatch(segment)
        for segment in segments
    )


def _safe_host(host: str) -> bool:
    if not host or not host.isascii() or host == "localhost":
        return False
    if host.endswith((".local", ".internal", ".localhost")):
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return "." in host and all(_HOST_LABEL.fullmatch(label) for label in host.split("."))
    return False


@dataclass(frozen=True)
class SimproConfig:
    base_url: str
    live_enabled: bool = False
    allowed_paths: tuple[str, ...] = ()
    approved_hosts: tuple[str, ...] = ()
    max_response_bytes: int = _DEFAULT_MAX_BYTES

    def __post_init__(self) -> None:
        if type(self.live_enabled) is not bool:
            raise TypeError("live_enabled must be bool")
        if type(self.base_url) is not str or not self.base_url.isascii():
            raise ValueError("base_url must be an ASCII HTTPS URL")
        if self.base_url != self.base_url.strip() or any(c.isspace() for c in self.base_url):
            raise ValueError("base_url must not contain whitespace")
        if any(c in self.base_url for c in ("@", "?", "#")):
            raise ValueError("base_url must not contain userinfo, query or fragment")
        try:
            url = httpx.URL(self.base_url)
        except (ValueError, httpx.InvalidURL):
            raise ValueError("Invalid base_url") from None
        if url.scheme != "https" or not _safe_host(url.host or "") or url.port not in (None, 443):
            raise ValueError("base_url requires HTTPS DNS hostname on port 443")
        base_path = url.path.rstrip("/")
        if base_path and not _safe_path(base_path):
            raise ValueError("Invalid base_url path")
        for attribute in ("allowed_paths", "approved_hosts"):
            value = getattr(self, attribute)
            if type(value) not in (tuple, list):
                raise TypeError(f"{attribute} must be a tuple or list")
            if any(type(entry) is not str for entry in value):
                raise TypeError(f"{attribute} requires plain strings")
            object.__setattr__(self, attribute, tuple(value))
        if any(not _safe_path(path) for path in self.allowed_paths):
            raise ValueError("Unsafe allowed_paths entry")
        if any(not _safe_host(host) or host != host.lower() for host in self.approved_hosts):
            raise ValueError("Invalid approved host")
        if type(self.max_response_bytes) is not int or not 1 <= self.max_response_bytes <= 10 * 1024 * 1024:
            raise ValueError("max_response_bytes out of range")
        if self.live_enabled and not self.allowed_paths:
            raise ValueError("Live access requires nonempty allowlist")


class SimproClient:
    def __init__(
        self,
        config: SimproConfig,
        *,
        transport: httpx.BaseTransport | None = None,
        token: str | None = None,
    ) -> None:
        if type(config) is not SimproConfig:
            raise TypeError("config must be SimproConfig")
        if token is not None and (
            type(token) is not str or not token or any(c.isspace() for c in token)
        ):
            raise ValueError("Invalid token")
        self._config = config
        self._token = token
        self._test_transport = transport is not None
        self._base = httpx.URL(config.base_url)
        self._http = httpx.Client(
            base_url=config.base_url,
            transport=transport,
            timeout=httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0),
            follow_redirects=False,
            trust_env=False,
        )

    @property
    def config(self) -> SimproConfig:
        return self._config

    def get_json(self, path: str) -> object:
        """Fetch allowlisted JSON without attaching raw HTTP objects to exceptions."""
        if not self._config.live_enabled:
            raise LiveAccessDisabled("Live access disabled")
        if type(path) is not str or path not in self._config.allowed_paths or not _safe_path(path):
            raise EndpointNotAllowed("Endpoint not allowlisted")
        if not self._test_transport and (
            not self._token or self._base.host not in self._config.approved_hosts
        ):
            raise LiveAccessDisabled("Authorized hostname and credential required")
        headers = {"Accept": "application/json", "Accept-Encoding": "identity"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        request = self._http.build_request("GET", path, headers=headers)
        expected = self._base.path.rstrip("/") + path
        if (
            request.url.host != self._base.host
            or request.url.scheme != "https"
            or request.url.path != expected
            or request.url.query
        ):
            raise EndpointNotAllowed("Endpoint normalized to unexpected destination")
        status: int | None = None
        response_error = False
        transport_error = False
        body = bytearray()
        started = time.monotonic()
        try:
            with self._http.stream("GET", path, headers=headers) as response:
                status = response.status_code
                if not 200 <= status < 300:
                    pass
                elif (
                    status == 204
                    or response.headers.get("content-type", "").split(";")[0].strip().lower()
                    != "application/json"
                    or response.headers.get("content-encoding", "identity").lower()
                    not in ("", "identity")
                ):
                    response_error = True
                else:
                    # Reject compressed bodies. Their expansion would bypass a raw-byte cap.
                    # Some mock transports supply a pre-consumed response.
                    chunks = (
                        (response.content,)
                        if response.is_stream_consumed
                        else response.iter_raw(chunk_size=8192)
                    )
                    for chunk in chunks:
                        if time.monotonic() - started > 20 or len(body) + len(chunk) > self._config.max_response_bytes:
                            response_error = True
                            break
                        body.extend(chunk)
        except Exception:
            # Deliberately raise only after leaving the handler. Underlying httpx
            # exceptions retain request auth headers and potentially response data.
            transport_error = True
        if transport_error:
            raise SimproTransportError("Request could not be completed")
        if status is not None and not 200 <= status < 300:
            raise SimproHTTPError(status)
        if response_error:
            raise SimproResponseError("JSON response rejected")
        invalid = False
        result: object = None
        try:
            result = json.loads(
                body.decode("utf-8"),
                parse_constant=_reject_constant,
                object_pairs_hook=_reject_duplicate_keys,
            )
        except (ValueError, UnicodeError, RecursionError):
            invalid = True
        if invalid:
            raise SimproResponseError("Invalid JSON response")
        return result

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def _reject_constant(_value: str) -> None:
    raise ValueError("Non-finite JSON literal")


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result
