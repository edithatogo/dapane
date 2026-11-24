# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
"""Local template customization using the same inputs as the model CLI."""

from io import BytesIO

from flask import Blueprint, Response, render_template, request, send_file
from pydantic import ValidationError

from .model_tables import FORMATS, MODELS, LabProfile, model_template_bytes

_MAX_PROFILE_BYTES = 64 * 1024
_MIMETYPES = {
    "csv": "text/csv",
    "json": "application/json",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

models = Blueprint("models", __name__)


@models.get("/models")
def show_templates() -> str:
    """Render the local model and profile form."""
    return render_template("models.html", models=MODELS, formats=FORMATS)


@models.post("/models/template")
def download_template() -> Response | tuple[str, int]:
    """Return a template using a bounded inline or uploaded JSON profile."""
    request.max_content_length = _MAX_PROFILE_BYTES + 8192
    model = request.form.get("model", "")
    format_name = request.form.get("format", "")
    entered_profile = request.form.get("profile", "").strip()
    uploaded_profile = request.files.get("profile_file")
    payload = entered_profile.encode()
    if uploaded_profile:
        if entered_profile:
            return "Choose one profile source.", 400
        payload = uploaded_profile.stream.read(_MAX_PROFILE_BYTES + 1)
    if len(payload) > _MAX_PROFILE_BYTES:
        return "The profile exceeds 64 KiB.", 413
    try:
        profile = LabProfile.model_validate_json(payload) if payload else None
        template = model_template_bytes(model, format_name, profile)
    except ValidationError:
        return "Enter a valid lab profile with plain-text names and labels.", 400
    except ValueError:
        return "Choose a listed model and format.", 400
    return send_file(
        BytesIO(template),
        mimetype=_MIMETYPES[format_name],
        as_attachment=True,
        download_name=f"{model}.{format_name}",
        max_age=0,
    )
