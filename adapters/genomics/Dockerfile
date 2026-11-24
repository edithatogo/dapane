# Copyright 2026 Dylan. SPDX-License-Identifier: Apache-2.0
FROM ghcr.io/astral-sh/uv:0.13.8@sha256:5cc1805e2426484abca4ad46ea783bab281fdb225fd82d8ce6d66a81254bac85 AS uv
FROM python:3.15.1-slim-trixie@sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51 AS base

FROM base AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PROJECT_ENVIRONMENT=/opt/genomics \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy
WORKDIR /build
COPY pyproject.toml uv.lock README.md LICENSE CITATION.cff config.yaml ./
COPY config/ config/
COPY configs/ configs/
COPY src/ src/
RUN uv sync --locked --no-dev --no-editable --python /usr/local/bin/python \
    --extra deployment --extra reporting --extra visualization

FROM base
COPY --from=build /opt/genomics /opt/genomics
RUN mkdir /prepared
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib
USER 10001:10001
WORKDIR /tmp
EXPOSE 8080
ENTRYPOINT ["/opt/genomics/bin/gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "genomics_microcosting.web:create_app('/prepared')"]
