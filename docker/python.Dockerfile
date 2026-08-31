FROM python:3.13-slim

ARG RUFF_VERSION=0.16.5
ARG MYPY_VERSION=2.3.1
ARG SEMGREP_VERSION=1.175.0

RUN python -m pip install --no-cache-dir \
    "pytest>=8.4,<9" \
    "fastapi>=0.116,<1" \
    "pydantic>=2.11,<3" \
    "sqlglot>=27,<28" \
    "ruff==${RUFF_VERSION}" \
    "mypy==${MYPY_VERSION}" \
    "semgrep==${SEMGREP_VERSION}"

WORKDIR /workspace
