FROM python:3.15.0a8-alpine3.23
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV TZ America/New_York
ENV C_FORCE_ROOT true
ENV UV_LINK_MODE=copy

RUN apk update && \
    apk add \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    bash \
    git

WORKDIR /tjstar