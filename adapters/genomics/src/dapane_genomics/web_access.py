# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Apply request-scoped credentials, roles, rate limits and audit records."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Lock
from time import monotonic
from typing import TYPE_CHECKING, Literal, cast
from uuid import uuid4

from flask import Response, g, request
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from werkzeug.security import check_password_hash

from genomics_microcosting.security import AccessControlManager, AuditTrail

if TYPE_CHECKING:
    from flask import Flask


class _Credential(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    password_hash: str = Field(
        pattern=r"^scrypt:32768:8:1\$[a-zA-Z0-9]{8,64}\$[a-f0-9]{128}$"
    )
    role: Literal["admin", "analyst", "viewer"]


class _AccessConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    users: dict[str, _Credential] = Field(min_length=1)
    requests_per_minute: int = Field(default=120, ge=1, le=10000)
    audit_file: str | None = None


def _permission(endpoint: str) -> str:
    if endpoint.startswith("export_"):
        return "export_data"
    if endpoint == "api_generate_viz":
        return "run_analysis"
    if endpoint in {"generate_report", "metrics", "alerts"}:
        return "view_reports"
    if endpoint.startswith("operations."):
        return "run_analysis" if request.method == "POST" else "view_reports"
    return "read_data"


class _RequestLimit:
    """Keep a single minute of usage per configured account in this worker."""

    def __init__(self, requests_per_minute: int) -> None:
        self.limit = requests_per_minute
        self.lock = Lock()
        self.counts: dict[str, tuple[float, int]] = {}

    def allow(self, username: str) -> bool:
        with self.lock:
            now = monotonic()
            started, count = self.counts.get(username, (now, 0))
            if now - started >= 60:
                started, count = now, 0
            if count >= self.limit:
                return False
            self.counts[username] = (started, count + 1)
            return True


def install_web_access(app: Flask) -> None:
    """Configure credentials from the operator-selected access file."""
    source = os.environ.get("GENOMICS_WEB_ACCESS_FILE")
    try:
        configuration = (
            _AccessConfiguration.model_validate_json(Path(source).read_bytes())
            if source
            else None
        )
    except ValidationError:
        raise ValueError("Invalid dashboard access configuration") from None
    manager = AccessControlManager(logger=app.logger)
    limit = None
    trail = None
    audit_lock = Lock()
    if configuration:
        for username, account in configuration.users.items():
            manager.add_user_to_role(username, account.role)
        limit = _RequestLimit(configuration.requests_per_minute)
        trail = AuditTrail(log_file=configuration.audit_file, logger=app.logger)

    @app.before_request
    def authorize_request() -> Response | None:
        g.genomics_request_id = uuid4().hex
        g.genomics_username = None
        endpoint = request.endpoint
        if endpoint in {"health_check", "static"} or endpoint is None:
            return None
        if configuration is None or limit is None:
            if endpoint.startswith("operations."):
                return Response(
                    "Configure dashboard access to use operational APIs", 404
                )
            return None
        credential = request.authorization
        username = (
            credential.username if credential and credential.type == "basic" else None
        )
        password = (
            credential.password if credential and credential.type == "basic" else None
        )
        account = configuration.users.get(username) if username is not None else None
        if (
            username is None
            or account is None
            or password is None
            or not check_password_hash(account.password_hash, password)
        ):
            return Response(
                "Authentication required",
                401,
                {"WWW-Authenticate": 'Basic realm="Genomics"'},
            )
        g.genomics_username = username
        if _permission(endpoint) not in manager.get_user_permissions(username):
            return Response("Permission denied", 403)
        if not limit.allow(username):
            return Response("Request limit reached", 429, {"Retry-After": "60"})
        return None

    @app.after_request
    def record_request(response: Response) -> Response:
        request_id = cast("str", g.genomics_request_id)
        response.headers["X-Request-ID"] = request_id
        endpoint = request.endpoint
        if (
            trail is not None
            and endpoint is not None
            and endpoint not in {"health_check", "static"}
        ):
            with audit_lock:
                trail.log_event(
                    "http_request",
                    cast("str | None", g.genomics_username),
                    endpoint,
                    f"{request_id} {response.status_code}",
                    success=response.status_code < 400,
                )
                del trail.events[:-500]
        return response
