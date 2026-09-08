FROM python:3.13-slim
RUN python -m pip install --no-cache-dir "PyYAML>=6,<7" "sqlglot>=27,<28"
WORKDIR /workspace
