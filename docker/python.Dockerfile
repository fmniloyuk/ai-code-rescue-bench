FROM python:3.13-slim

ARG RUFF_VERSION=0.16.5
ARG MYPY_VERSION=2.3.1
ARG SEMGREP_VERSION=1.175.0
ARG TREE_SITTER_VERSION=0.26.0
ARG TREE_SITTER_PYTHON_VERSION=0.25.0

RUN python -m pip install --no-cache-dir \
    "pytest>=8.4,<9" \
    "fastapi>=0.116,<1" \
    "pydantic>=2.11,<3" \
    "sqlglot>=27,<28" \
    "ruff==${RUFF_VERSION}" \
    "mypy==${MYPY_VERSION}" \
    "semgrep==${SEMGREP_VERSION}" \
    "tree-sitter==${TREE_SITTER_VERSION}" \
    "tree-sitter-python==${TREE_SITTER_PYTHON_VERSION}"

COPY tools/tree_sitter_summary.py /opt/rescuebench/tree_sitter_summary.py
WORKDIR /workspace
